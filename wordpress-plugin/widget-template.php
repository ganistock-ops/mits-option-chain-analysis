<?php
if (!defined('ABSPATH')) {
    exit;
}
?>
<!-- =========================================================================
     MITS OPTION CHAIN INTELLIGENCE WIDGET (AUTOMATED EOD EDITION)
     Compatible with: WordPress Custom HTML block, Elementor, Divi, or Theme files.
     Features auto-sync with background EOD pipeline (option_chain_summary.json).
     ========================================================================= -->

<!-- External High-Speed CDNs with Fallbacks -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

<div id="mits-oc-root" class="<?php echo esc_attr($theme_class); ?>">
  <style>
    /* Scoped CSS to prevent collision with WordPress themes */
    #mits-oc-root {
      --mits-bg-primary: #0f172a;
      --mits-bg-secondary: #1e293b;
      --mits-bg-card: rgba(30, 41, 59, 0.85);
      --mits-bg-input: #0f172a;
      --mits-border: rgba(148, 163, 184, 0.15);
      --mits-border-strong: rgba(148, 163, 184, 0.35);
      --mits-text: #f8fafc;
      --mits-text-muted: #94a3b8;
      --mits-call-color: #ef4444;
      --mits-call-bg: rgba(239, 68, 68, 0.12);
      --mits-call-border: rgba(239, 68, 68, 0.3);
      --mits-put-color: #10b981;
      --mits-put-bg: rgba(16, 185, 129, 0.12);
      --mits-put-border: rgba(16, 185, 129, 0.3);
      --mits-accent: #3b82f6;
      --mits-itm-gold: rgba(234, 179, 8, 0.12);
      --mits-itm-gold-border: rgba(234, 179, 8, 0.3);
      --mits-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
      
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--mits-bg-primary);
      color: var(--mits-text);
      border: 1px solid var(--mits-border);
      border-radius: 16px;
      padding: 24px;
      margin: 20px auto;
      max-width: 1400px;
      box-shadow: var(--mits-shadow);
      box-sizing: border-box;
      line-height: 1.5;
    }

    #mits-oc-root.mits-theme-light {
      --mits-bg-primary: #f8fafc;
      --mits-bg-secondary: #ffffff;
      --mits-bg-card: #ffffff;
      --mits-bg-input: #f1f5f9;
      --mits-border: rgba(100, 116, 139, 0.2);
      --mits-border-strong: rgba(100, 116, 139, 0.4);
      --mits-text: #0f172a;
      --mits-text-muted: #64748b;
      --mits-call-color: #dc2626;
      --mits-call-bg: rgba(220, 38, 38, 0.08);
      --mits-call-border: rgba(220, 38, 38, 0.25);
      --mits-put-color: #059669;
      --mits-put-bg: rgba(5, 150, 105, 0.08);
      --mits-put-border: rgba(5, 150, 105, 0.25);
      --mits-accent: #2563eb;
      --mits-itm-gold: rgba(202, 138, 4, 0.09);
      --mits-itm-gold-border: rgba(202, 138, 4, 0.3);
      --mits-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
    }

    #mits-oc-root *, #mits-oc-root *::before, #mits-oc-root *::after {
      box-sizing: border-box;
    }

    /* Header styling */
    .mits-header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--mits-border);
      margin-bottom: 16px;
    }
    .mits-brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .mits-brand-icon {
      width: 42px;
      height: 42px;
      background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 800;
      font-size: 18px;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    .mits-title {
      font-size: 22px;
      font-weight: 700;
      margin: 0;
      color: var(--mits-text);
      letter-spacing: -0.02em;
    }
    .mits-subtitle {
      font-size: 13px;
      color: var(--mits-text-muted);
      margin: 2px 0 0 0;
    }
    .mits-header-controls {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
    }
    .mits-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid var(--mits-border);
      background: var(--mits-bg-secondary);
      color: var(--mits-text);
      text-decoration: none;
      user-select: none;
    }
    .mits-btn:hover {
      border-color: var(--mits-accent);
      background: var(--mits-bg-card);
      transform: translateY(-1px);
    }
    .mits-btn-primary {
      background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
      color: white;
      border: none;
    }
    .mits-btn-primary:hover {
      background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    }
    .mits-btn-sm {
      padding: 5px 10px;
      font-size: 12px;
      border-radius: 6px;
    }

    /* Spot Price Badge */
    .mits-spot-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(59, 130, 246, 0.12);
      border: 1px solid rgba(59, 130, 246, 0.3);
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      color: var(--mits-accent);
    }
    .mits-spot-value {
      font-size: 16px;
      font-weight: 700;
      color: var(--mits-text);
    }
    .mits-spot-edit-btn {
      background: none;
      border: none;
      color: var(--mits-text-muted);
      cursor: pointer;
      padding: 2px 4px;
      border-radius: 4px;
      font-size: 12px;
      transition: color 0.15s;
    }
    .mits-spot-edit-btn:hover {
      color: var(--mits-accent);
    }

    /* Automated EOD Pipeline Banner */
    .mits-sync-banner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      background: rgba(16, 185, 129, 0.08);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 10px 16px;
      border-radius: 10px;
      margin-bottom: 20px;
      font-size: 13px;
    }
    .mits-sync-status {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      color: #34d399;
    }
    .mits-status-dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
      display: inline-block;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .mits-sync-controls {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    /* Upload / Input Card (Collapsible for manual overrides) */
    .mits-upload-card {
      background: var(--mits-bg-secondary);
      border: 2px dashed var(--mits-border-strong);
      border-radius: 14px;
      padding: 24px 20px;
      text-align: center;
      transition: all 0.2s ease;
      margin-bottom: 24px;
      position: relative;
      cursor: pointer;
      display: none; /* Hidden by default when automated EOD is active */
    }
    .mits-upload-card:hover {
      border-color: var(--mits-accent);
      background: rgba(59, 130, 246, 0.03);
    }
    .mits-upload-card.dragover {
      border-color: #3b82f6 !important;
      background: rgba(59, 130, 246, 0.1) !important;
      transform: scale(1.005);
    }
    .mits-upload-icon {
      width: 44px;
      height: 44px;
      margin: 0 auto 10px auto;
      color: var(--mits-accent);
      pointer-events: none;
    }
    .mits-upload-text {
      font-size: 15px;
      font-weight: 700;
      margin-bottom: 4px;
      pointer-events: none;
    }
    .mits-upload-hint {
      font-size: 12px;
      color: var(--mits-text-muted);
      margin-bottom: 14px;
      pointer-events: none;
    }
    .mits-upload-actions {
      display: flex;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;
      position: relative;
      z-index: 2;
    }

    .mits-file-input-hidden {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      border: 0;
      opacity: 0;
      pointer-events: none;
    }

    .mits-upload-status {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      margin-top: 14px;
      max-width: 90%;
      word-break: break-word;
      animation: fadeIn 0.3s ease;
    }
    .mits-upload-status.success {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #34d399;
    }
    .mits-upload-status.error {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid rgba(239, 68, 68, 0.4);
      color: #f87171;
    }
    .mits-upload-status.loading {
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.4);
      color: #60a5fa;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .mits-paste-box {
      display: none;
      margin-top: 16px;
      text-align: left;
      cursor: default;
    }
    .mits-textarea {
      width: 100%;
      height: 120px;
      background: var(--mits-bg-input);
      border: 1px solid var(--mits-border);
      border-radius: 8px;
      padding: 10px;
      color: var(--mits-text);
      font-family: monospace;
      font-size: 12px;
      resize: vertical;
      box-sizing: border-box;
    }
    .mits-textarea:focus {
      outline: none;
      border-color: var(--mits-accent);
    }

    /* Intelligence Quick KPI Cards */
    .mits-intel-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .mits-intel-card {
      background: var(--mits-bg-card);
      border: 1px solid var(--mits-border);
      border-radius: 12px;
      padding: 16px;
      position: relative;
      overflow: hidden;
      backdrop-filter: blur(8px);
    }
    .mits-intel-card::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--mits-accent);
      opacity: 0.8;
    }
    .mits-intel-card.pcr-card::before { background: #8b5cf6; }
    .mits-intel-card.res-card::before { background: var(--mits-call-color); }
    .mits-intel-card.sup-card::before { background: var(--mits-put-color); }
    .mits-intel-card.sentiment-card::before { background: #f59e0b; }

    .mits-card-label {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--mits-text-muted);
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .mits-card-val {
      font-size: 24px;
      font-weight: 700;
      color: var(--mits-text);
      line-height: 1.2;
    }
    .mits-card-sub {
      font-size: 12px;
      color: var(--mits-text-muted);
      margin-top: 6px;
    }
    .mits-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
    }

    /* Core Breakdown: Side-by-Side CE vs PE Columns */
    .mits-breakdown-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }
    @media (max-width: 900px) {
      .mits-breakdown-container {
        grid-template-columns: 1fr;
      }
    }

    .mits-panel {
      background: var(--mits-bg-card);
      border: 1px solid var(--mits-border);
      border-radius: 14px;
      padding: 20px;
      position: relative;
    }
    .mits-panel-ce {
      border-top: 4px solid var(--mits-call-color);
    }
    .mits-panel-pe {
      border-top: 4px solid var(--mits-put-color);
    }
    .mits-panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--mits-border);
    }
    .mits-panel-title {
      font-size: 18px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .mits-panel-title.ce-title { color: var(--mits-call-color); }
    .mits-panel-title.pe-title { color: var(--mits-put-color); }

    .mits-total-oi-display {
      text-align: right;
    }
    .mits-total-oi-label {
      font-size: 11px;
      color: var(--mits-text-muted);
      text-transform: uppercase;
    }
    .mits-total-oi-num {
      font-size: 20px;
      font-weight: 800;
    }

    .mits-ratio-wrap {
      margin-bottom: 20px;
    }
    .mits-ratio-header {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 6px;
    }
    .mits-ratio-bar {
      height: 10px;
      background: var(--mits-bg-input);
      border-radius: 9999px;
      overflow: hidden;
      display: flex;
    }
    .mits-ratio-otm {
      background: #3b82f6;
      transition: width 0.4s ease;
    }
    .mits-ratio-itm {
      background: #f59e0b;
      transition: width 0.4s ease;
    }

    .mits-subgrid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 16px;
    }
    .mits-stat-card {
      background: var(--mits-bg-secondary);
      border: 1px solid var(--mits-border);
      border-radius: 10px;
      padding: 12px 14px;
    }
    .mits-stat-title {
      font-size: 12px;
      font-weight: 600;
      color: var(--mits-text-muted);
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
    }
    .mits-stat-num {
      font-size: 18px;
      font-weight: 700;
      color: var(--mits-text);
    }
    .mits-stat-pct {
      font-size: 13px;
      font-weight: 600;
      color: var(--mits-accent);
      margin-left: 6px;
    }

    .mits-flow-section {
      background: rgba(15, 23, 42, 0.4);
      border: 1px solid var(--mits-border);
      border-radius: 10px;
      padding: 14px;
      margin-top: 12px;
    }
    .mits-flow-title {
      font-size: 13px;
      font-weight: 700;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .mits-flow-title.fresh {
      color: #10b981;
    }
    .mits-flow-title.unwind {
      color: #f87171;
    }
    .mits-flow-row {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      padding: 4px 0;
      border-bottom: 1px dashed var(--mits-border);
    }
    .mits-flow-row:last-child {
      border-bottom: none;
    }

    .mits-charts-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }
    @media (max-width: 900px) {
      .mits-charts-row {
        grid-template-columns: 1fr;
      }
    }
    .mits-chart-card {
      background: var(--mits-bg-card);
      border: 1px solid var(--mits-border);
      border-radius: 14px;
      padding: 16px;
    }
    .mits-chart-title {
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      color: var(--mits-text);
    }

    .mits-table-section {
      background: var(--mits-bg-card);
      border: 1px solid var(--mits-border);
      border-radius: 14px;
      padding: 20px;
      overflow: hidden;
    }
    .mits-table-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 14px;
    }
    .mits-table-title {
      font-size: 16px;
      font-weight: 700;
      color: var(--mits-text);
    }
    .mits-table-filters {
      display: flex;
      gap: 8px;
    }
    .mits-filter-btn {
      padding: 4px 10px;
      font-size: 12px;
      border-radius: 6px;
      border: 1px solid var(--mits-border);
      background: var(--mits-bg-secondary);
      color: var(--mits-text-muted);
      cursor: pointer;
    }
    .mits-filter-btn.active {
      background: var(--mits-accent);
      color: white;
      border-color: var(--mits-accent);
    }

    .mits-table-wrapper {
      max-height: 480px;
      overflow-y: auto;
      border: 1px solid var(--mits-border);
      border-radius: 8px;
    }
    .mits-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      text-align: right;
    }
    .mits-table th {
      position: sticky;
      top: 0;
      background: var(--mits-bg-secondary);
      padding: 8px 10px;
      font-weight: 700;
      border-bottom: 2px solid var(--mits-border);
      z-index: 2;
    }
    .mits-table td {
      padding: 7px 10px;
      border-bottom: 1px solid var(--mits-border);
    }
    .mits-table tr:hover {
      background: rgba(255, 255, 255, 0.03);
    }
    .mits-table tr.strike-atm {
      background: rgba(59, 130, 246, 0.15) !important;
      font-weight: bold;
    }
    .mits-table tr.strike-atm td {
      border-top: 1px solid var(--mits-accent);
      border-bottom: 1px solid var(--mits-accent);
    }
    .mits-table td.strike-col {
      text-align: center;
      font-weight: 800;
      background: var(--mits-bg-secondary);
      position: relative;
    }
    .mits-table td.itm-ce {
      background: var(--mits-itm-gold);
    }
    .mits-table td.itm-pe {
      background: var(--mits-itm-gold);
    }
    .val-pos { color: #10b981; }
    .val-neg { color: #ef4444; }

    .mits-cell-bar {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: flex-end;
    }
    .mits-bar-bg {
      position: absolute;
      top: 2px;
      bottom: 2px;
      right: 0;
      border-radius: 3px;
      opacity: 0.25;
      pointer-events: none;
    }
    .mits-bar-bg.ce { background: var(--mits-call-color); }
    .mits-bar-bg.pe { background: var(--mits-put-color); left: 0; right: auto; }

    .mits-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 20px;
      padding-top: 14px;
      border-top: 1px solid var(--mits-border);
      font-size: 12px;
      color: var(--mits-text-muted);
      flex-wrap: wrap;
      gap: 10px;
    }
  </style>

  <!-- WIDGET HEADER -->
  <div class="mits-header">
    <div class="mits-brand">
      <div class="mits-brand-icon">M</div>
      <div>
        <h2 class="mits-title">MITS Option Chain Intelligence</h2>
        <p class="mits-subtitle">Automated Post-Market Derivatives Breakdown & Flow Intelligence</p>
      </div>
    </div>

    <div class="mits-header-controls">
      <!-- Spot Price Badge with Quick Edit -->
      <div class="mits-spot-badge">
        <span>Spot:</span>
        <span class="mits-spot-value" id="mits-spot-display">24,350.50</span>
        <button type="button" class="mits-spot-edit-btn" id="mits-edit-spot-btn" title="Override Spot Price">✎</button>
      </div>

      <button type="button" class="mits-btn" id="mits-toggle-theme-btn" title="Toggle Theme">
        <span id="mits-theme-icon">☀️ Light</span>
      </button>
    </div>
  </div>

  <!-- AUTOMATED EOD PIPELINE SYNC BANNER -->
  <div class="mits-sync-banner" id="mits-sync-banner">
    <div class="mits-sync-status">
      <span class="mits-status-dot"></span>
      <span id="mits-sync-text">Automated EOD Pipeline: Syncing latest data...</span>
    </div>
    <div class="mits-sync-controls">
      <button type="button" class="mits-btn mits-btn-sm" id="mits-refresh-eod-btn" title="Fetch latest option_chain_summary.json">
        🔄 Refresh EOD
      </button>
      <button type="button" class="mits-btn mits-btn-sm" id="mits-toggle-upload-btn" title="Open Manual Upload Panel">
        Manual Upload ▾
      </button>
    </div>
  </div>

  <!-- UPLOAD / INPUT CARD (Collapsible) -->
  <div class="mits-upload-card" id="mits-drop-zone">
    <div class="mits-upload-content">
      <svg class="mits-upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
      </svg>
      <div class="mits-upload-text">Upload Custom Option Chain File (CSV / Excel / JSON)</div>
      <div class="mits-upload-hint">Drag & drop your document here, or click to browse</div>
      <div id="mits-upload-status" class="mits-upload-status" style="display: none;"></div>
    </div>

    <div class="mits-upload-actions">
      <button type="button" class="mits-btn mits-btn-primary" id="mits-browse-btn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
        Browse File
      </button>

      <input type="file" id="mits-file-input" class="mits-file-input-hidden" accept=".csv,.xlsx,.xls,.json,.txt,application/json,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel">

      <button type="button" class="mits-btn" id="mits-toggle-paste-btn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
        Paste CSV / JSON Text
      </button>
    </div>

    <div class="mits-paste-box" id="mits-paste-container">
      <textarea class="mits-textarea" id="mits-paste-input" placeholder="Paste Option Chain CSV data or NSE JSON payload here..."></textarea>
      <div style="margin-top: 8px; text-align: right;">
        <button type="button" class="mits-btn mits-btn-primary" id="mits-parse-paste-btn">Analyze Pasted Data</button>
      </div>
    </div>
  </div>

  <!-- SUMMARY INTELLIGENCE KPI CARDS -->
  <div class="mits-intel-grid">
    <div class="mits-intel-card pcr-card">
      <div class="mits-card-label">
        <span>Put-Call Ratio (PCR)</span>
        <span class="mits-badge" id="mits-pcr-status" style="background: rgba(139, 92, 246, 0.2); color: #a78bfa;">Neutral</span>
      </div>
      <div class="mits-card-val" id="mits-pcr-val">0.96</div>
      <div class="mits-card-sub" id="mits-pcr-fresh-sub">PCR Fresh (Buildup): 0.67</div>
    </div>

    <div class="mits-intel-card sentiment-card">
      <div class="mits-card-label">
        <span>Market Sentiment</span>
        <span class="mits-badge" id="mits-sentiment-badge" style="background: rgba(245, 158, 11, 0.2); color: #fbbf24;">Rangebound</span>
      </div>
      <div class="mits-card-val" id="mits-sentiment-val" style="font-size: 18px; color: #fbbf24;">Neutral Bias</div>
      <div class="mits-card-sub" id="mits-sentiment-desc">Writers active on both sides</div>
    </div>

    <div class="mits-intel-card res-card">
      <div class="mits-card-label">
        <span>Key Resistance</span>
        <span class="mits-badge" style="background: var(--mits-call-bg); color: var(--mits-call-color);">Call Wall</span>
      </div>
      <div class="mits-card-val" id="mits-res1-val" style="color: var(--mits-call-color);">24,500</div>
      <div class="mits-card-sub" id="mits-res2-sub">Next Resistance: 24,600</div>
    </div>

    <div class="mits-intel-card sup-card">
      <div class="mits-card-label">
        <span>Key Support</span>
        <span class="mits-badge" style="background: var(--mits-put-bg); color: var(--mits-put-color);">Put Wall</span>
      </div>
      <div class="mits-card-val" id="mits-sup1-val" style="color: var(--mits-put-color);">24,000</div>
      <div class="mits-card-sub" id="mits-sup2-sub">Next Support: 24,300</div>
    </div>

    <div class="mits-intel-card">
      <div class="mits-card-label">
        <span>Max Pain Strike</span>
        <span class="mits-badge" style="background: rgba(59, 130, 246, 0.2); color: #60a5fa;">Expiry Target</span>
      </div>
      <div class="mits-card-val" id="mits-maxpain-val">24,400</div>
      <div class="mits-card-sub" id="mits-maxpain-sub">Lowest payout for writers</div>
    </div>
  </div>

  <!-- CORE BREAKDOWN: CALL SIDE vs PUT SIDE -->
  <div class="mits-breakdown-container">
    
    <!-- CALL SIDE (CE) -->
    <div class="mits-panel mits-panel-ce">
      <div class="mits-panel-header">
        <div class="mits-panel-title ce-title">
          <span>●</span> CALL SIDE (CE) BREAKDOWN
        </div>
        <div class="mits-total-oi-display">
          <div class="mits-total-oi-label">Total Call OI</div>
          <div class="mits-total-oi-num" id="mits-ce-total-oi">1,088,700</div>
        </div>
      </div>

      <div class="mits-ratio-wrap">
        <div class="mits-ratio-header">
          <span style="color: #60a5fa;">OTM: <span id="mits-ce-otm-pct-label">80.8%</span></span>
          <span style="color: #fbbf24;">ITM: <span id="mits-ce-itm-pct-label">19.2%</span></span>
        </div>
        <div class="mits-ratio-bar">
          <div class="mits-ratio-otm" id="mits-ce-ratio-otm" style="width: 80.8%;"></div>
          <div class="mits-ratio-itm" id="mits-ce-ratio-itm" style="width: 19.2%;"></div>
        </div>
      </div>

      <div class="mits-subgrid">
        <div class="mits-stat-card">
          <div class="mits-stat-title">
            <span>OTM Calls</span>
            <span class="mits-badge" style="background: rgba(59, 130, 246, 0.15); color: #60a5fa;">≥ Spot</span>
          </div>
          <div class="mits-stat-num">
            <span id="mits-ce-otm-oi">880,000</span>
            <span class="mits-stat-pct" id="mits-ce-otm-pct">80.8%</span>
          </div>
          <div class="mits-card-sub">Share of Total Call OI</div>
        </div>

        <div class="mits-stat-card">
          <div class="mits-stat-title">
            <span>ITM Calls</span>
            <span class="mits-badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24;">< Spot</span>
          </div>
          <div class="mits-stat-num">
            <span id="mits-ce-itm-oi">208,700</span>
            <span class="mits-stat-pct" id="mits-ce-itm-pct">19.2%</span>
          </div>
          <div class="mits-card-sub">Share of Total Call OI</div>
        </div>
      </div>

      <div class="mits-flow-section">
        <div class="mits-flow-title fresh">
          <span>Fresh Additions (Buildup)</span>
          <span id="mits-ce-fresh-total">+154,200</span>
        </div>
        <div class="mits-flow-row">
          <span>OTM Fresh Additions:</span>
          <strong><span id="mits-ce-fresh-otm">+144,500</span> (<span id="mits-ce-fresh-otm-pct">93.7%</span>)</strong>
        </div>
        <div class="mits-flow-row">
          <span>ITM Fresh Additions:</span>
          <strong><span id="mits-ce-fresh-itm">+9,700</span> (<span id="mits-ce-fresh-itm-pct">6.3%</span>)</strong>
        </div>
      </div>

      <div class="mits-flow-section">
        <div class="mits-flow-title unwind">
          <span>Unwinding (OI Reduction)</span>
          <span id="mits-ce-unwind-total">-9,500</span>
        </div>
        <div class="mits-flow-row">
          <span>OTM Unwinding:</span>
          <strong><span id="mits-ce-unwind-otm">0</span> (<span id="mits-ce-unwind-otm-pct">0.0%</span>)</strong>
        </div>
        <div class="mits-flow-row">
          <span>ITM Unwinding:</span>
          <strong><span id="mits-ce-unwind-itm">-9,500</span> (<span id="mits-ce-unwind-itm-pct">100.0%</span>)</strong>
        </div>
      </div>
    </div>

    <!-- PUT SIDE (PE) -->
    <div class="mits-panel mits-panel-pe">
      <div class="mits-panel-header">
        <div class="mits-panel-title pe-title">
          <span>●</span> PUT SIDE (PE) BREAKDOWN
        </div>
        <div class="mits-total-oi-display">
          <div class="mits-total-oi-label">Total Put OI</div>
          <div class="mits-total-oi-num" id="mits-pe-total-oi">1,050,300</div>
        </div>
      </div>

      <div class="mits-ratio-wrap">
        <div class="mits-ratio-header">
          <span style="color: #60a5fa;">OTM: <span id="mits-pe-otm-pct-label">75.2%</span></span>
          <span style="color: #fbbf24;">ITM: <span id="mits-pe-itm-pct-label">24.8%</span></span>
        </div>
        <div class="mits-ratio-bar">
          <div class="mits-ratio-otm" id="mits-pe-ratio-otm" style="width: 75.2%;"></div>
          <div class="mits-ratio-itm" id="mits-pe-ratio-itm" style="width: 24.8%;"></div>
        </div>
      </div>

      <div class="mits-subgrid">
        <div class="mits-stat-card">
          <div class="mits-stat-title">
            <span>OTM Puts</span>
            <span class="mits-badge" style="background: rgba(59, 130, 246, 0.15); color: #60a5fa;">≤ Spot</span>
          </div>
          <div class="mits-stat-num">
            <span id="mits-pe-otm-oi">789,400</span>
            <span class="mits-stat-pct" id="mits-pe-otm-pct">75.2%</span>
          </div>
          <div class="mits-card-sub">Share of Total Put OI</div>
        </div>

        <div class="mits-stat-card">
          <div class="mits-stat-title">
            <span>ITM Puts</span>
            <span class="mits-badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24;">> Spot</span>
          </div>
          <div class="mits-stat-num">
            <span id="mits-pe-itm-oi">260,900</span>
            <span class="mits-stat-pct" id="mits-pe-itm-pct">24.8%</span>
          </div>
          <div class="mits-card-sub">Share of Total Put OI</div>
        </div>
      </div>

      <div class="mits-flow-section">
        <div class="mits-flow-title fresh">
          <span>Fresh Additions (Buildup)</span>
          <span id="mits-pe-fresh-total">+102,600</span>
        </div>
        <div class="mits-flow-row">
          <span>OTM Fresh Additions:</span>
          <strong><span id="mits-pe-fresh-otm">+102,600</span> (<span id="mits-pe-fresh-otm-pct">100.0%</span>)</strong>
        </div>
        <div class="mits-flow-row">
          <span>ITM Fresh Additions:</span>
          <strong><span id="mits-pe-fresh-itm">0</span> (<span id="mits-pe-fresh-itm-pct">0.0%</span>)</strong>
        </div>
      </div>

      <div class="mits-flow-section">
        <div class="mits-flow-title unwind">
          <span>Unwinding (OI Reduction)</span>
          <span id="mits-pe-unwind-total">-13,400</span>
        </div>
        <div class="mits-flow-row">
          <span>OTM Unwinding:</span>
          <strong><span id="mits-pe-unwind-otm">0</span> (<span id="mits-pe-unwind-otm-pct">0.0%</span>)</strong>
        </div>
        <div class="mits-flow-row">
          <span>ITM Unwinding:</span>
          <strong><span id="mits-pe-unwind-itm">-13,400</span> (<span id="mits-pe-unwind-itm-pct">100.0%</span>)</strong>
        </div>
      </div>
    </div>
  </div>

  <!-- CHARTS -->
  <div class="mits-charts-row">
    <div class="mits-chart-card">
      <div class="mits-chart-title">
        <span>Open Interest Distribution (CE vs PE)</span>
        <span style="font-size: 11px; color: var(--mits-text-muted);">Red: Calls | Green: Puts</span>
      </div>
      <div style="height: 240px; position: relative;">
        <canvas id="mits-oi-chart"></canvas>
      </div>
    </div>

    <div class="mits-chart-card">
      <div class="mits-chart-title">
        <span>Net Change in OI (Fresh Additions vs Unwinding)</span>
        <span style="font-size: 11px; color: var(--mits-text-muted);">Positive: Buildup | Negative: Exit</span>
      </div>
      <div style="height: 240px; position: relative;">
        <canvas id="mits-chg-chart"></canvas>
      </div>
    </div>
  </div>

  <!-- TABLE -->
  <div class="mits-table-section">
    <div class="mits-table-toolbar">
      <div>
        <span class="mits-table-title">Full Option Chain Matrix</span>
        <span style="font-size: 12px; color: var(--mits-text-muted); margin-left: 8px;" id="mits-strike-count-label">(12 Strikes Loaded)</span>
      </div>
      <div class="mits-table-filters">
        <button type="button" class="mits-filter-btn active" data-filter="all">All Strikes</button>
        <button type="button" class="mits-filter-btn" data-filter="near">Near ATM (±5)</button>
        <button type="button" class="mits-btn" id="mits-copy-summary-btn" style="padding: 4px 10px; font-size: 12px;">
          📋 Copy Summary
        </button>
      </div>
    </div>

    <div class="mits-table-wrapper">
      <table class="mits-table">
        <thead>
          <tr>
            <th colspan="4" style="text-align: center; color: var(--mits-call-color); border-right: 1px solid var(--mits-border);">CALLS (CE)</th>
            <th rowspan="2" style="text-align: center; width: 120px;">STRIKE</th>
            <th colspan="4" style="text-align: center; color: var(--mits-put-color); border-left: 1px solid var(--mits-border);">PUTS (PE)</th>
          </tr>
          <tr>
            <th>Type</th>
            <th>LTP</th>
            <th>Chg OI</th>
            <th style="border-right: 1px solid var(--mits-border);">OI</th>
            <th style="border-left: 1px solid var(--mits-border);">OI</th>
            <th>Chg OI</th>
            <th>LTP</th>
            <th>Type</th>
          </tr>
        </thead>
        <tbody id="mits-table-body">
        </tbody>
      </table>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="mits-footer">
    <div>
      <span>Market Intelligence Trading System (MITS) &bull; Automated EOD Pipeline</span>
    </div>
    <div>
      <span>Auto-syncs with <code>option_chain_summary.json</code> post-market &bull; Zero manual uploads</span>
    </div>
  </div>
</div>

<script>
(function() {
  const autoDemo = <?php echo ($auto_demo === 'true') ? 'true' : 'false'; ?>;
  const initialTheme = '<?php echo esc_js($args["theme"]); ?>';
  const summaryJsonUrl = <?php echo json_encode($summary_url); ?>;

  const state = {
    spotPrice: 24350.50,
    theme: initialTheme,
    filter: 'all',
    dataRows: [],
    oiChart: null,
    chgChart: null
  };

  const DEMO_DATA = [
    { strike: 23800, ce_oi: 15200, ce_chg: -1800, ce_ltp: 590.20, pe_oi: 85400, pe_chg: 8500, pe_ltp: 18.40 },
    { strike: 23900, ce_oi: 18400, ce_chg: -2400, ce_ltp: 495.50, pe_oi: 92300, pe_chg: 12400, pe_ltp: 24.10 },
    { strike: 24000, ce_oi: 35600, ce_chg: -4100, ce_ltp: 405.00, pe_oi: 185600, pe_chg: 24800, pe_ltp: 32.75 },
    { strike: 24100, ce_oi: 28900, ce_chg: -1200, ce_ltp: 320.15, pe_oi: 112000, pe_chg: 15600, pe_ltp: 46.20 },
    { strike: 24200, ce_oi: 42100, ce_chg: 1500,  ce_ltp: 242.80, pe_oi: 145200, pe_chg: 18900, pe_ltp: 67.50 },
    { strike: 24300, ce_oi: 68500, ce_chg: 8200,  ce_ltp: 172.40, pe_oi: 168900, pe_chg: 22400, pe_ltp: 98.30 },
    { strike: 24400, ce_oi: 145000, ce_chg: 28500, ce_ltp: 112.50, pe_oi: 98400,  pe_chg: -3200, pe_ltp: 142.10 },
    { strike: 24500, ce_oi: 210400, ce_chg: 42100, ce_ltp: 68.30,  pe_oi: 74500,  pe_chg: -5400, pe_ltp: 198.50 },
    { strike: 24600, ce_oi: 182300, ce_chg: 31200, ce_ltp: 39.20,  pe_oi: 41200,  pe_chg: -2800, pe_ltp: 268.00 },
    { strike: 24700, ce_oi: 134200, ce_chg: 19800, ce_ltp: 21.60,  pe_oi: 23400,  pe_chg: -1200, pe_ltp: 348.20 },
    { strike: 24800, ce_oi: 115600, ce_chg: 14500, ce_ltp: 11.40,  pe_oi: 14500,  pe_chg: -600,  pe_ltp: 435.00 },
    { strike: 24900, ce_oi: 92500,  ce_chg: 8400,  ce_ltp: 6.10,   pe_oi: 8900,   pe_chg: -200,  pe_ltp: 529.00 }
  ];

  function formatNum(num) {
    if (num === undefined || num === null || isNaN(num)) return "0";
    return Math.round(num).toLocaleString('en-IN');
  }

  function formatPct(num) {
    if (num === undefined || num === null || isNaN(num)) return "0.0%";
    return Number(num).toFixed(1) + "%";
  }

  function formatSigned(num) {
    if (num === undefined || num === null || isNaN(num)) return "0";
    const prefix = num > 0 ? "+" : "";
    return prefix + Math.round(num).toLocaleString('en-IN');
  }

  function cleanNum(val) {
    if (val === undefined || val === null) return 0;
    if (typeof val === 'number') return isNaN(val) ? 0 : val;
    const cleaned = String(val).replace(/,/g, '').replace(/₹/g, '').replace(/\$/g, '').replace(/ /g, '').trim();
    if (cleaned === '' || cleaned === '-' || cleaned === '--' || cleaned === 'null' || cleaned === 'NaN') return 0;
    const num = parseFloat(cleaned);
    return isNaN(num) ? 0 : num;
  }

  function norm(s) {
    return String(s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  function extractNum(obj, keys) {
    const normalizedKeys = keys.map(k => norm(k));
    for (const objKey in obj) {
      const kNorm = norm(objKey);
      if (normalizedKeys.includes(kNorm)) {
        return cleanNum(obj[objKey]);
      }
    }
    return 0;
  }

  function parseCSV(text) {
    const lines = text.split(/\r\n|\n|\r/);
    const result = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      const row = [];
      let inQuote = false;
      let entry = '';
      for (let c = 0; c < line.length; c++) {
        const char = line[c];
        if (char === '"') {
          inQuote = !inQuote;
        } else if ((char === ',' || char === '\t') && !inQuote) {
          row.push(entry.trim().replace(/^"|"$/g, ''));
          entry = '';
        } else {
          entry += char;
        }
      }
      row.push(entry.trim().replace(/^"|"$/g, ''));
      result.push(row);
    }
    return result;
  }

  function showStatus(message, type = 'loading') {
    const statusEl = document.getElementById('mits-upload-status');
    if (!statusEl) return;
    statusEl.style.display = 'inline-flex';
    statusEl.className = 'mits-upload-status ' + type;
    statusEl.innerHTML = message;
  }

  function showSyncBanner(message, isSuccess = true) {
    const bannerText = document.getElementById('mits-sync-text');
    if (bannerText) bannerText.innerHTML = message;
  }

  function calculateIntelligence(rows, spot) {
    let ceTotalOI = 0, peTotalOI = 0;
    let ceOtmOI = 0, ceItmOI = 0;
    let peOtmOI = 0, peItmOI = 0;

    let ceFreshOtm = 0, ceFreshItm = 0;
    let ceUnwindOtm = 0, ceUnwindItm = 0;

    let peFreshOtm = 0, peFreshItm = 0;
    let peUnwindOtm = 0, peUnwindItm = 0;

    const enrichedStrikes = rows.map(r => {
      const strike = Number(r.strike);
      const ce_oi = Number(r.ce_oi || 0);
      const ce_chg = Number(r.ce_chg || 0);
      const ce_ltp = Number(r.ce_ltp || 0);
      const pe_oi = Number(r.pe_oi || 0);
      const pe_chg = Number(r.pe_chg || 0);
      const pe_ltp = Number(r.pe_ltp || 0);

      const isCeItm = strike < spot;
      const isPeItm = strike > spot;

      ceTotalOI += ce_oi;
      peTotalOI += pe_oi;

      if (isCeItm) {
        ceItmOI += ce_oi;
        if (ce_chg > 0) ceFreshItm += ce_chg;
        else if (ce_chg < 0) ceUnwindItm += Math.abs(ce_chg);
      } else {
        ceOtmOI += ce_oi;
        if (ce_chg > 0) ceFreshOtm += ce_chg;
        else if (ce_chg < 0) ceUnwindOtm += Math.abs(ce_chg);
      }

      if (isPeItm) {
        peItmOI += pe_oi;
        if (pe_chg > 0) peFreshItm += pe_chg;
        else if (pe_chg < 0) peUnwindItm += Math.abs(pe_chg);
      } else {
        peOtmOI += pe_oi;
        if (pe_chg > 0) peFreshOtm += pe_chg;
        else if (pe_chg < 0) peUnwindOtm += Math.abs(pe_chg);
      }

      return {
        strike,
        ce_oi, ce_chg, ce_ltp,
        pe_oi, pe_chg, pe_ltp,
        isCeItm, isPeItm,
        diff: Math.abs(strike - spot)
      };
    }).sort((a, b) => a.strike - b.strike);

    const ceFreshTotal = ceFreshOtm + ceFreshItm;
    const ceUnwindTotal = ceUnwindOtm + ceUnwindItm;
    const peFreshTotal = peFreshOtm + peFreshItm;
    const peUnwindTotal = peUnwindOtm + peUnwindItm;

    const ceOtmPct = ceTotalOI > 0 ? (ceOtmOI / ceTotalOI * 100) : 0;
    const ceItmPct = ceTotalOI > 0 ? (ceItmOI / ceTotalOI * 100) : 0;
    const peOtmPct = peTotalOI > 0 ? (peOtmOI / peTotalOI * 100) : 0;
    const peItmPct = peTotalOI > 0 ? (peItmOI / peTotalOI * 100) : 0;

    const ceFreshOtmPct = ceFreshTotal > 0 ? (ceFreshOtm / ceFreshTotal * 100) : 0;
    const ceFreshItmPct = ceFreshTotal > 0 ? (ceFreshItm / ceFreshTotal * 100) : 0;
    const ceUnwindOtmPct = ceUnwindTotal > 0 ? (ceUnwindOtm / ceUnwindTotal * 100) : 0;
    const ceUnwindItmPct = ceUnwindTotal > 0 ? (ceUnwindItm / ceUnwindTotal * 100) : 0;

    const peFreshOtmPct = peFreshTotal > 0 ? (peFreshOtm / peFreshTotal * 100) : 0;
    const peFreshItmPct = peFreshTotal > 0 ? (peFreshItm / peFreshTotal * 100) : 0;
    const peUnwindOtmPct = peUnwindTotal > 0 ? (peUnwindOtm / peUnwindTotal * 100) : 0;
    const peUnwindItmPct = peUnwindTotal > 0 ? (peUnwindItm / peUnwindTotal * 100) : 0;

    const pcr = ceTotalOI > 0 ? (peTotalOI / ceTotalOI) : 0;
    const pcrFresh = ceFreshTotal > 0 ? (peFreshTotal / ceFreshTotal) : 0;

    let minLoss = Infinity;
    let maxPainStrike = enrichedStrikes.length > 0 ? enrichedStrikes[0].strike : spot;
    enrichedStrikes.forEach(target => {
      let loss = 0;
      enrichedStrikes.forEach(s => {
        if (target.strike > s.strike) loss += (target.strike - s.strike) * s.ce_oi;
        if (target.strike < s.strike) loss += (s.strike - target.strike) * s.pe_oi;
      });
      if (loss < minLoss) {
        minLoss = loss;
        maxPainStrike = target.strike;
      }
    });

    const topCe = [...enrichedStrikes].sort((a, b) => b.ce_oi - a.ce_oi);
    const topPe = [...enrichedStrikes].sort((a, b) => b.pe_oi - a.pe_oi);

    let sentiment = "Neutral / Rangebound";
    let sentimentColor = "#f59e0b";
    let sentimentDesc = "Call and Put writers in equilibrium";
    if (pcr >= 1.25) {
      sentiment = "Strongly Bullish";
      sentimentColor = "#10b981";
      sentimentDesc = "Aggressive Put writing; strong base";
    } else if (pcr >= 1.05) {
      sentiment = "Moderately Bullish";
      sentimentColor = "#34d399";
      sentimentDesc = "Put writers dominating Call writers";
    } else if (pcr <= 0.70) {
      sentiment = "Strongly Bearish";
      sentimentColor = "#ef4444";
      sentimentDesc = "Massive Call writing overhead";
    } else if (pcr <= 0.85) {
      sentiment = "Moderately Bearish";
      sentimentColor = "#f87171";
      sentimentDesc = "Call writing capping upward moves";
    }

    return {
      spot,
      ce: {
        totalOI: ceTotalOI,
        otmOI: ceOtmOI, otmPct: ceOtmPct,
        itmOI: ceItmOI, itmPct: ceItmPct,
        freshTotal: ceFreshTotal,
        freshOtm: ceFreshOtm, freshOtmPct: ceFreshOtmPct,
        freshItm: ceFreshItm, freshItmPct: ceFreshItmPct,
        unwindTotal: ceUnwindTotal,
        unwindOtm: ceUnwindOtm, unwindOtmPct: ceUnwindOtmPct,
        unwindItm: ceUnwindItm, unwindItmPct: ceUnwindItmPct,
      },
      pe: {
        totalOI: peTotalOI,
        otmOI: peOtmOI, otmPct: peOtmPct,
        itmOI: peItmOI, itmPct: peItmPct,
        freshTotal: peFreshTotal,
        freshOtm: peFreshOtm, freshOtmPct: peFreshOtmPct,
        freshItm: peFreshItm, freshItmPct: peFreshItmPct,
        unwindTotal: peUnwindTotal,
        unwindOtm: peUnwindOtm, unwindOtmPct: peUnwindOtmPct,
        unwindItm: peUnwindItm, unwindItmPct: peUnwindItmPct,
      },
      intelligence: {
        pcr: pcr.toFixed(2),
        pcrFresh: pcrFresh.toFixed(2),
        maxPain: maxPainStrike,
        r1: topCe[0] ? topCe[0].strike : null,
        r2: topCe[1] ? topCe[1].strike : null,
        s1: topPe[0] ? topPe[0].strike : null,
        s2: topPe[1] ? topPe[1].strike : null,
        sentiment, sentimentColor, sentimentDesc
      },
      strikes: enrichedStrikes
    };
  }

  function renderUI(intel) {
    document.getElementById('mits-spot-display').textContent = Number(intel.spot).toLocaleString('en-IN', { minimumFractionDigits: 2 });
    document.getElementById('mits-pcr-val').textContent = intel.intelligence.pcr;
    document.getElementById('mits-pcr-fresh-sub').textContent = `PCR Buildup: ${intel.intelligence.pcrFresh}`;
    document.getElementById('mits-pcr-status').textContent = intel.intelligence.pcr >= 1.05 ? "Bullish" : (intel.intelligence.pcr <= 0.85 ? "Bearish" : "Neutral");

    const sentVal = document.getElementById('mits-sentiment-val');
    sentVal.textContent = intel.intelligence.sentiment;
    sentVal.style.color = intel.intelligence.sentimentColor;
    document.getElementById('mits-sentiment-desc').textContent = intel.intelligence.sentimentDesc;
    document.getElementById('mits-sentiment-badge').textContent = intel.intelligence.sentiment.split(' ')[0];
    document.getElementById('mits-sentiment-badge').style.color = intel.intelligence.sentimentColor;

    document.getElementById('mits-res1-val').textContent = formatNum(intel.intelligence.r1);
    document.getElementById('mits-res2-sub').textContent = `Next Resistance: ${formatNum(intel.intelligence.r2)}`;
    document.getElementById('mits-sup1-val').textContent = formatNum(intel.intelligence.s1);
    document.getElementById('mits-sup2-sub').textContent = `Next Support: ${formatNum(intel.intelligence.s2)}`;
    document.getElementById('mits-maxpain-val').textContent = formatNum(intel.intelligence.maxPain);

    document.getElementById('mits-ce-total-oi').textContent = formatNum(intel.ce.totalOI);
    document.getElementById('mits-ce-otm-pct-label').textContent = formatPct(intel.ce.otmPct);
    document.getElementById('mits-ce-itm-pct-label').textContent = formatPct(intel.ce.itmPct);
    document.getElementById('mits-ce-ratio-otm').style.width = Math.min(100, Math.max(0, intel.ce.otmPct)) + "%";
    document.getElementById('mits-ce-ratio-itm').style.width = Math.min(100, Math.max(0, intel.ce.itmPct)) + "%";

    document.getElementById('mits-ce-otm-oi').textContent = formatNum(intel.ce.otmOI);
    document.getElementById('mits-ce-otm-pct').textContent = formatPct(intel.ce.otmPct);
    document.getElementById('mits-ce-itm-oi').textContent = formatNum(intel.ce.itmOI);
    document.getElementById('mits-ce-itm-pct').textContent = formatPct(intel.ce.itmPct);

    document.getElementById('mits-ce-fresh-total').textContent = "+" + formatNum(intel.ce.freshTotal);
    document.getElementById('mits-ce-fresh-otm').textContent = "+" + formatNum(intel.ce.freshOtm);
    document.getElementById('mits-ce-fresh-otm-pct').textContent = formatPct(intel.ce.freshOtmPct);
    document.getElementById('mits-ce-fresh-itm').textContent = "+" + formatNum(intel.ce.freshItm);
    document.getElementById('mits-ce-fresh-itm-pct').textContent = formatPct(intel.ce.freshItmPct);

    document.getElementById('mits-ce-unwind-total').textContent = "-" + formatNum(intel.ce.unwindTotal);
    document.getElementById('mits-ce-unwind-otm').textContent = formatNum(intel.ce.unwindOtm);
    document.getElementById('mits-ce-unwind-otm-pct').textContent = formatPct(intel.ce.unwindOtmPct);
    document.getElementById('mits-ce-unwind-itm').textContent = "-" + formatNum(intel.ce.unwindItm);
    document.getElementById('mits-ce-unwind-itm-pct').textContent = formatPct(intel.ce.unwindItmPct);

    document.getElementById('mits-pe-total-oi').textContent = formatNum(intel.pe.totalOI);
    document.getElementById('mits-pe-otm-pct-label').textContent = formatPct(intel.pe.otmPct);
    document.getElementById('mits-pe-itm-pct-label').textContent = formatPct(intel.pe.itmPct);
    document.getElementById('mits-pe-ratio-otm').style.width = Math.min(100, Math.max(0, intel.pe.otmPct)) + "%";
    document.getElementById('mits-pe-ratio-itm').style.width = Math.min(100, Math.max(0, intel.pe.itmPct)) + "%";

    document.getElementById('mits-pe-otm-oi').textContent = formatNum(intel.pe.otmOI);
    document.getElementById('mits-pe-otm-pct').textContent = formatPct(intel.pe.otmPct);
    document.getElementById('mits-pe-itm-oi').textContent = formatNum(intel.pe.itmOI);
    document.getElementById('mits-pe-itm-pct').textContent = formatPct(intel.pe.itmPct);

    document.getElementById('mits-pe-fresh-total').textContent = "+" + formatNum(intel.pe.freshTotal);
    document.getElementById('mits-pe-fresh-otm').textContent = "+" + formatNum(intel.pe.freshOtm);
    document.getElementById('mits-pe-fresh-otm-pct').textContent = formatPct(intel.pe.freshOtmPct);
    document.getElementById('mits-pe-fresh-itm').textContent = formatNum(intel.pe.freshItm);
    document.getElementById('mits-pe-fresh-itm-pct').textContent = formatPct(intel.pe.freshItmPct);

    document.getElementById('mits-pe-unwind-total').textContent = "-" + formatNum(intel.pe.unwindTotal);
    document.getElementById('mits-pe-unwind-otm').textContent = formatNum(intel.pe.unwindOtm);
    document.getElementById('mits-pe-unwind-otm-pct').textContent = formatPct(intel.pe.unwindOtmPct);
    document.getElementById('mits-pe-unwind-itm').textContent = "-" + formatNum(intel.pe.unwindItm);
    document.getElementById('mits-pe-unwind-itm-pct').textContent = formatPct(intel.pe.unwindItmPct);

    renderTable(intel.strikes, intel.spot);
    renderCharts(intel.strikes, intel.spot);
  }

  function renderTable(strikes, spot) {
    const tbody = document.getElementById('mits-table-body');
    tbody.innerHTML = '';

    let displayedStrikes = [...strikes];
    if (state.filter === 'near') {
      const sortedByDiff = [...strikes].sort((a, b) => a.diff - b.diff);
      const topNearby = new Set(sortedByDiff.slice(0, 10).map(s => s.strike));
      displayedStrikes = strikes.filter(s => topNearby.has(s.strike));
    }

    document.getElementById('mits-strike-count-label').textContent = `(${displayedStrikes.length} Strikes Loaded)`;
    const maxOI = Math.max(...strikes.map(s => Math.max(s.ce_oi, s.pe_oi)), 1);

    let closestStrike = strikes[0]?.strike;
    let minD = Infinity;
    strikes.forEach(s => {
      if (s.diff < minD) {
        minD = s.diff;
        closestStrike = s.strike;
      }
    });

    displayedStrikes.forEach(s => {
      const tr = document.createElement('tr');
      if (s.strike === closestStrike) tr.classList.add('strike-atm');

      const ceBarPct = Math.round((s.ce_oi / maxOI) * 100);
      const peBarPct = Math.round((s.pe_oi / maxOI) * 100);

      const ceChgClass = s.ce_chg > 0 ? "val-pos" : (s.ce_chg < 0 ? "val-neg" : "");
      const peChgClass = s.pe_chg > 0 ? "val-pos" : (s.pe_chg < 0 ? "val-neg" : "");

      tr.innerHTML = `
        <td class="${s.isCeItm ? 'itm-ce' : ''}" style="text-align: center; font-weight: 600; color: ${s.isCeItm ? '#fbbf24' : '#60a5fa'};">${s.isCeItm ? 'ITM' : 'OTM'}</td>
        <td class="${s.isCeItm ? 'itm-ce' : ''}">${s.ce_ltp.toFixed(2)}</td>
        <td class="${s.isCeItm ? 'itm-ce' : ''} ${ceChgClass}">${formatSigned(s.ce_chg)}</td>
        <td class="${s.isCeItm ? 'itm-ce' : ''} mits-cell-bar" style="border-right: 1px solid var(--mits-border);">
          <div class="mits-bar-bg ce" style="width: ${ceBarPct}%;"></div>
          <span style="position: relative; z-index: 1;">${formatNum(s.ce_oi)}</span>
        </td>
        
        <td class="strike-col">
          ${formatNum(s.strike)}
          ${s.strike === closestStrike ? '<span style="font-size: 9px; display: block; color: var(--mits-accent);">ATM</span>' : ''}
        </td>

        <td class="${s.isPeItm ? 'itm-pe' : ''} mits-cell-bar" style="border-left: 1px solid var(--mits-border); justify-content: flex-start;">
          <div class="mits-bar-bg pe" style="width: ${peBarPct}%;"></div>
          <span style="position: relative; z-index: 1;">${formatNum(s.pe_oi)}</span>
        </td>
        <td class="${s.isPeItm ? 'itm-pe' : ''} ${peChgClass}">${formatSigned(s.pe_chg)}</td>
        <td class="${s.isPeItm ? 'itm-pe' : ''}">${s.pe_ltp.toFixed(2)}</td>
        <td class="${s.isPeItm ? 'itm-pe' : ''}" style="text-align: center; font-weight: 600; color: ${s.isPeItm ? '#fbbf24' : '#60a5fa'};">${s.isPeItm ? 'ITM' : 'OTM'}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function renderCharts(strikes, spot) {
    if (typeof Chart === 'undefined') return;

    const labels = strikes.map(s => s.strike);
    const ceOI = strikes.map(s => s.ce_oi);
    const peOI = strikes.map(s => s.pe_oi);
    const ceChg = strikes.map(s => s.ce_chg);
    const peChg = strikes.map(s => s.pe_chg);

    const isDark = state.theme === 'dark';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';
    const textColor = isDark ? '#94a3b8' : '#64748b';

    const ctxOI = document.getElementById('mits-oi-chart');
    if (ctxOI) {
      if (state.oiChart) state.oiChart.destroy();
      state.oiChart = new Chart(ctxOI, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            { label: 'Call OI', data: ceOI, backgroundColor: 'rgba(239, 68, 68, 0.7)', borderColor: '#ef4444', borderWidth: 1, borderRadius: 4 },
            { label: 'Put OI', data: peOI, backgroundColor: 'rgba(16, 185, 129, 0.7)', borderColor: '#10b981', borderWidth: 1, borderRadius: 4 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: textColor, font: { size: 11 } } },
            tooltip: { callbacks: { label: (c) => ` ${c.dataset.label}: ${Number(c.raw).toLocaleString('en-IN')}` } }
          },
          scales: {
            x: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 10 } } },
            y: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 10 } } }
          }
        }
      });
    }

    const ctxChg = document.getElementById('mits-chg-chart');
    if (ctxChg) {
      if (state.chgChart) state.chgChart.destroy();
      state.chgChart = new Chart(ctxChg, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            { label: 'Call Chg OI', data: ceChg, backgroundColor: ceChg.map(v => v >= 0 ? 'rgba(239, 68, 68, 0.7)' : 'rgba(239, 68, 68, 0.25)'), borderRadius: 4 },
            { label: 'Put Chg OI', data: peChg, backgroundColor: peChg.map(v => v >= 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(16, 185, 129, 0.25)'), borderRadius: 4 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: textColor, font: { size: 11 } } },
            tooltip: { callbacks: { label: (c) => ` ${c.dataset.label}: ${c.raw > 0 ? '+' : ''}${Number(c.raw).toLocaleString('en-IN')}` } }
          },
          scales: {
            x: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 10 } } },
            y: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 10 } } }
          }
        }
      });
    }
  }

  function applySummaryJSON(summary) {
    if (!summary || !summary.call_breakdown || !summary.strikes) return false;

    state.spotPrice = Number(summary.spot_price);
    state.dataRows = summary.strikes;

    const intel = {
      spot: summary.spot_price,
      ce: {
        totalOI: summary.call_breakdown.total_oi,
        otmOI: summary.call_breakdown.otm.oi,
        otmPct: summary.call_breakdown.otm.oi_pct,
        itmOI: summary.call_breakdown.itm.oi,
        itmPct: summary.call_breakdown.itm.oi_pct,
        freshTotal: summary.call_breakdown.fresh_additions_total,
        freshOtm: summary.call_breakdown.otm.fresh_additions,
        freshOtmPct: summary.call_breakdown.otm.fresh_additions_pct,
        freshItm: summary.call_breakdown.itm.fresh_additions,
        freshItmPct: summary.call_breakdown.itm.fresh_additions_pct,
        unwindTotal: summary.call_breakdown.unwinding_total,
        unwindOtm: summary.call_breakdown.otm.unwinding,
        unwindOtmPct: summary.call_breakdown.otm.unwinding_pct,
        unwindItm: summary.call_breakdown.itm.unwinding,
        unwindItmPct: summary.call_breakdown.itm.unwinding_pct,
      },
      pe: {
        totalOI: summary.put_breakdown.total_oi,
        otmOI: summary.put_breakdown.otm.oi,
        otmPct: summary.put_breakdown.otm.oi_pct,
        itmOI: summary.put_breakdown.itm.oi,
        itmPct: summary.put_breakdown.itm.oi_pct,
        freshTotal: summary.put_breakdown.fresh_additions_total,
        freshOtm: summary.put_breakdown.otm.fresh_additions,
        freshOtmPct: summary.put_breakdown.otm.fresh_additions_pct,
        freshItm: summary.put_breakdown.itm.fresh_additions,
        freshItmPct: summary.put_breakdown.itm.fresh_additions_pct,
        unwindTotal: summary.put_breakdown.unwinding_total,
        unwindOtm: summary.put_breakdown.otm.unwinding,
        unwindOtmPct: summary.put_breakdown.otm.unwinding_pct,
        unwindItm: summary.put_breakdown.itm.unwinding,
        unwindItmPct: summary.put_breakdown.itm.unwinding_pct,
      },
      intelligence: {
        pcr: summary.intelligence.pcr.toFixed(2),
        pcrFresh: summary.intelligence.pcr_fresh.toFixed(2),
        maxPain: summary.intelligence.max_pain,
        r1: summary.intelligence.resistance_1,
        r2: summary.intelligence.resistance_2,
        s1: summary.intelligence.support_1,
        s2: summary.intelligence.support_2,
        sentiment: summary.intelligence.sentiment,
        sentimentColor: summary.intelligence.sentiment_color,
        sentimentDesc: summary.intelligence.bias_summary,
      },
      strikes: summary.strikes.map(s => ({
        ...s,
        isCeItm: s.ce_classification === "ITM",
        isPeItm: s.pe_classification === "ITM",
        diff: Math.abs(s.strike - summary.spot_price)
      }))
    };

    renderUI(intel);

    const meta = summary.metadata || {};
    showSyncBanner(`🟢 Automated EOD Synced &bull; ${meta.symbol || 'NIFTY'} @ <strong>${formatNum(summary.spot_price)}</strong> &bull; EOD Time: <strong>${meta.nse_timestamp || 'Latest'}</strong> &bull; Auto-calculated via Pipeline`);
    return true;
  }

  async function fetchAutomatedSummary() {
    showSyncBanner(`⏳ Syncing latest EOD Option Chain summary...`);
    try {
      const targetUrl = summaryJsonUrl || 'option_chain_summary.json';
      const sep = targetUrl.includes('?') ? '&' : '?';
      const resp = await fetch(targetUrl + sep + 't=' + Date.now());
      if (resp.ok) {
        const summary = await resp.json();
        if (applySummaryJSON(summary)) return true;
      }
    } catch (e) {
      console.log("Could not load automated summary JSON, checking benchmark fallback.", e);
    }
    // Fallback to internal demo data
    if (autoDemo) {
      state.spotPrice = 24350.50;
      state.dataRows = DEMO_DATA;
      const initialIntel = calculateIntelligence(state.dataRows, state.spotPrice);
      renderUI(initialIntel);
      showSyncBanner(`ℹ️ Automated EOD file pending. Displaying active benchmark model.`);
    } else {
      showSyncBanner(`⚠️ Option Chain summary not yet generated. Use manual upload below or run pipeline.`, false);
    }
    return false;
  }

  function parseContent(rawContent, filename = "") {
    let detectedSpot = null;
    let rows = [];

    const text = typeof rawContent === 'string' ? rawContent.replace(/^\uFEFF/, '').trim() : '';

    if (typeof rawContent === 'object' || text.startsWith('{') || text.startsWith('[')) {
      try {
        const json = typeof rawContent === 'object' ? rawContent : JSON.parse(text);
        if (json && json.call_breakdown && json.strikes) {
          applySummaryJSON(json);
          return;
        }
        if (json && json.records) {
          detectedSpot = cleanNum(json.records.underlyingValue);
          (json.records.data || []).forEach(item => {
            const strike = cleanNum(item.strikePrice);
            if (!strike || strike <= 0) return;
            const ce = item.CE || {};
            const pe = item.PE || {};
            if (!detectedSpot) detectedSpot = cleanNum(ce.underlyingValue || pe.underlyingValue);
            rows.push({
              strike,
              ce_oi: cleanNum(ce.openInterest),
              ce_chg: cleanNum(ce.changeinOpenInterest),
              ce_ltp: cleanNum(ce.lastPrice),
              pe_oi: cleanNum(pe.openInterest),
              pe_chg: cleanNum(pe.changeinOpenInterest),
              pe_ltp: cleanNum(pe.lastPrice),
            });
          });
        } else if (Array.isArray(json)) {
          json.forEach(item => {
            const strike = extractNum(item, ['strike', 'strikeprice', 'strike_price', 'k']);
            if (!strike || strike <= 0) return;
            const spotInItem = extractNum(item, ['spot', 'spotprice', 'spot_price', 'underlying', 'underlyingvalue']);
            if (spotInItem && !detectedSpot) detectedSpot = spotInItem;
            rows.push({
              strike,
              ce_oi: extractNum(item, ['ce_oi', 'call_oi', 'ceoi', 'calls_oi', 'callsopeninterest', 'oi', 'oice']),
              ce_chg: extractNum(item, ['ce_chg', 'ce_chg_oi', 'call_chg', 'callschnginoi', 'chnginoi', 'change']),
              ce_ltp: extractNum(item, ['ce_ltp', 'call_ltp', 'calls_ltp', 'ceprice', 'ltp']),
              pe_oi: extractNum(item, ['pe_oi', 'put_oi', 'peoi', 'puts_oi', 'putsopeninterest', 'oipe']),
              pe_chg: extractNum(item, ['pe_chg', 'pe_chg_oi', 'put_chg', 'putschnginoi']),
              pe_ltp: extractNum(item, ['pe_ltp', 'put_ltp', 'puts_ltp', 'peprice']),
            });
          });
        }
      } catch (e) {
        console.warn("JSON parse attempt not applicable, proceeding to CSV...", e);
      }
    }

    if (rows.length === 0 && text) {
      let lines = [];
      if (typeof Papa !== 'undefined') {
        try {
          const parsed = Papa.parse(text, { skipEmptyLines: true });
          lines = parsed.data || [];
        } catch (e) {
          lines = parseCSV(text);
        }
      } else {
        lines = parseCSV(text);
      }

      if (lines.length > 0) {
        for (let i = 0; i < Math.min(5, lines.length); i++) {
          const lineStr = lines[i].join(' ');
          const spotMatch = lineStr.match(/(?:underlying|spot)[^0-9]*([0-9]+(?:\.[0-9]+)?)/i);
          if (spotMatch) {
            detectedSpot = parseFloat(spotMatch[1]);
            break;
          }
        }

        let headerIdx = -1;
        for (let i = 0; i < Math.min(10, lines.length); i++) {
          const row = lines[i];
          if (row.some(c => norm(c).includes('strike'))) {
            headerIdx = i;
            break;
          }
        }

        if (headerIdx !== -1) {
          if (headerIdx + 1 < lines.length && lines[headerIdx + 1].some(c => norm(c).includes('strike'))) {
            headerIdx += 1;
          }

          const header = lines[headerIdx];
          const strikeColIdx = header.findIndex(c => norm(c).includes('strike'));
          const isNseSymmetric = strikeColIdx > 3 && (header.length - strikeColIdx) > 3;

          for (let r = headerIdx + 1; r < lines.length; r++) {
            const row = lines[r];
            if (!row || row.length <= strikeColIdx) continue;

            if (isNseSymmetric) {
              const strike = cleanNum(row[strikeColIdx]);
              if (!strike || strike <= 0) continue;
              rows.push({
                strike,
                ce_oi: cleanNum(row[0]),
                ce_chg: cleanNum(row[1]),
                ce_ltp: cleanNum(row[4]),
                pe_oi: cleanNum(row[row.length - 1]),
                pe_chg: cleanNum(row[row.length - 2]),
                pe_ltp: cleanNum(row[row.length - 5]),
              });
            } else {
              const rowObj = {};
              header.forEach((h, idx) => { rowObj[h] = row[idx]; });
              const strike = extractNum(rowObj, ['strike', 'strikeprice', 'strike_price', 'k']);
              if (!strike || strike <= 0) continue;

              const spotInRow = extractNum(rowObj, ['spot', 'spotprice', 'spot_price', 'underlying', 'underlyingvalue']);
              if (spotInRow && !detectedSpot) detectedSpot = spotInRow;

              rows.push({
                strike,
                ce_oi: extractNum(rowObj, ['ce_oi', 'call_oi', 'ceoi', 'calls_oi', 'callsopeninterest', 'oi', 'oice']),
                ce_chg: extractNum(rowObj, ['ce_chg', 'ce_chg_oi', 'call_chg', 'callschnginoi', 'chnginoi', 'change']),
                ce_ltp: extractNum(rowObj, ['ce_ltp', 'call_ltp', 'calls_ltp', 'ceprice', 'ltp']),
                pe_oi: extractNum(rowObj, ['pe_oi', 'put_oi', 'peoi', 'puts_oi', 'putsopeninterest', 'oipe']),
                pe_chg: extractNum(rowObj, ['pe_chg', 'pe_chg_oi', 'put_chg', 'putschnginoi']),
                pe_ltp: extractNum(rowObj, ['pe_ltp', 'put_ltp', 'puts_ltp', 'peprice']),
              });
            }
          }
        }
      }
    }

    if (rows.length === 0) {
      showStatus(`❌ Could not detect Option Chain columns in "${filename || 'file'}". Please ensure columns include Strike, CE OI, and PE OI.`, 'error');
      return;
    }

    const strikeMap = {};
    rows.forEach(r => {
      if (!strikeMap[r.strike]) strikeMap[r.strike] = r;
      else {
        strikeMap[r.strike].ce_oi += r.ce_oi;
        strikeMap[r.strike].ce_chg += r.ce_chg;
        strikeMap[r.strike].pe_oi += r.pe_oi;
        strikeMap[r.strike].pe_chg += r.pe_chg;
      }
    });
    state.dataRows = Object.values(strikeMap).sort((a, b) => a.strike - b.strike);

    if (detectedSpot && detectedSpot > 0) {
      state.spotPrice = detectedSpot;
    } else if (!state.spotPrice || state.spotPrice <= 0) {
      state.spotPrice = state.dataRows[Math.floor(state.dataRows.length / 2)].strike;
    }

    const intel = calculateIntelligence(state.dataRows, state.spotPrice);
    renderUI(intel);

    showStatus(`✓ Processed custom document (${state.dataRows.length} strikes). Spot: <strong>${formatNum(state.spotPrice)}</strong>`, 'success');
  }

  function handleFile(file) {
    if (!file) return;

    showStatus(`⏳ Reading <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)...`, 'loading');

    const name = file.name.toLowerCase();

    if (name.endsWith('.xlsx') || name.endsWith('.xls')) {
      if (typeof XLSX === 'undefined') {
        showStatus(`⚠️ SheetJS library is loading or blocked. Please convert to CSV or verify network connection.`, 'error');
        return;
      }
      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
            throw new Error("No sheet found in Excel workbook.");
          }
          const firstSheet = workbook.SheetNames[0];
          const csvText = XLSX.utils.sheet_to_csv(workbook.Sheets[firstSheet]);
          parseContent(csvText, file.name);
        } catch (err) {
          console.error("Excel parsing error:", err);
          showStatus(`❌ Failed to read Excel file: ${err.message}`, 'error');
        }
      };
      reader.onerror = function() {
        showStatus(`❌ Error reading file from device: ${file.name}`, 'error');
      };
      reader.readAsArrayBuffer(file);
    } else {
      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          parseContent(e.target.result, file.name);
        } catch (err) {
          console.error("File parsing error:", err);
          showStatus(`❌ Failed to parse file: ${err.message}`, 'error');
        }
      };
      reader.onerror = function() {
        showStatus(`❌ Error reading file from device: ${file.name}`, 'error');
      };
      reader.readAsText(file);
    }
  }

  function initEvents() {
    const root = document.getElementById('mits-oc-root');
    const fileInput = document.getElementById('mits-file-input');
    const dropZone = document.getElementById('mits-drop-zone');
    const browseBtn = document.getElementById('mits-browse-btn');
    const pasteToggle = document.getElementById('mits-toggle-paste-btn');
    const pasteBox = document.getElementById('mits-paste-container');
    const parsePasteBtn = document.getElementById('mits-parse-paste-btn');
    const pasteInput = document.getElementById('mits-paste-input');
    const themeBtn = document.getElementById('mits-toggle-theme-btn');
    const editSpotBtn = document.getElementById('mits-edit-spot-btn');
    const copySummaryBtn = document.getElementById('mits-copy-summary-btn');
    const refreshEodBtn = document.getElementById('mits-refresh-eod-btn');
    const toggleUploadBtn = document.getElementById('mits-toggle-upload-btn');

    // Refresh EOD Button
    if (refreshEodBtn) {
      refreshEodBtn.addEventListener('click', (e) => {
        e.preventDefault();
        fetchAutomatedSummary();
      });
    }

    // Toggle Manual Upload drawer
    if (toggleUploadBtn && dropZone) {
      toggleUploadBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const isHidden = window.getComputedStyle(dropZone).display === 'none';
        dropZone.style.display = isHidden ? 'block' : 'none';
        toggleUploadBtn.textContent = isHidden ? 'Manual Upload ▴' : 'Manual Upload ▾';
      });
    }

    if (browseBtn && fileInput) {
      browseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        fileInput.click();
      });
    }

    if (dropZone && fileInput) {
      dropZone.addEventListener('click', (e) => {
        if (e.target.closest('#mits-paste-container') || 
            e.target.closest('#mits-toggle-paste-btn') || 
            e.target.closest('#mits-parse-paste-btn') ||
            e.target.closest('#mits-browse-btn')) {
          return;
        }
        fileInput.click();
      });
    }

    if (fileInput) {
      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
          handleFile(e.target.files[0]);
          e.target.value = '';
        }
      });
    }

    if (dropZone) {
      ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
        }, false);
      });

      dropZone.addEventListener('dragenter', () => dropZone.classList.add('dragover'));
      dropZone.addEventListener('dragover', () => dropZone.classList.add('dragover'));
      dropZone.addEventListener('dragleave', (e) => {
        if (!dropZone.contains(e.relatedTarget)) {
          dropZone.classList.remove('dragover');
        }
      });
      dropZone.addEventListener('drop', (e) => {
        dropZone.classList.remove('dragover');
        const dt = e.dataTransfer;
        if (dt && dt.files && dt.files.length > 0) {
          handleFile(dt.files[0]);
        }
      });
    }

    if (pasteToggle && pasteBox) {
      pasteToggle.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        pasteBox.style.display = pasteBox.style.display === 'block' ? 'none' : 'block';
      });
    }

    if (parsePasteBtn && pasteInput) {
      parsePasteBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const text = pasteInput.value.trim();
        if (!text) {
          showStatus("⚠️ Please paste Option Chain CSV or JSON text first.", "error");
          return;
        }
        parseContent(text, "pasted-content.csv");
      });
    }

    if (themeBtn) {
      themeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        state.theme = state.theme === 'dark' ? 'light' : 'dark';
        if (state.theme === 'light') {
          root.classList.remove('mits-theme-dark');
          root.classList.add('mits-theme-light');
          document.getElementById('mits-theme-icon').textContent = '🌙 Dark';
        } else {
          root.classList.remove('mits-theme-light');
          root.classList.add('mits-theme-dark');
          document.getElementById('mits-theme-icon').textContent = '☀️ Light';
        }
        const intel = calculateIntelligence(state.dataRows, state.spotPrice);
        renderCharts(intel.strikes, intel.spot);
      });
    }

    if (editSpotBtn) {
      editSpotBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const current = state.spotPrice;
        const input = prompt("Enter new Spot Price to recalculate dynamic ITM/OTM categorizations:", current);
        if (input !== null) {
          const val = parseFloat(input.replace(/,/g, ''));
          if (!isNaN(val) && val > 0) {
            state.spotPrice = val;
            const intel = calculateIntelligence(state.dataRows, state.spotPrice);
            renderUI(intel);
            showStatus(`✓ Spot price updated to <strong>${formatNum(val)}</strong>. Recalculated dynamically.`, "success");
          } else {
            alert("Invalid spot price number.");
          }
        }
      });
    }

    document.querySelectorAll('.mits-filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.mits-filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.filter = e.target.getAttribute('data-filter');
        const intel = calculateIntelligence(state.dataRows, state.spotPrice);
        renderTable(intel.strikes, intel.spot);
      });
    });

    if (copySummaryBtn) {
      copySummaryBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const intel = calculateIntelligence(state.dataRows, state.spotPrice);
        const summaryText = 
`=== MITS OPTION CHAIN INTELLIGENCE ===
Spot Price: ${intel.spot}
PCR: ${intel.intelligence.pcr} | Sentiment: ${intel.intelligence.sentiment}
Max Pain: ${intel.intelligence.maxPain}
Resistance: ${intel.intelligence.r1} | Support: ${intel.intelligence.s1}

CALL SIDE (CE):
Total OI: ${formatNum(intel.ce.totalOI)}
OTM Calls: ${formatNum(intel.ce.otmOI)} (${formatPct(intel.ce.otmPct)})
ITM Calls: ${formatNum(intel.ce.itmOI)} (${formatPct(intel.ce.itmPct)})
Fresh Additions: ${formatNum(intel.ce.freshTotal)} (OTM: ${formatPct(intel.ce.freshOtmPct)}, ITM: ${formatPct(intel.ce.freshItmPct)})
Unwinding: ${formatNum(intel.ce.unwindTotal)} (OTM: ${formatPct(intel.ce.unwindOtmPct)}, ITM: ${formatPct(intel.ce.unwindItmPct)})

PUT SIDE (PE):
Total OI: ${formatNum(intel.pe.totalOI)}
OTM Puts: ${formatNum(intel.pe.otmOI)} (${formatPct(intel.pe.otmPct)})
ITM Puts: ${formatNum(intel.pe.itmOI)} (${formatPct(intel.pe.itmPct)})
Fresh Additions: ${formatNum(intel.pe.freshTotal)} (OTM: ${formatPct(intel.pe.freshOtmPct)}, ITM: ${formatPct(intel.pe.freshItmPct)})
Unwinding: ${formatNum(intel.pe.unwindTotal)} (OTM: ${formatPct(intel.pe.unwindOtmPct)}, ITM: ${formatPct(intel.pe.unwindItmPct)})
Generated via MITS Automated EOD Option Chain Pipeline`;

        navigator.clipboard.writeText(summaryText).then(() => {
          showStatus("✓ Option Chain Intelligence Summary copied to clipboard!", "success");
        }).catch(() => {
          alert("Clipboard permission denied. Please copy manually.");
        });
      });
    }
  }

  function init() {
    initEvents();
    // Automatically fetch EOD summary JSON generated by background pipeline
    fetchAutomatedSummary();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>
