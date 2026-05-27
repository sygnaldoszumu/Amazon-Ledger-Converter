"""
Simple NBP Currency Exchange Rate Module with CSV Caching
Fetches exchange rates between any two currencies for a specific date
using the National Bank of Poland (NBP) API. Results are cached to CSV
for fast subsequent lookups. Valid dates are also cached so NBP is never
queried twice for the same date.

Cache location:
    ~/.amazon_ledger_converter/exchange_rates.csv

Cache CSV columns:
    from_currency, to_currency, requested_date, valid_date, rate

Example:
    >>> rate = get_exchange_rate("USD", "PLN", "2/28/2026")
    >>> print(f"1 USD = {rate} PLN")
"""
import csv
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


BASE_URL = "https://api.nbp.pl/api"
CACHE_COLUMNS = ["from_currency", "to_currency", "requested_date", "valid_date", "rate"]


def _cache_path() -> Path:
    path = Path.home() / ".amazon_ledger_converter" / "exchange_rates.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


_DEFAULT_CACHE = _cache_path()


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _convert_date_format(date_str: str) -> str:
    """Convert M/D/YYYY, D.M.YYYY, or D-M-YYYY to YYYY-MM-DD. Strips any trailing time component."""
    s = date_str.strip().split()[0]
    if '/' in s:
        parts = s.split('/')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
    elif '.' in s:
        parts = s.split('.')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    elif '-' in s:
        parts = s.split('-')
        if len(parts) == 3:
            if len(parts[0]) == 4:   # YYYY-MM-DD — already correct
                return s
            return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    raise ValueError(
        f"Invalid date format: '{date_str}'. Use M/D/YYYY, D.M.YYYY, or D-M-YYYY."
    )


def _is_weekend(date_iso: str) -> bool:
    return datetime.strptime(date_iso, "%Y-%m-%d").weekday() >= 5


def _prev_day(date_iso: str) -> str:
    return (
        datetime.strptime(date_iso, "%Y-%m-%d") - timedelta(days=1)
    ).strftime("%Y-%m-%d")


def _has_nbp_data(date_iso: str) -> bool:
    url = f"{BASE_URL}/exchangerates/tables/A/{date_iso}/"
    try:
        return requests.get(url, timeout=10).status_code == 200
    except Exception:
        return False


def _get_rate_vs_pln(currency: str, date_iso: str) -> Optional[float]:
    if currency.upper() == "PLN":
        return 1.0
    for table in ["A", "B"]:
        url = f"{BASE_URL}/exchangerates/rates/{table}/{currency}/{date_iso}/"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "rates" in data and data["rates"]:
                    return float(data["rates"][0]["mid"])
        except Exception:
            continue
    return None


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def _read_cache(cache_file: Path) -> dict:
    """
    Returns a dict keyed by (from_currency, to_currency, requested_date)
    with values of {valid_date, rate}.
    Also builds a secondary index of requested_date → valid_date
    so we can skip NBP date checks for known dates.
    """
    cache = {}
    if cache_file.exists():
        try:
            with open(cache_file, 'r', newline='', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    key = (
                        row['from_currency'],
                        row['to_currency'],
                        row['requested_date'],
                    )
                    cache[key] = {
                        "valid_date": row["valid_date"],
                        "rate": float(row["rate"]),
                    }
        except Exception as e:
            print(f"Warning: could not read cache: {e}")
    return cache


def _write_to_cache(
    cache_file: Path,
    from_curr: str,
    to_curr: str,
    requested_date: str,
    valid_date: str,
    rate: float,
) -> None:
    file_exists = cache_file.exists()
    try:
        with open(cache_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(CACHE_COLUMNS)
            writer.writerow([from_curr, to_curr, requested_date, valid_date, rate])
    except Exception as e:
        print(f"Warning: could not write to cache: {e}")


def _resolve_valid_date(requested_date: str, cache: dict) -> Optional[str]:
    """
    Check if any cache entry already tells us the valid date for this
    requested_date — regardless of currency pair.
    """
    for key, value in cache.items():
        if key[2] == requested_date:
            return value["valid_date"]
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_valid_date(date: str, cache_file: Path = _DEFAULT_CACHE) -> str:
    """
    Return the closest working day on or before the given date.
    Checks the cache first — if any entry exists for this requested_date,
    the valid_date is already known and no HTTP call is made.

    Args:
        date:       Date in M/D/YYYY format (e.g., "3/1/2026")
        cache_file: Path to CSV cache file

    Returns:
        Closest valid working day in YYYY-MM-DD format.
    """
    requested_date = _convert_date_format(date)
    cache = _read_cache(cache_file)

    cached_valid = _resolve_valid_date(requested_date, cache)
    if cached_valid:
        return cached_valid

    candidate = requested_date
    now = datetime.now()

    for _ in range(30):
        date_obj = datetime.strptime(candidate, "%Y-%m-%d")
        if date_obj > now or _is_weekend(candidate):
            candidate = _prev_day(candidate)
            continue
        if _has_nbp_data(candidate):
            return candidate
        candidate = _prev_day(candidate)

    raise ValueError(f"No valid working day found within 30 days of '{date}'.")


def get_exchange_rate(
    from_currency: str,
    to_currency: str,
    date: str,
    cache_file: Path = _DEFAULT_CACHE,
) -> float:
    """
    Get the exchange rate between two currencies for the closest working day
    on or before the given date. Both the valid date and the rate are cached.

    Args:
        from_currency: Source currency code (e.g., 'USD', 'EUR')
        to_currency:   Target currency code (e.g., 'EUR', 'PLN')
        date:          Date in M/D/YYYY format (e.g., "2/28/2026")
        cache_file:    Path to CSV cache file

    Returns:
        Exchange rate as a float: 1 from_currency = X to_currency.
    """
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()
    requested_date = _convert_date_format(date)
    cache_key = (from_curr, to_curr, requested_date)

    cache = _read_cache(cache_file)

    # ── full cache hit: rate already known ───────────────────────────────────
    if cache_key in cache:
        return cache[cache_key]["rate"]

    # ── partial hit: valid date already known, skip NBP date check ──────────
    cached_valid = _resolve_valid_date(requested_date, cache)
    if cached_valid:
        valid_date = cached_valid
    else:
        valid_date = get_valid_date(date, cache_file)
        if valid_date != requested_date:
            orig = datetime.strptime(requested_date, "%Y-%m-%d").strftime("%m/%d/%Y")
            used = datetime.strptime(valid_date, "%Y-%m-%d").strftime("%m/%d/%Y")
            print(f"Note: {orig} had no data, using {used} instead")

    # ── fetch rates from NBP ─────────────────────────────────────────────────
    from_rate = _get_rate_vs_pln(from_curr, valid_date)
    to_rate = _get_rate_vs_pln(to_curr, valid_date)

    if from_rate is None or to_rate is None:
        missing = from_curr if from_rate is None else to_curr
        raise ValueError(f"Could not fetch rate for {missing} on {valid_date}.")

    if from_curr == "PLN":
        rate = round(1.0 / to_rate, 4)
    elif to_curr == "PLN":
        rate = round(from_rate, 4)
    else:
        rate = round(from_rate / to_rate, 4)

    _write_to_cache(cache_file, from_curr, to_curr, requested_date, valid_date, rate)
    return rate


if __name__ == "__main__":
    rates = get_exchange_rate("USD", "PLN", "2/28/2026")
    print(f"1 USD = {rates} PLN")
    rates = get_exchange_rate("USD", "PLN", "28.02.2026")
    print(f"1 USD = {rates} PLN")
    rates = get_exchange_rate("USD", "PLN", "28.2.2026")
    print(f"1 USD = {rates} PLN")
