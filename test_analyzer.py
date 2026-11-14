"""
Automated Unit Tests for MITS Option Chain Intelligence Engine
Verifies spot price detection, dynamic ITM/OTM strike classification,
CE/PE breakdown calculations, fresh additions/unwinding, and ratio intelligence.
"""

import unittest
import os
import tempfile
import json
from mits_option_chain_analyzer import OptionChainAnalyzer

class TestOptionChainAnalyzer(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_file = os.path.join(self.base_dir, "sample_data", "nse_option_chain_nifty.json")
        self.csv_simple = os.path.join(self.base_dir, "sample_data", "simple_option_chain.csv")
        self.csv_nse = os.path.join(self.base_dir, "sample_data", "nse_option_chain_nifty.csv")

    def test_json_parsing_and_calculations(self):
        analyzer = OptionChainAnalyzer()
        res = analyzer.parse_file(self.json_file)

        # 1. Spot Price Detection
        self.assertAlmostEqual(res["spot_price"], 24350.50, places=2)

        # 2. Call Side (CE) Breakdown
        ce = res["call_breakdown"]
        self.assertEqual(ce["total_oi"], 1088700.0)
        self.assertEqual(ce["otm"]["oi"], 880000.0)
        self.assertAlmostEqual(ce["otm"]["oi_pct"], 80.83, delta=0.1)
        self.assertEqual(ce["itm"]["oi"], 208700.0)
        self.assertAlmostEqual(ce["itm"]["oi_pct"], 19.17, delta=0.1)

        # Fresh Additions
        self.assertEqual(ce["fresh_additions_total"], 154200.0)
        self.assertEqual(ce["otm"]["fresh_additions"], 144500.0)
        self.assertAlmostEqual(ce["otm"]["fresh_additions_pct"], 93.71, delta=0.1)
        self.assertEqual(ce["itm"]["fresh_additions"], 9700.0)
        self.assertAlmostEqual(ce["itm"]["fresh_additions_pct"], 6.29, delta=0.1)

        # Unwinding
        self.assertEqual(ce["unwinding_total"], 9500.0)
        self.assertEqual(ce["otm"]["unwinding"], 0.0)
        self.assertEqual(ce["itm"]["unwinding"], 9500.0)
        self.assertAlmostEqual(ce["itm"]["unwinding_pct"], 100.0, delta=0.1)

        # 3. Put Side (PE) Breakdown
        pe = res["put_breakdown"]
        self.assertEqual(pe["total_oi"], 1050300.0)
        self.assertEqual(pe["otm"]["oi"], 789400.0)
        self.assertAlmostEqual(pe["otm"]["oi_pct"], 75.16, delta=0.1)
        self.assertEqual(pe["itm"]["oi"], 260900.0)
        self.assertAlmostEqual(pe["itm"]["oi_pct"], 24.84, delta=0.1)

        # Fresh Additions
        self.assertEqual(pe["fresh_additions_total"], 102600.0)
        self.assertEqual(pe["otm"]["fresh_additions"], 102600.0)
        self.assertAlmostEqual(pe["otm"]["fresh_additions_pct"], 100.0, delta=0.1)
        self.assertEqual(pe["itm"]["fresh_additions"], 0.0)

        # Unwinding
        self.assertEqual(pe["unwinding_total"], 13400.0)
        self.assertEqual(pe["otm"]["unwinding"], 0.0)
        self.assertEqual(pe["itm"]["unwinding"], 13400.0)
        self.assertAlmostEqual(pe["itm"]["unwinding_pct"], 100.0, delta=0.1)

        # 4. Intelligence
        intel = res["intelligence"]
        self.assertAlmostEqual(intel["pcr"], 0.965, delta=0.01)
        self.assertEqual(intel["max_pain"], 24400.0)
        self.assertEqual(intel["resistance_1"], 24500.0)
        self.assertEqual(intel["support_1"], 24000.0)

    def test_spot_price_override(self):
        """Test user manually providing an override spot price."""
        analyzer = OptionChainAnalyzer()
        res = analyzer.parse_file(self.json_file, spot_price_override=24550.0)
        self.assertEqual(res["spot_price"], 24550.0)
        # With spot = 24550, 24400 and 24500 become ITM for Call!
        strikes = {s["strike"]: s for s in res["strikes"]}
        self.assertEqual(strikes[24400]["ce_classification"], "ITM")
        self.assertEqual(strikes[24500]["ce_classification"], "ITM")
        self.assertEqual(strikes[24600]["ce_classification"], "OTM")

    def test_csv_nse_format(self):
        analyzer = OptionChainAnalyzer()
        res = analyzer.parse_file(self.csv_nse)
        self.assertAlmostEqual(res["spot_price"], 24350.50, places=2)
        self.assertEqual(res["call_breakdown"]["total_oi"], 1088700.0)
        self.assertEqual(res["put_breakdown"]["total_oi"], 1050300.0)

    def test_zero_division_safety(self):
        """Ensure no divide-by-zero crashes on empty or zero-filled data."""
        empty_data = [
            {"strike": 24000, "ce_oi": 0, "ce_chg": 0, "pe_oi": 0, "pe_chg": 0, "spot": 24000}
        ]
        analyzer = OptionChainAnalyzer()
        res = analyzer.parse_json(empty_data)
        self.assertEqual(res["call_breakdown"]["total_oi"], 0.0)
        self.assertEqual(res["call_breakdown"]["otm"]["oi_pct"], 0.0)
        self.assertEqual(res["intelligence"]["pcr"], 0.0)

if __name__ == "__main__":
    unittest.main()
