import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px

# Function to connect to the Database
def get_connection():
    try:
        DATABASE_URL = st.secrets["DATABASE_URL"]
        engine = create_engine(DATABASE_URL)
        return engine
    except KeyError:
        st.error("Database URL not found. Please set it in Streamlit secrets.")
        return None

# Function to fetch historical data for a specific feature
def get_historical_data(engine, feature):
    query = f"SELECT date, {feature} FROM Historical_Data;"
    try:
        df = pd.read_sql_query(query, engine)
        if df.empty:
            st.warning(f"No historical data found for feature: {feature}")
        return df
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return pd.DataFrame()

# Function to fetch future data for a specific feature
def get_future_data(engine, feature):
    query = f"SELECT date, {feature} FROM Present_with_forecast;"
    try:
        df = pd.read_sql_query(query, engine)
        if df.empty:
            st.warning(f"No future data found for feature: {feature}")
        return df
    except Exception as e:
        st.error(f"Error fetching future data: {str(e)}")
        return pd.DataFrame()

# Function to fetch irrigation needs data for a specific crop
def get_irrigation_needs(engine, crop):
    query = f"SELECT * FROM {crop.lower()}_irrigation_need;"
    try:
        df = pd.read_sql_query(query, engine)
        if df.empty:
            st.warning(f"No irrigation needs data found for crop: {crop}")
        return df
    except Exception as e:
        st.error(f"Error fetching irrigation needs data: {str(e)}")
        return pd.DataFrame()

# Function to create a line chart for irrigation needs
def plot_irrigation_needs(data, crop):
    fig = px.line(data, x='date', y='irrigation_amount_mm', title=f'Irrigation Needs Over Time for {crop}')
    return fig

# Main Streamlit app
def main():
    st.title('Environmental Condition & Crop Irrigation Dashboard')

    # Connect to PostgreSQL database
    engine = get_connection()
    if engine is None:
        return

    # Sidebar for crop selection
    crop_selected = st.sidebar.selectbox('Select Crop', ['Wheat', 'Rice', 'Maize','Sugarcane', 'Cotton', 'Barley', 'Potatoes', 'Pulses'])

    # Sidebar for selecting data feature
    feature_selected = st.sidebar.selectbox('Select Feature', [
        'temperature_2m_c', 'relative_humidity_2m', 'precipitation_mm', 
        'et₀_mm', 'wind_speed_10m_kmh', 'soil_temperature_28_to_100cm_c', 
        'soil_moisture_28_to_100cm_m3m3', 'shortwave_radiation_instant_wm2',
        'soil_moisture_lag1'
    ])

    # Historical data visualization
    st.header('4 Years Historical Data')
    historical_data = get_historical_data(engine, feature_selected)
    if not historical_data.empty:
        fig_hist = px.line(historical_data, x='date', y=feature_selected,
                           title=f'Historical {feature_selected}')
        st.plotly_chart(fig_hist)

    # Future data visualization
    st.header('6 Months Data With Forecast')
    future_data = get_future_data(engine, feature_selected)
    if not future_data.empty:
        fig_future = px.line(future_data, x='date', y=feature_selected,
                             title=f'Projected {feature_selected}')
        st.plotly_chart(fig_future)

    # Irrigation needs visualization
    st.header('Irrigation Needs')
    irrigation_needs = get_irrigation_needs(engine, crop_selected)
    if not irrigation_needs.empty:
        # Convert the date column to datetime
        irrigation_needs['date'] = pd.to_datetime(irrigation_needs['date'])

        fig_irrigation_needs = plot_irrigation_needs(irrigation_needs, crop_selected)
        st.plotly_chart(fig_irrigation_needs)
        st.write("Irrigation Needs Data Shape:", irrigation_needs.shape)
        st.write(irrigation_needs)
        
        # Add Alerts
        st.subheader("Irrigation Alerts")
        for index, row in irrigation_needs.iterrows():
            if row['irrigation_amount_mm'] > 0:
                st.warning(f"Irrigation needed on {row['date'].date()}: {row['irrigation_amount_mm']} mm of water required")
            else:
                st.success(f"No irrigation needed on {row['date'].date()}")

# Run the Streamlit app
if __name__ == '__main__':
    main()
