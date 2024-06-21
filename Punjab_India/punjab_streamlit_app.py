import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        return df
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return pd.DataFrame()

# Function to fetch future data for a specific feature
def get_future_data(engine, feature):
    query = f"SELECT date, {feature} FROM Future_Data;"
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching future data: {str(e)}")
        return pd.DataFrame()

# Function to fetch irrigation needs data for a specific crop
def get_irrigation_needs(engine, crop):
    query = f"SELECT * FROM {crop.lower()}_irrigation_need;"
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching irrigation needs data: {str(e)}")
        return pd.DataFrame()

# Main Streamlit app
def main():
    st.title('Enviromental Condition & Crop Irrigation Dashboard')

    # Connect to PostgreSQL database
    engine = get_connection()
    if engine is None:
        return

    # Sidebar for crop selection
    crop_selected = st.sidebar.selectbox('Select Crop', ['Wheat', 'Rice', 'Maize'])

    # Sidebar for selecting data feature
    feature_selected = st.sidebar.selectbox('Select Feature', [
        'temperature_2m_C', 'relative_humidity_2m', 'precipitation_mm', 
        'ET0_mm', 'wind_speed_10m_kmh', 'soil_temperature_28_to_100cm_C', 
        'soil_moisture_28_to_100cm_m3m3', 'shortwave_radiation_instant_wm2'
    ])

    # Historical data visualization
    st.header('4 Years Historical Data')
    historical_data = get_historical_data(engine, feature_selected)
    if not historical_data.empty:
        fig_hist = px.line(historical_data, x='date', y=feature_selected,
                           title=f'Historical {feature_selected}')
        st.plotly_chart(fig_hist)

    # Future data visualization
    st.header('6 Months Future Data')
    future_data = get_future_data(engine, feature_selected)
    if not future_data.empty:
        fig_future = px.line(future_data, x='date', y=feature_selected,
                             title=f'Projected {feature_selected}')
        st.plotly_chart(fig_future)

    # Irrigation needs tabular display
    st.header('Irrigation Needs')
    irrigation_needs = get_irrigation_needs(engine, crop_selected)
    if not irrigation_needs.empty:
        st.write(irrigation_needs)

# Run the Streamlit app
if __name__ == '__main__':
    main()
