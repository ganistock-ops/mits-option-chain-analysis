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
        self.assertEqual(ce["total_oi"], 29445045.0)
        self.assertEqual(ce["otm"]["oi"], 23924631.0)
        self.assertAlmostEqual(ce["otm"]["oi_pct"], 81.25, delta=0.1)
        self.assertEqual(ce["itm"]["oi"], 5520414.0)
        self.assertAlmostEqual(ce["itm"]["oi_pct"], 18.75, delta=0.1)
        self.assertAlmostEqual(ce["otm"]["oi_pct"] + ce["itm"]["oi_pct"], 100.0, delta=0.1)

        # Fresh Additions
        self.assertEqual(ce["fresh_additions_total"], 3776507.0)
        self.assertEqual(ce["otm"]["fresh_additions"], 3648983.0)
        self.assertAlmostEqual(ce["otm"]["fresh_additions_pct"], 96.62, delta=0.1)
        self.assertEqual(ce["itm"]["fresh_additions"], 127524.0)
        self.assertAlmostEqual(ce["itm"]["fresh_additions_pct"], 3.38, delta=0.1)

        # Unwinding
        self.assertEqual(ce["unwinding_total"], 471138.0)
        self.assertEqual(ce["otm"]["unwinding"], 0.0)
        self.assertEqual(ce["itm"]["unwinding"], 471138.0)
        self.assertAlmostEqual(ce["itm"]["unwinding_pct"], 100.0, delta=0.1)

        # 3. Put Side (PE) Breakdown
        pe = res["put_breakdown"]
        self.assertEqual(pe["total_oi"], 29900867.0)
        self.assertEqual(pe["otm"]["oi"], 25373153.0)
        self.assertAlmostEqual(pe["otm"]["oi_pct"], 84.86, delta=0.1)
        self.assertEqual(pe["itm"]["oi"], 4527714.0)
        self.assertAlmostEqual(pe["itm"]["oi_pct"], 15.14, delta=0.1)
        self.assertAlmostEqual(pe["otm"]["oi_pct"] + pe["itm"]["oi_pct"], 100.0, delta=0.1)

        # Fresh Additions
        self.assertEqual(pe["fresh_additions_total"], 3575165.0)
        self.assertEqual(pe["otm"]["fresh_additions"], 3500272.0)
        self.assertAlmostEqual(pe["otm"]["fresh_additions_pct"], 97.91, delta=0.1)
        self.assertEqual(pe["itm"]["fresh_additions"], 74893.0)
        self.assertAlmostEqual(pe["itm"]["fresh_additions_pct"], 2.09, delta=0.1)

        # Unwinding
        self.assertEqual(pe["unwinding_total"], 484076.0)
        self.assertEqual(pe["otm"]["unwinding"], 0.0)
        self.assertEqual(pe["itm"]["unwinding"], 484076.0)
        self.assertAlmostEqual(pe["itm"]["unwinding_pct"], 100.0, delta=0.1)

        # 4. Intelligence
        intel = res["intelligence"]
        self.assertAlmostEqual(intel["pcr"], 1.015, delta=0.01)
        self.assertEqual(intel["max_pain"], 24350.0)
        self.assertEqual(intel["resistance_1"], 24500.0)
        self.assertEqual(intel["support_1"], 24200.0)

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
        self.assertEqual(res["call_breakdown"]["total_oi"], 29445045.0)
        self.assertEqual(res["put_breakdown"]["total_oi"], 29900867.0)

    def test_zero_division_safety(self):
        """Ensure no divide-by-zero crashes on empty or zero-filled data."""
        empty_data = [
            {"strike": 24000, "ce_oi": 0, "ce_chg": 0, "pe_oi": 0, "pe_chg": 0, "spot": 24000}
        ]
        analyzer = OptionChainAnalyzer()
        res = analyzer.parse_json(empty_data)
        self.assertEqual(res["call_breakdown"]["total_oi"], 0.0)
        self.assertEqual(res["put_breakdown"]["total_oi"], 0.0)
        self.assertEqual(res["intelligence"]["pcr"], 0.0)


if __name__ == "__main__":
    unittest.main()
