import csv
import io
import json
import tempfile
from decimal import Decimal
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from products.models import Product
from tests.factories import create_product_with_stock


class LoadGoodsCommandTestCase(TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)

    def test_load_goods_imports_products_from_csv(self):
        goods_path = self._create_temp_file(
            "goods.csv",
            "name,description,price,category,quantity\n"
            "Lamp,Small lamp,17.90,Lighting,4\n",
        )

        call_command("load_goods", goods_path, stdout=io.StringIO())

        product = Product.objects.get(name="Lamp")
        self.assertEqual(product.description, "Small lamp")
        self.assertEqual(product.price, Decimal("17.90"))
        self.assertEqual(product.category.name, "Lighting")
        self.assertEqual(product.stock.quantity, 4)

    def test_load_goods_imports_products_from_json(self):
        goods_path = self._create_temp_file(
            "goods.json",
            json.dumps(
                [
                    {
                        "name": "Chair",
                        "description": "Wooden chair",
                        "price": "49.00",
                        "category": "Furniture",
                        "quantity": 2,
                    }
                ]
            ),
        )

        call_command("load_goods", goods_path, stdout=io.StringIO())

        product = Product.objects.get(name="Chair")
        self.assertEqual(product.price, Decimal("49.00"))
        self.assertEqual(product.stock.quantity, 2)

    def _create_temp_file(self, filename, content):
        path = Path(self.tmp_dir.name) / filename
        path.write_text(content, encoding="utf-8")
        return str(path)


class ExportProductResidueCommandTestCase(TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)

    def test_export_product_residue_writes_csv(self):
        product, stock = create_product_with_stock(
            name="Monitor",
            quantity=6,
        )
        output_path = Path(self.tmp_dir.name) / "residue.csv"

        call_command("export_product_residue", str(output_path), stdout=io.StringIO())

        with output_path.open(encoding="utf-8") as output_file:
            rows = list(csv.DictReader(output_file))

        self.assertEqual(rows[0]["product_id"], str(product.id))
        self.assertEqual(rows[0]["name"], "Monitor")
        self.assertEqual(rows[0]["category"], product.category.name)
        self.assertEqual(rows[0]["quantity"], str(stock.quantity))
