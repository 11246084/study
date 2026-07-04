#!/usr/bin/env bash
# Lightweight health monitor for the AdaptLearn VM (4 vCPU / 4 GiB).
# Logs a one-line water level every run and warns when memory or disk gets low.
#
# Install (on the VM):
#   sudo cp /opt/study/deploy/monitor.sh /opt/study/monitor.sh
#   chmod +x /opt/study/monitor.sh
#   crontab -e   ->   add:  * * * * * /opt/study/monitor.sh
#
# Read the log:      tail -f /var/log/study_health.log
# During a load test, run:  watch -n2 tail -n1 /var/log/study_health.log
#
# Warnings go to the log; wire ALERT_CMD below to email/LINE/Telegram if you
# want to be pinged. Left as an echo by default so nothing breaks silently.

set -u
LOG=/var/log/study_health.log
MEM_WARN=15   # warn when available memory drops below this %
DISK_WARN=10  # warn when free disk drops below this %

# Available memory as a percentage of total.
read -r mem_total mem_avail < <(awk '
  /^MemTotal:/     {t=$2}
  /^MemAvailable:/ {a=$2}
  END {print t, a}' /proc/meminfo)
mem_avail_pct=$(( mem_avail * 100 / mem_total ))

# Free disk on root as a percentage.
disk_used_pct=$(df --output=pcent / | tail -1 | tr -dc '0-9')
disk_free_pct=$(( 100 - disk_used_pct ))

# 1-minute load average and swap in use (MB).
loadavg=$(awk '{print $1}' /proc/loadavg)
swap_used=$(awk '/^SwapTotal:/{t=$2} /^SwapFree:/{f=$2} END{print (t-f)/1024}' /proc/meminfo)

# gunicorn + mysqld resident memory (MB), if present.
gunicorn_mb=$(ps -C gunicorn -o rss= 2>/dev/null | awk '{s+=$1} END{printf "%d", s/1024}')
mysql_mb=$(ps -C mysqld -o rss= 2>/dev/null | awk '{s+=$1} END{printf "%d", s/1024}')

line="$(date '+%F %T') mem_avail=${mem_avail_pct}% disk_free=${disk_free_pct}% load1=${loadavg} swap_used=${swap_used%.*}MB gunicorn=${gunicorn_mb:-0}MB mysql=${mysql_mb:-0}MB"
echo "$line" >> "$LOG"

# ---- Alerting: replace the echo with your notifier (see README-monitor.md) ----
ALERT_CMD() { echo "[ALERT] $1" >> "$LOG"; }

if [ "$mem_avail_pct" -lt "$MEM_WARN" ]; then
  ALERT_CMD "記憶體吃緊: available=${mem_avail_pct}% (gunicorn=${gunicorn_mb}MB mysql=${mysql_mb}MB)"
fi
if [ "$disk_free_pct" -lt "$DISK_WARN" ]; then
  ALERT_CMD "硬碟快滿: free=${disk_free_pct}%"
fi
