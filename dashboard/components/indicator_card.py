"""Card component for displaying indicators."""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_valid_update_date(date_value):
    """Ensure the last updated date is not in the future."""
    try:
        # Convert to datetime if it's not already
        if not isinstance(date_value, datetime):
            date_value = pd.to_datetime(date_value)
        
        # Check if date is in the future
        now = datetime.now()
        if date_value > now:
            # Return current date if future date detected
            logger.warning(f"Future date detected: {date_value}. Using current date instead.")
            return now.strftime('%b %d, %Y')
        
        return date_value.strftime('%b %d, %Y')
    except Exception as e:
        logger.error(f"Error formatting date: {e}")
        return "Unknown"

def create_indicator_card(indicator_id, indicator_info, show_forecast=True, use_absolute=False):
    """Create a standardized card for displaying an economic indicator with improved error handling."""
    if indicator_info is None:
        st.warning(f"No data available for {indicator_id}")
        return
    
    try:
        # Extract components from indicator_info tuple
        if len(indicator_info) >= 3:
            df, data_source, using_sample_data = indicator_info
        else:
            logger.error(f"Invalid indicator_info format for {indicator_id}")
            st.warning(f"Invalid data format for {indicator_id}")
            return
        
        if df is None or df.empty or 'value' not in df.columns:
            st.warning(f"No data available for {indicator_id}")
            return
        
        # Start the card container
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Get indicator name from source with fallback
        indicator_name = df['source'].iloc[0] if 'source' in df.columns else indicator_id.replace('_', ' ').title()
        st.markdown(f'<p class="indicator-title">{indicator_name}</p>', unsafe_allow_html=True)
        
        # Most recent data
        latest_data = df.iloc[-1].copy()
        preferred_direction = latest_data.get('preferred_direction', 'neutral')
        
        # Create columns for metrics
        col1, col2, col3 = st.columns([1.5, 1, 1])
        
        # Current value
        with col1:
            unit = latest_data.get('unit', '')
            value_display = format_metric_value(latest_data['value'], unit)
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="font-size: 1rem; color: #333333; font-weight: 600;">Current Value</div>
                    <div style="font-size: 1.8rem; color: #00103f; font-weight: 700;">{value_display}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Monthly change - UPDATED with better labels and explanations
        with col2:
            if 'monthly_change' in latest_data and not pd.isna(latest_data['monthly_change']):
                change_text, change_style = format_change(
                    latest_data['monthly_change'], 
                    preferred_direction,
                    use_absolute=use_absolute
                )
                
                # Get impact indicator with the indicator_id passed for better context
                indicator_symbol, impact_class, impact_type = get_impact_indicator(
                    latest_data['monthly_change'],
                    preferred_direction,
                    use_absolute=use_absolute,
                    indicator_id=indicator_id
                )
                
                # Add explanation of direction
                direction_explanation = "(better)" if impact_type == "positive" else "(worse)" if impact_type == "negative" else ""
                
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <div style="font-size: 1rem; color: #333333; font-weight: 600;">Month-over-Month</div>
                        <div style="font-size: 1.3rem;" class="{change_style}">{change_text}</div>
                        <div class="impact-indicator impact-{impact_class.split('-')[0]}" style="margin-top: 5px;">{indicator_symbol}</div>
                        <div style="font-size: 0.8rem; margin-top: 3px;">{direction_explanation}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="text-align: center;">
                        <div style="font-size: 1rem; color: #333333; font-weight: 600;">Month-over-Month</div>
                        <div style="font-size: 1.3rem;">N/A</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Year-over-year change - UPDATED with better labels and explanations
        with col3:
            if 'yoy_change' in latest_data and not pd.isna(latest_data['yoy_change']):
                change_text, change_style = format_change(
                    latest_data['yoy_change'], 
                    preferred_direction,
                    use_absolute=use_absolute
                )
                
                # Get impact indicator with the indicator_id passed for better context
                indicator_symbol, impact_class, impact_type = get_impact_indicator(
                    latest_data['yoy_change'],
                    preferred_direction,
                    use_absolute=use_absolute,
                    indicator_id=indicator_id
                )
                
                # Add explanation of direction
                direction_explanation = "(better)" if impact_type == "positive" else "(worse)" if impact_type == "negative" else ""
                
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <div style="font-size: 1rem; color: #333333; font-weight: 600;">Year-over-Year</div>
                        <div style="font-size: 1.3rem;" class="{change_style}">{change_text}</div>
                        <div class="impact-indicator impact-{impact_class.split('-')[0]}" style="margin-top: 5px;">{indicator_symbol}</div>
                        <div style="font-size: 0.8rem; margin-top: 3px;">{direction_explanation}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="text-align: center;">
                        <div style="font-size: 1rem; color: #333333; font-weight: 600;">Year-over-Year</div>
                        <div style="font-size: 1.3rem;">N/A</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Create chart with improved metadata handling
        from dashboard.components.charts import create_indicator_chart
        try:
            fig = create_indicator_chart(
                df, 
                None, 
                indicator_id=indicator_id, 
                unit=latest_data.get('unit', ''),
                preferred_direction=preferred_direction
            )
            
            # If forecasts are available and requested, add them to the chart
            if show_forecast:
                from dashboard.utils.data_loader import load_forecast_data
                forecast_info = load_forecast_data(indicator_id)
                if forecast_info and isinstance(forecast_info, tuple) and len(forecast_info) > 0:
                    forecast_df = forecast_info[0]
                    if not forecast_df.empty:
                        fig = create_indicator_chart(
                            df, 
                            forecast_df, 
                            show_forecast=True,
                            indicator_id=indicator_id, 
                            unit=latest_data.get('unit', ''),
                            preferred_direction=preferred_direction
                        )
            
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Unable to generate chart for this indicator")
        except Exception as e:
            logger.error(f"Error creating chart for {indicator_id}: {e}")
            st.warning("Error generating chart for this indicator")
        
        # Add forecast note if available and requested - COMPLETELY REVISED SECTION
        if show_forecast:
            from dashboard.utils.data_loader import load_forecast_data
            try:
                forecast_info = load_forecast_data(indicator_id)
                if forecast_info and isinstance(forecast_info, tuple) and len(forecast_info) > 0:
                    forecast_df = forecast_info[0]
                    if not forecast_df.empty and len(forecast_df) > 0:
                        last_forecast = forecast_df.iloc[-1]
                        forecast_change = last_forecast['value'] - latest_data['value']
                        forecast_date = pd.to_datetime(last_forecast['Date']).strftime('%b %Y') if 'Date' in last_forecast else "future"
                        
                        # Determine if we should show absolute or percentage change
                        if use_absolute:
                            change_value = forecast_change
                            change_str = f"{'+' if forecast_change > 0 else ''}{forecast_change:.2f}"
                        else:
                            # Use percentage for forecast change
                            if latest_data['value'] != 0:
                                change_value = (forecast_change / latest_data['value']) * 100
                                change_str = f"{'+' if change_value > 0 else ''}{change_value:.2f}%"
                            else:
                                change_value = 0
                                change_str = "0.00%"
                        
                        # Determine forecast impact based on preferred direction or indicator-specific logic
                        impact_type = get_impact_indicator(
                            forecast_change,
                            preferred_direction,
                            use_absolute=use_absolute,
                            indicator_id=indicator_id
                        )[2]  # Get just the impact type
                        
                        forecast_impact = impact_type
                        impact_description = "positive impact (better)" if impact_type == "positive" else "negative impact (worse)" if impact_type == "negative" else "neutral impact"
                        
                        unit_prefix = "$" if latest_data.get('unit') == '$' else ""
                        
                        # Traffic light indicator based on impact
                        traffic_light_class = "red" if forecast_impact == "negative" else "green" if forecast_impact == "positive" else "yellow"
                        
                        # Improved forecast section with better explanation
                        st.markdown(
                            f"""
                            <div class="forecast-section">
                                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                    <div class="impact-traffic-light impact-{traffic_light_class}"></div>
                                    <strong>Forecast:</strong> {unit_prefix}{last_forecast['value']:.2f} by {forecast_date}
                                </div>
                                <span class="{forecast_impact}-impact">
                                    {change_str} change from current value ({impact_description})
                                </span><br/>
                                <span style="font-size: 0.85rem; font-style: italic; margin-top: 5px; display: block;">
                                    This forecast shows the predicted future value compared to today's value of {unit_prefix}{latest_data['value']:.2f}.
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            except Exception as e:
                logger.error(f"Error displaying forecast note for {indicator_id}: {e}")
        
        # Add description if available
        if 'description' in latest_data and latest_data['description']:
            st.markdown(f"<p class='indicator-description'>{latest_data['description']}</p>", 
                        unsafe_allow_html=True)
        
        # Add sample data warning if applicable
        is_sample = using_sample_data or 'sample' in data_source.lower() or 'SAMPLE' in data_source
        if 'source' in df.columns:
            if any(df['source'].str.contains('sample', case=False)) or any(df['source'].str.contains('SAMPLE')):
                is_sample = True

        if is_sample:
            st.markdown('<div class="sample-data-warning"><strong>⚠️ SAMPLE DATA:</strong> Displaying generated sample data as actual data could not be loaded.</div>',
                        unsafe_allow_html=True)
        
        # Add last updated badge
        if 'Date' in latest_data:
            last_updated = get_valid_update_date(latest_data['Date'])
        else:
            last_updated = "Unknown"
        st.markdown(f"<p>Last updated: <span class='last-updated-badge'>{last_updated}</span></p>", unsafe_allow_html=True)
        
        # Close the card container
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Error rendering indicator card for {indicator_id}: {e}")
        st.warning(f"Error displaying indicator card for {indicator_id}")

def format_metric_value(value, unit=''):
    """Format metric value with appropriate unit."""
    if pd.isna(value):
        return "N/A"
    
    if unit == '$':
        return f"${value:.2f}"
    elif unit == '%':
        return f"{value:.2f}%"
    else:
        return f"{value:.2f}"

def format_change(change, preferred_direction='neutral', use_absolute=False):
    """Format change value with appropriate color and sign."""
    if pd.isna(change):
        return "N/A", "neutral-change"
    
    # For certain metrics like supply chain index, use absolute change
    if use_absolute:
        sign = "+" if change > 0 else ""
        if preferred_direction == 'down':
            style = "negative-change" if change > 0 else "positive-change"
        elif preferred_direction == 'up':
            style = "positive-change" if change > 0 else "negative-change"
        else:  # neutral
            style = "neutral-change"
        
        return f"{sign}{change:.2f}", style
    else:
        # Use percentage for other metrics
        sign = "+" if change > 0 else ""
        if preferred_direction == 'down':
            style = "negative-change" if change > 0 else "positive-change"
        elif preferred_direction == 'up':
            style = "positive-change" if change > 0 else "negative-change"
        else:  # neutral
            style = "neutral-change"
        
        return f"{sign}{change:.2f}%", style

def get_impact_indicator(change, preferred_direction='neutral', use_absolute=False, indicator_id=None):
    """Return impact indicator (↑/↓) with styling classes, properly accounting for business impact."""
    if pd.isna(change):
        return "", "neutral-impact", "neutral"
    
    # Set significance thresholds - these determine when a change is significant enough to have an impact
    significance_threshold = 2.0  # Default for percentage changes
    
    if use_absolute:
        significance_threshold = 0.1  # Different threshold for absolute changes (like supply chain index)
    
    # Check if the change is significant
    is_significant = abs(change) > significance_threshold
    
    # Handle special cases for specific indicators
    if indicator_id:
        # For commodity prices like oil, significant decreases are positive for most businesses (reduced costs)
        if indicator_id in ['wti_oil', 'ppi_steel_scrap']:
            preferred_direction = 'down'
        
        # For dollar index, weaker dollar (going down) tends to help US exporters
        elif indicator_id == 'dollar_index':
            preferred_direction = 'down'
        
        # For Baltic Dry Index, changes indicate shipping cost changes, lower is generally better
        elif indicator_id == 'baltic_dry_index':
            preferred_direction = 'down'
    
    if preferred_direction == 'down':
        # For metrics where decrease is good (like supply chain pressure, costs)
        impact = "positive" if change < 0 else ("negative" if is_significant else "neutral")
        indicator = "↓" if change < 0 else "↑"
    elif preferred_direction == 'up':
        # For metrics where increase is good
        impact = "positive" if change > 0 else ("negative" if is_significant else "neutral")
        indicator = "↑" if change > 0 else "↓"
    else:  # neutral
        # Even for neutral preference indicators, significant movements should have impact
        if is_significant:
            # Default to cost perspective - increases in most indicators imply higher costs
            impact = "negative" if change > 0 else "positive"
        else:
            impact = "neutral"
        indicator = "↑" if change > 0 else "↓"
    
    style_class = f"{impact}-impact"
    return indicator, style_class, impact

def highlight_latest_value(df, chart_container):
    """Highlight the latest value in the chart."""
    if not df.empty and 'Date' in df.columns and 'value' in df.columns:
        latest_date = df['Date'].max()
        latest_value = df.loc[df['Date'] == latest_date, 'value'].iloc[0]
        unit = df['unit'].iloc[0] if 'unit' in df.columns else ''
        
        formatted_value = latest_value
        if unit == '$':
            formatted_value = f"${latest_value:.2f}"
        else:
            formatted_value = f"{latest_value:.2f}"
        
        chart_container.markdown(f"""
        <div style="position: absolute; top: 10px; right: 20px; background-color: rgba(255,255,255,0.8); 
                    padding: 5px 10px; border-radius: 5px; border: 1px solid #ddd; z-index: 1000;">
            <span style="font-weight: bold;">Latest: {formatted_value}</span>
            <br><span style="font-size: 0.8rem;">({latest_date.strftime('%b %d, %Y')})</span>
        </div>
        """, unsafe_allow_html=True)