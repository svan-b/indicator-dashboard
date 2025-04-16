#!/usr/bin/env python3
"""
Economic Indicators Dashboard - Streamlit Entry Point
This is the main entry point for Streamlit Cloud deployment.
"""

import os
import sys
import logging
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Debug information
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")
logger.info(f"Python path: {sys.path}")

# Add current directory to path to ensure modules can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Create necessary directory structure
data_dir = os.path.join(current_dir, "data")
os.makedirs(data_dir, exist_ok=True)
for subdir in ["raw", "processed", "forecasts"]:
    os.makedirs(os.path.join(data_dir, subdir), exist_ok=True)

# Set page configuration
st.set_page_config(
    page_title="Economic Indicators Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import dashboard components - wrap in try/except for debugging
try:
    from dashboard.utils.styling import get_css
    from dashboard.utils.data_loader import load_all_indicators
    from dashboard.utils.data_processor import filter_time_period, download_link
    from dashboard.components.indicator_card import create_indicator_card
    from dashboard.pages.correlation_page import show_correlation_page
    from dashboard.pages.cost_indicators_page import show_cost_indicators_page
    
    logger.info("Successfully imported all required modules")
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    logger.error(f"Import error: {e}")
    # Show directory structure for debugging
    if os.path.exists("dashboard"):
        st.write("Dashboard directory found. Contents:")
        st.code("\n".join(os.listdir("dashboard")))
    else:
        st.error("Dashboard directory not found!")
        st.write(f"Available directories: {os.listdir('.')}")
    st.stop()

# Apply custom CSS
st.markdown(get_css(), unsafe_allow_html=True)

# Title and introduction
st.markdown('<h1 class="main-header">Economic Indicators Dashboard</h1>', unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=3600)
def load_data():
    logger.info("Loading indicator data...")
    try:
        all_indicators, forecasts, summary_data, corr_matrix = load_all_indicators()
        logger.info(f"Loaded {len(all_indicators)} indicators and {len(forecasts)} forecasts")
        return all_indicators, forecasts, summary_data, corr_matrix
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        st.error(f"Error loading data: {e}")
        return {}, {}, {}, None

all_indicators, forecasts, summary_data, corr_matrix = load_data()

# Dashboard Settings Sidebar
st.sidebar.markdown('<h2 class="sidebar-title">Dashboard Settings</h2>', unsafe_allow_html=True)
time_period = st.sidebar.selectbox(
    "Select Time Period",
    ["Last 6 Months", "Last 12 Months", "Last 24 Months", "All Available Data"],
    index=1
)
forecast_toggle = st.sidebar.checkbox("Show Forecasts", value=True)

# Store settings in session state
st.session_state['time_period'] = time_period
st.session_state['forecast_toggle'] = forecast_toggle

# Add sidebar for data downloads
st.sidebar.markdown('<h2 class="sidebar-title">Download Data</h2>', unsafe_allow_html=True)
st.sidebar.markdown('<p class="sidebar-text">Download the raw data for each indicator:</p>', unsafe_allow_html=True)

# Group indicators by category for better organization
standard_indicators = {k: v for k, v in all_indicators.items() if not any(x in k for x in ['equipment', 'steel', 'cement', 'explosives'])}
cost_indicators = {k: v for k, v in all_indicators.items() if k not in standard_indicators}

# Show standard indicators first
if standard_indicators:
    st.sidebar.markdown('<p class="sidebar-text"><strong>Standard Indicators:</strong></p>', unsafe_allow_html=True)
    for indicator_id, df_info in standard_indicators.items():
        df = df_info[0]
        if not df.empty:
            source_name = df['source'].iloc[0] if 'source' in df.columns else indicator_id.replace('_', ' ').title()
            st.sidebar.markdown(
                download_link(df, f"{indicator_id}.csv", f"{source_name}"),
                unsafe_allow_html=True
            )

# Then show cost indicators
if cost_indicators:
    st.sidebar.markdown('<p class="sidebar-text"><strong>Cost Indicators:</strong></p>', unsafe_allow_html=True)
    for indicator_id, df_info in cost_indicators.items():
        df = df_info[0]
        if not df.empty:
            source_name = df['source'].iloc[0] if 'source' in df.columns else indicator_id.replace('_', ' ').title()
            st.sidebar.markdown(
                download_link(df, f"{indicator_id}.csv", f"{source_name}"),
                unsafe_allow_html=True
            )

# Add dashboard selection
view_options = ["Main Dashboard", "Cost Indicators", "Correlation Analysis"]
selected_view = st.sidebar.radio("Select View", view_options)

# The rest of your main.py code here...
# I'm including the function for automated commentary since it's referenced below
def generate_automated_commentary(indicator_id, latest_value, monthly_change, yoy_change, forecast_change=None, preferred_direction='neutral'):
    """Generate automated commentary based on indicator metrics"""
    
    commentary = ""
    
    if indicator_id == 'supply_chain':
        if latest_value > 0:
            level_desc = f"The current value of {latest_value:.2f} indicates above-average supply chain pressure."
        else:
            level_desc = f"The current value of {latest_value:.2f} indicates below-average supply chain pressure."
            
        if monthly_change < -0.2:
            monthly_desc = f"Supply chain pressure has notably decreased by {abs(monthly_change):.2f} points over the last month, a positive development."
        elif monthly_change < 0:
            monthly_desc = f"Supply chain pressure has slightly decreased by {abs(monthly_change):.2f} points over the last month."
        elif monthly_change < 0.2:
            monthly_desc = f"Supply chain pressure has remained relatively stable with a small increase of {monthly_change:.2f} points over the last month."
        else:
            monthly_desc = f"Supply chain pressure has increased by {monthly_change:.2f} points over the last month, indicating worsening conditions."
            
        if forecast_change:
            if forecast_change < 0:
                forecast_desc = f"The forecast indicates improving conditions with a projected {abs(forecast_change):.2f} point decrease in pressure over the next few months."
            else:
                forecast_desc = f"The forecast suggests continued challenges with a projected {forecast_change:.2f} point increase in pressure over the next few months."
        else:
            forecast_desc = ""
            
        commentary = f"{level_desc} {monthly_desc} {forecast_desc}"
        
    elif indicator_id == 'empire_prices_paid':
        if latest_value > 50:
            level_desc = f"The current Empire Manufacturing Prices Paid index of {latest_value:.2f} indicates increasing input prices for manufacturers in New York state."
        else:
            level_desc = f"The current Empire Manufacturing Prices Paid index of {latest_value:.2f} indicates decreasing input prices for manufacturers in New York state."
            
        if monthly_change < -1:
            monthly_desc = f"The index has decreased by {abs(monthly_change):.2f}% month-over-month, suggesting easing price pressures."
        elif monthly_change < 1:
            monthly_desc = f"The index has remained relatively stable month-over-month ({monthly_change:.2f}%)."
        else:
            monthly_desc = f"The index has increased by {monthly_change:.2f}% month-over-month, suggesting growing price pressures."
            
        if yoy_change and not pd.isna(yoy_change):
            if yoy_change < -5:
                yoy_desc = f"Year-over-year, prices paid have decreased significantly ({yoy_change:.2f}%), indicating substantial relief in input costs."
            elif yoy_change < 0:
                yoy_desc = f"Year-over-year, prices paid have moderated ({yoy_change:.2f}%)."
            elif yoy_change < 5:
                yoy_desc = f"Year-over-year, prices paid have increased moderately ({yoy_change:.2f}%)."
            else:
                yoy_desc = f"Year-over-year, prices paid have increased significantly ({yoy_change:.2f}%), indicating persistent inflation in input costs."
        else:
            yoy_desc = ""
            
        commentary = f"{level_desc} {monthly_desc} {yoy_desc}"
    
    return commentary

# Main Content based on selected view
if selected_view == "Main Dashboard":
    # -------------------- Key Economic Indicators --------------------
    st.markdown('<h3 class="section-header">Key Economic Indicators</h3>', unsafe_allow_html=True)
    
    # Check if we have both indicators with data before creating columns
    supply_chain_info = all_indicators.get('supply_chain')
    empire_info = all_indicators.get('empire_prices_paid')
    
    supply_chain_has_data = False
    empire_has_data = False
    
    if supply_chain_info:
        supply_chain_data = filter_time_period(supply_chain_info[0], time_period)
        supply_chain_has_data = not supply_chain_data.empty
    
    if empire_info:
        empire_data = filter_time_period(empire_info[0], time_period)
        empire_has_data = not empire_data.empty
    
    # Only create columns if at least one indicator has data
    if supply_chain_has_data or empire_has_data:
        col1, col2 = st.columns(2)
        
        # Supply Chain Pressure Index
        with col1:
            if supply_chain_has_data:
                create_indicator_card('supply_chain', (supply_chain_data, supply_chain_info[1], supply_chain_info[2]), forecast_toggle, use_absolute=True)
                
                # Add automated commentary
                latest_data = supply_chain_data.iloc[-1]
                forecast_change = None
                if forecast_toggle and 'supply_chain' in forecasts:
                    forecast_df = forecasts['supply_chain'][0]
                    if not forecast_df.empty and len(forecast_df) > 0:
                        last_forecast = forecast_df.iloc[-1]
                        forecast_change = last_forecast['value'] - latest_data['value']
                
                commentary = generate_automated_commentary(
                    'supply_chain', 
                    latest_data['value'], 
                    latest_data.get('monthly_change', 0),
                    latest_data.get('yoy_change', 0),
                    forecast_change,
                    latest_data.get('preferred_direction', 'down')
                )
                
                if commentary:
                    st.markdown(f'<div class="analysis-section">{commentary}</div>', unsafe_allow_html=True)
            else:
                st.warning("Supply Chain Pressure Index data is not available")
        
        # Empire Manufacturing Prices Paid
        with col2:
            if empire_has_data:
                create_indicator_card('empire_prices_paid', (empire_data, empire_info[1], empire_info[2]), forecast_toggle)
                
                # Add automated commentary
                latest_data = empire_data.iloc[-1]
                forecast_change = None
                if forecast_toggle and 'empire_prices_paid' in forecasts:
                    forecast_df = forecasts['empire_prices_paid'][0]
                    if not forecast_df.empty and len(forecast_df) > 0:
                        last_forecast = forecast_df.iloc[-1]
                        forecast_change = last_forecast['value'] - latest_data['value']
                        if latest_data['value'] != 0:
                            forecast_change = (forecast_change / latest_data['value']) * 100
                
                commentary = generate_automated_commentary(
                    'empire_prices_paid', 
                    latest_data['value'], 
                    latest_data.get('monthly_change', 0),
                    latest_data.get('yoy_change', None),
                    forecast_change,
                    latest_data.get('preferred_direction', 'down')
                )
                
                if commentary:
                    st.markdown(f'<div class="analysis-section">{commentary}</div>', unsafe_allow_html=True)
            else:
                st.warning("NY Fed Empire Manufacturing Prices Paid data is not available")
    else:
        st.warning("No Key Economic Indicators data is available")

    # For brevity, I'm not including all of the main.py code here, but in your actual file
    # you would include all the code for displaying the other sections
    
    # Display the remaining dashboard sections:
    # - Key Price Indicators
    # - Raw Material & Input Costs
    # - Supply Chain Related Indicators
    # - Data Sources & Methodology
    
    # This is just a placeholder for those sections
    st.info("The full dashboard would show additional sections here.")

elif selected_view == "Cost Indicators":
    # Show the cost indicators page
    show_cost_indicators_page()

elif selected_view == "Correlation Analysis":
    # Show correlation analysis page
    show_correlation_page()

# Print success message to log
logger.info("Dashboard rendered successfully")