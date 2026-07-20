import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from products.models import Category, Product, Stock


class Command(BaseCommand):
    help = 'Loads products from a CSV or JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', help='Path to CSV or JSON file with goods.')

    def handle(self, *args, **options):
        file_path = Path(options['file_path'])
        if not file_path.exists():
            raise CommandError(f'File not found: {file_path}')

        rows = self._read_rows(file_path)
        loaded_count = 0

        with transaction.atomic():
            for row in rows:
                self._load_product(row)
                loaded_count += 1

        self.stdout.write(self.style.SUCCESS(f'Loaded goods: {loaded_count}'))

    def _read_rows(self, file_path):
        suffix = file_path.suffix.lower()
        if suffix == '.csv':
            with file_path.open(newline='', encoding='utf-8') as goods_file:
                return list(csv.DictReader(goods_file))
        if suffix == '.json':
            with file_path.open(encoding='utf-8') as goods_file:
                data = json.load(goods_file)
            if isinstance(data, dict):
                data = data.get('goods') or data.get('products')
            if not isinstance(data, list):
                raise CommandError('JSON file must contain a list of goods.')
            return data
        raise CommandError('Unsupported file format. Use CSV or JSON.')

    def _load_product(self, row):
        name = self._get_required(row, 'name')
        description = row.get('description', '')
        category_name = row.get('category') or row.get('category_name')
        price = self._parse_price(self._get_required(row, 'price'), name)
        quantity = self._parse_quantity(
            row.get('quantity', row.get('stock', 0)),
            name,
        )

        if not category_name:
            raise CommandError(f'Category is required for product "{name}".')

        category, _created = Category.objects.get_or_create(name=category_name)
        product = Product.objects.filter(name=name).first()

        if product is None:
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                category=category,
            )
        else:
            product.description = description
            product.price = price
            product.category = category
            product.save()

        Stock.objects.update_or_create(
            product=product,
            defaults={'quantity': quantity},
        )

    def _get_required(self, row, field):
        value = row.get(field)
        if value in (None, ''):
            raise CommandError(f'Field "{field}" is required.')
        return value

    def _parse_price(self, value, product_name):
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError):
            raise CommandError(f'Invalid price for product "{product_name}".')

    def _parse_quantity(self, value, product_name):
        try:
            quantity = int(value)
        except (TypeError, ValueError):
            raise CommandError(f'Invalid quantity for product "{product_name}".')
        if quantity < 0:
            raise CommandError(f'Quantity cannot be negative for product "{product_name}".')
        return quantity
