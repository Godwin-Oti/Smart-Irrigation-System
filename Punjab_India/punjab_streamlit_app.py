import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Function to connect to the Database
def get_connection():
    try:
        DATABASE_URL = st.secrets["DATABASE_URL"]
        engine = create_engine(DATABASE_URL)
        return engine
    except KeyError:
        st.error("Database URL not found. Please set it in Streamlit secrets.")
        return None

# Function to fetch historical data for a specific feature within a date range
def get_historical_data(engine, feature, start_date, end_date):
    query = f"SELECT date, {feature} FROM Historical_Data WHERE date BETWEEN '{start_date}' AND '{end_date}';"
    try:
        df = pd.read_sql_query(query, engine)
        if df.empty:
            st.warning(f"No historical data found for feature: {feature}")
        return df
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return pd.DataFrame()

# Function to create a line chart for irrigation needs
def plot_irrigation_needs(data, crop):
    if 'date' not in data.columns or 'irrigation_amount_mm' not in data.columns:
        st.error("The required columns 'date' and 'irrigation_amount_mm' are not present in the data.")
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['irrigation_amount_mm'], mode='lines', name=f'Irrigation Needs for {crop}'))
    fig.update_layout(title=f'Irrigation Needs Over Time for {crop}', xaxis_title='Date', yaxis_title='Irrigation Amount (mm)', template='plotly_white')
    return fig

# Main Streamlit app
def main():
    st.title('Environmental Condition & Crop Irrigation Dashboard')

    # Connect to PostgreSQL database
    engine = get_connection()
    if engine is None:
        return

    # Sidebar for crop selection
    crop_selected = st.sidebar.selectbox('Select Crop', ['Wheat', 'Rice', 'Maize', 'Sugarcane', 'Cotton', 'Barley', 'Potatoes', 'Pulses'])

    # Sidebar for selecting data feature
    feature_selected = st.sidebar.selectbox('Select Feature', [
        'temperature_2m_c', 'relative_humidity_2m', 'precipitation_mm', 
        'et₀_mm', 'wind_speed_10m_kmh', 'soil_temperature_28_to_100cm_c', 
        'soil_moisture_28_to_100cm_m3m3', 'shortwave_radiation_instant_wm2'
    ])

    # Tabs for different sections
    tab1, tab2 = st.columns([1, 1])

    with tab1:
        # Historical data visualization
        st.header('Historical Data Visualization')

        # Date range selection
        start_date = st.date_input("Select start date", datetime.today() - relativedelta(years=1))
        end_date = st.date_input("Select end date", datetime.today())

        # Fetch historical data based on selected date range
        historical_data = get_historical_data(engine, feature_selected, start_date, end_date)
        if not historical_data.empty:
            # Ensure the date column is datetime type
            historical_data['date'] = pd.to_datetime(historical_data['date'])

            # Sort data by date
            historical_data = historical_data.sort_values(by='date')

            # Plot the historical data
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Scatter(x=historical_data['date'], y=historical_data[feature_selected],
                                          mode='lines',
                                          name=f'Historical {feature_selected}'))
            fig_hist.update_layout(
                title=f'Historical {feature_selected}',
                xaxis_title='Date',
                yaxis_title=feature_selected,
                template='plotly_white'
            )
            st.plotly_chart(fig_hist)

    with tab2:
        # Your existing code for crop details
        st.header(f"{crop_selected} Crop Details")
        # ...

# Run the Streamlit app
if __name__ == '__main__':
    main()
