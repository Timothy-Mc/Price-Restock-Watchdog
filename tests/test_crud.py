import pytest
from sqlalchemy.exc import IntegrityError

from storage import crud
from storage.models import PriceHistory
from config import config


def test_add_price_history_does_not_commit(session, product):
    crud.add_price_history(session, product, 19.99, True)

    session.rollback()

    assert session.query(PriceHistory).count() == 0


def test_update_product_does_not_commit(session, product):
    crud.update_product(session, product, 19.99, True)

    session.rollback()

    assert product.current_price is None


def test_record_price_check_success_resets_failure_state(session, product):
    product.consecutive_failures = 3
    product.is_broken = True
    session.commit()

    result = crud.record_price_check(session, product, 42.50, True)

    assert result.current_price == 42.50
    assert result.in_stock is True
    assert result.last_checked is not None
    assert result.consecutive_failures == 0
    assert result.is_broken is False


def test_record_price_check_failure_increments_without_tripping_is_broken(session, product, monkeypatch):
    monkeypatch.setattr(config, "MAX_CONSECUTIVE_FAILURES", 3)

    result = crud.record_price_check(session, product, None, None, error="Timeout")

    assert result.consecutive_failures == 1
    assert result.is_broken is False
    assert result.current_price is None
    assert result.last_checked is not None


def test_record_price_check_marks_broken_at_configured_threshold(session, product, monkeypatch):
    monkeypatch.setattr(config, "MAX_CONSECUTIVE_FAILURES", 2)

    crud.record_price_check(session, product, None, None, error="Timeout")
    result = crud.record_price_check(session, product, None, None, error="Timeout")

    assert result.consecutive_failures == 2
    assert result.is_broken is True


def test_record_price_check_rolls_back_on_commit_failure(session, product, monkeypatch):
    def failing_commit():
        raise IntegrityError("mock failure", {}, Exception("boom"))

    monkeypatch.setattr(session, "commit", failing_commit)

    with pytest.raises(IntegrityError):
        crud.record_price_check(session, product, None, None, error="Timeout")

    assert product.consecutive_failures == 0
