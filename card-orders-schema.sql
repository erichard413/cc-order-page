CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    join_date TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_cc_admin BOOLEAN NOT NULL DEFAULT FALSE,
    bank INTEGER REFERENCES banks ON DELETE SET NULL
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_type TEXT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    bundle_qty INTEGER,
    description TEXT NOT NULL,
    img_src TEXT
);
CREATE TABLE banks (
    bank_id INTEGER PRIMARY KEY,
    bank_name TEXT NOT NULL,
    website TEXT,
    city TEXT,
    state VARCHAR(2),
    zip TEXT NOT NULL,
    address TEXT
);
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    quantity INT NOT NULL DEFAULT 1,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INT REFERENCES users ON DELETE SET NULL,
    order_date TEXT NOT NULL,
    order_status TEXT NOT NULL,
    bank_id INTEGER REFERENCES banks ON DELETE SET NULL,
    note VARCHAR(255),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    address TEXT NOT NULL,
    state VARCHAR(2) NOT NULL,
    city TEXT NOT NULL,
    zip TEXT NOT NULL,
    admin_note TEXT,
    shipped_date TEXT,
    tracking TEXT
);
