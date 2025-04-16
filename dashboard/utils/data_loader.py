"""Data loading utilities."""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base data directory - improved path resolution
def get_data_dir():
    """Get data directory with more robust path handling for Streamlit Cloud."""
    
    # Streamlit Cloud prioritization - look for data directory in repo root
    if os.path.exists("data"):
        logger.info("Using data directory at project root (Streamlit Cloud compatible)")
        return "data"
    
    # For local development
    potential_paths = [
        os.path.join(os.getcwd(), "data"),
        os.path.join(os.path.dirname(os.getcwd()), "data"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
        os.path.join(os.path.expanduser("~"), "Commercial and Market Research", "indicator_data"),
        r"C:\Users\vanbo\Commercial and Market Research\indicator_data",
    ]
    
    for path in potential_paths:
        if os.path.exists(path):
            logger.info(f"Found data directory at: {path}")
            return path
    
    # If no existing path found, create and use the repo-root path
    default_path = "data"
    logger.info(f"No existing data directory found. Creating at: {default_path}")
    os.makedirs(default_path, exist_ok=True)
    return default_path

def verify_data_availability():
    """Verify data files exist and log their status."""
    data_dir = get_data_dir()
    
    directories = {
        "raw": os.path.join(data_dir, "raw"),
        "processed": os.path.join(data_dir, "processed"),
        "forecasts": os.path.join(data_dir, "forecasts")
    }
    
    for dir_name, dir_path in directories.items():
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            logger.info(f"Found {len(files)} files in {dir_name} directory")
            if len(files) > 0:
                logger.info(f"Sample files: {', '.join(files[:5])}")
            if not files:
                logger.warning(f"No files found in {dir_name} directory")
        else:
            logger.error(f"Directory not found: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created empty directory: {dir_path}")
    
    return all(os.path.exists(dir_path) for dir_path in directories.values())

# Get base data directory
BASE_DATA_DIR = get_data_dir()

# Set up subdirectories
RAW_DIR = os.path.join(BASE_DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(BASE_DATA_DIR, "processed")
FORECASTS_DIR = os.path.join(BASE_DATA_DIR, "forecasts")

# Ensure directories exist
for directory in [RAW_DIR, PROCESSED_DIR, FORECASTS_DIR]:
    os.makedirs(directory, exist_ok=True)

def load_indicator_data(indicator_id):
    """Load indicator data from files or generate sample data if not available."""
    logger.info(f"Loading data for indicator: {indicator_id}")
    
    data_source = ""
    using_sample_data = False
    
    # Try multiple possible file names and paths
    possible_files = [
        os.path.join(PROCESSED_DIR, f"{indicator_id}_monthly.csv"),
        os.path.join(PROCESSED_DIR, f"{indicator_id}.csv"),
        os.path.join(RAW_DIR, f"{indicator_id}.csv"),
        os.path.join(RAW_DIR, f"{indicator_id}_sample.csv"),
        os.path.join(BASE_DATA_DIR, f"{indicator_id}.csv")
    ]
    
    for file_path in possible_files:
        if os.path.exists(file_path):
            try:
                logger.info(f"Loading data from: {file_path}")
                df = pd.read_csv(file_path)
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Important: Do NOT filter out future dates
                # current_date = datetime.now()
                # df = df[df['Date'] <= current_date]
                
                # Add missing columns if needed
                if 'monthly_change' not in df.columns and 'value' in df.columns and len(df) > 1:
                    df['monthly_change'] = df['value'].pct_change() * 100
                if 'yoy_change' not in df.columns and 'value' in df.columns and len(df) >= 12:
                    df['yoy_change'] = df['value'].pct_change(12) * 100
                if 'source' not in df.columns:
                    df['source'] = get_default_source_name(indicator_id)
                if 'unit' not in df.columns:
                    df['unit'] = get_default_unit(indicator_id)
                if 'preferred_direction' not in df.columns:
                    df['preferred_direction'] = get_default_preferred_direction(indicator_id)
                if 'description' not in df.columns:
                    df['description'] = get_default_description(indicator_id)
                if 'last_updated_date' not in df.columns:
                    df['last_updated_date'] = df['Date'].max().strftime("%b-%y")
                
                data_source = f"Data from file: {os.path.basename(file_path)}"
                logger.info(f"Successfully loaded {indicator_id} data with latest date: {df['Date'].max()}")
                return df, data_source, using_sample_data
            except Exception as e:
                logger.error(f"Error reading file {file_path} for {indicator_id}: {e}")
    
    # If no file data available, use sample data
    logger.warning(f"No data files found for {indicator_id}. Using sample data.")
    using_sample_data = True
    df = generate_sample_data(indicator_id)
    data_source = f"Sample data ({get_default_source_name(indicator_id)})"
    return df, data_source, using_sample_data

def load_forecast_data(indicator_id):
    """Load forecast data from files or generate sample data if not available."""
    logger.info(f"Loading forecast data for indicator: {indicator_id}")
    
    data_source = ""
    using_sample_data = False
    
    # Try multiple possible file names and paths
    possible_files = [
        os.path.join(FORECASTS_DIR, f"{indicator_id}_forecast.csv"),
        os.path.join(FORECASTS_DIR, f"{indicator_id}.csv"),
        os.path.join(BASE_DATA_DIR, f"{indicator_id}_forecast.csv"),
    ]
    
    for file_path in possible_files:
        if os.path.exists(file_path):
            try:
                logger.info(f"Loading forecast data from: {file_path}")
                df = pd.read_csv(file_path)
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Filter to keep only forecasts for current month and future
                current_month = datetime.now().replace(day=1)
                df = df[df['Date'] >= current_month]
                
                # Add missing columns if needed
                if 'indicator_id' not in df.columns:
                    df['indicator_id'] = indicator_id
                if 'source' not in df.columns:
                    df['source'] = f"{get_default_source_name(indicator_id)} - FORECAST"
                if 'preferred_direction' not in df.columns:
                    df['preferred_direction'] = get_default_preferred_direction(indicator_id)
                if 'unit' not in df.columns and indicator_id == 'wti_oil':
                    df['unit'] = '$'
                    
                data_source = f"Forecast from file: {os.path.basename(file_path)}"
                return df, data_source, using_sample_data
            except Exception as e:
                logger.error(f"Error reading forecast file {file_path} for {indicator_id}: {e}")
    
    # Try to get actual indicator data to generate more accurate forecasts
    try:
        indicator_data = load_indicator_data(indicator_id)[0]
        if not indicator_data.empty:
            logger.warning(f"No forecast file found for {indicator_id}. Generating sample forecast based on actual data.")
            using_sample_data = True
            df = generate_sample_forecast_from_actual(indicator_id, indicator_data)
            data_source = f"Generated forecast based on actual data ({get_default_source_name(indicator_id)})"
            return df, data_source, using_sample_data
    except Exception as e:
        logger.error(f"Error generating forecast from actual data for {indicator_id}: {e}")
    
    # If no forecast data available and couldn't generate from actual, use completely sample forecast
    logger.warning(f"No forecast file found for {indicator_id}. Using sample forecast.")
    using_sample_data = True
    df = generate_sample_forecast(indicator_id)
    data_source = f"Sample forecast data ({get_default_source_name(indicator_id)})"
    return df, data_source, using_sample_data

def generate_sample_forecast_from_actual(indicator_id, actual_data):
    """Generate sample forecast based on actual data for more accurate continuity."""
    current_month = datetime.now().replace(day=1)
    forecast_dates = pd.date_range(start=current_month, periods=6, freq='MS')
    num_periods = len(forecast_dates)
    
    # Get the last actual value
    if not actual_data.empty and 'value' in actual_data.columns:
        last_value = actual_data['value'].iloc[-1]
        
        # Calculate recent trend (last 3-6 months if available)
        lookback = min(6, len(actual_data))
        recent_values = actual_data['value'].tail(lookback)
        
        if len(recent_values) > 1:
            # Calculate average monthly percentage change
            monthly_pct_changes = recent_values.pct_change().dropna()
            avg_monthly_pct_change = monthly_pct_changes.mean() if not monthly_pct_changes.empty else 0.005
            
            # Use this to project future values
            values = []
            for i in range(num_periods):
                if i == 0:
                    # First forecast value should be very close to last actual
                    new_value = last_value * (1 + avg_monthly_pct_change + np.random.normal(0, 0.001))
                else:
                    # Subsequent values follow the trend with some randomness
                    new_value = values[-1] * (1 + avg_monthly_pct_change + np.random.normal(0, 0.002 * i))
                values.append(new_value)
            
            # Generate confidence intervals that widen with time
            lower_ci = [val * (1 - 0.01 - 0.005*i) for i, val in enumerate(values)]
            upper_ci = [val * (1 + 0.01 + 0.005*i) for i, val in enumerate(values)]
            
            df = pd.DataFrame({
                'Date': forecast_dates,
                'value': values,
                'lower_ci': lower_ci,
                'upper_ci': upper_ci,
                'source': f"{get_default_source_name(indicator_id)} - FORECAST",
                'indicator_id': [indicator_id] * num_periods,
                'preferred_direction': [get_default_preferred_direction(indicator_id)] * num_periods
            })
            
            # Add unit for specific indicators
            if indicator_id == 'wti_oil':
                df['unit'] = '$'
            
            return df
    
    # If we couldn't generate from actual data, fall back to standard sample
    return generate_sample_forecast(indicator_id)

def load_all_indicators():
    """Load all economic indicators and their forecasts."""
    # Verify data is available
    verify_data_availability()
    
    all_indicators = {}
    forecasts = {}
    summary_data = {}
    
    # List of all indicators to load - UPDATED to include cost indicators
    indicators = [
        # Original indicators
        'cruspi',
        'cruspi_long',
        'wti_oil',
        'supply_chain',
        'ppi_steel_scrap',
        'pmi_input_us',
        'ism_supplier_deliveries',
        'baltic_dry_index',
        'dollar_index',
        'empire_prices_paid',
        # Cost indicators - ADDED
        'komatsu_equipment',
        'sms_equipment',
        'caterpillar_equipment',
        'fabricated_steel',
        'cement_ready_mix',
        'explosives'
    ]
    
    # Load each indicator
    for indicator_id in indicators:
        try:
            df_info = load_indicator_data(indicator_id)
            df = df_info[0]
            data_source = df_info[1]
            using_sample_data = df_info[2]
            
            if not df.empty:
                all_indicators[indicator_id] = (df, data_source, using_sample_data)
                
                # Load forecast data
                forecast_info = load_forecast_data(indicator_id)
                forecast_df = forecast_info[0]
                forecast_source = forecast_info[1]
                forecast_using_sample = forecast_info[2]
                
                if not forecast_df.empty:
                    forecasts[indicator_id] = (forecast_df, forecast_source, forecast_using_sample)
        except Exception as e:
            logger.error(f"Error loading indicator {indicator_id}: {e}")
    
    # Generate summary data
    for indicator_id, df_info in all_indicators.items():
        try:
            df = df_info[0]
            data_source = df_info[1]
            using_sample_data = df_info[2]
            
            if not df.empty:
                latest_data = df.iloc[-1].to_dict()
                forecast_info = forecasts.get(indicator_id, (pd.DataFrame(), "", False))
                forecast_df = forecast_info[0]
                
                # Determine trend
                trend_text, trend_class, trend_desc = determine_trend(df, forecast_df)
                
                summary_data[indicator_id] = {
                    'indicator_id': indicator_id,
                    'name': latest_data.get('source', ''),
                    'current_value': latest_data.get('value', 0),
                    'monthly_change': latest_data.get('monthly_change', 0),
                    'yoy_change': latest_data.get('yoy_change', 0),
                    'unit': latest_data.get('unit', ''),
                    'preferred_direction': latest_data.get('preferred_direction', 'neutral'),
                    'description': latest_data.get('description', ''),
                    'trend_text': trend_text,
                    'trend_class': trend_class,
                    'trend_description': trend_desc,
                    'last_updated': pd.to_datetime(latest_data.get('Date')).strftime('%b %Y') if 'Date' in latest_data else datetime.now().strftime('%b %Y'),
                    'data_source': data_source,
                    'using_sample_data': using_sample_data,
                    # Add yearly_adjustment if available for cost indicators
                    'yearly_adjustment': latest_data.get('yearly_adjustment', None)
                }
        except Exception as e:
            logger.error(f"Error generating summary for {indicator_id}: {e}")
    
    # Create correlation matrix
    corr_matrix = create_correlation_matrix(all_indicators)
    
    return all_indicators, forecasts, summary_data, corr_matrix

def determine_trend(df, forecast_df=None):
    """Determine trend based on historical and forecast data."""
    if df.empty or 'value' not in df.columns:
        return "→ Stable", "trend-stable", "Trend cannot be determined due to insufficient data."
    
    trend_text = "→ Stable"
    trend_class = "trend-stable"
    trend_desc = "Prices have been relatively stable."
    
    if len(df) >= 2:
        recent_values = df['value'].tail(min(6, len(df)))
        forecast_values = None
        
        if forecast_df is not None and not forecast_df.empty and 'value' in forecast_df.columns:
            forecast_values = forecast_df['value']
        
        recent_trend = recent_values.pct_change().mean() * 100
        forecast_trend = 0
        
        if forecast_values is not None and len(forecast_values) >= 2:
            forecast_trend = (forecast_values.iloc[-1] - forecast_values.iloc[0]) / forecast_values.iloc[0] * 100
        
        combined_trend = (recent_trend + forecast_trend) / 2 if forecast_values is not None else recent_trend
        
        if combined_trend > 0.7:
            trend_text = "↑ Increasing"
            trend_class = "trend-up"
            trend_desc = "Prices have been trending upward."
        elif combined_trend < -0.7:
            trend_text = "↓ Decreasing"
            trend_class = "trend-down"
            trend_desc = "Prices have been trending downward."
    
    return trend_text, trend_class, trend_desc

def create_correlation_matrix(indicators):
    """Create a correlation matrix from the indicator data"""
    if not indicators or len(indicators) < 2:
        return pd.DataFrame()
    
    monthly_data = {}
    for indicator_id, df_info in indicators.items():
        df = df_info[0]  # Get the DataFrame from the tuple
        if not df.empty and 'Date' in df.columns and 'value' in df.columns:
            df['YearMonth'] = df['Date'].dt.strftime('%Y-%m')
            monthly = df.groupby('YearMonth').last().reset_index()
            monthly_data[indicator_id] = monthly[['YearMonth', 'value']].rename(columns={'value': indicator_id})
    
    if len(monthly_data) < 2:
        return pd.DataFrame()
    
    merged_df = None
    for indicator_id, df in monthly_data.items():
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on='YearMonth', how='outer')
    
    if merged_df is not None and merged_df.shape[1] > 1:
        merged_df = merged_df.drop('YearMonth', axis=1)
        return merged_df.corr()
    
    return pd.DataFrame()

def get_default_source_name(indicator_id):
    """Return default source name for an indicator."""
    sources = {
        'cruspi': "CRU Steel Price Index",
        'cruspi_long': "CRU Long Products Index",
        'wti_oil': "WTI Crude Oil Price",
        'supply_chain': "NY Fed Supply Chain Pressure Index",
        'ppi_steel_scrap': "BLS Steel Scrap Price Index",
        'pmi_input_us': "ISM Manufacturing PMI Input Prices",
        'ism_supplier_deliveries': "ISM Supplier Deliveries Index",
        'baltic_dry_index': "Baltic Dry Index (BDIY Index)",
        'dollar_index': "US Dollar Index (DXY Curncy)",
        'empire_prices_paid': "NY Fed Empire State Manufacturing 6M Ahead Prices Paid",
        # Added cost indicators
        'komatsu_equipment': "Komatsu Heavy Equipment Cost Index",
        'sms_equipment': "SMS Equipment Cost Index",
        'caterpillar_equipment': "Caterpillar Equipment Cost Index",
        'fabricated_steel': "Fabricated Structural Steel Cost Index",
        'cement_ready_mix': "Cement and Ready-Mix Cost Index",
        'explosives': "Explosives & Accessories Cost Index"
    }
    return sources.get(indicator_id, indicator_id.replace('_', ' ').title())

def get_default_unit(indicator_id):
    """Return default unit for an indicator."""
    units = {
        'wti_oil': '$',
        'empire_prices_paid': '',
        # Cost indicators are index values
        'komatsu_equipment': '',
        'sms_equipment': '',
        'caterpillar_equipment': '',
        'fabricated_steel': '',
        'cement_ready_mix': '',
        'explosives': ''
    }
    return units.get(indicator_id, '')

def get_default_preferred_direction(indicator_id):
    """Return default preferred direction for an indicator."""
    directions = {
        'supply_chain': 'down',
        'pmi_input_us': 'down',
        'ppi_steel_scrap': 'down',
        'wti_oil': 'down',
        'ism_supplier_deliveries': 'down',
        'empire_prices_paid': 'down',
        'cruspi': 'neutral',
        'cruspi_long': 'neutral',
        'baltic_dry_index': 'neutral',
        'dollar_index': 'neutral',
        # For cost indicators, lower is generally better
        'komatsu_equipment': 'down',
        'sms_equipment': 'down',
        'caterpillar_equipment': 'down',
        'fabricated_steel': 'down',
        'cement_ready_mix': 'down',
        'explosives': 'down'
    }
    return directions.get(indicator_id, 'neutral')

def get_default_description(indicator_id):
    """Return default description for an indicator."""
    descriptions = {
        'cruspi': 'CRU Steel Price Index tracks steel price movements globally',
        'cruspi_long': 'CRU Steel Price Index for Long Products tracks price movements for steel long products',
        'wti_oil': 'West Texas Intermediate Crude Oil price, U.S. benchmark for oil prices',
        'supply_chain': 'Tracks global supply chain conditions (negative values = lower pressure)',
        'ppi_steel_scrap': 'Producer Price Index for Metals and Metal Products: Carbon Steel Scrap',
        'pmi_input_us': 'PMI Input Prices index tracks price changes paid by manufacturers',
        'ism_supplier_deliveries': 'ISM Manufacturing Report on Business Supplier Deliveries Index. Values above 50 indicate slower deliveries, values below 50 indicate faster deliveries.',
        'baltic_dry_index': 'The Baltic Dry Index is a shipping and trade index measuring changes in the cost of transporting various raw materials. It serves as an indicator of global trade volume and economic activity.',
        'dollar_index': 'The US Dollar Index measures the value of the US dollar relative to a basket of foreign currencies. A higher index indicates a stronger dollar relative to other major currencies.',
        'empire_prices_paid': 'Empire State Manufacturing Survey 6-Month Ahead Prices Paid measures future inflation expectations in the NY manufacturing sector. Values reflect expected price changes over the next 6 months.',
        # Add descriptions for cost indicators
        'komatsu_equipment': 'Composite cost index for Komatsu Heavy Equipment based on weighted BLS PPI components',
        'sms_equipment': 'Composite cost index for SMS Equipment based on weighted BLS PPI components',
        'caterpillar_equipment': 'Composite cost index for Caterpillar Equipment based on weighted BLS PPI components',
        'fabricated_steel': 'Composite cost index for Fabricated Structural Steel based on weighted BLS PPI components',
        'cement_ready_mix': 'Composite cost index for Cement and Ready-Mix based on weighted BLS PPI components',
        'explosives': 'Composite cost index for Explosives & Accessories based on weighted BLS PPI components'
    }
    return descriptions.get(indicator_id, f"{indicator_id.replace('_', ' ').title()} indicator")

# Function to generate sample data for an indicator
def generate_sample_data(indicator_id):
    """Generate sample data for an indicator if it's not found in data files."""
    logger.info(f"Generating sample data for {indicator_id}")
    
    # Current date and two years back for sample data range
    end_date = datetime.now()
    start_date = datetime(end_date.year - 2, end_date.month, 1)
    
    # Create monthly dates
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # Variables for different indicator types
    base_value = 100.0
    trend = 0.5  # Default monthly percentage increase
    volatility = 1.0
    
    # Customize parameters based on indicator type
    if 'equipment' in indicator_id:
        base_value = 180.0
        trend = 0.3
        volatility = 1.5
    elif 'steel' in indicator_id:
        base_value = 200.0
        trend = 0.4
        volatility = 2.0
    elif 'cement' in indicator_id:
        base_value = 220.0
        trend = 0.25
        volatility = 1.2
    elif 'explosives' in indicator_id:
        base_value = 175.0
        trend = 0.35
        volatility = 1.8
    
    # Generate values with realistic patterns
    values = []
    yearly_adjustments = []
    
    for i, date in enumerate(dates):
        if i == 0:
            # First value is base
            value = base_value
        else:
            # Calculate month's change with seasonal component
            month = date.month
            seasonal = 0.2 * np.sin(2 * np.pi * month / 12)
            monthly_change = (trend / 100) + seasonal + np.random.normal(0, volatility / 100)
            
            # Apply to previous value
            value = values[-1] * (1 + monthly_change)
        
        values.append(value)
        
        # For cost indicators, add a yearly adjustment column (random value between 2-5%)
        # This is calculated as the YoY percentage change
        if 'equipment' in indicator_id or 'steel' in indicator_id or 'cement' in indicator_id or 'explosives' in indicator_id:
            if i >= 12:  # Only after we have a full year of data
                yearly_adj = ((value / values[i-12]) - 1) * 100
                yearly_adjustments.append(yearly_adj)
            else:
                yearly_adjustments.append(np.nan)
        else:
            yearly_adjustments.append(np.nan)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'value': values,
        'yearly_adjustment': yearly_adjustments
    })
    
    # Add calculated columns
    df['monthly_change'] = df['value'].pct_change() * 100
    df['yoy_change'] = df['value'].pct_change(12) * 100
    
    # Add metadata
    df['source'] = get_default_source_name(indicator_id) + " (Sample Data)"
    df['indicator_id'] = indicator_id
    df['unit'] = get_default_unit(indicator_id)
    df['preferred_direction'] = get_default_preferred_direction(indicator_id)
    df['description'] = get_default_description(indicator_id) + " (Sample Data)"
    
    return df

def generate_sample_forecast(indicator_id):
    """Generate sample forecast data for an indicator."""
    logger.info(f"Generating sample forecast for {indicator_id}")
    
    # Create dates for the next 6 months
    current_month = datetime.now().replace(day=1)
    dates = pd.date_range(start=current_month, periods=6, freq='MS')
    
    # Base value - should match with end of historical data
    base_value = 100.0
    
    # Customize base value by indicator type
    if 'equipment' in indicator_id:
        base_value = 180.0
    elif 'steel' in indicator_id:
        base_value = 200.0
    elif 'cement' in indicator_id:
        base_value = 220.0
    elif 'explosives' in indicator_id:
        base_value = 175.0
    
    # Generate forecast values with mild trend and some volatility
    values = []
    trend = 0.002  # Default mild monthly increase
    
    for i in range(len(dates)):
        if i == 0:
            # First forecast value
            value = base_value * (1 + np.random.normal(0, 0.01))
        else:
            # Subsequent values follow a mild trend with some randomness
            value = values[-1] * (1 + trend + np.random.normal(0, 0.005 * (i+1)))
        
        values.append(value)
    
    # Create confidence intervals that widen with time
    lower_ci = [val * (1 - 0.01 - 0.005*i) for i, val in enumerate(values)]
    upper_ci = [val * (1 + 0.01 + 0.005*i) for i, val in enumerate(values)]
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'value': values,
        'lower_ci': lower_ci,
        'upper_ci': upper_ci,
    })
    
    # Add metadata
    df['source'] = f"{get_default_source_name(indicator_id)} - FORECAST (Sample)"
    df['indicator_id'] = indicator_id
    df['unit'] = get_default_unit(indicator_id)
    df['preferred_direction'] = get_default_preferred_direction(indicator_id)
    
    return df