import csv
import random
from faker import Faker
from faker.providers import BaseProvider

class CustomProvider(BaseProvider):
    def product_name(self):
        products = [
            'Ноутбук', 'Смартфон', 'Телевизор', 'Планшет', 'Камера',
            'Принтер', 'Монитор', 'Клавиатура', 'Мышь', 'Наушники',
            'Колонки', 'Смарт-часы', 'Игровая консоль', 'Внешний диск',
            'Маршрутизатор', 'Модем', 'Сканер', 'Видеокарта', 'Процессор', 'Материнская плата'
        ]
        return self.random_element(products)

    def warehouse_name(self):
        prefixes = ['Центральный', 'Северный', 'Южный', 'Восточный', 'Западный', 'Главный', 'Региональный']
        suffixes = ['Склад', 'Логистический Центр', 'Распределительный Центр', 'Хаб', 'Терминал']
        return f"{self.random_element(prefixes)} {self.random_element(suffixes)}"

    def product_category(self):
        categories = ['A', 'B', 'C', 'D']
        return self.random_element(categories)

fake = Faker('ru_RU')
fake.add_provider(CustomProvider)

# Генерация регионов
regions = []
with open('regions.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['region_id', 'region_name'])
    region_ids = set()
    while len(regions) < 10:
        region_name = fake.region()
        if region_name not in [region['region_name'] for region in regions]:
            region_id = len(regions) + 1
            regions.append({'region_id': region_id, 'region_name': region_name})
            writer.writerow([region_id, region_name])
            region_ids.add(region_id)

# Генерация складов
warehouses = []
with open('warehouses.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['warehouse_id', 'warehouse_name', 'region_id'])
    for warehouse_id in range(1, 6):
        warehouse_name = fake.warehouse_name()
        region = random.choice(regions)
        warehouses.append({
            'warehouse_id': warehouse_id,
            'warehouse_name': warehouse_name,
            'region_id': region['region_id']
        })
        writer.writerow([warehouse_id, warehouse_name, region['region_id']])

# Генерация товаров
products = []
with open('products.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['product_id', 'product_name', 'product_category'])
    for product_id in range(1, 21):
        product_name = fake.product_name()
        product_category = fake.product_category()
        products.append({
            'product_id': product_id,
            'product_name': product_name,
            'product_category': product_category
        })
        writer.writerow([product_id, product_name, product_category])

# Генерация остатков товаров на складах
with open('stock_balances.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['warehouse_id', 'product_id', 'quantity'])
    for warehouse in warehouses:
        for product in products:
            quantity = random.randint(0, 100)
            writer.writerow([warehouse['warehouse_id'], product['product_id'], quantity])
