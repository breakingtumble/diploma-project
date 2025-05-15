CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    marketplace_key TEXT,
    url TEXT,
    name TEXT,
    currency TEXT
);

CREATE TABLE parsed_products (
    id SERIAL PRIMARY KEY,
    product_id INT,
    price_proceeded NUMERIC,
    etl_date TIMESTAMP,
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    hashed_password TEXT,
    email TEXT,
    role TEXT
);

CREATE TABLE users_products_subscriptions (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL
                   REFERENCES users(id)
                     ON UPDATE CASCADE
                     ON DELETE RESTRICT,
    product_id   INTEGER NOT NULL
                   REFERENCES products(id)
                     ON UPDATE CASCADE
                     ON DELETE RESTRICT
);

INSERT INTO products (marketplace_key, url) VALUES ('rozetka','https://hard.rozetka.com.ua/ua/gigabyte-gv-n4070wf3oc-12gd/p374531307/');
INSERT INTO products (marketplace_key, url) VALUES ('rozetka','https://hard.rozetka.com.ua/ua/kingston_fury_kf432c16bb1k2_32/p310064098/');
INSERT INTO products (marketplace_key, url) VALUES ('rozetka','https://hard.rozetka.com.ua/ua/kingston_fury_kf432s20ibk2_32/p310063553/');
INSERT INTO products (marketplace_key, url) VALUES ('touch', 'https://touch.com.ua/ua/item/smartfon-apple-iphone-16-128gb-teal-myed3/');