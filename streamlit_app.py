#!/usr/bin/env python3
"""
Economic Indicators Dashboard - Streamlit Entry Point
This is the main entry point for Streamlit Cloud deployment.
"""

# Essential imports first
import os
import sys
import streamlit as st

# Set page configuration early to avoid warnings
st.set_page_config(
    page_title="Economic Indicators Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple logger fallback in case of import issues
class SimpleLogger:
    def info(self, msg): 
        print(f"INFO: {msg}")
    def error(self, msg): 
        print(f"ERROR: {msg}")
    def warning(self, msg): 
        print(f"WARNING: {msg}")

# Initialize logger with fallback
try:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized successfully")
except Exception as e:
    logger = SimpleLogger()
    st.sidebar.error(f"Logging initialization issue: {str(e)}")

# Try to import other required libraries
try:
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import plotly.graph_objects as go
    import plotly.express as px
    logger.info("Basic libraries imported successfully")
except Exception as e:
    st.error(f"Failed to import basic libraries: {str(e)}")
    logger.error(f"Import error for basic libraries: {str(e)}")
    st.stop()

# Add path handling
try:
    # Add current directory to path to ensure modules can be imported
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    logger.info(f"Added current directory to path: {current_dir}")
except Exception as e:
    st.warning(f"Path handling issue (non-critical): {str(e)}")

# Create necessary directory structure
try:
    # Ensure data directories exist
    data_dir = "data"  # Use relative path for better Cloud compatibility
    os.makedirs(data_dir, exist_ok=True)
    for subdir in ["raw", "processed", "forecasts"]:
        subdir_path = os.path.join(data_dir, subdir)
        os.makedirs(subdir_path, exist_ok=True)
        logger.info(f"Ensured directory exists: {subdir_path}")
except Exception as e:
    st.warning(f"Directory creation issue (non-critical): {str(e)}")

# Debug information
try:
    st.sidebar.markdown("### Debug Info")
    if st.sidebar.checkbox("Show debug info", False):
        st.sidebar.write(f"Python version: {sys.version}")
        st.sidebar.write(f"Current directory: {os.getcwd()}")
        st.sidebar.write(f"Directory contents: {os.listdir('.')}")
        if os.path.exists("data"):
            st.sidebar.write(f"Data directory contents: {os.listdir('data')}")
            for subdir in ["raw", "processed", "forecasts"]:
                path = os.path.join("data", subdir)
                if os.path.exists(path):
                    st.sidebar.write(f"{subdir} directory contents: {os.listdir(path)}")
except Exception as e:
    st.sidebar.warning(f"Debug info error (non-critical): {str(e)}")

# Title and introduction
st.markdown('<h1 style="color:#00103f; font-size:2.5rem; font-weight:700;">Economic Indicators Dashboard</h1>', unsafe_allow_html=True)

# Import dashboard components
try:
    from dashboard.utils.styling import get_css
    from dashboard.utils.data_loader import load_all_indicators, verify_data_availability
    from dashboard.utils.data_processor import filter_time_period, download_link
    from dashboard.components.indicator_card import create_indicator_card
    from dashboard.pages.correlation_page import show_correlation_page
    from dashboard.pages.cost_indicators_page import show_cost_indicators_page
    
    # Apply custom CSS
    st.markdown(get_css(), unsafe_allow_html=True)
    
    logger.info("Successfully imported all required modules")
except ImportError as e:
    st.error(f"Failed to import required modules: {str(e)}")
    logger.error(f"Import error: {str(e)}")
    
    # Show directory structure for debugging
    if os.path.exists("dashboard"):
        st.write("Dashboard directory found. Contents:")
        st.code("\n".join(os.listdir("dashboard")))
        for subdir in ["utils", "components", "pages"]:
            if os.path.exists(os.path.join("dashboard", subdir)):
                st.write(f"dashboard/{subdir} contents:")
                st.code("\n".join(os.listdir(os.path.join("dashboard", subdir))))
    else:
        st.error("Dashboard directory not found!")
        st.write(f"Available directories: {os.listdir('.')}")
    st.stop()

# Verify data availability before loading
try:
    data_available = verify_data_availability()
    if not data_available:
        st.warning("Some data directories were not found. Sample data will be used.")
except Exception as e:
    st.warning(f"Data verification error (non-critical): {str(e)}")

# Load data with caching
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
st.sidebar.markdown('<h2 style="color:#00103f; font-size:1.5rem; font-weight:600; margin-top:1.5rem;">Dashboard Settings</h2>', unsafe_allow_html=True)
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
st.sidebar.markdown('<h2 style="color:#00103f; font-size:1.5rem; font-weight:600; margin-top:1.5rem;">Download Data</h2>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="color:#333333; font-size:0.9rem;">Download the raw data for each indicator:</p>', unsafe_allow_html=True)

# Group indicators by category for better organization
standard_indicators = {k: v for k, v in all_indicators.items() if not any(x in k for x in ['equipment', 'steel', 'cement', 'explosives'])}
cost_indicators = {k: v for k, v in all_indicators.items() if k not in standard_indicators}

# Show standard indicators first
if standard_indicators:
    st.sidebar.markdown('<p style="color:#333333; font-size:0.9rem;"><strong>Standard Indicators:</strong></p>', unsafe_allow_html=True)
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
    st.sidebar.markdown('<p style="color:#333333; font-size:0.9rem;"><strong>Cost Indicators:</strong></p>', unsafe_allow_html=True)
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

# Function for automated commentary
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
    try:
        # -------------------- Key Economic Indicators --------------------
        st.markdown('<h3 style="color:#00103f; font-size:1.8rem; font-weight:600; margin-top:1.5rem;">Key Economic Indicators</h3>', unsafe_allow_html=True)
        
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
                        st.markdown(f'<div style="background-color:#f5f5f5; padding:1rem; border-radius:0.5rem; border-left:4px solid #0072CE; margin-top:0.5rem; font-size:0.95rem; color:#333333; line-height:1.4;">{commentary}</div>', unsafe_allow_html=True)
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
                        st.markdown(f'<div style="background-color:#f5f5f5; padding:1rem; border-radius:0.5rem; border-left:4px solid #0072CE; margin-top:0.5rem; font-size:0.95rem; color:#333333; line-height:1.4;">{commentary}</div>', unsafe_allow_html=True)
                else:
                    st.warning("NY Fed Empire Manufacturing Prices Paid data is not available")
        else:
            st.warning("No Key Economic Indicators data is available")

        # This is just a placeholder for additional sections
        st.info("Additional dashboard sections would appear here in the complete version.")
        
    except Exception as e:
        st.error(f"Error in Main Dashboard view: {str(e)}")
        logger.error(f"Main Dashboard error: {str(e)}")

elif selected_view == "Cost Indicators":
    try:
        # Show the cost indicators page
        show_cost_indicators_page()
    except Exception as e:
        st.error(f"Error in Cost Indicators view: {str(e)}")
        logger.error(f"Cost Indicators error: {str(e)}")

elif selected_view == "Correlation Analysis":
    try:
        # Show correlation analysis page
        show_correlation_page()
    except Exception as e:
        st.error(f"Error in Correlation Analysis view: {str(e)}")
        logger.error(f"Correlation Analysis error: {str(e)}")

# Print success message to log
logger.info("Dashboard rendered successfully")