BEGIN;

-- Создание таблицы regions
DROP TABLE IF EXISTS regions CASCADE;
CREATE TABLE regions (
    region_id INTEGER PRIMARY KEY,
    region_name TEXT NOT null,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Создание таблицы products
DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_category CHAR(1) NOT NULL CHECK (product_category IN ('A', 'B', 'C', 'D')),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Создание таблицы warehouses
DROP TABLE IF EXISTS warehouses CASCADE;
CREATE TABLE warehouses (
    warehouse_id INTEGER PRIMARY KEY,
    warehouse_name TEXT NOT NULL,
    region_id INTEGER NOT null,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Создание таблицы stock_balances
DROP TABLE IF EXISTS stock_balances CASCADE;
CREATE TABLE stock_balances (
    warehouse_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (warehouse_id, product_id)
);

-- Загрузка данных
COPY regions (region_id, region_name)
FROM '/tmp/csv/regions.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8');

COPY products (product_id, product_name, product_category)
FROM '/tmp/csv/products.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8');

COPY warehouses (warehouse_id, warehouse_name, region_id)
FROM '/tmp/csv/warehouses.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8');

COPY stock_balances (warehouse_id, product_id, quantity)
FROM '/tmp/csv/stock_balances.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8');

COMMIT;