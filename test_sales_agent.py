import unittest
from unittest.mock import patch

import pandas as pd

from dashboard_data import prepare_sales
from sales_agent import compare_months


class SalesAgentTest(unittest.TestCase):
    def test_uses_supplied_database_snapshot(self):
        snapshot = prepare_sales(pd.DataFrame([
            {"sale_date": "2026-07-01", "product": "A", "category": "Home", "country": "HU", "quantity": 1, "revenue": 100},
            {"sale_date": "2026-08-01", "product": "A", "category": "Home", "country": "HU", "quantity": 1, "revenue": 70},
        ]))
        with patch("sales_agent.load_sales", side_effect=AssertionError("CSV was read")):
            result = compare_months("2026-08", "category", snapshot)

        self.assertEqual(result["current_revenue_eur"], 70)
        self.assertEqual(result["previous_revenue_eur"], 100)
        self.assertEqual(result["segments"][0]["change_eur"], -30)

    def test_rejects_invalid_month_and_breakdown(self):
        with self.assertRaises(ValueError):
            compare_months("2026-13", "category", pd.DataFrame())
        with self.assertRaises(ValueError):
            compare_months("2026-08", "revenue", pd.DataFrame())


if __name__ == "__main__":
    unittest.main()
