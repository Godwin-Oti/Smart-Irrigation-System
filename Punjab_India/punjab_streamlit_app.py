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
    query = f"SELECT date, {feature} FROM historical_data;"
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return pd.DataFrame()

# Function to fetch future data for a specific feature
def get_future_data(engine, feature):
    query = f"SELECT date, {feature} FROM future_data;"
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
    st.title('Crop Irrigation Dashboard')

    # Connect to PostgreSQL database
    engine = get_connection()
    if engine is None:
        return

    # Sidebar for crop selection
    crop_selected = st.sidebar.selectbox('Select Crop', ['Wheat', 'Rice', 'Maize'])

    # Sidebar for selecting data feature (e.g., temperature, precipitation, ET₀)
    feature_selected = st.sidebar.selectbox('Select Feature', ['temperature_2m (°C)', 'precipitation (mm)', 'ET₀ (mm)'])

    # Historical data visualization
    st.header('Historical Data')
    historical_data = get_historical_data(engine, feature_selected)
    if not historical_data.empty:
        fig_hist = px.line(historical_data, x='date', y=feature_selected,
                           title=f'Historical {feature_selected}')
        st.plotly_chart(fig_hist)

    # Future data visualization
    st.header('Future Data')
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
