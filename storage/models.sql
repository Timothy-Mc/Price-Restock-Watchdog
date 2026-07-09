CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    name TEXT,
    target_price REAL,
    current_price REAL,
    in_stock INTEGER,
    last_checked DATETIME
);

CREATE TABLE price_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    price REAL,
    in_stock INTEGER,
    checked_at DATETIME CURRENT_TIMESTAMP
);