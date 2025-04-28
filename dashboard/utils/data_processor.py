"""Data processing utilities."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import base64
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def filter_time_period(df, time_period):
    """Filter dataframe based on selected time period with improved handling of recent data."""
    if df is None or df.empty or 'Date' not in df.columns:
        return df
    
    # Create a copy to avoid modifying the original
    filtered_df = df.copy()
    
    # Ensure we are getting the absolute latest data by setting end_date to the max of the dataframe
    # This avoids any filtering issue that might exclude the most recent data point
    end_date = filtered_df['Date'].max()
    
    # Add explicit debugging for the latest date
    latest_date = filtered_df['Date'].max()
    logger.info(f"Latest date in original data: {latest_date}")
    
    if time_period == "Last 6 Months":
        # Make sure to use the latest date minus 6 months, not today - 6 months
        start_date = end_date - pd.DateOffset(months=6)
    elif time_period == "Last 12 Months":
        start_date = end_date - pd.DateOffset(months=12)
    elif time_period == "Last 24 Months":
        start_date = end_date - pd.DateOffset(months=24)
    else:
        start_date = filtered_df['Date'].min()
    
    # Explicitly include the end_date to ensure the most recent data is included
    # Use inclusive bounds on both sides to avoid any filtering errors
    result_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]
    
    # Double-check that the latest date is included by logging it
    if not result_df.empty:
        result_latest = result_df['Date'].max()
        logger.info(f"Latest date in filtered data for time period {time_period}: {result_latest}")
        # If we lost the latest date, add it back
        if result_latest != latest_date:
            logger.warning(f"Latest date was filtered out! Adding it back manually.")
            latest_row = filtered_df[filtered_df['Date'] == latest_date]
            result_df = pd.concat([result_df, latest_row]).drop_duplicates()
    
    return result_df

def download_link(df, filename, link_text):
    """Generate a link to download the dataframe as a CSV file."""
    if df is None or df.empty:
        return f'<a href="#" class="download-button disabled">{link_text} (No data)</a>'
    
    try:
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-button">{link_text}</a>'
        return href
    except Exception as e:
        logger.error(f"Error creating download link: {e}")
        return f'<a href="#" class="download-button disabled">{link_text} (Error)</a>'

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

def get_trend_indicator(last_values, forecast_values=None):
    """Determine trend direction based on recent values and forecast."""
    if last_values is None or len(last_values) < 2:
        return "→ Stable", "trend-stable"
    
    # Calculate recent trend as percentage change
    recent_trend = 0
    try:
        recent_trend = last_values.pct_change().mean() * 100
    except Exception as e:
        logger.error(f"Error calculating recent trend: {e}")
    
    forecast_trend = 0
    if forecast_values is not None and len(forecast_values) >= 2:
        try:
            forecast_trend = (forecast_values.iloc[-1] - forecast_values.iloc[0]) / forecast_values.iloc[0] * 100
        except Exception as e:
            logger.error(f"Error calculating forecast trend: {e}")
    
    combined_trend = (recent_trend + forecast_trend) / 2 if forecast_values is not None else recent_trend
    
    if combined_trend > 0.7:
        return "↑ Increasing", "trend-up"
    elif combined_trend < -0.7:
        return "↓ Decreasing", "trend-down"
    else:
        return "→ Stable", "trend-stable"