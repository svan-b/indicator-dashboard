#!/usr/bin/env python3
"""
Run script for the Economic Indicators Dashboard.
This script sets up the proper paths and launches the Streamlit application.
"""

import os
import sys
import subprocess
import logging

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
    
    # Create the necessary directory structure if it doesn't exist
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    for subdir in ["raw", "processed", "forecasts"]:
        os.makedirs(os.path.join(data_dir, subdir), exist_ok=True)
    
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
        streamlit_args = [main_py]
        
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