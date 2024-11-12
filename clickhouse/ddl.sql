-- таблица остатков (репликация данных из Kafka)
CREATE TABLE kafka_wms_stock_balances (
  `before.warehouse_id` Nullable(UInt32),
  `before.product_id` Nullable(UInt32),
  `before.quantity` Nullable(UInt32),
  `after.warehouse_id` Nullable(UInt32),
  `after.product_id` Nullable(UInt32),
  `after.quantity` Nullable(UInt32),
  `op` FixedString(1),
  `ts_ms` DateTime64(3),
  `_offset` UInt64,
  `_partition` UInt64
) ENGINE = MergeTree()
ORDER BY (`op`,`ts_ms`);

-- Представление для витрины остатков
create view stock_balances_v as
select
  coalesce(`after.warehouse_id`, `before.warehouse_id`) as warehouse_id,
  coalesce(`after.product_id`, `before.product_id`) as product_id,
  argMax(
    toUInt32(if(op = 'd', 0, `after`.quantity)),
    ts_ms
  ) as quantity
from kafka_wms_stock_balances
group by warehouse_id, product_id
having quantity > 0
;

-- Регионы
CREATE TABLE regions (
  region_id UInt32,
  region_name String,
  updated_at DateTime64(3)
) ENGINE = MergeTree()
ORDER BY (region_id);

-- Склады
CREATE TABLE warehouses (
  warehouse_id UInt32,
  warehouse_name String,
  region_id UInt32,
  updated_at DateTime64(3)
) ENGINE = MergeTree()
ORDER BY (warehouse_id);

-- Товары
CREATE TABLE products (
  product_id UInt32,
  product_name String,
  product_category FixedString(1),
  updated_at DateTime64(3)
) ENGINE = MergeTree()
ORDER BY (product_id);