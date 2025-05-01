#!/usr/bin/env python3
"""
Setup script for data directory - prepares data structure for Streamlit Cloud
Copies sample data to the appropriate data folders
"""

import os
import shutil
import glob
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_dir_structure():
    """Create necessary directory structure for data."""
    data_dir = "data"
    subdirs = ["raw", "processed", "forecasts"]
    
    logger.info(f"Creating data directory structure in {os.getcwd()}")
    
    # Create main data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Created data directory: {data_dir}")
    
    # Create subdirectories
    for subdir in subdirs:
        subdir_path = os.path.join(data_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)
            logger.info(f"Created subdirectory: {subdir_path}")

def find_sample_data():
    """Find sample data files in the project directory."""
    # Patterns to search for
    patterns = [
        "**/indicator_data/raw/*.csv",
        "**/indicator_data/processed/*.csv",
        "**/indicator_data/forecasts/*.csv",
        "**/data/raw/*.csv",
        "**/data/processed/*.csv",
        "**/data/forecasts/*.csv"
    ]
    
    found_files = []
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            logger.info(f"Found data file: {match}")
            found_files.append(match)
    
    # Prioritize CRUspi direct data
    cruspi_direct = None
    for file in found_files:
        if 'cruspi_direct' in file.lower():
            cruspi_direct = file
            logger.info(f"Found CRUspi direct data: {cruspi_direct}")
            break
    
    # If we found CRUspi direct, put it at the front of the list for priority
    if cruspi_direct:
        found_files.remove(cruspi_direct)
        found_files.insert(0, cruspi_direct)
        logger.info(f"Prioritizing CRUspi direct data for copying")
    
    logger.info(f"Found {len(found_files)} sample data files")
    return found_files

def copy_data_files(source_files):
    """Copy sample data files to the data directory."""
    # Map to track where each file should go
    dest_map = {
        "raw": os.path.join("data", "raw"),
        "processed": os.path.join("data", "processed"),
        "forecasts": os.path.join("data", "forecasts")
    }
    
    copied_count = 0
    cruspi_processed = False
    
    for source_file in source_files:
        # Special handling for CRUspi direct data
        if 'cruspi_direct' in source_file.lower():
            # Copy to both raw and processed directories
            try:
                # Copy to raw directory as is
                raw_dest_file = os.path.join(dest_map["raw"], "cruspi_direct.csv")
                shutil.copy2(source_file, raw_dest_file)
                logger.info(f"Copied CRUspi direct data to: {raw_dest_file}")
                
                # Also create processed version with standardized name for easier loading
                processed_dest_file = os.path.join(dest_map["processed"], "cruspi.csv")
                shutil.copy2(source_file, processed_dest_file)
                logger.info(f"Copied CRUspi direct data to processed dir: {processed_dest_file}")
                
                # Mark CRUspi as processed to avoid copying sample data
                cruspi_processed = True
                copied_count += 2
            except Exception as e:
                logger.error(f"Failed to copy CRUspi direct data: {e}")
            continue
            
        # Skip CRUspi sample files if we already processed the direct data
        if cruspi_processed and ('cruspi_sample' in source_file.lower() or 'cruspi.csv' in source_file.lower()):
            logger.info(f"Skipping CRUspi sample file since direct data was processed: {source_file}")
            continue
        
        # Regular file handling for other files
        for key, dest_dir in dest_map.items():
            if key in source_file:
                # Get filename from path
                filename = os.path.basename(source_file)
                dest_file = os.path.join(dest_dir, filename)
                
                # Only copy if destination doesn't exist or source is newer
                if not os.path.exists(dest_file) or \
                   os.path.getmtime(source_file) > os.path.getmtime(dest_file):
                    try:
                        shutil.copy2(source_file, dest_file)
                        logger.info(f"Copied {source_file} to {dest_file}")
                        copied_count += 1
                    except Exception as e:
                        logger.error(f"Failed to copy {source_file}: {e}")
                break
    
    logger.info(f"Copied {copied_count} files to data directory")
    return copied_count

def create_sample_data():
    """Create basic sample data files if none are found."""
    from datetime import datetime, timedelta
    import numpy as np
    import pandas as pd
    
    logger.info("Creating basic sample data files...")
    
    # Sample indicators to create
    indicators = [
        {'id': 'cruspi', 'name': 'CRU Steel Price Index', 'base_value': 160, 'unit': ''},
        {'id': 'wti_oil', 'name': 'WTI Crude Oil Price', 'base_value': 75, 'unit': '$'},
        {'id': 'supply_chain', 'name': 'NY Fed Supply Chain Pressure Index', 'base_value': 0.5, 'unit': ''},
        {'id': 'ppi_steel_scrap', 'name': 'BLS Steel Scrap Price Index', 'base_value': 550, 'unit': ''},
        {'id': 'komatsu_equipment', 'name': 'Komatsu Heavy Equipment Cost Index', 'base_value': 200, 'unit': ''}
    ]
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years of data
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    created_count = 0
    
    for indicator in indicators:
        # Generate sample values
        np.random.seed(hash(indicator['id']) % 1000)  # Consistent randomness
        
        values = []
        for i, date in enumerate(dates):
            if i == 0:
                value = indicator['base_value']
            else:
                # Add some randomness and trend
                trend = 0.002  # Small upward trend
                seasonal = 0.01 * np.sin(2 * np.pi * i / 12)  # Seasonal component
                noise = np.random.normal(0, 0.01)  # Random noise
                
                value = values[-1] * (1 + trend + seasonal + noise)
            values.append(value)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'value': values
        })
        
        # Add calculated columns
        df['monthly_change'] = df['value'].pct_change() * 100
        df['yoy_change'] = df['value'].pct_change(12) * 100
        
        # Add metadata
        df['source'] = f"{indicator['name']} (Sample Data)"
        df['indicator_id'] = indicator['id']
        df['unit'] = indicator['unit']
        df['preferred_direction'] = 'down' if 'cost' in indicator['id'] or indicator['id'] == 'supply_chain' else 'neutral'
        df['description'] = f"Sample data for {indicator['name']}"
        
        # Save to processed dir
        output_file = os.path.join("data", "processed", f"{indicator['id']}.csv")
        df.to_csv(output_file, index=False)
        logger.info(f"Created sample data file: {output_file}")
        created_count += 1
        
        # Create forecast
        forecast_dates = pd.date_range(start=end_date, periods=6, freq='MS')
        last_value = df['value'].iloc[-1]
        
        forecast_values = []
        for i in range(len(forecast_dates)):
            if i == 0:
                value = last_value * (1 + np.random.normal(0, 0.005))
            else:
                value = forecast_values[-1] * (1 + 0.002 + np.random.normal(0, 0.005))
            forecast_values.append(value)
        
        # Create confidence intervals
        lower_ci = [val * (1 - 0.01 - 0.005*i) for i, val in enumerate(forecast_values)]
        upper_ci = [val * (1 + 0.01 + 0.005*i) for i, val in enumerate(forecast_values)]
        
        # Create forecast DataFrame
        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'value': forecast_values,
            'lower_ci': lower_ci,
            'upper_ci': upper_ci,
            'source': f"{indicator['name']} - FORECAST (Sample)",
            'indicator_id': indicator['id'],
            'unit': indicator['unit'],
            'preferred_direction': 'down' if 'cost' in indicator['id'] or indicator['id'] == 'supply_chain' else 'neutral'
        })
        
        # Save forecast
        forecast_file = os.path.join("data", "forecasts", f"{indicator['id']}_forecast.csv")
        forecast_df.to_csv(forecast_file, index=False)
        logger.info(f"Created sample forecast file: {forecast_file}")
        created_count += 1
    
    return created_count

if __name__ == "__main__":
    logger.info("Starting data directory setup")
    
    # Clear any cached data files to ensure we always use the latest
    import glob
    import os
    
    # Get data directory
    data_dir = "data"
    if os.path.exists(data_dir):
        # Check for files to clear cache
        for subdir in ['raw', 'processed', 'forecasts']:
            dir_path = os.path.join(data_dir, subdir)
            if os.path.exists(dir_path):
                cache_files = glob.glob(os.path.join(dir_path, "*.cache.*"))
                for cache_file in cache_files:
                    try:
                        os.remove(cache_file)
                        logger.info(f"Removed cache file: {cache_file}")
                    except Exception as e:
                        logger.error(f"Error removing cache file {cache_file}: {e}")
    
    # Ensure the directory structure exists
    ensure_dir_structure()
    
    # Find and copy existing sample data files
    source_files = find_sample_data()
    copied_count = copy_data_files(source_files)
    
    # If no files were copied, create some basic sample data
    if copied_count == 0:
        logger.warning("No sample data files found to copy")
        created_count = create_sample_data()
        logger.info(f"Created {created_count} sample data files")
    
    logger.info("Data directory setup complete")
    
    # List contents of data directory for verification
    for root, dirs, files in os.walk("data"):
        logger.info(f"Directory: {root}")
        for file in files:
            logger.info(f"  File: {file}")
    
    logger.info("Setup complete!")