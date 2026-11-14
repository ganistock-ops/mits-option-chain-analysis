"""
MITS Automated Option Chain Pipeline (EOD Derivatives Intelligence Engine)
Standalone Background Task for Fetching, Parsing, and Computing Option Chain Breakdown.

Author: Market Intelligence Trading System (MITS)
Workspace: MITS Option Chain Analysis (Standalone, Isolated)
"""

import os
import sys
import json
import time
import math
import argparse
import datetime
from typing import Dict, Any, List, Optional

try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False
    import requests

def clean_num(val: Any) -> float:
    """Robust numeric cleaner handling strings with commas, currency symbols, dashes, and blanks."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return 0.0 if math.isnan(val) else float(val)
    s = str(val).replace(",", "").replace("₹", "").replace("$", "").replace(" ", "").strip()
    if s in ("", "-", "--", "null", "none", "nan", "NaN", "undefined"):
        return 0.0
    try:
        return float(s)
    except Exception:
        return 0.0

def norm_str(s: Any) -> str:
    """Normalizes string for case-insensitive, punctuation-free matching."""
    return "".join(c for c in str(s or "").lower() if c.isalnum())


class MITSOptionChainPipeline:
    """
    Automated pipeline that fetches EOD Option Chain data from NSE,
    classifies every strike into ITM/OTM, computes exact cumulative open interest totals,
    breakdowns, buildup & unwinding, and saves structured JSON for display widgets.
    """

    NSE_HOME_URL = "https://www.nseindia.com"
    NSE_OC_PAGE = "https://www.nseindia.com/option-chain"
    NSE_API_BASE = "https://www.nseindia.com/api/option-chain-indices?symbol="

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    API_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain",
        "X-Requested-With": "XMLHttpRequest",
    }

    def __init__(self, symbol: str = "NIFTY", output_path: str = "option_chain_summary.json", expiry: Optional[str] = None):
        self.symbol = symbol.upper()
        self.output_path = output_path
        self.target_expiry = expiry
        self.spot_price: float = 0.0
        self.timestamp: str = ""
        self.expiry_date: str = ""
        self.data_source: str = "UNKNOWN"
        self.raw_data: Dict[str, Any] = {}

    def fetch_live_data(self) -> Optional[Dict[str, Any]]:
        """
        Attempts to fetch live Option Chain data directly from NSE India API.
        Uses curl_cffi with TLS fingerprint impersonation to bypass bot management.
        """
        api_url = f"{self.NSE_API_BASE}{self.symbol}"
        print(f"[PIPELINE] Attempting to fetch live EOD data for {self.symbol} from NSE...")

        if HAS_CURL_CFFI:
            try:
                session = cffi_requests.Session(impersonate="chrome120")
                session.headers.update(self.DEFAULT_HEADERS)
                resp_home = session.get(self.NSE_HOME_URL, timeout=12)
                if resp_home.status_code == 200:
                    time.sleep(1.0)
                    resp_oc = session.get(self.NSE_OC_PAGE, timeout=12)
                    time.sleep(1.0)
                    resp_api = session.get(api_url, headers=self.API_HEADERS, timeout=15)
                    if resp_api.status_code == 200:
                        data = resp_api.json()
                        if "records" in data and data["records"].get("data"):
                            print(f"[SUCCESS] Successfully fetched {self.symbol} live EOD data via curl_cffi.")
                            self.data_source = "NSE_LIVE_TLS"
                            return data
            except Exception as e:
                print(f"[WARN] curl_cffi live fetch encountered error: {e}")

        # Fallback to standard requests
        try:
            import requests
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
            os.path.join(os.path.dirname(__file__), "sample_data", "nse_option_chain_nifty.csv"),
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
        """
        Core mathematical calculations with 100% dynamic formulas and exact NSE data mirroring.
        Ensures Total Call OI and Total Put OI match cumulative totals from raw data with zero arbitrary filtering.
        """
        # 1. Spot Price & Metadata Detection
        records = data.get("records", {})
        if not records and "data" in data:
            records = data

        raw_spot = records.get("underlyingValue")
        self.timestamp = records.get("timestamp") or datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")

        # Check if NSE official pre-filtered block is available for the current expiry
        filtered = data.get("filtered", {})
        filtered_data = filtered.get("data", [])

        available_expiries = records.get("expiryDates", [])
        if self.target_expiry and self.target_expiry in available_expiries:
            active_expiry = self.target_expiry
        elif available_expiries:
            active_expiry = available_expiries[0]
        else:
            active_expiry = "CURRENT"
        self.expiry_date = active_expiry

        # Prefer filtered.data if it belongs to the active expiry; otherwise records.data
        if filtered_data and not self.target_expiry:
            data_items = filtered_data
        else:
            data_items = records.get("data", [])
            if not data_items and isinstance(data, list):
                data_items = data

        raw_strikes: List[Dict[str, Any]] = []

        for item in data_items:
            item_expiry = item.get("expiryDate")
            # If multiple expiries exist and user didn't specify 'ALL', filter by active expiry
            if item_expiry and active_expiry != "CURRENT" and item_expiry != active_expiry and len(available_expiries) > 1:
                continue

            strike = clean_num(item.get("strikePrice") or item.get("strike") or 0)
            if strike <= 0:
                continue

            ce_info = item.get("CE", {}) if isinstance(item.get("CE"), dict) else {}
            pe_info = item.get("PE", {}) if isinstance(item.get("PE"), dict) else {}

            if not raw_spot:
                raw_spot = ce_info.get("underlyingValue") or pe_info.get("underlyingValue")

            ce_oi = clean_num(ce_info.get("openInterest", item.get("ce_oi", 0)))
            ce_chg = clean_num(ce_info.get("changeinOpenInterest", item.get("ce_chg", 0)))
            ce_ltp = clean_num(ce_info.get("lastPrice", item.get("ce_ltp", 0)))

            pe_oi = clean_num(pe_info.get("openInterest", item.get("pe_oi", 0)))
            pe_chg = clean_num(pe_info.get("changeinOpenInterest", item.get("pe_chg", 0)))
            pe_ltp = clean_num(pe_info.get("lastPrice", item.get("pe_ltp", 0)))

            raw_strikes.append({
                "strike": strike,
                "ce_oi": ce_oi,
                "ce_chg": ce_chg,
                "ce_ltp": ce_ltp,
                "pe_oi": pe_oi,
                "pe_chg": pe_chg,
                "pe_ltp": pe_ltp,
            })

        # Deduplicate and sort by strike without dropping any data
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
                if r["ce_ltp"] > 0:
                    unique_strikes[k]["ce_ltp"] = r["ce_ltp"]
                if r["pe_ltp"] > 0:
                    unique_strikes[k]["pe_ltp"] = r["pe_ltp"]

        sorted_strikes = [unique_strikes[k] for k in sorted(unique_strikes.keys())]

        # Resolve Spot Price
        if raw_spot and clean_num(raw_spot) > 0:
            self.spot_price = clean_num(raw_spot)
        elif sorted_strikes:
            self.spot_price = sorted_strikes[len(sorted_strikes) // 2]["strike"]
        else:
            self.spot_price = 24350.50

        spot = self.spot_price

        # 2. Dynamic Strike Classification & Cumulative Accumulation
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

            # Dynamic Classification Rules:
            # Calls (CE): Strike < Spot => ITM, Strike >= Spot => OTM
            # Puts (PE): Strike <= Spot => OTM, Strike > Spot => ITM
            is_ce_itm = k < spot
            is_pe_itm = k > spot

            ce_classification = "ITM" if is_ce_itm else "OTM"
            pe_classification = "ITM" if is_pe_itm else "OTM"

            ce_total_oi += ce_oi
            pe_total_oi += pe_oi

            # Call breakdown: ITM vs OTM
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

            # Put breakdown: ITM vs OTM
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

        # Calculate Totals & Exact Percentages
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

        # Max Pain Strike
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

        # Support & Resistance (Top 2 CE & PE OI Walls)
        top_ce = sorted(processed_strikes, key=lambda x: x["ce_oi"], reverse=True)
        top_pe = sorted(processed_strikes, key=lambda x: x["pe_oi"], reverse=True)
        r1 = top_ce[0]["strike"] if len(top_ce) > 0 else None
        r2 = top_ce[1]["strike"] if len(top_ce) > 1 else None
        s1 = top_pe[0]["strike"] if len(top_pe) > 0 else None
        s2 = top_pe[1]["strike"] if len(top_pe) > 1 else None

        # Market Sentiment Logic
        if pcr >= 1.25:
            sentiment = "Strongly Bullish"
            sentiment_color = "#10b981"
            bias_summary = f"Heavy Put writing at {s1}. Put writers strongly dominant over Call writers."
        elif pcr >= 1.05:
            sentiment = "Moderately Bullish"
            sentiment_color = "#34d399"
            bias_summary = f"Healthy Put writing support at {s1}. Mild upward bias."
        elif pcr <= 0.70:
            sentiment = "Strongly Bearish"
            sentiment_color = "#ef4444"
            bias_summary = f"Severe Call writing overhead at {r1}. Strong downward pressure."
        elif pcr <= 0.85:
            sentiment = "Moderately Bearish"
            sentiment_color = "#f87171"
            bias_summary = f"Call writers capping upside moves near {r1}."
        else:
            sentiment = "Neutral / Rangebound"
            sentiment_color = "#f59e0b"
            bias_summary = f"Rangebound between {s1} (Support) and {r1} (Resistance). Both writers active."

        return {
            "metadata": {
                "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "nse_timestamp": self.timestamp,
                "symbol": self.symbol,
                "expiry_date": self.expiry_date,
                "data_source": self.data_source,
                "pipeline_version": "2.1.0",
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
            "strikes": processed_strikes
        }

    def _convert_csv_to_records(self, csv_text: str) -> Dict[str, Any]:
        """
        Robust parser for CSV option chains (official NSE multi-header format and simple CSV).
        Dynamically locates Strike, CE OI, CE Chg, CE LTP, PE OI, PE Chg, PE LTP columns.
        Uses clean_num so '-' or empty cells never cause strikes to be dropped.
        """
        import csv, re
        lines = [l.strip() for l in csv_text.splitlines() if l.strip()]
        detected_spot = None

        for l in lines[:5]:
            m = re.search(r"(?:underlying|spot)[^0-9]*([0-9]+(?:\.[0-9]+)?)", l, re.IGNORECASE)
            if m:
                detected_spot = float(m.group(1))
                break

        # Locate header row
        parsed_lines = list(csv.reader(lines))
        header_idx = -1
        for i, row in enumerate(parsed_lines[:10]):
            if any("strike" in norm_str(c) for c in row):
                header_idx = i
                break

        if header_idx != -1 and header_idx + 1 < len(parsed_lines) and any("strike" in norm_str(c) for c in parsed_lines[header_idx + 1]):
            header_idx += 1

        if header_idx == -1:
            header_idx = 0

        header = [c.strip() for c in parsed_lines[header_idx]]
        norm_header = [norm_str(c) for c in header]

        # Find strike column
        strike_col_idx = -1
        for i, c in enumerate(norm_header):
            if "strike" in c:
                strike_col_idx = i
                break

        is_symmetric = strike_col_idx > 3 and (len(header) - strike_col_idx) > 3

        # Resolve CE columns (before strike_col_idx)
        ce_oi_idx = -1
        ce_chg_idx = -1
        ce_ltp_idx = -1
        if is_symmetric:
            for i in range(strike_col_idx):
                cn = norm_header[i]
                if cn in ("oi", "openinterest") and ce_oi_idx == -1:
                    ce_oi_idx = i
                elif ("chg" in cn or "change" in cn) and "oi" in cn and ce_chg_idx == -1:
                    ce_chg_idx = i
                elif ("ltp" in cn or "lastprice" in cn) and ce_ltp_idx == -1:
                    ce_ltp_idx = i

            # Fallbacks for standard NSE positions
            if ce_oi_idx == -1: ce_oi_idx = 0
            if ce_chg_idx == -1: ce_chg_idx = 1
            if ce_ltp_idx == -1: ce_ltp_idx = 4

            # Resolve PE columns (after strike_col_idx)
            pe_oi_idx = -1
            pe_chg_idx = -1
            pe_ltp_idx = -1
            for i in range(strike_col_idx + 1, len(header)):
                cn = norm_header[i]
                if cn in ("oi", "openinterest"):
                    pe_oi_idx = i
                elif ("chg" in cn or "change" in cn) and "oi" in cn:
                    pe_chg_idx = i
                elif ("ltp" in cn or "lastprice" in cn) and pe_ltp_idx == -1:
                    pe_ltp_idx = i

            # Fallback to scanning from right if not matched
            non_empty_indices = [idx for idx in range(strike_col_idx + 1, len(header)) if norm_header[idx]]
            if pe_oi_idx == -1 and non_empty_indices:
                pe_oi_idx = non_empty_indices[-1]
            if pe_chg_idx == -1 and len(non_empty_indices) >= 2:
                pe_chg_idx = non_empty_indices[-2]
            if pe_ltp_idx == -1 and len(non_empty_indices) >= 5:
                pe_ltp_idx = non_empty_indices[-5]

        data_rows = []
        for row in parsed_lines[header_idx + 1:]:
            if len(row) <= strike_col_idx or strike_col_idx == -1:
                continue

            strike_raw = str(row[strike_col_idx]).strip()
            # Skip NSE summary Total row or empty rows
            if not strike_raw or norm_str(strike_raw) == "total":
                continue

            k = clean_num(strike_raw)
            if k <= 0:
                continue

            try:
                if is_symmetric:
                    ce_oi = clean_num(row[ce_oi_idx]) if ce_oi_idx < len(row) else 0.0
                    ce_chg = clean_num(row[ce_chg_idx]) if ce_chg_idx < len(row) else 0.0
                    ce_ltp = clean_num(row[ce_ltp_idx]) if ce_ltp_idx < len(row) else 0.0

                    pe_oi = clean_num(row[pe_oi_idx]) if pe_oi_idx < len(row) else 0.0
                    pe_chg = clean_num(row[pe_chg_idx]) if pe_chg_idx < len(row) else 0.0
                    pe_ltp = clean_num(row[pe_ltp_idx]) if pe_ltp_idx < len(row) else 0.0
                else:
                    d = dict(zip(norm_header, row))
                    ce_oi = clean_num(d.get("ceoi") or d.get("calloi") or d.get("oi") or 0)
                    ce_chg = clean_num(d.get("cechgoi") or d.get("callchg") or d.get("chnginoi") or d.get("cechg") or 0)
                    ce_ltp = clean_num(d.get("celtp") or d.get("callltp") or d.get("ltp") or 0)

                    pe_oi = clean_num(d.get("peoi") or d.get("putoi") or 0)
                    pe_chg = clean_num(d.get("pechgoi") or d.get("putchg") or d.get("pechg") or 0)
                    pe_ltp = clean_num(d.get("peltp") or d.get("putltp") or 0)

                    if not detected_spot and d.get("spotprice"):
                        detected_spot = clean_num(d["spotprice"])

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
        """Prints a clean CLI summary table for terminal and GitHub Actions log visibility."""
        meta = summary["metadata"]
        intel = summary["intelligence"]
        ce = summary["call_breakdown"]
        pe = summary["put_breakdown"]
        spot = summary["spot_price"]

        print("\n" + "=" * 76)
        print(f"  MITS AUTOMATED EOD OPTION CHAIN | {meta['symbol']} @ {spot:,.2f}  ")
        print("=" * 76)
        print(f"Source: {meta['data_source']} | Expiry: {meta['expiry_date']} | Status: {intel['sentiment']}")
        print(f"Strikes Parsed: {meta['total_strikes']} | PCR: {intel['pcr']} | Max Pain: {intel['max_pain']:,.0f}")
        print(f"Key Resistance (Call Wall): {intel['resistance_1']:,.0f} | Key Support (Put Wall): {intel['support_1']:,.0f}")
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
