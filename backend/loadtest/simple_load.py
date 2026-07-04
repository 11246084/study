"""Dependency-free load test for AdaptLearn (stdlib only — no pip/gevent needed).

Simulates N students hitting the platform concurrently: login, dashboard reads,
lesson reads, event batches, and the heavy quiz start->submit path. Prints live
progress and a final latency/error summary so you can see if 55 users is fine.

Run it from a machine OTHER than the VM (so the load generator doesn't steal the
server's CPU). Any Python 3.8+ works — no installation required.

    python backend/loadtest/simple_load.py --host http://140.131.115.76 \
           --users 55 --duration 120 --ramp 10

Prep first (on the VM, from backend/):
    python manage.py seed_test_students --count 55
    # then open at least Unit 1 in 管理中心 so quizzes are reachable

Read the result:
    Failures should be ~0%. p95 latency should stay well under 1s. If p95 climbs
    or failures appear, the server hit a ceiling — check gunicorn workers / VM
    memory (tail -f /var/log/study_health.log on the VM while this runs).
"""
import argparse
import json
import random
import threading
import time
import urllib.error
import urllib.request
from collections import defaultdict

# ---- stats (shared across threads, guarded by a lock) -----------------------
_lock = threading.Lock()
_latencies = defaultdict(list)   # endpoint name -> [seconds, ...]
_errors = defaultdict(int)       # endpoint name -> count
_counts = defaultdict(int)       # endpoint name -> count
_stop = threading.Event()


def record(name, elapsed, ok):
    with _lock:
        _counts[name] += 1
        _latencies[name].append(elapsed)
        if not ok:
            _errors[name] += 1


def call(method, url, name, token=None, body=None, expect=(200, 201)):
    """One HTTP call; returns (ok, parsed_json_or_None). Never raises."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read()
            ok = resp.status in expect
            elapsed = time.perf_counter() - start
            record(name, elapsed, ok)
            try:
                return ok, json.loads(payload) if payload else None
            except json.JSONDecodeError:
                return ok, None
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - start
        # For quiz start, a closed unit legitimately returns 403 — not a failure.
        ok = e.code in expect
        record(name, elapsed, ok)
        return ok, None
    except Exception:
        elapsed = time.perf_counter() - start
        record(name, elapsed, False)
        return False, None


def student_loop(base, username, password, deadline):
    """One simulated student: login once, then act until the deadline."""
    ok, data = call('POST', f'{base}/api/auth/login/', 'auth/login',
                    body={'username': username, 'password': password})
    token = data.get('access') if (ok and data) else None
    if not token:
        return

    while not _stop.is_set() and time.time() < deadline:
        roll = random.random()
        if roll < 0.45:                      # dashboard (most common)
            call('GET', f'{base}/api/learning/adaptive-path/', 'learning/adaptive-path', token)
            call('GET', f'{base}/api/learning/progress/', 'learning/progress', token)
        elif roll < 0.70:                    # read a lesson + heartbeat
            lid = random.randint(1, 24)
            call('GET', f'{base}/api/courses/lesson/{lid}/', 'courses/lesson', token)
            call('POST', f'{base}/api/learning/heartbeat/', 'learning/heartbeat', token, body={})
        elif roll < 0.85:                    # batch event upload
            batch = [{
                'event_uuid': f'{username}-{random.random()}',
                'event_type': random.choice(['answer_change', 'material_scroll', 'focus']),
                'page_url': 'http://loadtest/lesson.html', 'app_version': 'loadtest',
            } for _ in range(random.randint(1, 5))]
            call('POST', f'{base}/api/learning/events/', 'learning/events', token, body=batch)
        else:                                # heavy path: start -> submit a quiz
            take_quiz(base, token)

        # human think-time between actions
        time.sleep(random.uniform(3, 12))


def take_quiz(base, token):
    quiz_id = random.randint(1, 24)
    ok, data = call('POST', f'{base}/api/assessments/start/', 'assessments/start', token,
                    body={'quiz_id': quiz_id}, expect=(201, 403))
    if not ok or not data:
        return
    attempt_id = data.get('id')
    questions = (data.get('quiz_data') or {}).get('questions') or []
    if not attempt_id or not questions:
        return
    answers = []
    for q in questions:
        if q.get('question_type') == 'multiple_choice' and q.get('choices'):
            ans = str(random.choice(q['choices'])['id'])
        else:
            ans = 'x'
        answers.append({'question_id': q['id'], 'student_answer': ans})
    time.sleep(random.uniform(2, 6))   # student answering
    call('POST', f'{base}/api/assessments/submit/', 'assessments/submit', token,
         body={'attempt_id': attempt_id, 'quiz_id': quiz_id, 'answers': answers})


def pct(values, p):
    if not values:
        return 0.0
    values = sorted(values)
    k = max(0, min(len(values) - 1, int(round((p / 100) * (len(values) - 1)))))
    return values[k]


def print_summary(elapsed):
    with _lock:
        names = sorted(_counts)
        total = sum(_counts.values())
        total_err = sum(_errors.values())
        print('\n' + '=' * 78)
        print(f'{"endpoint":28} {"reqs":>7} {"err":>5} {"p50":>8} {"p95":>8} {"max":>8}')
        print('-' * 78)
        for n in names:
            lat = _latencies[n]
            print(f'{n:28} {_counts[n]:>7} {_errors[n]:>5} '
                  f'{pct(lat,50)*1000:>7.0f}m {pct(lat,95)*1000:>7.0f}m {max(lat)*1000:>7.0f}m')
        print('-' * 78)
        rps = total / elapsed if elapsed else 0
        err_pct = (total_err / total * 100) if total else 0
        print(f'TOTAL {total} reqs in {elapsed:.0f}s  |  {rps:.1f} req/s  |  '
              f'failures {total_err} ({err_pct:.1f}%)')
        print('=' * 78)
        if err_pct < 1 and pct(sum(_latencies.values(), []), 95) < 1.0:
            print('結果: 綠燈 — 失敗率 <1%、p95 <1s,這個負載撐得住。')
        else:
            print('結果: 注意 — 失敗率或 p95 偏高,server 可能到達瓶頸(檢查 gunicorn worker / 記憶體)。')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='http://140.131.115.76')
    ap.add_argument('--users', type=int, default=55)
    ap.add_argument('--duration', type=int, default=120, help='seconds')
    ap.add_argument('--ramp', type=float, default=10, help='users started per second')
    ap.add_argument('--password', default='loadtest-pw')
    ap.add_argument('--count', type=int, default=0, help='username pool size (default = users)')
    args = ap.parse_args()

    base = args.host.rstrip('/')
    pool = args.count or args.users
    deadline = time.time() + args.duration
    print(f'壓測開始: {args.users} 人 → {base},持續 {args.duration}s,'
          f'每秒啟動 {args.ramp} 人。帳號 loadtest001..loadtest{pool:03d}')

    threads = []
    for i in range(args.users):
        n = (i % pool) + 1
        t = threading.Thread(target=student_loop,
                             args=(base, f'loadtest{n:03d}', args.password, deadline),
                             daemon=True)
        t.start()
        threads.append(t)
        time.sleep(1.0 / args.ramp if args.ramp > 0 else 0)

    start = time.time()
    try:
        while time.time() < deadline:
            time.sleep(5)
            with _lock:
                total = sum(_counts.values())
                err = sum(_errors.values())
            print(f'  ...{time.time()-start:4.0f}s  reqs={total}  failures={err}')
    except KeyboardInterrupt:
        print('\n中斷,結算中...')
    _stop.set()
    for t in threads:
        t.join(timeout=5)
    print_summary(time.time() - start)


if __name__ == '__main__':
    main()
