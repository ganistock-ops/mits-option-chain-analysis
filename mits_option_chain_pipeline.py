"""
MITS Option Chain Automated EOD Pipeline
----------------------------------------
Autonomous post-market background pipeline that fetches EOD Option Chain data,
performs deep mathematical calculations, and generates structured JSON output
for automated WordPress widget / frontend consumption with zero manual uploads.

Author: Market Intelligence Trading System (MITS)
Workspace: MITS Option Chain Analysis (Standalone)
"""

import os
import sys
import json
import time
import argparse
import datetime
from typing import Dict, Any, List, Optional, Tuple

# Try importing curl_cffi for anti-bot TLS bypass, fallback to requests
HAS_CURL_CFFI = False
try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    pass

import requests

class MITSOptionChainPipeline:
    """
    Automated EOD Option Chain Pipeline:
    - Fetches data from NSE India API with session cookies & realistic headers
    - Detects Spot Price programmatically
    - Dynamically categorizes strikes into ITM & OTM for CE & PE
    - Computes Total OI, Fresh Additions (buildup), Unwinding (liquidation), PCR, Max Pain
    - Writes structured 'option_chain_summary.json'
    """

    NSE_HOME_URL = "https://www.nseindia.com"
    NSE_INDICES_URL = "https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    NSE_EQUITIES_URL = "https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    API_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain",
        "X-Requested-With": "XMLHttpRequest",
    }

    def __init__(self, symbol: str = "NIFTY", output_path: str = "option_chain_summary.json", expiry: Optional[str] = None):
        self.symbol = symbol.upper().strip()
        self.output_path = output_path
        self.target_expiry = expiry
        self.raw_data: Optional[Dict[str, Any]] = None
        self.spot_price: float = 0.0
        self.expiry_date: str = ""
        self.timestamp: str = ""
        self.data_source: str = "LIVE_NSE"

    def fetch_live_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches live/EOD option chain payload from NSE API.
        Employs session cookie acquisition and curl_cffi/requests fallback.
        """
        is_index = self.symbol in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
        api_url = (self.NSE_INDICES_URL if is_index else self.NSE_EQUITIES_URL).format(symbol=self.symbol)

        print(f"[PIPELINE] Attempting to fetch live EOD data for {self.symbol} from NSE...")

        # Method 1: curl_cffi with Chrome TLS impersonation
        if HAS_CURL_CFFI:
            try:
                session = cffi_requests.Session()
                # 1. Acquire cookies
                resp_home = session.get(self.NSE_HOME_URL, headers=self.DEFAULT_HEADERS, impersonate="chrome120", timeout=12)
                if resp_home.status_code == 200:
                    time.sleep(1.0)
                    # 2. Query API
                    resp_api = session.get(api_url, headers=self.API_HEADERS, impersonate="chrome120", timeout=15)
                    if resp_api.status_code == 200:
                        data = resp_api.json()
                        if "records" in data and data["records"].get("data"):
                            print(f"[SUCCESS] Successfully fetched {self.symbol} live EOD data via curl_cffi.")
                            self.data_source = "NSE_LIVE_CURL_CFFI"
                            return data
            except Exception as e:
                print(f"[WARN] curl_cffi live fetch encountered error: {e}")

        # Method 2: Standard requests.Session
        try:
            session = requests.Session()
            session.headers.update(self.DEFAULT_HEADERS)
            resp_home = session.get(self.NSE_HOME_URL, timeout=12)
            if resp_home.status_code == 200:
                time.sleep(1.0)
                resp_api = session.get(api_url, headers=self.API_HEADERS, timeout=15)
                if resp_api.status_code == 200:
                    data = resp_api.json()
                    if "records" in data and data["records"].get("data"):
                        print(f"[SUCCESS] Successfully fetched {self.symbol} live EOD data via requests.")
                        self.data_source = "NSE_LIVE_REQUESTS"
                        return data
        except Exception as e:
            print(f"[WARN] Standard requests live fetch encountered error: {e}")

        return None

    def load_fallback_or_file(self, input_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Loads input from an explicit file or uses the resilient local fallback.
        Ensures the pipeline NEVER crashes if NSE blocks runner IPs or is on holiday.
        """
        if input_file and os.path.exists(input_file):
            print(f"[PIPELINE] Loading provided input file: {input_file}")
            self.data_source = f"LOCAL_FILE_{os.path.basename(input_file)}"
            with open(input_file, "r", encoding="utf-8-sig") as f:
                content = f.read().strip()
                if content.startswith("{") or content.startswith("["):
                    return json.loads(content)
                else:
                    return self._convert_csv_to_records(content)

        # Look for local sample / cached files in workspace
        candidate_paths = [
            os.path.join(os.path.dirname(__file__), "sample_data", "nse_option_chain_nifty.json"),
            os.path.join(os.path.dirname(__file__), "sample_data", "simple_option_chain.csv"),
            os.path.join(os.path.dirname(__file__), "option_chain_summary.json"),
        ]

        for p in candidate_paths:
            if os.path.exists(p):
                print(f"[PIPELINE] Using cached/sample dataset as resilient fallback: {p}")
                self.data_source = f"CACHED_FALLBACK_{os.path.basename(p)}"
                with open(p, "r", encoding="utf-8-sig") as f:
                    content = f.read().strip()
                    if content.startswith("{"):
                        return json.loads(content)
                    elif content.startswith("Strike") or "strike" in content.lower():
                        return self._convert_csv_to_records(content)

        raise RuntimeError("No live NSE connection and no fallback datasets found.")

    def run(self, input_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes complete pipeline end-to-end:
        1. Fetch/Load EOD data
        2. Detect Spot Price
        3. Dynamic ITM/OTM categorization & math breakdown
        4. Write structured option_chain_summary.json
        """
        raw_payload = None

        if not input_file:
            raw_payload = self.fetch_live_data()

        if not raw_payload:
            print("[INFO] Falling back to local offline / cached data structure...")
            raw_payload = self.load_fallback_or_file(input_file)

        self.raw_data = raw_payload
        summary = self.process_analytics(raw_payload)

        # Write to JSON
        output_abs = os.path.abspath(self.output_path)
        os.makedirs(os.path.dirname(output_abs) if os.path.dirname(output_abs) else ".", exist_ok=True)
        with open(output_abs, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] EOD Option Chain Analytics saved to: {output_abs}")
        self.print_console_summary(summary)
        return summary

    def process_analytics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Core mathematical calculations with 100% dynamic formulas."""
        # 1. Spot Price Detection
        records = data.get("records", {})
        if not records and "data" in data:
            records = data

        raw_spot = records.get("underlyingValue")
        self.timestamp = records.get("timestamp") or datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")

        # Expiry selection (nearest expiry if not provided)
        available_expiries = records.get("expiryDates", [])
        if self.target_expiry and self.target_expiry in available_expiries:
            active_expiry = self.target_expiry
        elif available_expiries:
            active_expiry = available_expiries[0]
        else:
            active_expiry = "CURRENT"
        self.expiry_date = active_expiry

        data_items = records.get("data", [])
        if not data_items and isinstance(data, list):
            data_items = data

        raw_strikes: List[Dict[str, Any]] = []

        for item in data_items:
            # Filter by expiry if multiple expiries exist
            item_expiry = item.get("expiryDate")
            if item_expiry and active_expiry != "CURRENT" and item_expiry != active_expiry:
                continue

            strike = float(item.get("strikePrice") or item.get("strike") or 0)
            if strike <= 0:
                continue

            ce_info = item.get("CE", {})
            pe_info = item.get("PE", {})

            # Detect spot if not at root
            if not raw_spot:
                raw_spot = ce_info.get("underlyingValue") or pe_info.get("underlyingValue")

            raw_strikes.append({
                "strike": strike,
                "ce_oi": float(ce_info.get("openInterest") or item.get("ce_oi") or 0),
                "ce_chg": float(ce_info.get("changeinOpenInterest") or item.get("ce_chg") or 0),
                "ce_ltp": float(ce_info.get("lastPrice") or item.get("ce_ltp") or 0),
                "pe_oi": float(pe_info.get("openInterest") or item.get("pe_oi") or 0),
                "pe_chg": float(pe_info.get("changeinOpenInterest") or item.get("pe_chg") or 0),
                "pe_ltp": float(pe_info.get("lastPrice") or item.get("pe_ltp") or 0),
            })

        # Sort and deduplicate by strike
        unique_strikes: Dict[float, Dict[str, Any]] = {}
        for r in raw_strikes:
            k = r["strike"]
            if k not in unique_strikes:
                unique_strikes[k] = r
            else:
                unique_strikes[k]["ce_oi"] += r["ce_oi"]
                unique_strikes[k]["ce_chg"] += r["ce_chg"]
                unique_strikes[k]["pe_oi"] += r["pe_oi"]
                unique_strikes[k]["pe_chg"] += r["pe_chg"]

        sorted_strikes = [unique_strikes[k] for k in sorted(unique_strikes.keys())]

        # Resolve Spot Price
        if raw_spot and float(raw_spot) > 0:
            self.spot_price = float(raw_spot)
        elif sorted_strikes:
            self.spot_price = sorted_strikes[len(sorted_strikes) // 2]["strike"]
        else:
            self.spot_price = 0.0

        spot = self.spot_price

        # 2. Dynamic Strike Categorization & OI Accumulation
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

        processed_strikes: List[Dict[str, Any]] = []

        for r in sorted_strikes:
            k = r["strike"]
            ce_oi = r["ce_oi"]
            ce_chg = r["ce_chg"]
            pe_oi = r["pe_oi"]
            pe_chg = r["pe_chg"]

            # Dynamic Rules:
            # Calls (CE): Strike < Spot => ITM, Strike >= Spot => OTM
            # Puts (PE): Strike <= Spot => OTM, Strike > Spot => ITM
            is_ce_itm = k < spot
            is_pe_itm = k > spot

            ce_classification = "ITM" if is_ce_itm else "OTM"
            pe_classification = "ITM" if is_pe_itm else "OTM"

            ce_total_oi += ce_oi
            pe_total_oi += pe_oi

            # Call breakdown
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

            # Put breakdown
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
                "strike": k,
                "spot_diff": round(k - spot, 2),
                "ce_classification": ce_classification,
                "pe_classification": pe_classification,
                "ce_oi": ce_oi,
                "ce_chg": ce_chg,
                "ce_ltp": r["ce_ltp"],
                "pe_oi": pe_oi,
                "pe_chg": pe_chg,
                "pe_ltp": r["pe_ltp"],
            })

        # Calculate Totals & Percentages
        ce_fresh_total = ce_fresh_otm + ce_fresh_itm
        ce_unwind_total = ce_unwind_otm + ce_unwind_itm
        pe_fresh_total = pe_fresh_otm + pe_fresh_itm
        pe_unwind_total = pe_unwind_otm + pe_unwind_itm

        call_breakdown = {
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

        put_breakdown = {
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

        # 3. Key Ratios & Intelligence
        pcr = round(pe_total_oi / ce_total_oi, 3) if ce_total_oi > 0 else 0.0
        pcr_fresh = round(pe_fresh_total / ce_fresh_total, 3) if ce_fresh_total > 0 else 0.0

        # Max Pain
        min_loss = float("inf")
        max_pain_strike = spot
        for trial in processed_strikes:
            t = trial["strike"]
            loss = 0.0
            for s in processed_strikes:
                k = s["strike"]
                if t > k:
                    loss += (t - k) * s["ce_oi"]
                if t < k:
                    loss += (k - t) * s["pe_oi"]
            if loss < min_loss:
                min_loss = loss
                max_pain_strike = t

        # Support & Resistance (Top 2 CE & PE OI)
        top_ce = sorted(processed_strikes, key=lambda x: x["ce_oi"], reverse=True)
        top_pe = sorted(processed_strikes, key=lambda x: x["pe_oi"], reverse=True)
        r1 = top_ce[0]["strike"] if len(top_ce) > 0 else None
        r2 = top_ce[1]["strike"] if len(top_ce) > 1 else None
        s1 = top_pe[0]["strike"] if len(top_pe) > 0 else None
        s2 = top_pe[1]["strike"] if len(top_pe) > 1 else None

        # Sentiment
        if pcr >= 1.25:
            sentiment = "Strongly Bullish"
            sentiment_color = "#10b981"
            bias_summary = f"Bullish stance (PCR {pcr:.2f}). Put writers dominating with solid floor at {s1}."
        elif pcr >= 1.05:
            sentiment = "Moderately Bullish"
            sentiment_color = "#34d399"
            bias_summary = f"Mild bullish bias. Put additions leading; watch resistance at {r1}."
        elif pcr <= 0.70:
            sentiment = "Strongly Bearish"
            sentiment_color = "#ef4444"
            bias_summary = f"Heavy bearish bias (PCR {pcr:.2f}). Intense Call writing capping at {r1}."
        elif pcr <= 0.85:
            sentiment = "Moderately Bearish"
            sentiment_color = "#f87171"
            bias_summary = f"Mild bearish bias. Call additions exceed Put additions; resistance at {r1}."
        else:
            sentiment = "Neutral / Rangebound"
            sentiment_color = "#f59e0b"
            bias_summary = f"Rangebound between {s1} (Support) and {r1} (Resistance). Both writers active."

        return {
            "metadata": {
                "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "nse_timestamp": self.timestamp,
                "symbol": self.symbol,
                "expiry_date": active_expiry,
                "data_source": self.data_source,
                "pipeline_version": "2.0.0",
                "total_strikes": len(processed_strikes),
            },
            "spot_price": spot,
            "call_breakdown": call_breakdown,
            "put_breakdown": put_breakdown,
            "intelligence": {
                "pcr": pcr,
                "pcr_fresh": pcr_fresh,
                "max_pain": max_pain_strike,
                "resistance_1": r1,
                "resistance_2": r2,
                "support_1": s1,
                "support_2": s2,
                "sentiment": sentiment,
                "sentiment_color": sentiment_color,
                "bias_summary": bias_summary,
            },
            "strikes": processed_strikes,
        }

    def _convert_csv_to_records(self, csv_text: str) -> Dict[str, Any]:
        """Converts raw CSV text into NSE-compatible records structure."""
        import csv, re
        lines = [l.strip() for l in csv_text.splitlines() if l.strip()]
        detected_spot = None

        for l in lines[:5]:
            m = re.search(r"(?:underlying|spot)[^0-9]*([0-9]+(?:\.[0-9]+)?)", l, re.IGNORECASE)
            if m:
                detected_spot = float(m.group(1))
                break

        # Locate header
        parsed_lines = list(csv.reader(lines))
        header_idx = -1
        for i, row in enumerate(parsed_lines[:10]):
            if any("strike" in c.lower() for c in row):
                header_idx = i
                break

        if header_idx != -1 and header_idx + 1 < len(parsed_lines) and any("strike" in c.lower() for c in parsed_lines[header_idx + 1]):
            header_idx += 1

        header = [c.strip().lower() for c in parsed_lines[header_idx]]
        strike_idx = [i for i, c in enumerate(header) if "strike" in c][0]
        is_symmetric = strike_idx > 3 and (len(header) - strike_idx) > 3

        data_rows = []
        for row in parsed_lines[header_idx + 1:]:
            if len(row) <= strike_idx:
                continue
            try:
                if is_symmetric:
                    k = float(row[strike_idx].replace(",", ""))
                    ce_oi = float(row[0].replace(",", "") or 0)
                    ce_chg = float(row[1].replace(",", "") or 0)
                    ce_ltp = float(row[4].replace(",", "") or 0)
                    pe_oi = float(row[-1].replace(",", "") or 0)
                    pe_chg = float(row[-2].replace(",", "") or 0)
                    pe_ltp = float(row[-5].replace(",", "") or 0)
                else:
                    d = dict(zip(header, row))
                    k = float(d.get("strike", 0) or d.get("strikeprice", 0))
                    ce_oi = float(d.get("ce_oi", 0) or d.get("call_oi", 0) or 0)
                    ce_chg = float(d.get("ce_chg", 0) or d.get("call_chg", 0) or 0)
                    ce_ltp = float(d.get("ce_ltp", 0) or d.get("call_ltp", 0) or 0)
                    pe_oi = float(d.get("pe_oi", 0) or d.get("put_oi", 0) or 0)
                    pe_chg = float(d.get("pe_chg", 0) or d.get("put_chg", 0) or 0)
                    pe_ltp = float(d.get("pe_ltp", 0) or d.get("put_ltp", 0) or 0)
                    if not detected_spot and d.get("spot_price"):
                        detected_spot = float(d["spot_price"])

                data_rows.append({
                    "strikePrice": k,
                    "CE": {"openInterest": ce_oi, "changeinOpenInterest": ce_chg, "lastPrice": ce_ltp},
                    "PE": {"openInterest": pe_oi, "changeinOpenInterest": pe_chg, "lastPrice": pe_ltp},
                })
            except Exception:
                continue

        return {
            "records": {
                "underlyingValue": detected_spot or (data_rows[len(data_rows)//2]["strikePrice"] if data_rows else 0),
                "data": data_rows,
                "timestamp": datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
                "expiryDates": ["CURRENT"],
            }
        }

    def print_console_summary(self, summary: Dict[str, Any]):
        """Prints a clean CLI summary table for GitHub Actions log visibility."""
        meta = summary["metadata"]
        intel = summary["intelligence"]
        ce = summary["call_breakdown"]
        pe = summary["put_breakdown"]
        spot = summary["spot_price"]

        print("\n" + "=" * 76)
        print(f"  MITS AUTOMATED EOD OPTION CHAIN | {meta['symbol']} @ {spot:,.2f}  ")
        print("=" * 76)
        print(f"Source: {meta['data_source']} | Expiry: {meta['expiry_date']} | Status: {intel['sentiment']}")
        print(f"PCR: {intel['pcr']} | Max Pain: {intel['max_pain']:,.0f} | Resistance: {intel['resistance_1']:,.0f} | Support: {intel['support_1']:,.0f}")
        print(f"Market Bias: {intel['bias_summary']}")
        print("-" * 76)
        print(f"{'METRIC':<32} | {'CALL SIDE (CE)':<18} | {'PUT SIDE (PE)':<18}")
        print("-" * 76)
        print(f"{'Total Open Interest':<32} | {ce['total_oi']:>18,.0f} | {pe['total_oi']:>18,.0f}")
        print(f"{'  - OTM Open Interest':<32} | {ce['otm']['oi']:>10,.0f} ({ce['otm']['oi_pct']:>5.1f}%) | {pe['otm']['oi']:>10,.0f} ({pe['otm']['oi_pct']:>5.1f}%)")
        print(f"{'  - ITM Open Interest':<32} | {ce['itm']['oi']:>10,.0f} ({ce['itm']['oi_pct']:>5.1f}%) | {pe['itm']['oi']:>10,.0f} ({pe['itm']['oi_pct']:>5.1f}%)")
        print("-" * 76)
        print(f"{'Fresh Additions (Total)':<32} | {ce['fresh_additions_total']:>18,.0f} | {pe['fresh_additions_total']:>18,.0f}")
        print(f"{'  - OTM Fresh Additions':<32} | {ce['otm']['fresh_additions']:>10,.0f} ({ce['otm']['fresh_additions_pct']:>5.1f}%) | {pe['otm']['fresh_additions']:>10,.0f} ({pe['otm']['fresh_additions_pct']:>5.1f}%)")
        print(f"{'  - ITM Fresh Additions':<32} | {ce['itm']['fresh_additions']:>10,.0f} ({ce['itm']['fresh_additions_pct']:>5.1f}%) | {pe['itm']['fresh_additions']:>10,.0f} ({pe['itm']['fresh_additions_pct']:>5.1f}%)")
        print("-" * 76)
        print(f"{'Unwinding (Total)':<32} | {ce['unwinding_total']:>18,.0f} | {pe['unwinding_total']:>18,.0f}")
        print(f"{'  - OTM Unwinding':<32} | {ce['otm']['unwinding']:>10,.0f} ({ce['otm']['unwinding_pct']:>5.1f}%) | {pe['otm']['unwinding']:>10,.0f} ({pe['otm']['unwinding_pct']:>5.1f}%)")
        print(f"{'  - ITM Unwinding':<32} | {ce['itm']['unwinding']:>10,.0f} ({ce['itm']['unwinding_pct']:>5.1f}%) | {pe['itm']['unwinding']:>10,.0f} ({pe['itm']['unwinding_pct']:>5.1f}%)")
        print("=" * 76 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MITS Automated EOD Option Chain Pipeline")
    parser.add_argument("--symbol", "-s", type=str, default="NIFTY", help="Underlying Index or Stock (NIFTY, BANKNIFTY, etc.)")
    parser.add_argument("--output", "-o", type=str, default="option_chain_summary.json", help="Path to save output JSON")
    parser.add_argument("--input", "-i", type=str, default=None, help="Optional manual input CSV/JSON to process")
    parser.add_argument("--expiry", "-e", type=str, default=None, help="Target expiry date (e.g. 28-Nov-2026)")

    args = parser.parse_args()

    pipeline = MITSOptionChainPipeline(
        symbol=args.symbol,
        output_path=args.output,
        expiry=args.expiry
    )
    pipeline.run(input_file=args.input)
