"""Card component for displaying indicators."""

import streamlit as st
import pandas as pd
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        
        # Monthly change
        with col2:
            if 'monthly_change' in latest_data and not pd.isna(latest_data['monthly_change']):
                change_text, change_style = format_change(
                    latest_data['monthly_change'], 
                    preferred_direction,
                    use_absolute=use_absolute
                )
                
                # Get impact indicator
                indicator_symbol, impact_class, _ = get_impact_indicator(
                    latest_data['monthly_change'],
                    preferred_direction,
                    use_absolute=use_absolute
                )
                
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <div style="font-size: 1rem; color: #333333; font-weight: 600;">Monthly</div>
                        <div style="font-size: 1.3rem;" class="{change_style}">{change_text}</div>
                        <div class="impact-indicator impact-{impact_class.split('-')[0]}" style="margin-top: 5px;">{indicator_symbol}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style="text-align: center;">
                        <div style="font-size: 1rem; color: #333333; font-weight: 600;">Monthly</div>
                        <div style="font-size: 1.3rem;">N/A</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Year-over-year change
        with col3:
            if 'yoy_change' in latest_data and not pd.isna(latest_data['yoy_change']):
                change_text, change_style = format_change(
                    latest_data['yoy_change'], 
                    preferred_direction,
                    use_absolute=use_absolute
                )
                
                # Get impact indicator
                indicator_symbol, impact_class, _ = get_impact_indicator(
                    latest_data['yoy_change'],
                    preferred_direction,
                    use_absolute=use_absolute
                )
                
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <div style="font-size: 1rem; color: #333333; font-weight: 600;">Year-over-Year</div>
                        <div style="font-size: 1.3rem;" class="{change_style}">{change_text}</div>
                        <div class="impact-indicator impact-{impact_class.split('-')[0]}" style="margin-top: 5px;">{indicator_symbol}</div>
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
        
        # Add forecast note if available and requested
        if show_forecast:
            from dashboard.utils.data_loader import load_forecast_data
            try:
                forecast_info = load_forecast_data(indicator_id)
                if forecast_info and isinstance(forecast_info, tuple) and len(forecast_info) > 0:
                    forecast_df = forecast_info[0]
                    if not forecast_df.empty and len(forecast_df) > 0:
                        last_forecast = forecast_df.iloc[-1]
                        forecast_change = last_forecast['value'] - latest_data['value']
                        
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
                        
                        # Determine forecast impact based on preferred direction
                        if preferred_direction == 'down':
                            forecast_impact = "negative" if forecast_change > 0 else "positive"
                        elif preferred_direction == 'up':
                            forecast_impact = "positive" if forecast_change > 0 else "negative"
                        else:
                            forecast_impact = "neutral"
                        
                        forecast_date = pd.to_datetime(last_forecast['Date']).strftime('%b %Y') if 'Date' in last_forecast else "future"
                        unit_prefix = "$" if latest_data.get('unit') == '$' else ""
                        
                        st.markdown(
                            f"""
                            <div class="forecast-section">
                            <strong>Forecast:</strong> {unit_prefix}{last_forecast['value']:.2f} by {forecast_date} 
                            <span class="{forecast_impact}-impact">({change_str} change, {forecast_impact} impact)</span>
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
        if using_sample_data:
            st.markdown('<p class="sample-data-warning">⚠️ Using sample data as actual data could not be loaded.</p>', 
                        unsafe_allow_html=True)
        
        # Add last updated badge
        last_updated = pd.to_datetime(latest_data['Date']).strftime('%b %d, %Y') if 'Date' in latest_data else "Unknown"
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

def get_impact_indicator(change, preferred_direction='neutral', use_absolute=False):
    """Return impact indicator (↑/↓) with styling classes."""
    if pd.isna(change):
        return "", "neutral-impact", "neutral"
    
    if preferred_direction == 'down':
        # For metrics where decrease is good (like supply chain pressure)
        impact = "positive" if change < 0 else "negative"
        indicator = "↓" if change < 0 else "↑"
    elif preferred_direction == 'up':
        # For metrics where increase is good
        impact = "positive" if change > 0 else "negative"
        indicator = "↑" if change > 0 else "↓"
    else:  # neutral
        # For metrics with no clear preference
        impact = "neutral"
        indicator = "↑" if change > 0 else "↓"
    
    style_class = f"{impact}-impact"
    return indicator, style_class, impact