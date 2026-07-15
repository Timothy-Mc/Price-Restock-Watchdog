from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from storage.models import Base, Product


@pytest.fixture
def session_factory():
    """A sessionmaker bound to a fresh in-memory SQLite database.

    Uses StaticPool so every session opened from this factory shares the
    same in-memory database — needed to verify that data survives across
    separate sessions (i.e. was actually committed, not just flushed).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def session(session_factory):
    db = session_factory()
    yield db
    db.close()


@pytest.fixture
def product(session):
    p = Product(
        url="https://example.com/product",
        name="Test Product",
        target_price=100.0,
        alert_email=None,
        created_at=datetime.now(),
        in_stock=False,
        consecutive_failures=0,
        is_broken=False,
    )
    session.add(p)
    session.commit()
    return p
