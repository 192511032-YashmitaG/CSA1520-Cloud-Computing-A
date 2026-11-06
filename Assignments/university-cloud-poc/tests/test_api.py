import concurrent.futures, json, time, urllib.request, urllib.error
BASE = "http://127.0.0.1:5000"
def get(path):
    with urllib.request.urlopen(BASE + path, timeout=5) as r:
        return r.status, json.loads(r.read().decode())
def main():
    checks = [("health", "/health", 200), ("student list", "/api/students", 200), ("existing student", "/api/students/1", 200), ("missing student", "/api/students/999", 404)]
    failed = 0
    for name, path, expected in checks:
        try:
            if expected == 404:
                try: urllib.request.urlopen(BASE + path, timeout=5)
                except urllib.error.HTTPError as e: status, body = e.code, json.loads(e.read().decode())
            else: status, body = get(path)
            ok = status == expected
            print(f"{'PASS' if ok else 'FAIL'} | {name:18} | HTTP {status} (expected {expected}) | {body}")
            failed += not ok
        except Exception as e:
            print(f"FAIL | {name:18} | {e}"); failed += 1
    print("\nConcurrent request test: 100 GET requests using 10 workers")
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(lambda _: get("/health")[0], range(100)))
    elapsed = time.perf_counter() - started
    success = sum(x == 200 for x in results)
    print(f"Requests: {len(results)} | Successful: {success} | Failed: {len(results)-success} | Elapsed: {elapsed:.3f}s | Throughput: {len(results)/elapsed:.1f} req/s")
    failed += success != 100
    print("\nRESULT:", "ALL TESTS PASSED" if failed == 0 else f"{failed} TEST(S) FAILED")
    raise SystemExit(0 if failed == 0 else 1)
if __name__ == "__main__": main()
