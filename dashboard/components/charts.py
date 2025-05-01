"""Chart components for the dashboard."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Teck Resources colors
TECK_NAVY = "#00103f"     # Primary accent color
TECK_ORANGE = "#ce3e0d"   # Secondary accent color  
TECK_BLUE = "#0072CE"     # Additional blue for variety
TECK_LIGHT_BLUE = "#68B2E3"
TECK_GRAY = "#333333"     # Dark gray for text (improved contrast)
TECK_LIGHT_GRAY = "#f5f5f5" # Background color

def create_indicator_chart(df, forecast_df=None, show_forecast=True, indicator_id=None, unit=None, preferred_direction=None):
    """Create a standard plotly chart for an indicator with improved forecast continuity."""
    if df is None or df.empty or 'Date' not in df.columns or 'value' not in df.columns:
        logger.warning("Cannot create chart: DataFrame is empty or missing required columns")
        return None
    
    # Get metadata from df if not provided
    if unit is None and 'unit' in df.columns:
        unit = df['unit'].iloc[0]
    
    if preferred_direction is None and 'preferred_direction' in df.columns:
        preferred_direction = df['preferred_direction'].iloc[0]
    
    if indicator_id is None and 'indicator_id' in df.columns:
        indicator_id = df['indicator_id'].iloc[0]
    
    # Create figure
    fig = go.Figure()
    
    # Format hover template based on unit
    if unit == '$':
        hover_template = '%{x|%b %Y}: $%{y:.2f}<extra></extra>'
    else:
        hover_template = '%{x|%b %Y}: %{y:.2f}<extra></extra>'
    
    # Add historical data trace
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['value'],
            name='Historical',
            line=dict(color=TECK_NAVY, width=3),
            hovertemplate=hover_template
        )
    )
    
    # Add forecast if available and requested
    if show_forecast and forecast_df is not None and not forecast_df.empty and 'Date' in forecast_df.columns and 'value' in forecast_df.columns:
        # Extract last historical point 
        last_hist_date = df['Date'].iloc[-1]
        last_hist_value = df['value'].iloc[-1]
        
        # Adjust the first forecast point to better align with the historical trend
        if len(forecast_df) > 0:
            # Calculate a smoother transition for the first forecast point
            # Use a weighted average between the last historical value and the first forecast value
            first_forecast_value = forecast_df['value'].iloc[0]
            adjusted_first_value = last_hist_value * 0.7 + first_forecast_value * 0.3
            
            # Update the first forecast point's value
            adjusted_forecast_df = forecast_df.copy()
            adjusted_forecast_df.iloc[0, adjusted_forecast_df.columns.get_loc('value')] = adjusted_first_value
            
            # Also adjust the confidence intervals
            if 'lower_ci' in adjusted_forecast_df.columns and 'upper_ci' in adjusted_forecast_df.columns:
                # Adjust first point's confidence interval
                first_lower = adjusted_forecast_df['lower_ci'].iloc[0]
                first_upper = adjusted_forecast_df['upper_ci'].iloc[0]
                
                # Make the CI narrower at the first point to avoid discontinuity
                ci_range = first_upper - first_lower
                adjusted_forecast_df.iloc[0, adjusted_forecast_df.columns.get_loc('lower_ci')] = adjusted_first_value - (ci_range * 0.3)
                adjusted_forecast_df.iloc[0, adjusted_forecast_df.columns.get_loc('upper_ci')] = adjusted_first_value + (ci_range * 0.3)
        else:
            adjusted_forecast_df = forecast_df
        
        # Create forecast trace that starts at the last historical data point
        forecast_dates = [last_hist_date] + list(adjusted_forecast_df['Date'])
        forecast_values = [last_hist_value] + list(adjusted_forecast_df['value'])
        
        # Add line for forecast
        fig.add_trace(
            go.Scatter(
                x=forecast_dates,
                y=forecast_values,
                name='Forecast',
                line=dict(color=TECK_ORANGE, width=2, dash='dash'),
                hovertemplate=hover_template
            )
        )
        
        # Add confidence interval if available
        if 'lower_ci' in adjusted_forecast_df.columns and 'upper_ci' in adjusted_forecast_df.columns:
            # Include last historical point in confidence interval
            lower_ci = [last_hist_value] + list(adjusted_forecast_df['lower_ci'])
            upper_ci = [last_hist_value] + list(adjusted_forecast_df['upper_ci'])
            
            # Combine x, upper_ci, and lower_ci for area plot
            x_fill = forecast_dates + forecast_dates[::-1]
            y_fill = upper_ci + lower_ci[::-1]
            
            fig.add_trace(
                go.Scatter(
                    x=x_fill,
                    y=y_fill,
                    fill='toself',
                    fillcolor='rgba(206, 62, 13, 0.2)',
                    line=dict(color='rgba(0, 0, 0, 0)'),
                    name='95% Confidence Interval',
                    hoverinfo='skip'
                )
            )
    
    # Add reference line at reference level if needed
    if indicator_id == 'supply_chain':
        fig.add_hline(
            y=0, 
            line_dash="dot", 
            line_color="#888888", 
            annotation_text="Historical Average",
            annotation_position="bottom right"
        )
    elif indicator_id in ['pmi_input_us', 'ism_supplier_deliveries', 'empire_prices_paid']:
        fig.add_hline(
            y=50, 
            line_dash="dot", 
            line_color="#888888", 
            annotation_text="Neutral Level",
            annotation_position="bottom right"
        )
    
    # Customize yaxis title based on unit
    yaxis_title = ""
    if unit == '$':
        if indicator_id == 'wti_oil':
            yaxis_title = "USD per Barrel"
        else:
            yaxis_title = "USD"
    else:
        yaxis_title = "Index Value"
    
    # Update layout
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=yaxis_title,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333333', size=12)
    )
    
    # Set y-axis to currency format if unit is $
    if unit == '$':
        fig.update_yaxes(tickprefix='$')
    
    return fig

def create_correlation_matrix_chart(corr_matrix):
    """Create a heatmap visualization of correlation matrix with improved text contrast."""
    if corr_matrix is None or corr_matrix.empty:
        logger.warning("Cannot create correlation matrix chart: Matrix is empty")
        return None
    
    # Create better labels that are more readable
    labels = {col: col.replace('_', ' ').title() for col in corr_matrix.columns}
    
    # Use a new colorscale with better contrast for text
    colorscale = [
        [0, "#0000CC"],       # Dark blue for strong negative correlation
        [0.2, "#6699FF"],     # Medium blue for medium negative correlation
        [0.4, "#CCDDFF"],     # Very light blue for weak negative correlation
        [0.5, "#FFFFFF"],     # White for no correlation
        [0.6, "#FFDDCC"],     # Very light red for weak positive correlation
        [0.8, "#FF6666"],     # Medium red for medium positive correlation
        [1, "#CC0000"]        # Dark red for strong positive correlation
    ]
    
    # Create the heatmap
    fig = px.imshow(
        corr_matrix,
        x=[labels.get(col, col) for col in corr_matrix.columns],
        y=[labels.get(col, col) for col in corr_matrix.columns],
        color_continuous_scale=colorscale,
        zmin=-1,
        zmax=1
    )
    
    # Add correlation values as text with MAXIMUM contrast - simpler approach
    annotations = []
    for i, row in enumerate(corr_matrix.index):
        for j, col in enumerate(corr_matrix.columns):
            value = corr_matrix.iloc[i, j]
            
            # MUCH simpler contrast approach - based purely on the absolute value
            # This ensures dark cells ALWAYS have white text
            abs_value = abs(value)
            
            # WHITE text for ANY cell with correlation > 0.4 (medium to dark cells)
            # BLACK text for correlation < 0.4 (light cells)
            if abs_value >= 0.4:
                text_color = 'white'  # White text for ALL darker cells
            else:
                text_color = 'black'  # Black text only for very light cells
                
            # Use larger font for diagonal elements (which are always 1.0)
            font_size = 14 if i == j else 12
                
            annotations.append(
                dict(
                    x=j,
                    y=i,
                    text=f"{value:.2f}",
                    font=dict(
                        color=text_color, 
                        size=font_size,
                        family="Arial"
                    ),
                    showarrow=False
                )
            )
    
    # Update layout with larger size and more appropriate settings
    fig.update_layout(
        height=800,  # Increased height
        width=1000,  # Set explicit width
        margin=dict(l=60, r=60, t=40, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333333', size=12),
        annotations=annotations,
        coloraxis_colorbar=dict(
            title="Correlation", 
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1.0", "-0.5", "0.0", "0.5", "1.0"]
        )
    )
    
    return fig