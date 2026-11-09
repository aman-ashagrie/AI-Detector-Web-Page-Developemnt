import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import requests

ANALYSE_URL = "http://127.0.0.1:8000/api/analyse/"
HEALTH_URL = "http://127.0.0.1:8000/api/health"

# Usage: python flood_test.py regex   (crafted input that makes the regex backtrack)
#        python flood_test.py busy    (many max-size essays at once)
SCENARIO = sys.argv[1] if len(sys.argv) > 1 else "regex"

if SCENARIO == "regex":
    PAYLOAD = {"text": "<script>" * 5000}
    N_REQUESTS = 50
else:
    essay = "The students wrote their essays carefully. Each paragraph discussed a different idea. " * 120
    PAYLOAD = {"text": essay[:9990]}
    N_REQUESTS = 200


def send_attack(_):
    start = time.perf_counter()
    try:
        r = requests.post(ANALYSE_URL, json=PAYLOAD, timeout=180)
        return r.status_code, time.perf_counter() - start
    except requests.exceptions.Timeout:
        return "timeout", time.perf_counter() - start
    except requests.exceptions.RequestException:
        return "connection error", time.perf_counter() - start


print(f"Scenario: {SCENARIO}, {N_REQUESTS} requests of {len(PAYLOAD['text']):,} characters")

with ThreadPoolExecutor(max_workers=N_REQUESTS) as pool:
    futures = [pool.submit(send_attack, i) for i in range(N_REQUESTS)]
    time.sleep(2)
    start = time.perf_counter()
    try:
        requests.get(HEALTH_URL, timeout=30)
        print(f"Health check during attack: {time.perf_counter() - start:.2f} s")
    except requests.exceptions.Timeout:
        print("Health check TIMED OUT: server unusable for normal users")
    results = [f.result() for f in futures]

times = sorted(t for _, t in results)
print("Status codes:", dict(Counter(code for code, _ in results)))
print(f"Median response: {times[len(times) // 2]:.2f} s")
print(f"Slowest response: {times[-1]:.2f} s")
