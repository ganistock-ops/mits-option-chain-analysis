<?php
/**
 * Plugin Name: MITS Option Chain Intelligence Widget
 * Plugin URI: https://marketintelligence.trading/
 * Description: Professional Standalone Option Chain Intelligence & Breakdown Widget. Features dynamic ITM/OTM strike categorization, CE & PE breakdowns, fresh additions, unwinding, and visual analytics.
 * Version: 1.0.0
 * Author: Market Intelligence Trading System (MITS)
 * Author URI: https://marketintelligence.trading/
 * License: GPL-2.0+
 * Text Domain: mits-option-chain
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

class MITSOptionChainPlugin {

    public function __construct() {
        add_shortcode('mits_option_chain', array($this, 'render_shortcode'));
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
    }

    /**
     * Registers settings in WP Admin
     */
    public function register_settings() {
        register_setting('mits_oc_options_group', 'mits_oc_default_theme');
        register_setting('mits_oc_options_group', 'mits_oc_default_demo');
        register_setting('mits_oc_options_group', 'mits_oc_summary_url');
    }

    /**
     * Adds Settings link under Settings menu in WP Admin
     */
    public function add_admin_menu() {
        add_options_page(
            'MITS Option Chain Settings',
            'MITS Option Chain',
            'manage_options',
            'mits-option-chain-settings',
            array($this, 'render_settings_page')
        );
    }

    /**
     * Settings Page UI
     */
    public function render_settings_page() {
        ?>
        <div class="wrap">
            <h1>MITS Option Chain Intelligence - Settings</h1>
            <p>Configure default display preferences for the <code>[mits_option_chain]</code> shortcode.</p>

            <form method="post" action="options.php">
                <?php
                settings_fields('mits_oc_options_group');
                do_settings_sections('mits_oc_options_group');
                $default_theme = get_option('mits_oc_default_theme', 'dark');
                $default_demo = get_option('mits_oc_default_demo', '1');
                $default_summary_url = get_option('mits_oc_summary_url', 'option_chain_summary.json');
                ?>
                <table class="form-table">
                    <tr valign="top">
                        <th scope="row">Default Theme</th>
                        <td>
                            <select name="mits_oc_default_theme">
                                <option value="dark" <?php selected($default_theme, 'dark'); ?>>Dark Mode (Default)</option>
                                <option value="light" <?php selected($default_theme, 'light'); ?>>Light Mode</option>
                            </select>
                            <p class="description">Select the default color palette when the widget loads.</p>
                        </td>
                    </tr>
                    <tr valign="top">
                        <th scope="row">Automated EOD Summary URL / Path</th>
                        <td>
                            <input type="text" name="mits_oc_summary_url" value="<?php echo esc_attr($default_summary_url); ?>" class="regular-text" placeholder="option_chain_summary.json" />
                            <p class="description">URL or relative path to <code>option_chain_summary.json</code> produced daily by the background pipeline (e.g. <code>option_chain_summary.json</code>, <code>/wp-content/uploads/option_chain_summary.json</code>, or raw GitHub link). The widget will automatically fetch and display this data with zero manual file uploads.</p>
                        </td>
                    </tr>
                    <tr valign="top">
                        <th scope="row">Auto-Load Benchmark Demo</th>
                        <td>
                            <label>
                                <input type="checkbox" name="mits_oc_default_demo" value="1" <?php checked($default_demo, '1'); ?> />
                                Preload NIFTY 50 Benchmark data if the automated summary JSON is temporarily unreachable
                            </label>
                            <p class="description">Ensures visitors always see live calculations and charts immediately.</p>
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>

            <hr/>
            <h2>How to Embed the Widget</h2>
            <p>Add this shortcode to any Page, Post, or Elementor / Gutenberg Custom HTML block:</p>
            <pre style="background: #fff; padding: 12px; border: 1px solid #ccd0d4; max-width: 600px; font-weight: bold;">[mits_option_chain]</pre>
            <p>You can also override attributes inline:</p>
            <pre style="background: #fff; padding: 12px; border: 1px solid #ccd0d4; max-width: 600px;">[mits_option_chain theme="light" summary_url="option_chain_summary.json"]</pre>
        </div>
        <?php
    }

    /**
     * Renders the complete widget via shortcode
     */
    public function render_shortcode($atts) {
        $saved_theme = get_option('mits_oc_default_theme', 'dark');
        $saved_demo = get_option('mits_oc_default_demo', '1');
        $saved_summary_url = get_option('mits_oc_summary_url', 'option_chain_summary.json');

        $args = shortcode_atts(array(
            'theme' => $saved_theme ? $saved_theme : 'dark',
            'demo' => $saved_demo ? 'true' : 'false',
            'summary_url' => $saved_summary_url ? $saved_summary_url : 'option_chain_summary.json',
        ), $atts, 'mits_option_chain');

        $theme_class = ($args['theme'] === 'light') ? 'mits-theme-light' : 'mits-theme-dark';
        $auto_demo = ($args['demo'] === 'true' || $args['demo'] === '1') ? 'true' : 'false';
        $summary_url = !empty($args['summary_url']) ? esc_url_raw($args['summary_url']) : 'option_chain_summary.json';

        // Read standalone template and embed
        $template_file = plugin_dir_path(__FILE__) . 'widget-template.php';
        
        ob_start();
        if (file_exists($template_file)) {
            include $template_file;
        } else {
            // Fallback inline rendering
            echo $this->get_widget_html($theme_class, $auto_demo);
        }
        return ob_get_clean();
    }

    private function get_widget_html($theme_class, $auto_demo) {
        // Output widget content
        $html_file = dirname(__FILE__) . '/../mits-option-chain-widget.html';
        if (file_exists($html_file)) {
            $content = file_get_contents($html_file);
            // Extract body content between <body> and </body>
            if (preg_match('/<body>(.*?)<\/body>/s', $content, $matches)) {
                return $matches[1];
            }
            return $content;
        }
        return '<p>MITS Option Chain widget file not found.</p>';
    }
}

// Initialize Plugin
new MITSOptionChainPlugin();
