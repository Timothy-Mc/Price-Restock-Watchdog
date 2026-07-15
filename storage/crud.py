from datetime import datetime
from storage.models import Product, PriceHistory

def add_product(session, url, name, target_price, alert_email):

    product = Product(
        url=url,
        name=name,
        target_price=target_price,
        alert_email=alert_email,
        created_at=datetime.now(),
        in_stock=False,
        consecutive_failures=0,
        is_broken=0,
    )

    session.add(product)
    session.commit()

    return product

def get_products(session):
    return session.query(Product).all()

def get_product(session, product_id):
    return session.query(Product).filter(Product.id == product_id).first()

def update_product(session, product, price, in_stock):
    product.current_price = price
    product.in_stock = in_stock

def add_price_history(session, product, price, in_stock, error=None):

    history = PriceHistory(
        product_id=product.id,
        price=price,
        in_stock=in_stock,
        checked_at=datetime.now(),
        error=error
    )

    session.add(history)

    return history

def delete_product(session, product):
    session.delete(product)
    session.commit()


def record_price_check(session, product, price, in_stock, error=None):
    add_price_history(session, product, price, in_stock, error)

    product.last_checked = datetime.now()

    if error:
        product.consecutive_failures += 1
    else:
        update_product(session, product, price, in_stock)

    if product.consecutive_failures >= 5:
        product.is_broken = True

    session.commit()

    return product