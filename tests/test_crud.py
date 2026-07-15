from storage import crud
from storage.models import PriceHistory


def test_add_price_history_does_not_commit(session, product):
    crud.add_price_history(session, product, 19.99, True)

    session.rollback()

    assert session.query(PriceHistory).count() == 0


def test_update_product_does_not_commit(session, product):
    crud.update_product(session, product, 19.99, True)

    session.rollback()

    assert product.current_price is None
