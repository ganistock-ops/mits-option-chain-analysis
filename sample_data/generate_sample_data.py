"""
Sample Data Generator for MITS Option Chain Intelligence
Generates authentic full-scale NSE-style JSON, multi-header CSV, and simple CSV for NIFTY 50.
Covers the entire realistic strike range: 22,000 to 26,000 at 50-point intervals (81 strikes).
"""

import json
import csv
import math
import os

SPOT_PRICE = 24350.50
EXPIRY_DATE = "28-Nov-2026"
TIMESTAMP = "14-Nov-2026 15:30:00"

def generate_strike_data():
    strikes = list(range(22000, 26050, 50))
    rows = []
    
    for k in strikes:
        dist = k - SPOT_PRICE
        abs_dist = abs(dist)
        
        # CE OI profile: peak in OTM near ATM (24400 - 24800), peak at 24500 and 25000
        if k < SPOT_PRICE:  # ITM CE
            base_ce_oi = max(5000, int(450000 * math.exp(-abs_dist / 600)))
            if k >= 24200:
                ce_chg = int(base_ce_oi * 0.08)
            else:
                ce_chg = -int(base_ce_oi * 0.12)
        else:  # OTM CE
            mult = 1.6 if k in (24500, 25000) else (1.3 if k in (24400, 24600, 24700, 24800) else 1.0)
            base_ce_oi = int(mult * max(8000, int(1650000 * math.exp(-abs_dist / 750))))
            ce_chg = int(base_ce_oi * 0.18) if k <= 25200 else int(base_ce_oi * 0.05)

        # PE OI profile: peak in OTM near ATM (23900 - 24300), peak at 24000 and 24200
        if k <= SPOT_PRICE:  # OTM PE
            mult = 1.6 if k in (24000, 24200) else (1.3 if k in (24100, 24300, 23800) else 1.0)
            base_pe_oi = int(mult * max(8000, int(1550000 * math.exp(-abs_dist / 750))))
            pe_chg = int(base_pe_oi * 0.17) if k >= 23500 else int(base_pe_oi * 0.04)
        else:  # ITM PE
            base_pe_oi = max(5000, int(420000 * math.exp(-abs_dist / 600)))
            if k <= 24500:
                pe_chg = int(base_pe_oi * 0.07)
            else:
                pe_chg = -int(base_pe_oi * 0.14)

        # Realistic LTP calculations based on Black-Scholes approximations
        ce_intrinsic = max(0.0, SPOT_PRICE - k)
        pe_intrinsic = max(0.0, k - SPOT_PRICE)
        time_val = max(1.5, 180.0 * math.exp(-abs_dist / 700.0))
        ce_ltp = round(ce_intrinsic + time_val, 2)
        pe_ltp = round(pe_intrinsic + time_val, 2)

        rows.append({
            "strike": k,
            "ce_oi": base_ce_oi,
            "ce_chg": ce_chg,
            "ce_ltp": ce_ltp,
            "pe_oi": base_pe_oi,
            "pe_chg": pe_chg,
            "pe_ltp": pe_ltp
        })
    return rows

DATA = generate_strike_data()

def generate_json(filepath):
    records_data = []
    tot_ce_oi = 0
    tot_pe_oi = 0
    tot_ce_vol = 0
    tot_pe_vol = 0

    for item in DATA:
        tot_ce_oi += item["ce_oi"]
        tot_pe_oi += item["pe_oi"]
        ce_vol = item["ce_oi"] * 2
        pe_vol = item["pe_oi"] * 2
        tot_ce_vol += ce_vol
        tot_pe_vol += pe_vol

        records_data.append({
            "strikePrice": item["strike"],
            "expiryDate": EXPIRY_DATE,
            "CE": {
                "strikePrice": item["strike"],
                "expiryDate": EXPIRY_DATE,
                "underlying": "NIFTY",
                "openInterest": item["ce_oi"],
                "changeinOpenInterest": item["ce_chg"],
                "pchangeinOpenInterest": round((item["ce_chg"] / max(1, item["ce_oi"] - item["ce_chg"])) * 100, 2),
                "totalTradedVolume": ce_vol,
                "impliedVolatility": 13.5,
                "lastPrice": item["ce_ltp"],
                "change": 12.5 if item["ce_chg"] > 0 else -10.2,
                "bidQty": 1500,
                "bidprice": round(item["ce_ltp"] - 0.5, 2),
                "askQty": 2000,
                "askPrice": round(item["ce_ltp"] + 0.5, 2),
                "underlyingValue": SPOT_PRICE
            },
            "PE": {
                "strikePrice": item["strike"],
                "expiryDate": EXPIRY_DATE,
                "underlying": "NIFTY",
                "openInterest": item["pe_oi"],
                "changeinOpenInterest": item["pe_chg"],
                "pchangeinOpenInterest": round((item["pe_chg"] / max(1, item["pe_oi"] - item["pe_chg"])) * 100, 2),
                "totalTradedVolume": pe_vol,
                "impliedVolatility": 14.1,
                "lastPrice": item["pe_ltp"],
                "change": -8.5 if item["pe_chg"] > 0 else 15.0,
                "bidQty": 1800,
                "bidprice": round(item["pe_ltp"] - 0.5, 2),
                "askQty": 2200,
                "askPrice": round(item["pe_ltp"] + 0.5, 2),
                "underlyingValue": SPOT_PRICE
            }
        })
    
    payload = {
        "records": {
            "expiryDates": [EXPIRY_DATE],
            "data": records_data,
            "timestamp": TIMESTAMP,
            "underlyingValue": SPOT_PRICE,
            "totOI": tot_ce_oi + tot_pe_oi,
            "totVol": tot_ce_vol + tot_pe_vol
        },
        "filtered": {
            "data": records_data,
            "CE": {
                "totOI": tot_ce_oi,
                "totVol": tot_ce_vol
            },
            "PE": {
                "totOI": tot_pe_oi,
                "totVol": tot_pe_vol
            }
        }
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Generated JSON: {filepath} ({len(DATA)} strikes, Total CE OI: {tot_ce_oi:,}, Total PE OI: {tot_pe_oi:,})")

def generate_nse_csv(filepath):
    # Official multi-header 21-column NSE India format with Total summary row
    lines = [
        f"Underlying Index: NIFTY {SPOT_PRICE}" + "," * 20,
        "CALLS" + "," * 9 + "STRIKE" + "," + "PUTS" + "," * 9,
        "OI,Chng in OI,Volume,IV,LTP,Net Chng,Bid Qty,Bid Price,Ask Price,Ask Qty,Strike Price,Bid Qty,Bid Price,Ask Price,Ask Qty,Net Chng,LTP,IV,Volume,Chng in OI,OI"
    ]
    tot_ce_oi = sum(item["ce_oi"] for item in DATA)
    tot_pe_oi = sum(item["pe_oi"] for item in DATA)
    tot_ce_chg = sum(item["ce_chg"] for item in DATA)
    tot_pe_chg = sum(item["pe_chg"] for item in DATA)
    tot_ce_vol = sum(item["ce_oi"] * 2 for item in DATA)
    tot_pe_vol = sum(item["pe_oi"] * 2 for item in DATA)

    for item in DATA:
        lines.append(
            f"{item['ce_oi']},{item['ce_chg']},{item['ce_oi']*2},13.5,{item['ce_ltp']},-10.2,1500,{round(item['ce_ltp']-0.5,2)},{round(item['ce_ltp']+0.5,2)},2000,{item['strike']},1800,{round(item['pe_ltp']-0.5,2)},{round(item['pe_ltp']+0.5,2)},2200,-8.5,{item['pe_ltp']},14.1,{item['pe_oi']*2},{item['pe_chg']},{item['pe_oi']}"
        )

    # Official NSE Total summary row
    lines.append(
        f"{tot_ce_oi},{tot_ce_chg},{tot_ce_vol},-,13.5,-,-,-,-,-,Total,-,-,-,-,-,14.1,-,{tot_pe_vol},{tot_pe_chg},{tot_pe_oi}"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Generated NSE CSV: {filepath}")

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

if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    generate_json(os.path.join(out_dir, "nse_option_chain_nifty.json"))
    generate_nse_csv(os.path.join(out_dir, "nse_option_chain_nifty.csv"))
    generate_simple_csv(os.path.join(out_dir, "simple_option_chain.csv"))
