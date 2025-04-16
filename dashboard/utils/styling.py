"""Styling utilities for the dashboard."""

# Teck Resources colors
TECK_NAVY = "#00103f"     # Primary accent color
TECK_ORANGE = "#ce3e0d"   # Secondary accent color  
TECK_BLUE = "#0072CE"     # Additional blue for variety
TECK_LIGHT_BLUE = "#68B2E3"
TECK_GRAY = "#333333"     # Dark gray for text (improved contrast)
TECK_LIGHT_GRAY = "#f5f5f5" # Background color

def get_css():
    """Return the CSS styling for the dashboard."""
    return """
    <style>
        /* Main Header Styles */
        .main-header {
            color: #00103f;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            line-height: 1.2;
        }
        
        /* NEW: Fix for empty white rectangles */
        .stMarkdown a + div {
            display: none !important;
        }
        
        .section-header + div {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        div:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Fix for streamlit's anchor container */
        .st-emotion-cache-ue6h4q {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Fix for header anchor containers */
        .main-header + div, .section-header + div, .sub-header + div {
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Original styles */
        .sub-header {
            color: #00103f;
            font-size: 1.8rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            line-height: 1.3;
        }
        .section-header {
            color: #00103f;
            font-size: 1.4rem;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
            /* Remove white bars under headings */
            border-bottom: none;
            padding-bottom: 0;
        }
        .card {
            border-radius: 8px;
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16);
            padding: 20px;
            margin-bottom: 20px;
            background-color: white;
            /* Remove white bars */
            border-top: none;
        }
        .metric-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 1.25rem;
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16);
            height: 100%;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #00103f;
            line-height: 1.2;
        }
        .metric-label {
            font-size: 1.1rem;
            color: #333333;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .positive-change {
            color: #00A651;
            font-weight: 600;
        }
        .negative-change {
            color: #ce3e0d;
            font-weight: 600;
        }
        .positive-impact {
            color: #00A651;
            font-weight: 600;
        }
        .negative-impact {
            color: #ce3e0d;
            font-weight: 600;
        }
        .neutral-change {
            color: #333333;
            font-weight: 600;
        }
        .forecast-section {
            background-color: #f5f5f5;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #00103f;
            margin-top: 1rem;
            font-size: 1rem;
            color: #333333;
            line-height: 1.4;
        }
        .analysis-section {
            background-color: #f5f5f5;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #0072CE;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.95rem;
            color: #333333;
            line-height: 1.4;
        }
        div.stTabs > div > div > div > div.stMarkdown {
            color: #00103f;
        }
        .trend-up {
            color: #00A651;
            font-weight: bold;
        }
        .trend-down {
            color: #ce3e0d;
            font-weight: bold;
        }
        .trend-stable {
            color: #333333;
            font-weight: bold;
        }
        .key-metrics {
            padding: 15px;
            background-color: white;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16);
        }
        .metric-grid {
            display: grid;
            grid-template-columns: 3fr 1fr 1fr 1fr 1fr;
            gap: 10px;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }
        .metric-grid-header {
            font-weight: bold;
            color: #00103f;
            border-bottom: 2px solid #00103f;
            padding-bottom: 15px;
            font-size: 1.1rem;
        }
        .indicator-title {
            font-weight: bold;
            margin-bottom: 5px;
            color: #00103f;
            font-size: 1.4rem;
            line-height: 1.3;
        }
        .indicator-description {
            font-size: 0.95rem;
            color: #333333;
            font-style: italic;
            margin-top: 5px;
            line-height: 1.4;
        }
        .stApp {
            background-color: #f5f5f5;
        }
        .impact-indicator {
            display: inline-block;
            width: 24px;
            height: 24px;
            line-height: 24px;
            text-align: center;
            border-radius: 50%;
            margin-left: 8px;
            font-weight: bold;
            font-size: 14px;
        }
        .impact-positive {
            background-color: #00A651;
            color: white;
        }
        .impact-negative {
            background-color: #ce3e0d;
            color: white;
        }
        .impact-neutral {
            background-color: #888888;
            color: white;
        }
        .last-updated-badge {
            background-color: #0072CE;
            color: white;
            font-size: 0.8rem;
            font-weight: normal;
            padding: 3px 8px;
            border-radius: 12px;
            margin-left: 10px;
            vertical-align: middle;
        }
        /* Fix Streamlit's default text colors for better contrast */
        .stMetric {
            color: #333333 !important;
        }
        .stMetric > div[data-testid="stMetricLabel"] {
            color: #333333 !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
        }
        .stMetric > div[data-testid="stMetricValue"] {
            color: #00103f !important;
            font-weight: 700 !important;
            font-size: 2.2rem !important;
        }
        .stMetric > div[data-testid="stMetricDelta"] {
            font-weight: 600 !important;
            font-size: 1rem !important;
        }
        .css-1vbkxwb p {
            color: #333333 !important;
            font-size: 1rem !important;
            line-height: 1.5 !important;
        }
        p {
            color: #333333 !important;
            font-size: 1rem !important;
            line-height: 1.5 !important;
        }
        h1, h2, h3, h4, h5 {
            color: #333333 !important;
            line-height: 1.3 !important;
        }
        /* Improved chart styling - more Fidelity-like */
        .js-plotly-plot .plotly .gtitle {
            fill: #333333 !important;
            font-size: 16px !important;
        }
        .js-plotly-plot .plotly .xtitle, 
        .js-plotly-plot .plotly .ytitle {
            fill: #333333 !important;
            font-size: 14px !important;
        }
        .js-plotly-plot .plotly .xtick text, 
        .js-plotly-plot .plotly .ytick text {
            fill: #333333 !important;
            font-size: 12px !important;
        }
        .js-plotly-plot .plotly .legend .legendtext {
            fill: #333333 !important;
            font-size: 12px !important;
        }
        /* Fix for any undefined text in charts */
        .js-plotly-plot .plotly .annotation-text {
            fill: #333333 !important;
            font-size: 12px !important;
        }
        .js-plotly-plot .plotly .annotation-arrow-g path {
            stroke: #333333 !important;
        }
        /* Download button styling */
        .download-button {
            background-color: #00103f;
            color: white !important;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            text-decoration: none;
            display: inline-block;
            font-weight: 600;
            margin: 0.5rem 0;
            text-align: center;
            border: none;
            cursor: pointer;
            font-size: 0.9rem;
            width: 100%;
        }
        .download-button:hover {
            background-color: #0d2d6d;
            text-decoration: none;
        }
        .download-button.disabled {
            background-color: #cccccc;
            color: #666666 !important;
            cursor: not-allowed;
        }
        /* Sidebar styling - white background with dark text */
        .css-1d391kg, .css-1lcbmhc, .css-hxt7ib, .css-1oe6wy4 {
            background-color: white !important;
        }
        .sidebar-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: #00103f !important;
        }
        .sidebar-text {
            font-size: 0.9rem;
            color: #333333 !important;
            margin-bottom: 0.5rem;
        }
        /* Make sure all sidebar text is visible with dark color */
        .css-1d391kg p, .css-1lcbmhc p, .css-hxt7ib p {
            color: #333333 !important;
        }
        .css-1d391kg label, .css-1lcbmhc label, .css-hxt7ib label {
            color: #333333 !important;
        }
        .css-1d391kg span, .css-1lcbmhc span, .css-hxt7ib span {
            color: #333333 !important;
        }
        .css-81oif8 {
            color: #333333 !important;
        }
        div[data-testid="stSidebarUserContent"] {
            background-color: white !important;
        }
        /* Data source styling */
        .data-source {
            font-size: 0.8rem;
            color: #666666 !important;
            font-style: italic;
            margin-top: 0.5rem;
        }
        /* Sample data warning */
        .sample-data-warning {
            background-color: #fff3cd;
            color: #856404 !important;
            padding: 0.5rem;
            border-radius: 4px;
            margin-top: 0.5rem;
            font-size: 0.85rem;
            border-left: 4px solid #ffeeba;
        }
        /* Rounded borders for cards like Fidelity */
        .card, .metric-container, .forecast-section, .analysis-section {
            border-radius: 8px;
            overflow: hidden;
        }
        /* Fix any white gaps or lines in the dashboard */
        .stMarkdown {
            margin-bottom: 0 !important;
        }
        .stMarkdown > div {
            margin-bottom: 0 !important;
        }
        
        /* NEW: Fix for header link containers specifically */
        .st-emotion-cache-ffhzg2 {
            display: none !important;
        }
        
        /* NEW: Additional fix for anchor containers */
        .st-emotion-cache-1inwz65 {
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
    </style>
    """