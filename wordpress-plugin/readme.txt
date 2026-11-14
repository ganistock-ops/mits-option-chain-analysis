=== MITS Option Chain Intelligence Widget ===
Contributors: MITS Team
Tags: option chain, trading, nse, stock market, options intelligence, nifty, banknifty
Requires at least: 5.6
Tested up to: 6.6
Stable tag: 1.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Standalone Option Chain Intelligence & Breakdown Widget for WordPress. Dynamically calculates ITM/OTM distribution, Call & Put buildups, and market sentiment.

== Description ==

MITS Option Chain Intelligence Widget is a lightweight, zero-backend, client-side intelligence dashboard for WordPress.

Key Features:
* **Automated EOD Pipeline Auto-Sync**: Automatically fetches and renders `option_chain_summary.json` generated post-market by GitHub Actions or scheduled runner — zero manual uploads required!
* **Dynamic Spot Detection & Strike Classification**: Categorizes strikes into In-The-Money (ITM) and Out-of-The-Money (OTM) dynamically based on spot price.
* **Call Side (CE) Breakdown**: Total Call OI, OTM vs ITM OI numbers & percentages, Fresh Additions (buildup), and Unwinding (reductions).
* **Put Side (PE) Breakdown**: Total Put OI, OTM vs ITM OI numbers & percentages, Fresh Additions (buildup), and Unwinding (reductions).
* **Market Intelligence Indicators**: Real-time Put-Call Ratio (PCR), Fresh PCR, Max Pain Strike calculation, Major Resistance (Call Wall), Major Support (Put Wall), and Sentiment Bias.
* **Universal File Fallback**: Optional collapsible manual upload drawer supporting CSV, Excel (.xlsx, .xls), or JSON from NSE India, Sensibull, Zerodha, or pasted text.
* **Visual Charts & Heatmap**: Built-in interactive Chart.js bar charts and color-coded option chain matrix with ITM highlighting.
* **Dark & Light Modes**: Seamless toggle between sleek dark and light themes.

== Installation ==

1. Upload `mits-option-chain-plugin.zip` via WordPress Admin -> Plugins -> Add New -> Upload Plugin.
2. Activate the plugin through the 'Plugins' menu in WordPress.
3. Insert `[mits_option_chain]` into any post, page, or Elementor / Gutenberg Custom HTML block.

== Shortcode Attributes ==

* `[mits_option_chain theme="dark"]` - Loads with Dark Mode (default).
* `[mits_option_chain theme="light"]` - Loads with Light Mode.
* `[mits_option_chain summary_url="/option_chain_summary.json"]` - Custom path/URL to daily pipeline JSON.
* `[mits_option_chain demo="true"]` - Automatically preloads NIFTY 50 benchmark dataset if summary is pending.
