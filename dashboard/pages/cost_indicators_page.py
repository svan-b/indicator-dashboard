"""Cost indicators page for the dashboard."""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from dashboard.utils.data_loader import load_all_indicators
from dashboard.utils.data_processor import filter_time_period, download_link, format_metric_value
from dashboard.components.indicator_card import create_indicator_card

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def show_cost_indicators_page():
    """Display cost indicators page."""
    # Load data
    try:
        all_indicators, forecasts, summary_data, corr_matrix = load_all_indicators()
        
        st.markdown('<h2 class="sub-header">Cost Indicators</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="cost-description">
        This page displays composite cost indicators for various equipment and materials. Each indicator is calculated 
        using a weighted combination of relevant Producer Price Indices (PPI) from the U.S. Bureau of Labor Statistics.
        These indicators help track cost trends for budgeting and forecasting purposes.
        </div>
        """, unsafe_allow_html=True)
        
        # Filter for cost indicators
        cost_indicators = {k: v for k, v in all_indicators.items() if k in [
            'komatsu_equipment', 'sms_equipment', 'caterpillar_equipment',
            'fabricated_steel', 'cement_ready_mix', 'explosives'
        ]}
        
        if not cost_indicators:
            st.warning("No cost indicator data found. Please ensure the data is properly loaded.")
            st.info("The system will try to generate sample data if real data isn't available.")
            # Try to generate sample data for cost indicators
            from dashboard.utils.data_loader import generate_sample_data
            for indicator_id in ['komatsu_equipment', 'sms_equipment', 'caterpillar_equipment',
                               'fabricated_steel', 'cement_ready_mix', 'explosives']:
                try:
                    df = generate_sample_data(indicator_id)
                    data_source = f"Sample data ({indicator_id})"
                    cost_indicators[indicator_id] = (df, data_source, True)
                except Exception as e:
                    logger.error(f"Error generating sample data for {indicator_id}: {e}")
        
        # Dashboard Settings from sidebar
        time_period = st.session_state.get('time_period', "Last 12 Months")
        forecast_toggle = st.session_state.get('forecast_toggle', True)
        
        # Summary of year-over-year adjustments
        st.markdown('<h3 class="section-header">Year-Over-Year Adjustments (Cost Escalation)</h3>', unsafe_allow_html=True)
        
        # Improved code for creating the yearly adjustments table
        yearly_data = []
        for indicator_id, indicator_info in cost_indicators.items():
            df = indicator_info[0]
            if not df.empty:
                try:
                    # Check if yearly_adjustment column exists AND is not all NaN
                    if 'yearly_adjustment' in df.columns and not pd.isna(df['yearly_adjustment']).all():
                        # Get the latest non-NaN yearly adjustment value
                        yearly_adj_series = df['yearly_adjustment'].dropna()
                        if not yearly_adj_series.empty:
                            yearly_adj = yearly_adj_series.iloc[-1]
                            indicator_name = df['source'].iloc[0].replace(" (Composite)", "").replace(" (SAMPLE DATA)", "").replace(" (Sample Data)", "")
                            
                            # Calculate effective period with plain ASCII hyphen instead of en-dash
                            latest_date = df['Date'].iloc[-1]
                            effective_start = pd.Timestamp(latest_date.year, 4, 1)  # April 1st of current year
                            effective_end = pd.Timestamp(latest_date.year + 1, 3, 31)  # March 31st of next year
                            
                            # Use plain ASCII hyphen instead of en-dash or other special characters
                            effective_date = f"{effective_start.strftime('%b %d, %Y')} - {effective_end.strftime('%b %d, %Y')}"
                            
                            yearly_data.append({
                                "Indicator": indicator_name,
                                "Adjustment": f"{'+' if yearly_adj > 0 else ''}{yearly_adj:.2f}%", 
                                "Effective Period": effective_date
                            })
                except Exception as e:
                    logger.error(f"Error processing yearly adjustment for {indicator_id}: {e}")
        
        if yearly_data:
            yearly_df = pd.DataFrame(yearly_data)
            
            # Apply styling to the dataframe
            if len(yearly_df) > 0:
                # Create a cleaner table with better formatting
                st.write("### Cost Adjustments Summary")
                
                # Use a plain HTML table for better control over formatting
                html_table = "<table style='width:100%; border-collapse:collapse; margin-bottom:20px;'>"
                html_table += "<thead><tr style='background-color:#f0f2f6;'>"
                html_table += "<th style='padding:8px; text-align:left; border-bottom:2px solid #ddd;'>Indicator</th>"
                html_table += "<th style='padding:8px; text-align:center; border-bottom:2px solid #ddd;'>Adjustment</th>"
                html_table += "<th style='padding:8px; text-align:left; border-bottom:2px solid #ddd;'>Effective Period</th>"
                html_table += "</tr></thead><tbody>"
                
                for _, row in yearly_df.iterrows():
                    html_table += "<tr style='border-bottom:1px solid #ddd;'>"
                    html_table += f"<td style='padding:8px; text-align:left;'>{row['Indicator']}</td>"
                    
                    # Color the adjustment based on value
                    adj_value = float(row['Adjustment'].replace('+', '').replace('%', ''))
                    if adj_value > 3.0:
                        color = "#ce3e0d"  # Red for high adjustments
                    elif adj_value < 0:
                        color = "#00A651"  # Green for negative adjustments
                    else:
                        color = "#333333"  # Default text color
                    
                    html_table += f"<td style='padding:8px; text-align:center; font-weight:bold; color:{color};'>{row['Adjustment']}</td>"
                    html_table += f"<td style='padding:8px; text-align:left;'>{row['Effective Period']}</td>"
                    html_table += "</tr>"
                
                html_table += "</tbody></table>"
                
                # Display the HTML table
                st.markdown(html_table, unsafe_allow_html=True)
                
                # Also continue to show the standard dataframe (as a backup and for download feature)
                with st.expander("View as dataframe"):
                    st.dataframe(
                        yearly_df,
                        column_config={
                            "Indicator": st.column_config.TextColumn("Indicator"),
                            "Adjustment": st.column_config.TextColumn("Adjustment"),
                            "Effective Period": st.column_config.TextColumn("Effective Period")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Add download link for adjustments
                st.markdown(
                    download_link(yearly_df, "cost_adjustments.csv", "Download Cost Adjustments Table"),
                    unsafe_allow_html=True
                )
            else:
                st.warning("No year-over-year adjustment data available")
        else:
            st.warning("No year-over-year adjustment data available")
        
        # Group indicators by category
        equipment_indicators = {k: v for k, v in cost_indicators.items() if 'equipment' in k}
        material_indicators = {k: v for k, v in cost_indicators.items() if k not in equipment_indicators}
        
        # Equipment Cost Indicators
        if equipment_indicators:
            st.markdown('<h3 class="section-header">Equipment Cost Indicators</h3>', unsafe_allow_html=True)
            
            # Create two columns per row
            cols = st.columns(2)
            
            # Display equipment indicators
            for i, (indicator_id, indicator_info) in enumerate(equipment_indicators.items()):
                with cols[i % 2]:
                    df = indicator_info[0]
                    # Filter by time period
                    filtered_df = filter_time_period(df, time_period)
                    # Create indicator card
                    create_indicator_card(indicator_id, (filtered_df, indicator_info[1], indicator_info[2]), forecast_toggle)
        
        # Material Cost Indicators
        if material_indicators:
            st.markdown('<h3 class="section-header">Material Cost Indicators</h3>', unsafe_allow_html=True)
            
            # Create two columns per row
            cols = st.columns(2)
            
            # Display material indicators
            for i, (indicator_id, indicator_info) in enumerate(material_indicators.items()):
                with cols[i % 2]:
                    df = indicator_info[0]
                    # Filter by time period
                    filtered_df = filter_time_period(df, time_period)
                    # Create indicator card
                    create_indicator_card(indicator_id, (filtered_df, indicator_info[1], indicator_info[2]), forecast_toggle)
        
        # Display methodology section
        st.markdown('<h3 class="section-header">Methodology</h3>', unsafe_allow_html=True)
        
        # Create tabs to show different methodologies
        methodology_tabs = st.tabs(["Overview", "Komatsu Heavy Equipment", "Other Equipment", "Materials"])
        
        with methodology_tabs[0]:
            st.markdown("""
            <div class="methodology-description">
            <p>These cost indicators are calculated using weighted combinations of Producer Price Indices (PPI) 
            from the U.S. Bureau of Labor Statistics. Each indicator is constructed from component indices 
            weighted according to their importance in the cost structure of the equipment or material.</p>
            
            <p><strong>Yearly Adjustment Calculation:</strong></p>
            <ul>
                <li>Based on weighted change of the component indices</li>
                <li>Comparing year-over-year data (typically January to December)</li>
                <li>Published as a percentage change applied for specified effective period</li>
            </ul>
            
            <p>These indicators are used for budgeting, forecasting, and contract escalation purposes.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with methodology_tabs[1]:
            st.markdown("""
            <div class="methodology-description">
            <p><strong>Komatsu Heavy Equipment Components and Weights:</strong></p>
            <ul>
                <li>PPI Labor/Compensation - 30% - CMU2010000000000D</li>
                <li>PPI Steel Mill Products - 35% - WPU1017</li>
                <li>PPI Industrial Commodities Less Fuel – 30% - WPU03T15M05</li>
                <li>PPI Fuel Products – 5% - WPU05</li>
            </ul>
            <p>2025 Komatsu Equip Indices: <strong>+2.95%</strong></p>
            <p>2025 Komatsu Equip Price: <strong>+2.95%</strong> (Effective Apr 1, 2025 – Mar 31, 2026)</p>
            <p>Source: <a href="https://data.bls.gov/cgi-bin/srgate" target="_blank">https://data.bls.gov/cgi-bin/srgate</a></p>
            </div>
            """, unsafe_allow_html=True)
            
        with methodology_tabs[2]:
            st.markdown("""
            <div class="methodology-description">
            <p><strong>SMS Equipment Components and Weights:</strong></p>
            <ul>
                <li>PPI Labor/Compensation - 35% - CMU2010000000000D</li>
                <li>PPI Steel Mill Products - 30% - WPU1017</li>
                <li>PPI Industrial Commodities Less Fuel – 25% - WPU03T15M05</li>
                <li>PPI Fuel Products – 10% - WPU05</li>
            </ul>
            
            <p><strong>Caterpillar Equipment Components and Weights:</strong></p>
            <ul>
                <li>PPI Labor/Compensation - 30% - CMU2010000000000D</li>
                <li>PPI Steel Mill Products - 30% - WPU1017</li>
                <li>PPI Mining Machinery - 30% - WPU1142</li>
                <li>PPI Fuel Products – 10% - WPU05</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with methodology_tabs[3]:
            st.markdown("""
            <div class="methodology-description">
            <p><strong>Fabricated Structural Steel Components and Weights:</strong></p>
            <ul>
                <li>PPI Labor/Compensation - 40% - CMU2010000000000D</li>
                <li>PPI Steel Mill Products - 50% - WPU1017</li>
                <li>PPI Fabricated Structural Metal - 10% - WPU107</li>
            </ul>
            
            <p><strong>Cement and Ready-Mix Components and Weights:</strong></p>
            <ul>
                <li>PPI Labor/Compensation - 35% - CMU2010000000000D</li>
                <li>PPI Cement - 45% - WPU1332</li>
                <li>PPI Concrete Products - 20% - WPU133</li>
            </ul>
            
            <p><strong>Explosives & Accessories Components and Weights:</strong></p>
            <ul>
                <li>PPI Labor/Compensation - 25% - CMU2010000000000D</li>
                <li>PPI Industrial Chemicals - 50% - WPU061</li>
                <li>PPI Mining Machinery - 25% - WPU1142</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Error in cost indicators page: {e}")
        st.error(f"Error loading cost indicators data: {e}")
        st.info("Please check that the data loader is properly returning cost indicator data.")

if __name__ == "__main__":
    show_cost_indicators_page()