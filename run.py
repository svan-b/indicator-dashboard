#!/usr/bin/env python3
"""
Run script for the Economic Indicators Dashboard.
This script sets up the proper paths and launches the Streamlit application.
"""

import os
import sys
import subprocess
import logging
import shutil
import glob

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dashboard_run.log')
    ]
)

logger = logging.getLogger(__name__)

def ensure_data_dirs():
    """Ensure data directories exist and are properly set up."""
    data_dir = "data"
    subdirs = ["raw", "processed", "forecasts"]
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        logger.info(f"Creating data directory at {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
    
    # Create subdirectories
    for subdir in subdirs:
        subdir_path = os.path.join(data_dir, subdir)
        if not os.path.exists(subdir_path):
            logger.info(f"Creating {subdir} subdirectory")
            os.makedirs(subdir_path, exist_ok=True)
    
    # Look for data files in indicator_data directory
    indicator_data_dir = os.path.expanduser("~/Commercial and Market Research/indicator_data")
    alt_data_dir = os.path.expanduser("~/Commercial and Market Research/Economic_Dashboard_Modular/data")
    
    data_sources = [
        (os.path.join(indicator_data_dir, "raw"), os.path.join(data_dir, "raw")),
        (os.path.join(indicator_data_dir, "processed"), os.path.join(data_dir, "processed")),
        (os.path.join(indicator_data_dir, "forecasts"), os.path.join(data_dir, "forecasts")),
        (os.path.join(alt_data_dir, "raw"), os.path.join(data_dir, "raw")),
        (os.path.join(alt_data_dir, "processed"), os.path.join(data_dir, "processed")),
        (os.path.join(alt_data_dir, "forecasts"), os.path.join(data_dir, "forecasts"))
    ]
    
    files_copied = 0
    
    # Try to copy data files if data directories are empty
    for src_dir, dest_dir in data_sources:
        if os.path.exists(src_dir):
            logger.info(f"Found source directory: {src_dir}")
            for file in glob.glob(os.path.join(src_dir, "*.csv")):
                dest_file = os.path.join(dest_dir, os.path.basename(file))
                if not os.path.exists(dest_file):
                    try:
                        shutil.copy(file, dest_file)
                        logger.info(f"Copied {file} to {dest_file}")
                        files_copied += 1
                    except Exception as e:
                        logger.error(f"Error copying {file}: {e}")
    
    if files_copied > 0:
        logger.info(f"Copied {files_copied} data files to local data directory")
    else:
        logger.warning("No data files were copied. Sample data may be used instead.")

def run_dashboard():
    """Run the Streamlit dashboard with improved path handling."""
    # Get absolute path to project directory
    current_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = current_dir
    
    # Try to detect if we're in a subdirectory and move up as needed
    if os.path.basename(current_dir) == "dashboard":
        project_root = os.path.dirname(current_dir)
    
    logger.info(f"Current directory: {current_dir}")
    logger.info(f"Project root: {project_root}")
    
    # Ensure data directories exist and contain data
    ensure_data_dirs()
    
    # Log information about file structure
    logger.info("Checking file structure...")
    dashboard_dir = os.path.join(project_root, "dashboard")
    main_py = os.path.join(dashboard_dir, "main.py")
    
    if os.path.exists(main_py):
        logger.info(f"Found main.py at: {main_py}")
    else:
        logger.error(f"main.py not found at {main_py}")
        # Try to find it elsewhere
        for root, dirs, files in os.walk(project_root):
            if "main.py" in files:
                main_py = os.path.join(root, "main.py")
                logger.info(f"Found main.py at alternative location: {main_py}")
                break
    
    # Log Python path
    logger.info(f"Current Python path: {sys.path}")
    
    # Add project root to Python path
    sys.path.insert(0, project_root)
    
    # Set working directory to project root
    os.chdir(project_root)
    logger.info(f"Changed working directory to: {os.getcwd()}")
    
    # Modify environment variables for the subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root
    
    # Run Streamlit with the modified environment
    logger.info("Starting Economic Indicators Dashboard...")
    
    try:
        streamlit_cmd = ["streamlit", "run"]
        
        # Determine which file to run: main.py or streamlit_app.py (for local or cloud)
        if os.path.exists("streamlit_app.py"):
            app_file = "streamlit_app.py"
            logger.info("Using streamlit_app.py (Cloud-compatible entry point)")
        elif os.path.exists(main_py):
            app_file = main_py
            logger.info(f"Using main.py at {main_py}")
        else:
            logger.error("Could not find either streamlit_app.py or main.py!")
            sys.exit(1)
            
        streamlit_args = [app_file]
        
        # Check if we're using a custom port
        port = os.environ.get("STREAMLIT_PORT")
        if port:
            streamlit_args.extend(["--server.port", port])
        
        # Add any other custom Streamlit arguments
        if "--server.headless" in sys.argv:
            streamlit_args.append("--server.headless")
        
        cmd = streamlit_cmd + streamlit_args
        logger.info(f"Running command: {' '.join(cmd)}")
        
        subprocess.run(cmd, env=env, check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error("Streamlit command not found. Please install Streamlit with 'pip install streamlit'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_dashboard()