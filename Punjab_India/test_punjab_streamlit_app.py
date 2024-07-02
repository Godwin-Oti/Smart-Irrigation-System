import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

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
            st.warning(f"No historical data found for feature: {feature} between {start_date} and {end_date}")
        return df
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return pd.DataFrame()

# Function to fetch future data for a specific feature within a date range
def get_future_data(engine, feature, start_date, end_date):
    query = f"SELECT date, {feature} FROM Present_with_forecast WHERE date BETWEEN '{start_date}' AND '{end_date}';"
    try:
        df = pd.read_sql_query(query, engine)
        if df.empty:
            st.warning(f"No future data found for feature: {feature} between {start_date} and {end_date}")
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
    if 'date' not in data.columns or 'irrigation_amount_mm' not in data.columns:
        st.error("The required columns 'date' and 'irrigation_amount_mm' are not present in the data.")
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['irrigation_amount_mm'], mode='lines', name=f'Irrigation Needs for {crop}'))
    fig.update_layout(title=f'Irrigation Needs Over Time for {crop}', xaxis_title='Date', yaxis_title='Irrigation Amount (mm)', template='plotly_white')
    return fig

# Function to fetch crop details
def get_crop_details(engine, crop):
    query = f"SELECT * FROM {crop.lower()}_data;"
    try:
        df = pd.read_sql_query(query, engine)
        if df.empty:
            st.warning(f"No details found for crop: {crop}")
        return df
    except Exception as e:
        st.error(f"Error fetching crop details: {str(e)}")
        return pd.DataFrame()

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
            st.session_state.page = 1

    elif st.session_state.page == 1:
        tabs = st.tabs(["Historical & Future Data", "Crop Details & Irrigation Needs"])

        with tabs[0]:
            st.header('Historical and Future Data')

            # Date range selection
            start_date = st.date_input('Start date', datetime.today() - timedelta(days=365*4))
            end_date = st.date_input('End date', datetime.today())

            # Select feature for data visualization
            feature_selected = st.selectbox('Select Feature', [
                'temperature_2m_c', 'relative_humidity_2m', 'precipitation_mm', 
                'et₀_mm', 'wind_speed_10m_kmh', 'soil_temperature_28_to_100cm_c', 
                'soil_moisture_28_to_100cm_m3m3', 'shortwave_radiation_instant_wm2'
            ])

            st.subheader('4 Years Historical Data')
            historical_data = get_historical_data(engine, feature_selected, start_date, end_date)
            if not historical_data.empty:
                # Ensure the date column is datetime type
                historical_data['date'] = pd.to_datetime(historical_data['date'])

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

            st.subheader('6 Months Data With Forecast')
            future_data = get_future_data(engine, feature_selected, start_date, end_date)
            if not future_data.empty:
                # Ensure the date column is datetime type
                future_data['date'] = pd.to_datetime(future_data['date'])

                # Plot the future data
                fig_future = go.Figure()
                fig_future.add_trace(go.Scatter(x=future_data['date'], y=future_data[feature_selected],
                                                mode='lines',
                                                name=f'Projected {feature_selected}'))
                fig_future.update_layout(
                    title=f'Projected {feature_selected}',
                    xaxis_title='Date',
                    yaxis_title=feature_selected,
                    template='plotly_white'
                )
                st.plotly_chart(fig_future)

        with tabs[1]:
            st.header('Crop Details and Irrigation Needs')

            st.subheader('Irrigation Needs')
            irrigation_needs = get_irrigation_needs(engine, crop_selected)
            if not irrigation_needs.empty:
                # Ensure the date column is datetime type
                irrigation_needs['date'] = pd.to_datetime(irrigation_needs['date'])

                # Plot irrigation needs
                fig_irrigation_needs = plot_irrigation_needs(irrigation_needs, crop_selected)
                if fig_irrigation_needs:
                    st.plotly_chart(fig_irrigation_needs)
                    st.write("Irrigation Needs Data Shape:", irrigation_needs.shape)
                    st.write(irrigation_needs)

                # Irrigation alerts for the present and next day
                st.subheader("Irrigation Alerts")
                today = pd.Timestamp('today').normalize()
                upcoming_days = irrigation_needs[(irrigation_needs['date'] >= today) & (irrigation_needs['date'] <= today + pd.Timedelta(days=1))]
                for index, row in upcoming_days.iterrows():
                    if row['irrigation_amount_mm'] > 0:
                        st.warning(f"Irrigation needed on {row['date'].date()}: {row['irrigation_amount_mm']} mm of water required")
                    else:
                        st.success(f"No irrigation needed on {row['date'].date()}")

            st.subheader('Crop Details')
            crop_details = get_crop_details(engine, crop_selected)
            if not crop_details.empty:
                st.write(crop_details)

        if st.button('Back'):
            st.session_state.page = 0

if __name__ == '__main__':
    main()
