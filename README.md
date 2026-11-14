# MITS Option Chain Intelligence Widget & Automated EOD Pipeline (Standalone)

> **MITS Option Chain Analysis** — An isolated, institutional-grade Option Chain Intelligence Engine, Automated EOD Pipeline, and WordPress Widget for Indian & Global Derivatives Markets. Zero manual file uploads required.

---

## 📌 Overview

This repository provides an end-to-end, fully automated derivatives intelligence solution:
1. **Automated Background EOD Pipeline (`mits_option_chain_pipeline.py`)**: Post-market automated fetching (using TLS browser impersonation via `curl_cffi` / `requests`), spot price detection, dynamic ITM/OTM strike classification, deep Open Interest analytics, and structured JSON output generation (`option_chain_summary.json`).
2. **GitHub Actions Post-Market Cron (`.github/workflows/eod_option_chain.yml`)**: Automated daily pipeline execution at 4:00 PM IST (10:30 UTC) and 5:00 PM IST (11:30 UTC) every trading day (Monday–Friday). Automatically commits and pushes updated analytics back to the repository.
3. **Automated Zero-Upload WordPress Widget (`mits-option-chain-widget.html` / `mits-option-chain-plugin.zip`)**: Client-side dashboard that auto-syncs with `option_chain_summary.json` on page load, rendering live calculations, PCR, Max Pain, and charts with zero manual intervention (with a collapsible manual upload drawer available as a fallback).

---

## 🧮 Mathematical Breakdown & Calculation Methodology

All calculations are performed dynamically with zero hardcoding:

### 1. Spot Price & Strike Classification
* **Spot Detection**: Automatically parsed from `records.underlyingValue` (JSON) or file header metadata (e.g. `Underlying Index: NIFTY 24350.50`). A manual override button is also provided in the UI.
* **Call Options (CE)**:
  $$\text{Strike} < \text{Spot Price} \implies \mathbf{ITM}$$
  $$\text{Strike} \ge \text{Spot Price} \implies \mathbf{OTM}$$
* **Put Options (PE)**:
  $$\text{Strike} \le \text{Spot Price} \implies \mathbf{OTM}$$
  $$\text{Strike} > \text{Spot Price} \implies \mathbf{ITM}$$

### 2. Call Side (CE) Breakdown
* **Total Call OI**: $\sum \text{CE OI}$
* **OTM Calls OI**: $\sum_{\text{Strike} \ge \text{Spot}} \text{CE OI}$
  * **Share %**: $\left( \frac{\text{OTM CE OI}}{\text{Total CE OI}} \right) \times 100\%$
* **ITM Calls OI**: $\sum_{\text{Strike} < \text{Spot}} \text{CE OI}$
  * **Share %**: $\left( \frac{\text{ITM CE OI}}{\text{Total CE OI}} \right) \times 100\%$
* **Fresh Additions (Buildup)**: Strikes where $\text{Change in OI} > 0$:
  * $\text{Total Fresh Additions} = \sum_{\Delta \text{OI} > 0} \Delta \text{OI}$
  * $\text{OTM Fresh Additions \%} = \left( \frac{\sum_{\text{OTM}, \Delta \text{OI} > 0} \Delta \text{OI}}{\text{Total Fresh Additions}} \right) \times 100\%$
  * $\text{ITM Fresh Additions \%} = \left( \frac{\sum_{\text{ITM}, \Delta \text{OI} > 0} \Delta \text{OI}}{\text{Total Fresh Additions}} \right) \times 100\%$
* **Unwinding (OI Reduction)**: Strikes where $\text{Change in OI} < 0$:
  * $\text{Total Unwinding} = \sum_{\Delta \text{OI} < 0} |\Delta \text{OI}|$
  * $\text{OTM Unwinding \%} = \left( \frac{\sum_{\text{OTM}, \Delta \text{OI} < 0} |\Delta \text{OI}|}{\text{Total Unwinding}} \right) \times 100\%$
  * $\text{ITM Unwinding \%} = \left( \frac{\sum_{\text{ITM}, \Delta \text{OI} < 0} |\Delta \text{OI}|}{\text{Total Unwinding}} \right) \times 100\%$

### 3. Put Side (PE) Breakdown
* **Total Put OI**: $\sum \text{PE OI}$
* **OTM Puts OI**: $\sum_{\text{Strike} \le \text{Spot}} \text{PE OI}$
  * **Share %**: $\left( \frac{\text{OTM PE OI}}{\text{Total PE OI}} \right) \times 100\%$
* **ITM Puts OI**: $\sum_{\text{Strike} > \text{Spot}} \text{PE OI}$
  * **Share %**: $\left( \frac{\text{ITM PE OI}}{\text{Total PE OI}} \right) \times 100\%$
* **Fresh Additions (Buildup)**: Strikes where $\Delta \text{PE OI} > 0$:
  * $\text{OTM Fresh \%} = \left( \frac{\sum_{\text{OTM}, \Delta \text{PE OI} > 0} \Delta \text{PE OI}}{\text{Total PE Fresh}} \right) \times 100\%$
  * $\text{ITM Fresh \%} = \left( \frac{\sum_{\text{ITM}, \Delta \text{PE OI} > 0} \Delta \text{PE OI}}{\text{Total PE Fresh}} \right) \times 100\%$
* **Unwinding (Exit)**: Strikes where $\Delta \text{PE OI} < 0$:
  * $\text{OTM Unwinding \%} = \left( \frac{\sum_{\text{OTM}, \Delta \text{PE OI} < 0} |\Delta \text{PE OI}|}{\text{Total PE Unwinding}} \right) \times 100\%$
  * $\text{ITM Unwinding \%} = \left( \frac{\sum_{\text{ITM}, \Delta \text{PE OI} < 0} |\Delta \text{PE OI}|}{\text{Total PE Unwinding}} \right) \times 100\%$

### 4. Advanced Intelligence Indicators
* **Put-Call Ratio (PCR)**: $\frac{\text{Total PE OI}}{\text{Total CE OI}}$
  * $> 1.25$: Strongly Bullish
  * $1.05 - 1.25$: Moderately Bullish
  * $0.85 - 1.05$: Neutral / Rangebound
  * $0.70 - 0.85$: Moderately Bearish
  * $< 0.70$: Strongly Bearish
* **Max Pain Strike**: Strike $S$ that minimizes total option writer payout:
  $$\min_S \left[ \sum_K \max(0, S - K) \times \text{CE OI}_K + \sum_K \max(0, K - S) \times \text{PE OI}_K \right]$$
* **Support & Resistance**:
  * Resistance 1 & 2: Highest and second-highest Call OI strikes ("Call Walls").
  * Support 1 & 2: Highest and second-highest Put OI strikes ("Put Walls").

---

## 🤖 Automated EOD Pipeline (`mits_option_chain_pipeline.py`)

The automated pipeline completely eliminates manual file uploads by executing in the background, fetching fresh EOD option chain data, performing all mathematical calculations, and exporting clean structured analytics to `option_chain_summary.json`.

### Pipeline Execution
```bash
# Fetch live EOD NIFTY data and export summary JSON
python mits_option_chain_pipeline.py --symbol NIFTY --output option_chain_summary.json

# Fetch BANKNIFTY EOD data
python mits_option_chain_pipeline.py --symbol BANKNIFTY --output option_chain_summary.json

# Process local file via pipeline engine
python mits_option_chain_pipeline.py --file sample_data/nse_option_chain_nifty.json
```

### Pipeline Key Features
* **Bypass NSE Restrictions**: Automatically leverages `curl_cffi` (impersonating `chrome120` TLS fingerprints) with automatic fallback to standard `requests` sessions and cookies initialization.
* **Resilient Offline Fallback**: In case of network sandbox limits or NSE holiday closures, seamlessly falls back to cached EOD snapshots, ensuring downstream CI/CD runners never exit with an error.
* **Deterministic Structured JSON**: Outputs `option_chain_summary.json` containing Spot Price, CE/PE Total OI, OTM/ITM breakdowns, Fresh Additions (OTM vs ITM), Unwinding (OTM vs ITM), PCR, Fresh PCR, Max Pain, Resistance/Support walls, and Strike-level matrix.

---

## ⏰ Daily GitHub Actions Automation (`.github/workflows/eod_option_chain.yml`)

The repository includes a ready-to-run GitHub Actions workflow that automates the entire process every trading day:

### Workflow Schedule & Triggers
* **Cron Schedule 1**: `30 10 * * 1-5` — 4:00 PM IST (10:30 UTC), Monday through Friday (post-market settlement).
* **Cron Schedule 2**: `30 11 * * 1-5` — 5:00 PM IST (11:30 UTC), Monday through Friday (final verified EOD figures).
* **Manual Trigger**: `workflow_dispatch` button enabled in GitHub Actions tab for instantaneous on-demand runs.

### What GitHub Actions Does:
1. Clones the repository.
2. Installs Python 3.11 with dependencies (`requests`, `curl_cffi`).
3. Executes `mits_option_chain_pipeline.py --symbol NIFTY --output option_chain_summary.json`.
4. Automatically commits and pushes the updated `option_chain_summary.json` back to the repository (`git commit -m "Auto-update EOD Option Chain Summary [skip ci]"`).
5. The WordPress widget or static site fetches this updated JSON immediately on client load with zero human touch!

---

## 🚀 WordPress Integration Options

### Zero Manual Upload Workflow (Default)
When the widget is embedded, it automatically queries `option_chain_summary.json?t=<timestamp>` on initial page load. Visitors immediately see:
* Live Spot Price & timestamp banner (`🟢 Automated EOD Synced • NIFTY @ 24,350.50 • EOD Time: ...`)
* Total Call & Put OI with dynamic OTM/ITM percentage distribution bars
* Fresh Buildups (Calls vs Puts, OTM vs ITM) & Unwinding metrics
* PCR, Max Pain, Call Wall (Resistance) and Put Wall (Support)
* Visual Chart.js open interest distributions and searchable strike table

*Note: A collapsible "Manual Upload ▾" panel is available on top if users wish to inspect private custom files.*

### Option 1: WordPress Custom HTML Block (Fastest, No Plugins Required)
1. Open any WordPress Page or Post in the Block Editor (Gutenberg) or Elementor / Divi.
2. Add a **Custom HTML** block (or Elementor **HTML** widget).
3. Open `mits-option-chain-widget.html` from this repository, copy its entire contents, and paste it into the HTML block.
4. Save and Publish! The widget is 100% self-contained, responsive, and auto-fetches `option_chain_summary.json`.

### Option 2: WordPress Plugin Archive (`mits-option-chain-plugin.zip`)
1. Download `mits-option-chain-plugin.zip` from this repository.
2. Go to your WordPress Dashboard $\to$ **Plugins** $\to$ **Add New Plugin** $\to$ **Upload Plugin**.
3. Choose `mits-option-chain-plugin.zip` and click **Install Now**, then **Activate**.
4. Insert the shortcode `[mits_option_chain]` into any page, post, or widget area.
5. Shortcode parameters:
   ```text
   [mits_option_chain]
   [mits_option_chain theme="light" summary_url="option_chain_summary.json"]
   [mits_option_chain summary_url="https://raw.githubusercontent.com/username/repo/main/option_chain_summary.json"]
   ```
6. Manage global defaults under **Settings $\to$ MITS Option Chain Settings**.

---

## 🐍 Python Engine & CLI Tool (`mits_option_chain_analyzer.py`)

A standalone Python analytical engine is provided for terminal use, automated scheduled pipelines, or backend API integration.

### Quick Run with Demo Data
```bash
python mits_option_chain_analyzer.py
```

### Analyze Custom File (CSV, JSON)
```bash
python mits_option_chain_analyzer.py --file path/to/option_chain.csv
python mits_option_chain_analyzer.py --file path/to/option_chain.json
```

### Override Spot Price
```bash
python mits_option_chain_analyzer.py --file sample_data/simple_option_chain.csv --spot 24500.0
```

### Export Output as JSON
```bash
python mits_option_chain_analyzer.py --file sample_data/simple_option_chain.csv --json
```

---

## 🧪 Automated Unit Tests (`test_analyzer.py`)

Run the automated test suite to verify calculation precision, spot price overrides, and edge cases:

```bash
python -m unittest test_analyzer.py
```

Output:
```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.011s

OK
```

---

## 📁 Project Structure

```text
MITS-Option Chain Analysis/
├── .github/
│   └── workflows/
│       └── eod_option_chain.yml         # Daily GitHub Actions scheduled post-market pipeline
├── README.md                            # Complete documentation & WordPress integration guide
├── mits-option-chain-widget.html        # Standalone, single-file drop-in WordPress HTML/JS widget
├── mits-option-chain-plugin.zip         # Ready-to-install WordPress Plugin zip archive
├── mits_option_chain_pipeline.py        # Automated EOD data fetcher, classification & JSON pipeline
├── mits_option_chain_analyzer.py        # Standalone Python parser & calculation engine
├── option_chain_summary.json            # Structured EOD analytics output consumed by widget
├── test_analyzer.py                     # Unit test suite verifying all mathematical metrics
├── wordpress-plugin/                    # Source files for the WordPress Plugin
│   ├── mits-option-chain-widget.php     # Main plugin loader & shortcode registry
│   ├── widget-template.php              # Scoped HTML/CSS/JS frontend template with auto-sync
│   └── readme.txt                       # WordPress Plugin Directory readme format
└── sample_data/                         # Realistic option chain datasets
    ├── nse_option_chain_nifty.csv       # Multi-header official NSE format
    ├── nse_option_chain_nifty.json      # Official NSE API records format
    ├── simple_option_chain.csv          # Standard tabular CSV format
    └── generate_sample_data.py          # Data generation script
```

---

## 🔒 Safety & Isolation Note
This repository is completely standalone and isolated. It has zero references, imports, or dependencies to any other projects.
