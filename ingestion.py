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
from urllib.parse import urljoin

import requests

from data_generator import generate_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("ingestion")

DEFAULT_TIMEOUT = 5
REQUIRED_KEYS = ("requests", "offers", "evaluations", "orders", "order_changes")


def validate_dataset(dataset):
    """Validate the top-level shape before data reaches the warehouse."""
    if not isinstance(dataset, dict):
        raise ValueError("Dataset must be a mapping of table names to row lists")
    missing = [key for key in REQUIRED_KEYS if key not in dataset]
    if missing:
        raise ValueError(f"Dataset is missing required keys: {', '.join(missing)}")
    for key in REQUIRED_KEYS:
        if not isinstance(dataset[key], list):
            raise ValueError(f"Dataset field '{key}' must be a list")
        if any(not isinstance(row, dict) for row in dataset[key]):
            raise ValueError(f"Dataset field '{key}' must contain objects")
    return dataset


def fetch_from_api(base_url):
    """Attempt to pull requests/offers/evaluations from the live API.

    Returns a partial dataset dict on success. Orders and order changes are
    not exposed on public endpoints in the current API, so this only covers
    the request/offer/evaluation portion of the schema.
    """
    base_url = base_url.rstrip("/") + "/"
    endpoints = {
        "requests": urljoin(base_url, "api/requests"),
        "offers": urljoin(base_url, "api/public/offers"),
        "evaluations": urljoin(base_url, "api/public/evaluations"),
    }
    dataset = {}
    for key, url in endpoints.items():
        resp = requests.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        dataset[key] = resp.json()
    return validate_dataset({
        **dataset,
        "orders": [],
        "order_changes": [],
    })


def load_data(base_url=None, n_requests=180):
    """Returns a full dataset dict, live if possible, else synthetic."""
    if n_requests < 0:
        raise ValueError("n_requests must be non-negative")
    if base_url:
        try:
            log.info("Attempting live ingestion from %s", base_url)
            partial = fetch_from_api(base_url)
            log.info("Live ingestion succeeded: %s", {k: len(v) for k, v in partial.items()})
            # Do not mix synthetic orders with live requests: generated foreign
            # keys and KPI values would be unrelated to the live source.
            return validate_dataset({**partial, "orders": [], "order_changes": []})
        except (requests.RequestException, ValueError, TypeError) as exc:
            log.warning("Live ingestion failed (%s). Falling back to synthetic dataset.", exc)

    log.info("Using synthetic dataset (n_requests=%d)", n_requests)
    return validate_dataset(generate_dataset(n_requests=n_requests))
