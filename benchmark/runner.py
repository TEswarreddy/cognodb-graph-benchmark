import time


def run_latency_test(
    session,
    query,
    parameters,
    warmup_iterations=20,
    measured_iterations=100,
):
    """
    Execute a query with warm-up and measured iterations.

    Latency is measured from query submission until
    the complete result has been consumed.
    """

    # -------------------------
    # Warm-up
    # -------------------------

    for _ in range(warmup_iterations):

        result = session.run(
            query,
            parameters,
        )

        result.consume()

    # -------------------------
    # Measured iterations
    # -------------------------

    latencies_ms = []

    for _ in range(measured_iterations):

        start = time.perf_counter()

        result = session.run(
            query,
            parameters,
        )

        result.consume()

        elapsed = (
            time.perf_counter() - start
        )

        latencies_ms.append(
            elapsed * 1000
        )

    return latencies_ms