from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "odoo-claude"
SCRIPTS = PLUGIN / "skills" / "odoo-indexer" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from indexlib import index, search, status  # noqa: E402


class OdooIndexerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.src = self.base / "src"
        self.module = self.src / "sale_custom"
        (self.module / "models").mkdir(parents=True)
        (self.module / "views").mkdir()
        (self.module / "static" / "src" / "js").mkdir(parents=True)
        self.db = self.base / "index.sqlite3"

        (self.module / "__manifest__.py").write_text(
            "{'name': 'Sale Custom', 'version': '18.0.1.0.0', "
            "'depends': ['sale', 'mail'], 'data': ['views/sale_order.xml']}\n",
            encoding="utf-8",
        )
        (self.module / "models" / "sale_order.py").write_text(
            "from odoo import fields, models\n\n"
            "class SaleOrder(models.Model):\n"
            "    _inherit = 'sale.order'\n\n"
            "    partner_code = fields.Char(index=True)\n"
            "    partnerXcode = fields.Char()\n\n"
            "    def action_custom(self):\n"
            "        return True\n",
            encoding="utf-8",
        )
        (self.module / "views" / "sale_order.xml").write_text(
            '<odoo>\n'
            '  <record id="view_order_form_custom" model="ir.ui.view">\n'
            '    <field name="inherit_id" ref="sale.view_order_form"/>\n'
            '  </record>\n'
            '  <template id="sale_custom_template"><t t-name="sale_custom.Card"/></template>\n'
            '</odoo>\n',
            encoding="utf-8",
        )
        (self.module / "static" / "src" / "js" / "card.js").write_text(
            "class SaleCard extends Component {}\n"
            "SaleCard.template = 'sale_custom.Card';\n"
            "registry.category('actions').add('sale_custom.action', SaleCard);\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_index_and_queries(self):
        result = index([self.src.resolve()], self.db, full=True)
        self.assertGreaterEqual(result["symbols"], 8)
        self.assertEqual(search(self.db, "field", "partner_code", parent="sale.order")[0]["name"], "partner_code")
        self.assertEqual(search(self.db, "method", "action_custom", parent="sale.order")[0]["name"], "action_custom")
        self.assertEqual(search(self.db, "xmlid", "sale_custom.view_order_form_custom")[0]["kind"], "view")
        self.assertEqual(search(self.db, "ref", "sale.view_order_form")[0]["kind"], "ref")
        self.assertEqual(search(self.db, "registry", "sale_custom.action")[0]["parent"], "actions")

    def test_underscore_is_literal(self):
        index([self.src.resolve()], self.db, full=True)
        rows = search(self.db, "field", "partner_code", parent="sale.order")
        self.assertEqual([row["name"] for row in rows], ["partner_code"])

    def test_percent_wildcard(self):
        index([self.src.resolve()], self.db, full=True)
        rows = search(self.db, "model-inherit", "sale.%")
        self.assertIn("sale.order", [row["name"] for row in rows])

    def test_incremental_and_status(self):
        first = index([self.src.resolve()], self.db, full=True)
        second = index([self.src.resolve()], self.db, full=False)
        self.assertGreater(first["changed_files"], 0)
        self.assertEqual(second["changed_files"], 0)
        self.assertGreater(second["unchanged_files"], 0)
        self.assertGreater(status(self.db)["symbols"], 0)

    def test_cli_json(self):
        subprocess.run(
            [sys.executable, str(SCRIPTS / "index_odoo.py"), "--root", str(self.src), "--db", str(self.db), "--full", "--json"],
            check=True, capture_output=True, text=True,
        )
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "query_odoo.py"), "field", "partner_code", "--parent", "sale.order", "--db", str(self.db), "--json"],
            check=True, capture_output=True, text=True,
        )
        rows = json.loads(proc.stdout)
        self.assertEqual(rows[0]["name"], "partner_code")


if __name__ == "__main__":
    unittest.main()
