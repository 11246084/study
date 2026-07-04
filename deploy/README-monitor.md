# VM 監看與壓測(4 vCPU / 4 GiB,預計 55 人)

兩件事:**平時監看**知道 VM 現在的水位、**收案前壓測**確認 55 人不會爆。

## A. 平時監看 — `deploy/monitor.sh`

每分鐘記一行到 `/var/log/study_health.log`,記憶體/硬碟過線就寫 `[ALERT]`。

安裝(在 VM 上):

```bash
chmod +x /opt/study/deploy/monitor.sh
crontab -e
# 加入這行:
* * * * * /opt/study/deploy/monitor.sh
```

看即時水位:

```bash
tail -f /var/log/study_health.log
```

每行長這樣:
```
2026-07-04 14:30:01 mem_avail=42% disk_free=71% load1=0.35 swap_used=0MB gunicorn=680MB mysql=520MB
```

判讀:
- `mem_avail` **< 15%** → 記憶體吃緊,快被 OOM Killer 砍。
- `disk_free` **< 10%** → 硬碟快滿(事件量大要特別顧)。
- `load1` 持續 **> 4**(= vCPU 數)→ CPU 塞車。
- `swap_used` 一直漲 → 記憶體不夠、開始吃 swap,會變慢。

### 想被主動通知(選配)

把 `monitor.sh` 裡的 `ALERT_CMD()` 換成你的通知方式,例如 Telegram bot:

```bash
ALERT_CMD() {
  curl -s "https://api.telegram.org/bot<TOKEN>/sendMessage" \
    -d chat_id=<CHAT_ID> -d text="AdaptLearn VM: $1" >/dev/null
}
```

## B. 收案前壓測 — `backend/loadtest/`

真正回答「55 人會不會爆」的方法:模擬 55 人登入 → 讀教材 → 集體交卷,一邊看 `htop`。

### 1. 準備(在 VM 上,backend/ 目錄)

```bash
python manage.py seed_test_students --count 55   # 建 loadtest001~055 測試帳號
# 到 管理中心 → 學習路徑,至少打開 Unit 1,quiz 才進得去
```

### 2. 跑壓測(在你自己的電腦,不要在 VM 上跑)

```bash
pip install -r backend/loadtest/requirements.txt
locust -f backend/loadtest/locustfile.py --host http://140.131.115.76
```

開 http://localhost:8089,設 **Users = 55、Ramp up = 10**,開始。

集體交卷尖峰(無頭模式、2 分鐘):

```bash
locust -f backend/loadtest/locustfile.py --host http://140.131.115.76 \
       --headless -u 55 -r 55 -t 2m
```

### 3. 判讀

同時在 VM 開 `htop` 和 `free -h`,看壓測期間:

| 觀察 | 沒問題 | 要處理 |
|------|--------|--------|
| locust Failures | 0% | 出現 5xx / timeout |
| locust p95 延遲 | 平穩、< 1s | 隨人數飆高 |
| VM `mem_avail` | 還有 > 15% | 逼近 0、開始用 swap |
| VM `load1` | < 4 | 長時間 > 4 |

全綠 = 55 人穩。若記憶體逼近上限 → 照下面調 gunicorn + 加 swap。

### 4. 收案前務必清掉測試帳號

```bash
python manage.py seed_test_students --delete
```

## C. 建議的保命設定(壓測前先套)

**gunicorn 降 worker、加 gthread**(4 GiB 別開預設 9 個 worker):編輯
`/etc/systemd/system/gunicorn.service` 的 ExecStart:

```
--workers 4 --threads 4 --worker-class gthread --max-requests 1000 --max-requests-jitter 100
```
`sudo systemctl daemon-reload && sudo systemctl restart gunicorn`

**加 2 GB swap 當保命符**:

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```
