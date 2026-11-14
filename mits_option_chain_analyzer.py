"""
MITS Option Chain Intelligence Engine
Standalone Parser and Analytics Engine for Option Chain Documents (CSV, Excel, JSON).

Author: Market Intelligence Trading System (MITS)
Workspace: MITS Option Chain Analysis (Standalone)
"""

import os
import sys
import json
import csv
import re
from typing import Dict, Any, List, Optional, Tuple

class OptionChainAnalyzer:
    """
    Parser and calculation engine for Option Chain data.
    Performs dynamic ITM/OTM categorization, CE & PE breakdowns,
    fresh additions/unwinding calculations, and sentiment intelligence.
    """

    def __init__(self, spot_price: Optional[float] = None):
        self.spot_price = spot_price
        self.raw_rows: List[Dict[str, Any]] = []
        self.underlying: str = "NIFTY"
        self.timestamp: str = ""
        self.analysis: Dict[str, Any] = {}

    def parse_file(self, filepath: str, spot_price_override: Optional[float] = None) -> Dict[str, Any]:
        """Loads and parses a CSV or JSON file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)
            return self.parse_json(content, spot_price_override)
        elif ext in [".csv", ".txt"]:
            with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
                content = f.read()
            return self.parse_csv(content, spot_price_override)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Supported formats: .json, .csv, .txt")

    def parse_json(self, data: Any, spot_price_override: Optional[float] = None) -> Dict[str, Any]:
        """Parses NSE-style JSON or generic JSON array."""
        self.raw_rows = []
        detected_spot = None

        # Pattern 1: NSE official format with 'records'
        if isinstance(data, dict) and "records" in data:
            records = data.get("records", {})
            detected_spot = records.get("underlyingValue")
            self.timestamp = records.get("timestamp", "")
            
            data_list = records.get("data", [])
            for item in data_list:
                strike = float(item.get("strikePrice", 0))
                ce_data = item.get("CE", {})
                pe_data = item.get("PE", {})

                if not detected_spot and ce_data.get("underlyingValue"):
                    detected_spot = float(ce_data["underlyingValue"])
                elif not detected_spot and pe_data.get("underlyingValue"):
                    detected_spot = float(pe_data["underlyingValue"])

                if not self.underlying:
                    self.underlying = ce_data.get("underlying") or pe_data.get("underlying") or "NIFTY"

                self.raw_rows.append({
                    "strike": strike,
                    "ce_oi": float(ce_data.get("openInterest", 0) or 0),
                    "ce_chg": float(ce_data.get("changeinOpenInterest", 0) or 0),
                    "ce_ltp": float(ce_data.get("lastPrice", 0) or 0),
                    "pe_oi": float(pe_data.get("openInterest", 0) or 0),
                    "pe_chg": float(pe_data.get("changeinOpenInterest", 0) or 0),
                    "pe_ltp": float(pe_data.get("lastPrice", 0) or 0),
                })

        # Pattern 2: Flat list of dictionaries
        elif isinstance(data, list):
            for row in data:
                strike = self._extract_num(row, ["strike", "strikeprice", "strike_price", "k"])
                if strike is None:
                    continue
                ce_oi = self._extract_num(row, ["ce_oi", "call_oi", "ceoi", "calls_oi", "calls open interest"]) or 0
                ce_chg = self._extract_num(row, ["ce_chg", "ce_chg_oi", "call_chg", "calls_chng in oi", "calls_change"]) or 0
                ce_ltp = self._extract_num(row, ["ce_ltp", "call_ltp", "calls_ltp", "ce_last_price"]) or 0
                pe_oi = self._extract_num(row, ["pe_oi", "put_oi", "peoi", "puts_oi", "puts open interest"]) or 0
                pe_chg = self._extract_num(row, ["pe_chg", "pe_chg_oi", "put_chg", "puts_chng in oi", "puts_change"]) or 0
                pe_ltp = self._extract_num(row, ["pe_ltp", "put_ltp", "puts_ltp", "pe_last_price"]) or 0
                
                spot_in_row = self._extract_num(row, ["spot", "spot_price", "underlying", "underlyingvalue"])
                if spot_in_row and not detected_spot:
                    detected_spot = spot_in_row

                self.raw_rows.append({
                    "strike": strike,
                    "ce_oi": ce_oi,
                    "ce_chg": ce_chg,
                    "ce_ltp": ce_ltp,
                    "pe_oi": pe_oi,
                    "pe_chg": pe_chg,
                    "pe_ltp": pe_ltp
                })

        return self._finalize_parsing(detected_spot, spot_price_override)

    def parse_csv(self, csv_text: str, spot_price_override: Optional[float] = None) -> Dict[str, Any]:
        """Parses CSV text supporting both NSE multi-header format and simple tabular format."""
        self.raw_rows = []
        detected_spot = None

        lines = [line.strip() for line in csv_text.splitlines() if line.strip()]
        if not lines:
            raise ValueError("CSV content is empty.")

        # Check top lines for Spot Price metadata (e.g. 'Underlying Index: NIFTY 24350.50' or 'Spot: 24350')
        for i in range(min(5, len(lines))):
            line = lines[i]
            spot_match = re.search(r"(?:underlying|spot)[^0-9]*([0-9]+(?:\.[0-9]+)?)", line, re.IGNORECASE)
            if spot_match:
                detected_spot = float(spot_match.group(1))
                break

        # Detect header row index
        header_idx = -1
        header_cols: List[str] = []
        for i, line in enumerate(lines[:10]):
            cols = [c.strip().lower() for c in next(csv.reader([line]))]
            if any("strike" in c for c in cols):
                header_idx = i
                header_cols = cols
                break

        if header_idx == -1:
            # Fallback to line 0 if no header found
            header_idx = 0
            header_cols = [c.strip().lower() for c in next(csv.reader([lines[0]]))]

        # Check if this is an NSE standard 23-column format:
        # CE columns on left, Strike in middle, PE columns on right
        strike_col_idx = None
        for idx, col in enumerate(header_cols):
            if "strike" in col:
                strike_col_idx = idx
                break

        is_nse_symmetric = False
        if strike_col_idx is not None and strike_col_idx > 3 and (len(header_cols) - strike_col_idx) > 3:
            is_nse_symmetric = True

        for line_idx in range(header_idx + 1, len(lines)):
            line = lines[line_idx]
            reader = list(csv.reader([line]))
            if not reader or not reader[0]:
                continue
            cols = [c.strip() for c in reader[0]]
            if len(cols) <= max(1, strike_col_idx or 0):
                continue

            try:
                if is_nse_symmetric and strike_col_idx is not None:
                    # CE is on the left of Strike, PE is on the right of Strike
                    strike_val = self._clean_num(cols[strike_col_idx])
                    if strike_val is None:
                        continue

                    # NSE typical CE columns: 0=OI, 1=Chng in OI, 2=Volume, 3=IV, 4=LTP ...
                    ce_oi = self._clean_num(cols[0]) or 0
                    ce_chg = self._clean_num(cols[1]) or 0
                    ce_ltp = self._clean_num(cols[4]) if len(cols) > 4 else 0

                    # NSE typical PE columns: Strike+1=Bid Qty... or from the end
                    # Usually PE LTP is col Strike+7 (or 16), Chng in OI is Strike+10 (or 19), OI is Strike+11 (or 20)
                    # Let's inspect column positions relative to total length
                    pe_oi = self._clean_num(cols[-1]) or 0
                    pe_chg = self._clean_num(cols[-2]) or 0
                    pe_ltp = self._clean_num(cols[-5]) if len(cols) >= 5 else 0

                    self.raw_rows.append({
                        "strike": strike_val,
                        "ce_oi": ce_oi,
                        "ce_chg": ce_chg,
                        "ce_ltp": ce_ltp,
                        "pe_oi": pe_oi,
                        "pe_chg": pe_chg,
                        "pe_ltp": pe_ltp
                    })
                else:
                    # Tabular with named columns
                    row_dict = dict(zip(header_cols, cols))
                    strike_val = self._extract_num(row_dict, ["strike", "strikeprice", "strike_price", "strike price", "k"])
                    if strike_val is None:
                        continue
                    ce_oi = self._extract_num(row_dict, ["ce_oi", "call_oi", "ceoi", "calls_oi", "oi_ce", "calls open interest", "oi"]) or 0
                    ce_chg = self._extract_num(row_dict, ["ce_chg", "ce_chg_oi", "call_chg", "calls_chng in oi", "chng in oi", "chg_ce"]) or 0
                    ce_ltp = self._extract_num(row_dict, ["ce_ltp", "call_ltp", "calls_ltp", "ltp_ce", "ltp"]) or 0
                    pe_oi = self._extract_num(row_dict, ["pe_oi", "put_oi", "peoi", "puts_oi", "oi_pe", "puts open interest"]) or 0
                    pe_chg = self._extract_num(row_dict, ["pe_chg", "pe_chg_oi", "put_chg", "puts_chng in oi", "chg_pe"]) or 0
                    pe_ltp = self._extract_num(row_dict, ["pe_ltp", "put_ltp", "puts_ltp", "ltp_pe"]) or 0

                    spot_val = self._extract_num(row_dict, ["spot", "spot_price", "spot price", "underlying", "underlyingvalue"])
                    if spot_val and not detected_spot:
                        detected_spot = spot_val

                    self.raw_rows.append({
                        "strike": strike_val,
                        "ce_oi": ce_oi,
                        "ce_chg": ce_chg,
                        "ce_ltp": ce_ltp,
                        "pe_oi": pe_oi,
                        "pe_chg": pe_chg,
                        "pe_ltp": pe_ltp
                    })
            except Exception:
                continue

        return self._finalize_parsing(detected_spot, spot_price_override)

    def _finalize_parsing(self, detected_spot: Optional[float], spot_price_override: Optional[float]) -> Dict[str, Any]:
        """Resolves spot price, sorts rows, and executes complete analysis."""
        if spot_price_override is not None and spot_price_override > 0:
            self.spot_price = float(spot_price_override)
        elif detected_spot is not None and detected_spot > 0:
            self.spot_price = float(detected_spot)
        elif self.raw_rows:
            # Fallback estimation: strike with closest CE LTP to PE LTP or median strike
            strikes = sorted([r["strike"] for r in self.raw_rows])
            self.spot_price = strikes[len(strikes) // 2]
        else:
            self.spot_price = 0.0

        # Sort rows by strike ascending and deduplicate by strike
        unique_strikes = {}
        for r in self.raw_rows:
            k = r["strike"]
            if k not in unique_strikes:
                unique_strikes[k] = r
            else:
                # Merge if duplicated
                unique_strikes[k]["ce_oi"] += r["ce_oi"]
                unique_strikes[k]["ce_chg"] += r["ce_chg"]
                unique_strikes[k]["pe_oi"] += r["pe_oi"]
                unique_strikes[k]["pe_chg"] += r["pe_chg"]

        self.raw_rows = [unique_strikes[k] for k in sorted(unique_strikes.keys())]
        self.analysis = self.calculate_metrics()
        return self.analysis

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Executes all core mathematical breakdowns:
        - Spot Price & Strike Classification (Dynamic ITM/OTM)
        - Call Side (CE) Breakdown: Total OI, OTM vs ITM (Abs + %), Fresh Additions, Unwinding
        - Put Side (PE) Breakdown: Total OI, OTM vs ITM (Abs + %), Fresh Additions, Unwinding
        - Advanced Intelligence: PCR, Max Pain, Support & Resistance, Sentiment Bias
        """
        spot = self.spot_price or 0.0
        
        # Categorize strikes and enrich table
        processed_strikes = []
        ce_total_oi = 0.0
        pe_total_oi = 0.0

        ce_otm_oi = 0.0
        ce_itm_oi = 0.0
        pe_otm_oi = 0.0
        pe_itm_oi = 0.0

        ce_fresh_otm = 0.0
        ce_fresh_itm = 0.0
        ce_unwind_otm = 0.0
        ce_unwind_itm = 0.0

        pe_fresh_otm = 0.0
        pe_fresh_itm = 0.0
        pe_unwind_otm = 0.0
        pe_unwind_itm = 0.0

        for r in self.raw_rows:
            strike = r["strike"]
            ce_oi = r["ce_oi"]
            ce_chg = r["ce_chg"]
            pe_oi = r["pe_oi"]
            pe_chg = r["pe_chg"]

            # Dynamic Classification:
            # CALL (CE): Strike < Spot => ITM; Strike >= Spot => OTM
            # PUT (PE): Strike <= Spot => OTM; Strike > Spot => ITM
            is_ce_itm = strike < spot
            is_pe_itm = strike > spot

            ce_classification = "ITM" if is_ce_itm else "OTM"
            pe_classification = "ITM" if is_pe_itm else "OTM"

            # Sum Total OI
            ce_total_oi += ce_oi
            pe_total_oi += pe_oi

            # Call OI Breakdown
            if is_ce_itm:
                ce_itm_oi += ce_oi
                if ce_chg > 0:
                    ce_fresh_itm += ce_chg
                elif ce_chg < 0:
                    ce_unwind_itm += abs(ce_chg)
            else:
                ce_otm_oi += ce_oi
                if ce_chg > 0:
                    ce_fresh_otm += ce_chg
                elif ce_chg < 0:
                    ce_unwind_otm += abs(ce_chg)

            # Put OI Breakdown
            if is_pe_itm:
                pe_itm_oi += pe_oi
                if pe_chg > 0:
                    pe_fresh_itm += pe_chg
                elif pe_chg < 0:
                    pe_unwind_itm += abs(pe_chg)
            else:
                pe_otm_oi += pe_oi
                if pe_chg > 0:
                    pe_fresh_otm += pe_chg
                elif pe_chg < 0:
                    pe_unwind_otm += abs(pe_chg)

            processed_strikes.append({
                "strike": strike,
                "spot_diff": round(strike - spot, 2),
                "ce_classification": ce_classification,
                "pe_classification": pe_classification,
                "ce_oi": ce_oi,
                "ce_chg": ce_chg,
                "ce_ltp": r.get("ce_ltp", 0.0),
                "pe_oi": pe_oi,
                "pe_chg": pe_chg,
                "pe_ltp": r.get("pe_ltp", 0.0),
            })

        # Calculate CE Totals & Percentages
        ce_fresh_total = ce_fresh_otm + ce_fresh_itm
        ce_unwind_total = ce_unwind_otm + ce_unwind_itm

        ce_breakdown = {
            "total_oi": ce_total_oi,
            "otm": {
                "oi": ce_otm_oi,
                "oi_pct": round((ce_otm_oi / ce_total_oi * 100), 2) if ce_total_oi > 0 else 0.0,
                "fresh_additions": ce_fresh_otm,
                "fresh_additions_pct": round((ce_fresh_otm / ce_fresh_total * 100), 2) if ce_fresh_total > 0 else 0.0,
                "unwinding": ce_unwind_otm,
                "unwinding_pct": round((ce_unwind_otm / ce_unwind_total * 100), 2) if ce_unwind_total > 0 else 0.0,
            },
            "itm": {
                "oi": ce_itm_oi,
                "oi_pct": round((ce_itm_oi / ce_total_oi * 100), 2) if ce_total_oi > 0 else 0.0,
                "fresh_additions": ce_fresh_itm,
                "fresh_additions_pct": round((ce_fresh_itm / ce_fresh_total * 100), 2) if ce_fresh_total > 0 else 0.0,
                "unwinding": ce_unwind_itm,
                "unwinding_pct": round((ce_unwind_itm / ce_unwind_total * 100), 2) if ce_unwind_total > 0 else 0.0,
            },
            "fresh_additions_total": ce_fresh_total,
            "unwinding_total": ce_unwind_total,
        }

        # Calculate PE Totals & Percentages
        pe_fresh_total = pe_fresh_otm + pe_fresh_itm
        pe_unwind_total = pe_unwind_otm + pe_unwind_itm

        pe_breakdown = {
            "total_oi": pe_total_oi,
            "otm": {
                "oi": pe_otm_oi,
                "oi_pct": round((pe_otm_oi / pe_total_oi * 100), 2) if pe_total_oi > 0 else 0.0,
                "fresh_additions": pe_fresh_otm,
                "fresh_additions_pct": round((pe_fresh_otm / pe_fresh_total * 100), 2) if pe_fresh_total > 0 else 0.0,
                "unwinding": pe_unwind_otm,
                "unwinding_pct": round((pe_unwind_otm / pe_unwind_total * 100), 2) if pe_unwind_total > 0 else 0.0,
            },
            "itm": {
                "oi": pe_itm_oi,
                "oi_pct": round((pe_itm_oi / pe_total_oi * 100), 2) if pe_total_oi > 0 else 0.0,
                "fresh_additions": pe_fresh_itm,
                "fresh_additions_pct": round((pe_fresh_itm / pe_fresh_total * 100), 2) if pe_fresh_total > 0 else 0.0,
                "unwinding": pe_unwind_itm,
                "unwinding_pct": round((pe_unwind_itm / pe_unwind_total * 100), 2) if pe_unwind_total > 0 else 0.0,
            },
            "fresh_additions_total": pe_fresh_total,
            "unwinding_total": pe_unwind_total,
        }

        # Key Intelligence Ratios
        pcr = round(pe_total_oi / ce_total_oi, 3) if ce_total_oi > 0 else 0.0
        pcr_fresh = round(pe_fresh_total / ce_fresh_total, 3) if ce_fresh_total > 0 else 0.0

        # Max Pain Calculation
        # For every strike S, calculate option buyers total payout if market expires at S
        max_pain_strike = None
        min_loss = float("inf")
        strikes_list = [r["strike"] for r in processed_strikes]
        
        for trial_strike in strikes_list:
            total_loss = 0.0
            for r in processed_strikes:
                k = r["strike"]
                # CE payout: max(0, trial_strike - k) * CE_OI
                if trial_strike > k:
                    total_loss += (trial_strike - k) * r["ce_oi"]
                # PE payout: max(0, k - trial_strike) * PE_OI
                if trial_strike < k:
                    total_loss += (k - trial_strike) * r["pe_oi"]
            
            if total_loss < min_loss:
                min_loss = total_loss
                max_pain_strike = trial_strike

        # Key Support & Resistance (Top 2 CE OI and Top 2 PE OI)
        sorted_ce_oi = sorted(processed_strikes, key=lambda x: x["ce_oi"], reverse=True)
        sorted_pe_oi = sorted(processed_strikes, key=lambda x: x["pe_oi"], reverse=True)

        resistances = [r["strike"] for r in sorted_ce_oi[:2]] if sorted_ce_oi else []
        supports = [r["strike"] for r in sorted_pe_oi[:2]] if sorted_pe_oi else []

        # Market Sentiment Interpretation
        if pcr >= 1.25:
            sentiment = "Strongly Bullish"
            sentiment_color = "#10b981"
            bias_summary = f"Bullish bias with PCR at {pcr:.2f}. Heavy Put writing indicates strong floor at {supports[0] if supports else 'support'}."
        elif pcr >= 1.05:
            sentiment = "Moderately Bullish"
            sentiment_color = "#34d399"
            bias_summary = f"Mild bullish bias. Put writers outnumber Call writers. Watch resistance at {resistances[0] if resistances else 'resistance'}."
        elif pcr >= 0.85:
            sentiment = "Neutral / Rangebound"
            sentiment_color = "#f59e0b"
            bias_summary = f"Rangebound market between {supports[0] if supports else 'Support'} and {resistances[0] if resistances else 'Resistance'}. Both Call and Put writers active."
        elif pcr >= 0.70:
            sentiment = "Moderately Bearish"
            sentiment_color = "#f87171"
            bias_summary = f"Mild bearish bias with PCR at {pcr:.2f}. Heavy Call writing capped near {resistances[0] if resistances else 'resistance'}."
        else:
            sentiment = "Strongly Bearish"
            sentiment_color = "#ef4444"
            bias_summary = f"Strong bearish pressure. Heavy Call additions in OTM strikes and weak Put support."

        return {
            "spot_price": spot,
            "underlying": self.underlying,
            "timestamp": self.timestamp,
            "total_strikes": len(processed_strikes),
            "call_breakdown": ce_breakdown,
            "put_breakdown": pe_breakdown,
            "intelligence": {
                "pcr": pcr,
                "pcr_fresh": pcr_fresh,
                "max_pain": max_pain_strike,
                "resistance_1": resistances[0] if len(resistances) > 0 else None,
                "resistance_2": resistances[1] if len(resistances) > 1 else None,
                "support_1": supports[0] if len(supports) > 0 else None,
                "support_2": supports[1] if len(supports) > 1 else None,
                "sentiment": sentiment,
                "sentiment_color": sentiment_color,
                "bias_summary": bias_summary,
            },
            "strikes": processed_strikes
        }

    @staticmethod
    def _clean_num(val: Any) -> Optional[float]:
        """Cleans numeric strings with commas, dashes, and currency symbols."""
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip().replace(",", "").replace(" ", "").replace("₹", "").replace("$", "")
        if s in ["", "-", "--", "None", "null", "NaN"]:
            return 0.0
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def _extract_num(d: Dict[str, Any], candidates: List[str]) -> Optional[float]:
        """Searches a dictionary for any matching candidate key and converts to float."""
        for c in candidates:
            for k, v in d.items():
                if k.lower().strip() == c.lower().strip():
                    return OptionChainAnalyzer._clean_num(v)
        return None

    def print_cli_summary(self):
        """Prints a human-readable CLI report."""
        if not self.analysis:
            print("No analysis available.")
            return

        res = self.analysis
        spot = res["spot_price"]
        ce = res["call_breakdown"]
        pe = res["put_breakdown"]
        intel = res["intelligence"]

        print("=" * 78)
        print(f"  MITS OPTION CHAIN INTELLIGENCE REPORT | SPOT: {spot:,.2f}")
        print("=" * 78)
        print(f"PCR: {intel['pcr']} | Max Pain: {intel['max_pain']} | Sentiment: {intel['sentiment']}")
        print(f"Major Resistance: {intel['resistance_1']} (R2: {intel['resistance_2']})")
        print(f"Major Support:    {intel['support_1']} (S2: {intel['support_2']})")
        print(f"Market Bias:      {intel['bias_summary']}")
        print("-" * 78)
        print(f"{'METRIC':<35} | {'CALL SIDE (CE)':<18} | {'PUT SIDE (PE)':<18}")
        print("-" * 78)
        print(f"{'Total Open Interest (OI)':<35} | {ce['total_oi']:>18,.0f} | {pe['total_oi']:>18,.0f}")
        print(f"{'OTM Open Interest':<35} | {ce['otm']['oi']:>10,.0f} ({ce['otm']['oi_pct']:>5.1f}%) | {pe['otm']['oi']:>10,.0f} ({pe['otm']['oi_pct']:>5.1f}%)")
        print(f"{'ITM Open Interest':<35} | {ce['itm']['oi']:>10,.0f} ({ce['itm']['oi_pct']:>5.1f}%) | {pe['itm']['oi']:>10,.0f} ({pe['itm']['oi_pct']:>5.1f}%)")
        print("-" * 78)
        print(f"{'Fresh Additions (Total)':<35} | {ce['fresh_additions_total']:>18,.0f} | {pe['fresh_additions_total']:>18,.0f}")
        print(f"{'  - OTM Fresh Additions':<35} | {ce['otm']['fresh_additions']:>10,.0f} ({ce['otm']['fresh_additions_pct']:>5.1f}%) | {pe['otm']['fresh_additions']:>10,.0f} ({pe['otm']['fresh_additions_pct']:>5.1f}%)")
        print(f"{'  - ITM Fresh Additions':<35} | {ce['itm']['fresh_additions']:>10,.0f} ({ce['itm']['fresh_additions_pct']:>5.1f}%) | {pe['itm']['fresh_additions']:>10,.0f} ({pe['itm']['fresh_additions_pct']:>5.1f}%)")
        print("-" * 78)
        print(f"{'Unwinding (Total)':<35} | {ce['unwinding_total']:>18,.0f} | {pe['unwinding_total']:>18,.0f}")
        print(f"{'  - OTM Unwinding':<35} | {ce['otm']['unwinding']:>10,.0f} ({ce['otm']['unwinding_pct']:>5.1f}%) | {pe['otm']['unwinding']:>10,.0f} ({pe['otm']['unwinding_pct']:>5.1f}%)")
        print(f"{'  - ITM Unwinding':<35} | {ce['itm']['unwinding']:>10,.0f} ({ce['itm']['unwinding_pct']:>5.1f}%) | {pe['itm']['unwinding']:>10,.0f} ({pe['itm']['unwinding_pct']:>5.1f}%)")
        print("=" * 78)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MITS Option Chain Intelligence Engine")
    parser.add_argument("--file", "-f", type=str, help="Path to Option Chain CSV or JSON file", required=False)
    parser.add_argument("--spot", "-s", type=float, help="Manual Spot Price override", required=False)
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    # If no file provided, run default on sample data
    file_path = args.file
    if not file_path:
        default_sample = os.path.join(os.path.dirname(__file__), "sample_data", "simple_option_chain.csv")
        if os.path.exists(default_sample):
            file_path = default_sample
            print(f"[INFO] No file specified. Running demonstration with sample: {file_path}")
        else:
            parser.print_help()
            sys.exit(1)

    analyzer = OptionChainAnalyzer()
    try:
        results = analyzer.parse_file(file_path, spot_price_override=args.spot)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            analyzer.print_cli_summary()
    except Exception as e:
        print(f"[ERROR] Failed to analyze file: {e}")
        sys.exit(1)
