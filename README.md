# Economic Indicators Dashboard

A Streamlit dashboard for monitoring key economic indicators relevant to the steel and mining industry. This dashboard displays data from various sources, including CRU steel price indices, NY Fed Supply Chain Pressure Index, oil prices, and more.

## Features

- Interactive visualization of key economic indicators
- Forecast projections for each indicator
- Cost indicators section for equipment and materials
- Correlation analysis between indicators
- Mobile-friendly responsive design
- Downloadable data for each indicator

## Running the Dashboard

### Local Development

To run the dashboard locally:

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the dashboard: `python run.py`

### Streamlit Cloud

The dashboard is deployed on Streamlit Cloud at:
https://indicator-dashboard-dyp7oscj3twv9stxdb5zbn.streamlit.app

## Data Sources

The dashboard uses data from various sources:

- CRU Steel Price Index (CRUspi)
- NY Fed Global Supply Chain Pressure Index
- WTI Crude Oil Price
- BLS Producer Price Index for Carbon Steel Scrap
- Baltic Dry Index
- US Dollar Index (DXY)
- PMI Input Prices
- ISM Supplier Deliveries Index
- Custom cost indicators based on BLS PPI components

## Project Structure

```
indicator-dashboard/
├── dashboard/            # Main dashboard code
│   ├── components/       # Reusable UI components
│   ├── pages/            # Dashboard page modules
│   ├── utils/            # Utility functions
│   └── main.py           # Entry point for local dev
├── data/                 # Data files
│   ├── raw/              # Raw data files
│   ├── processed/        # Processed data files
│   └── forecasts/        # Forecast data files
├── notebooks/            # Jupyter notebooks for analysis
├── run.py                # Script to run the dashboard locally
├── setup_data_dir.py     # Script to set up data directory
├── streamlit_app.py      # Entry point for Streamlit Cloud
└── requirements.txt      # Python dependencies
```

## Data Flow

1. Jupyter notebooks download data from various sources and save to data directories
2. Data loader components read from these directories
3. Dashboard components visualize and analyze the data

## Deployment

This dashboard is designed to work both locally and in the Streamlit Cloud environment. The `streamlit_app.py` file serves as the entry point for cloud deployment.

### Data in Cloud Environment

For cloud deployment, the app uses:
1. Pre-generated data files included in the repository
2. Sample data generation as a fallback for missing data

## Troubleshooting

If you encounter issues with missing data:

1. Run `python setup_data_dir.py` to initialize the data directory structure
2. Check the log output for any errors
3. If using locally generated data, ensure files are in the correct directories

## License

This project is proprietary and confidential.

## Contact

For questions or issues, please contact scott.vanbolhuis@teck.com