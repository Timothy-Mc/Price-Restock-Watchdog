# Design: `record_price_check()`

## Context

`storage/crud.py` currently has separate `add_price_history()` and
`update_product()` functions, each committing independently. CLAUDE.md
identifies the next missing piece as a combined `record_price_check()` that
performs the history write, product update, and failure tracking as a single
atomic operation — this is the function every future scrape check (manual or
scheduled) will call to persist its result.

## Goal

Give the scheduler (not yet built) one function to call after every scrape
attempt, success or failure, that:
- always records what happened in `price_history`
- updates the product's live state only when the scrape succeeded
- tracks consecutive failures and flips `is_broken` after a threshold
- commits as a single transaction, so a crash mid-write can never leave
  `price_history` and `products` disagreeing about what happened

## Signature

```python
def record_price_check(session, product, price, in_stock, error=None) -> Product:
```

Takes raw scrape outputs directly rather than a `ScrapeResult` object,
because `scraper/` doesn't exist yet. When it's built, its caller (the
scheduler) unpacks whatever `scrape_url()` returns into these four
arguments. `price`/`in_stock` are `None` and `error` is set on a failed
check.

## Behavior

1. Always writes a `PriceHistory` row via `add_price_history()` — price,
   in_stock, and error all pass through untouched.
2. Always sets `product.last_checked = datetime.now()` — this timestamp
   means "last time a check was attempted," not "last successful check," so
   the UI can distinguish "still running, just failing" from "scheduler is
   stuck."
3. On success (`error is None`):
   - calls `update_product()` to set `current_price` and `in_stock`
   - resets `product.consecutive_failures = 0`
   - resets `product.is_broken = False`
4. On failure (`error is not None`):
   - increments `product.consecutive_failures`
   - if `consecutive_failures >= MAX_CONSECUTIVE_FAILURES`, sets
     `product.is_broken = True`
5. Single `session.commit()` at the end of the function, wrapped in
   try/except that calls `session.rollback()` and re-raises on failure.
   This is the only commit in the whole operation — the atomicity guarantee
   the function exists to provide.
6. Returns the updated `product`.

## Supporting changes

- **`add_price_history()`** loses its internal `session.commit()`. Becomes a
  pure "stage a `PriceHistory` row" function — the caller commits.
- **`update_product()`** loses its internal `session.commit()`, and no
  longer sets `last_checked` (that responsibility moves entirely to
  `record_price_check()`, since it now applies on both success and failure).
  It only sets `current_price` and `in_stock`.
- **`config.py`** gains `MAX_CONSECUTIVE_FAILURES =
  int(os.getenv("MAX_CONSECUTIVE_FAILURES", 5))`, consistent with how
  `CHECK_INTERVAL` is already handled — avoids a magic number in
  `crud.py` and makes the threshold tunable without a code change.

## Why a single commit matters

If `add_price_history()` and `update_product()` each commit independently
and `record_price_check()` just calls both in sequence, a crash between the
two commits (power loss, forced reboot — this runs unattended in the
background) can leave a `PriceHistory` row recorded with no corresponding
update to `consecutive_failures`/`is_broken`, or vice versa. Stripping the
internal commits and committing once in `record_price_check()` makes the
whole operation atomic: it either fully lands or fully doesn't.

## Blast radius

No existing caller depends on `add_price_history()` or `update_product()`
committing internally — `testers/test.crud.py` only calls `add_product()`
and `delete_product()`, which are unaffected. No scheduler exists yet to
update. This is a self-contained, low-risk change.

## Out of scope

- The scheduler that will call `record_price_check()`.
- Alert edge-triggering (`maybe_send_alert()`) — per CLAUDE.md, the caller
  reads `previous_price`/`previous_in_stock` *before* calling
  `record_price_check()`, since this function overwrites those fields on
  success. Alert logic is a separate piece of work.
