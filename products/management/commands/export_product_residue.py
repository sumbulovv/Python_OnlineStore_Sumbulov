import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from products.models import Product


class Command(BaseCommand):
    help = 'Exports product stock residues to a CSV or JSON file.'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            nargs='?',
            help='Output path. CSV is used by default, JSON when the suffix is .json.',
        )

    def handle(self, *args, **options):
        file_path = options.get('file_path')
        rows = list(self._build_rows())

        if file_path:
            output_path = Path(file_path)
            if output_path.suffix.lower() == '.json':
                self._write_json(output_path, rows)
            else:
                self._write_csv(output_path, rows)
            self.stdout.write(self.style.SUCCESS(f'Exported product residues: {len(rows)}'))
            return

        writer = csv.DictWriter(
            self.stdout,
            fieldnames=['product_id', 'name', 'category', 'quantity'],
        )
        writer.writeheader()
        writer.writerows(rows)

    def _build_rows(self):
        products = Product.objects.select_related('category', 'stock').order_by('name')
        for product in products:
            yield {
                'product_id': product.id,
                'name': product.name,
                'category': product.category.name,
                'quantity': product.stock.quantity if hasattr(product, 'stock') else 0,
            }

    def _write_csv(self, output_path, rows):
        with output_path.open('w', newline='', encoding='utf-8') as output_file:
            writer = csv.DictWriter(
                output_file,
                fieldnames=['product_id', 'name', 'category', 'quantity'],
            )
            writer.writeheader()
            writer.writerows(rows)

    def _write_json(self, output_path, rows):
        with output_path.open('w', encoding='utf-8') as output_file:
            json.dump(rows, output_file, ensure_ascii=False, indent=2)
