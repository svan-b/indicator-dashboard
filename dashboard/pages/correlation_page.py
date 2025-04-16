"""Correlation analysis page."""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from dashboard.utils.data_loader import load_all_indicators
from dashboard.components.charts import create_correlation_matrix_chart

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def show_correlation_page():
    """Display correlation analysis page."""
    # Load data 
    try:
        all_indicators, forecasts, summary_data, corr_matrix = load_all_indicators()
        
        st.markdown('<h2 class="sub-header">Indicator Correlation Analysis</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="correlation-description">
        This analysis shows the correlation between different economic indicators. A correlation closer to 1 indicates a strong positive relationship, 
        while a value closer to -1 indicates a strong negative relationship. Values near 0 indicate little to no linear relationship.
        </div>
        """, unsafe_allow_html=True)
        
        if corr_matrix is not None and not corr_matrix.empty:
            st.markdown('<div class="correlation-matrix">', unsafe_allow_html=True)
            
            corr_chart = create_correlation_matrix_chart(corr_matrix)
            if corr_chart:
                st.plotly_chart(corr_chart, use_container_width=True)
            
            # REMOVED: The second correlation matrix visualization (table)
            # This line removes the dataframe that was causing issues
            
            st.markdown("""
            <h3 style="color: #00103f; font-size: 1.4rem; margin-top: 1.5rem;">Key Insights:</h3>
            <ul style="color: #333333; margin-top: 1rem; margin-bottom: 1rem;">
                <li><strong>Strong positive correlations</strong> indicate indicators that move together in the same direction</li>
                <li><strong>Strong negative correlations</strong> indicate indicators that move in opposite directions</li>
                <li>Understanding these relationships can help predict how changes in one indicator might affect others</li>
            </ul>
            """, unsafe_allow_html=True)
            
            csv = corr_matrix.to_csv()
            st.download_button(
                label="Download Correlation Matrix",
                data=csv,
                file_name="indicator_correlations.csv",
                mime="text/csv",
                key="download-corr-csv"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Not enough data to generate correlation matrix. Ensure you have multiple indicators with overlapping time periods.")
    except Exception as e:
        logger.error(f"Error in correlation page: {e}")
        st.error(f"Error loading correlation data: {e}")
        st.info("Check if the data loader is properly returning the correlation matrix.")

if __name__ == "__main__":
    show_correlation_page()