"""
Sample Data Generator for MITS Option Chain Intelligence
Generates realistic NSE-style JSON, NSE-style CSV, and Simple CSV for NIFTY 50.
"""

import json
import csv
import os

SPOT_PRICE = 24350.50

# Strikes and realistic OI / Change in OI data
DATA = [
    # strike, ce_oi, ce_chg, ce_ltp, pe_oi, pe_chg, pe_ltp
    {"strike": 23800, "ce_oi": 15200, "ce_chg": -1800, "ce_ltp": 590.20, "pe_oi": 85400, "pe_chg": 8500, "pe_ltp": 18.40},
    {"strike": 23900, "ce_oi": 18400, "ce_chg": -2400, "ce_ltp": 495.50, "pe_oi": 92300, "pe_chg": 12400, "pe_ltp": 24.10},
    {"strike": 24000, "ce_oi": 35600, "ce_chg": -4100, "ce_ltp": 405.00, "pe_oi": 185600, "pe_chg": 24800, "pe_ltp": 32.75},
    {"strike": 24100, "ce_oi": 28900, "ce_chg": -1200, "ce_ltp": 320.15, "pe_oi": 112000, "pe_chg": 15600, "pe_ltp": 46.20},
    {"strike": 24200, "ce_oi": 42100, "ce_chg": 1500,  "ce_ltp": 242.80, "pe_oi": 145200, "pe_chg": 18900, "pe_ltp": 67.50},
    {"strike": 24300, "ce_oi": 68500, "ce_chg": 8200,  "ce_ltp": 172.40, "pe_oi": 168900, "pe_chg": 22400, "pe_ltp": 98.30},
    # ATM Boundary (Spot = 24350.50)
    {"strike": 24400, "ce_oi": 145000, "ce_chg": 28500, "ce_ltp": 112.50, "pe_oi": 98400,  "pe_chg": -3200, "pe_ltp": 142.10},
    {"strike": 24500, "ce_oi": 210400, "ce_chg": 42100, "ce_ltp": 68.30,  "pe_oi": 74500,  "pe_chg": -5400, "pe_ltp": 198.50},
    {"strike": 24600, "ce_oi": 182300, "ce_chg": 31200, "ce_ltp": 39.20,  "pe_oi": 41200,  "pe_chg": -2800, "pe_ltp": 268.00},
    {"strike": 24700, "ce_oi": 134200, "ce_chg": 19800, "ce_ltp": 21.60,  "pe_oi": 23400,  "pe_chg": -1200, "pe_ltp": 348.20},
    {"strike": 24800, "ce_oi": 115600, "ce_chg": 14500, "ce_ltp": 11.40,  "pe_oi": 14500,  "pe_chg": -600,  "pe_ltp": 435.00},
    {"strike": 24900, "ce_oi": 92500,  "ce_chg": 8400,  "ce_ltp": 6.10,   "pe_oi": 8900,   "pe_chg": -200,  "pe_ltp": 529.00},
]

def generate_json(filepath):
    records_data = []
    for item in DATA:
        records_data.append({
            "strikePrice": item["strike"],
            "expiryDate": "28-Nov-2026",
            "CE": {
                "strikePrice": item["strike"],
                "expiryDate": "28-Nov-2026",
                "underlying": "NIFTY",
                "openInterest": item["ce_oi"],
                "changeinOpenInterest": item["ce_chg"],
                "pchangeinOpenInterest": round((item["ce_chg"] / max(1, item["ce_oi"] - item["ce_chg"])) * 100, 2),
                "totalTradedVolume": item["ce_oi"] * 2,
                "impliedVolatility": 13.5,
                "lastPrice": item["ce_ltp"],
                "change": 12.5 if item["ce_chg"] > 0 else -10.2,
                "bidQty": 1500,
                "bidprice": item["ce_ltp"] - 0.5,
                "askQty": 2000,
                "askPrice": item["ce_ltp"] + 0.5,
                "underlyingValue": SPOT_PRICE
            },
            "PE": {
                "strikePrice": item["strike"],
                "expiryDate": "28-Nov-2026",
                "underlying": "NIFTY",
                "openInterest": item["pe_oi"],
                "changeinOpenInterest": item["pe_chg"],
                "pchangeinOpenInterest": round((item["pe_chg"] / max(1, item["pe_oi"] - item["pe_chg"])) * 100, 2),
                "totalTradedVolume": item["pe_oi"] * 2,
                "impliedVolatility": 14.1,
                "lastPrice": item["pe_ltp"],
                "change": -8.5 if item["pe_chg"] > 0 else 15.0,
                "bidQty": 1800,
                "bidprice": item["pe_ltp"] - 0.5,
                "askQty": 2200,
                "askPrice": item["pe_ltp"] + 0.5,
                "underlyingValue": SPOT_PRICE
            }
        })
    
    payload = {
        "records": {
            "expiryDates": ["28-Nov-2026"],
            "data": records_data,
            "timestamp": "14-Nov-2026 10:00:00",
            "underlyingValue": SPOT_PRICE
        }
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Generated JSON: {filepath}")

def generate_simple_csv(filepath):
    headers = ["Strike", "CE_OI", "CE_Chg_OI", "CE_LTP", "PE_OI", "PE_Chg_OI", "PE_LTP", "Spot_Price"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for item in DATA:
            writer.writerow([
                item["strike"],
                item["ce_oi"],
                item["ce_chg"],
                item["ce_ltp"],
                item["pe_oi"],
                item["pe_chg"],
                item["pe_ltp"],
                SPOT_PRICE
            ])
    print(f"Generated Simple CSV: {filepath}")

def generate_nse_csv(filepath):
    # Standard NSE option chain CSV structure with multi-level headers and underlying value in header
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([f"Underlying Index: NIFTY {SPOT_PRICE}", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
        writer.writerow(["CALLS", "", "", "", "", "", "", "", "", "", "STRIKE", "PUTS", "", "", "", "", "", "", "", "", ""])
        writer.writerow([
            "OI", "Chng in OI", "Volume", "IV", "LTP", "Net Chng", "Bid Qty", "Bid Price", "Ask Price", "Ask Qty",
            "Strike Price",
            "Bid Qty", "Bid Price", "Ask Price", "Ask Qty", "Net Chng", "LTP", "IV", "Volume", "Chng in OI", "OI"
        ])
        for item in DATA:
            writer.writerow([
                item["ce_oi"],
                item["ce_chg"],
                item["ce_oi"] * 2,
                13.5,
                item["ce_ltp"],
                12.5 if item["ce_chg"] > 0 else -10.2,
                1500,
                item["ce_ltp"] - 0.5,
                item["ce_ltp"] + 0.5,
                2000,
                item["strike"],
                1800,
                item["pe_ltp"] - 0.5,
                item["pe_ltp"] + 0.5,
                2200,
                -8.5 if item["pe_chg"] > 0 else 15.0,
                item["pe_ltp"],
                14.1,
                item["pe_oi"] * 2,
                item["pe_chg"],
                item["pe_oi"]
            ])
    print(f"Generated NSE CSV: {filepath}")

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    generate_json(os.path.join(base, "nse_option_chain_nifty.json"))
    generate_simple_csv(os.path.join(base, "simple_option_chain.csv"))
    generate_nse_csv(os.path.join(base, "nse_option_chain_nifty.csv"))
