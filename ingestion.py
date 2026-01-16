"""
Ingestion layer.

Tries to pull real data from the ServiceManagementSystem public REST
endpoints (GET /api/requests, GET /api/public/offers, GET /api/public/evaluations)
using `requests`. If the API is unreachable (no deployment running, network
restrictions, etc.) it transparently falls back to the synthetic data
generator so the rest of the pipeline (storage, analytics, reporting) always
has data to work with.
"""
import logging

import requests

from data_generator import generate_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("ingestion")

DEFAULT_TIMEOUT = 5


def fetch_from_api(base_url):
    """Attempt to pull requests/offers/evaluations from the live API.

    Returns a partial dataset dict on success. Orders and order changes are
    not exposed on public endpoints in the current API, so this only covers
    the request/offer/evaluation portion of the schema.
    """
    endpoints = {
        "requests": f"{base_url}/api/requests",
        "offers": f"{base_url}/api/public/offers",
        "evaluations": f"{base_url}/api/public/evaluations",
    }
    dataset = {}
    for key, url in endpoints.items():
        resp = requests.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        dataset[key] = resp.json()
    return dataset


def load_data(base_url=None, n_requests=180):
    """Returns a full dataset dict, live if possible, else synthetic."""
    if base_url:
        try:
            log.info("Attempting live ingestion from %s", base_url)
            partial = fetch_from_api(base_url)
            log.info("Live ingestion succeeded: %s", {k: len(v) for k, v in partial.items()})
            # Live public API doesn't expose orders/order_changes, so those
            # come from the synthetic generator to keep downstream analytics complete.
            synthetic = generate_dataset(n_requests=n_requests)
            partial["orders"] = synthetic["orders"]
            partial["order_changes"] = synthetic["order_changes"]
            return partial
        except (requests.RequestException, ValueError) as exc:
            log.warning("Live ingestion failed (%s). Falling back to synthetic dataset.", exc)

    log.info("Using synthetic dataset (n_requests=%d)", n_requests)
    return generate_dataset(n_requests=n_requests)
