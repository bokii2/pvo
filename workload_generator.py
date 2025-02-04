import requests
import time
import concurrent.futures
import matplotlib.pyplot as plt
import logging
from dataclasses import dataclass
from typing import List, Tuple, Dict
import json
import statistics
from IPython.display import display, HTML

CONFIG = {
    'BASE_URL': 'IP_OF_THE_VM',
    'DEFAULT_N_VALUE': 100000,
    'REQUEST_COUNTS': [1, 10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    'TIMEOUT': 30,
    'MAX_RETRIES': 3
}

@dataclass
class RequestResult:
    response_data: Dict
    execution_time: float
    success: bool
    error: str = None

@dataclass
class WorkloadResult:
    total_time: float
    throughput: float
    avg_calculation_time: float
    request_count: int
    success_rate: float
    latencies: List[float]

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def send_request(n: int, timeout: int = CONFIG['TIMEOUT']) -> RequestResult:
    start_time = time.time()
    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            response = requests.get(
                f"{CONFIG['BASE_URL']}/sum",
                params={'n': n},
                timeout=timeout
            )
            response.raise_for_status()
            return RequestResult(
                response_data=response.json(),
                execution_time=time.time() - start_time,
                success=True
            )
        except requests.exceptions.RequestException as e:
            if attempt == CONFIG['MAX_RETRIES'] - 1:
                return RequestResult(
                    response_data=None,
                    execution_time=time.time() - start_time,
                    success=False,
                    error=str(e)
                )
            time.sleep(1)

def run_workload(num_requests: int, n: int) -> WorkloadResult:
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(send_request, n) for _ in range(num_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    end_time = time.time()
    total_time = end_time - start_time

    successful_results = [r for r in results if r.success]
    success_rate = len(successful_results) / num_requests
    latencies = [r.execution_time for r in successful_results]

    return WorkloadResult(
        total_time=total_time,
        throughput=num_requests / total_time if total_time > 0 else 0,
        avg_calculation_time=statistics.mean(latencies) if latencies else 0,
        request_count=num_requests,
        success_rate=success_rate,
        latencies=latencies
    )

def create_and_display_plots(results: List[WorkloadResult]):
    plt.figure(figsize=(20, 12))

    plt.subplot(231)
    plt.plot([r.request_count for r in results], [r.total_time for r in results], marker='o')
    plt.title("Execution Time")
    plt.xlabel("Number of Requests")
    plt.ylabel("Time (s)")
    plt.grid(True)

    plt.subplot(232)
    plt.plot([r.request_count for r in results], [r.throughput for r in results], marker='o')
    plt.title("Throughput")
    plt.xlabel("Number of Requests")
    plt.ylabel("Requests/s")
    plt.grid(True)

    plt.subplot(233)
    speedups = [results[0].total_time/r.total_time for r in results]
    plt.plot([r.request_count for r in results], speedups, marker='o')
    plt.title("Speedup")
    plt.xlabel("Number of Requests")
    plt.ylabel("Speedup Factor")
    plt.grid(True)

    plt.subplot(234)
    plt.plot([r.request_count for r in results],
             [r.success_rate * 100 for r in results], marker='o')
    plt.title("Success Rate")
    plt.xlabel("Number of Requests")
    plt.ylabel("Success Rate (%)")
    plt.grid(True)

    plt.subplot(235)
    valid_results = [(r.request_count, r.latencies) for r in results if r.latencies]
    if valid_results:
        counts, latencies = zip(*valid_results)
        plt.boxplot(latencies, labels=[str(c) for c in counts])
        plt.title("Latency Distribution\n(Successful Requests Only)")
        plt.xlabel("Number of Requests")
        plt.ylabel("Latency (s)")
        plt.xticks(rotation=45)
        plt.grid(True)
    else:
        plt.text(0.5, 0.5, "No successful requests to display latency data",
                ha='center', va='center')

    plt.tight_layout()
    plt.show()

def main():
    setup_logging()
    logging.info("Starting performance tests")

    results = []
    for count in CONFIG['REQUEST_COUNTS']:
        logging.info(f"Running workload with {count} requests...")
        result = run_workload(count, CONFIG['DEFAULT_N_VALUE'])
        results.append(result)

        print(f"Completed {count} requests: "
              f"Throughput: {result.throughput:.2f} req/s, "
              f"Success Rate: {result.success_rate*100:.1f}%")

    print("\nPerformance Plots:")
    create_and_display_plots(results)

    logging.info("Performance tests completed")
    return results

if __name__ == "__main__":
    main()
