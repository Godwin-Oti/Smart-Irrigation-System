import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.graph_objects as go

# Initialize session state for page navigation and feature selection
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'feature_selected' not in st.session_state:
    st.session_state.feature_selected = 'temperature_2m_c'  # Default feature selection

# Function to move to the next page
def next_page():
    st.session_state.page += 1

# Function to go back to the previous page
def prev_page():
    st.session_state.page -= 1

# Connect to PostgreSQL database
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

# Function to visualize historical and future data
def visualize_data(engine, feature_selected):
    st.header('Historical and Future Data')

    st.subheader('Select Feature for Data Visualization')
    st.session_state.feature_selected = st.selectbox('Select Feature', [
        'temperature_2m_c', 'relative_humidity_2m', 'precipitation_mm', 
        'et₀_mm', 'wind_speed_10m_kmh', 'soil_temperature_28_to_100cm_c', 
        'soil_moisture_28_to_100cm_m3m3', 'shortwave_radiation_instant_wm2'
    ], index=[i for i, f in enumerate([
        'temperature_2m_c', 'relative_humidity_2m', 'precipitation_mm', 
        'et₀_mm', 'wind_speed_10m_kmh', 'soil_temperature_28_to_100cm_c', 
        'soil_moisture_28_to_100cm_m3m3', 'shortwave_radiation_instant_wm2'
    ]) if f == st.session_state.feature_selected][0])

    st.subheader('4 Years Historical Data')
    historical_data = get_historical_data(engine, st.session_state.feature_selected)
    if not historical_data.empty:
        # Check for duplicate dates
        if historical_data.duplicated(subset='date').any():
            st.warning("Duplicate dates found in historical data.")

        # Ensure the date column is datetime type
        historical_data['date'] = pd.to_datetime(historical_data['date'])

        # Sort data by date
        historical_data = historical_data.sort_values(by='date')

        # Plot the historical data
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(x=historical_data['date'], y=historical_data[st.session_state.feature_selected],
                                      mode='lines',
                                      name=f'Historical {st.session_state.feature_selected}'))
        fig_hist.update_layout(
            title=f'Historical {st.session_state.feature_selected}',
            xaxis_title='Date',
            yaxis_title=st.session_state.feature_selected,
            template='plotly_white'
        )
        st.plotly_chart(fig_hist)

    st.subheader('6 Months Data With Forecast')
    future_data = get_future_data(engine, st.session_state.feature_selected)
    if not future_data.empty:
        # Ensure the date column is datetime type
        future_data['date'] = pd.to_datetime(future_data['date'])

        # Sort data by date
        future_data = future_data.sort_values(by='date')

        # Plot the future data
        fig_future = go.Figure()
        fig_future.add_trace(go.Scatter(x=future_data['date'], y=future_data[st.session_state.feature_selected],
                                        mode='lines',
                                        name=f'Projected {st.session_state.feature_selected}'))
        fig_future.update_layout(
            title=f'Projected {st.session_state.feature_selected}',
            xaxis_title='Date',
            yaxis_title=st.session_state.feature_selected,
            template='plotly_white'
        )
        st.plotly_chart(fig_future)

# Main Streamlit app
def main():
    st.title('Smart Irrigation App')

    # Sidebar for crop selection
    crop_selected = st.sidebar.selectbox('Select Crop', ['Wheat', 'Rice', 'Maize', 'Sugarcane', 'Cotton', 'Barley', 'Potatoes', 'Pulses'])

    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 0

    # Connect to PostgreSQL database
    engine = get_connection()
    if engine is None:
        return

    if st.session_state.page == 0:
        # Landing page section
        st.image("Punjab_India/irrigation photo.jpg", use_column_width=True)
        st.subheader("Welcome to the Smart Irrigation App")
        st.markdown("""
        This app provides comprehensive data and insights to help you optimize your irrigation practices.
        
        ### Features:
        - *Historical Data Visualization*: Analyze environmental conditions over the past 4 years.
        - *Future Data Forecast*: Plan ahead with 6 months of projected weather data.
        - *Irrigation Needs*: Get precise irrigation requirements for your selected crop.
        - *Crop Details*: Access detailed information about various crops.

        ### How It Works:
        1. Select your crop from the sidebar.
        2. Choose the environmental feature you want to analyze.
        3. Explore the historical and future data visualizations.
        4. Check the irrigation needs and alerts for your crop.
        """)
        if st.button('Next'):
            next_page()

    elif st.session_state.page == 1:
        # Data Visualization page
        visualize_data(engine, st.session_state.feature_selected)

        if st.button('Next'):
            next_page()
        if st.button('Back'):
            prev_page()

if __name__ == '__main__':
    main()
