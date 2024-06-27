import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
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

# Function to fetch soil moisture data
def get_soil_moisture_data(engine):
    query = "SELECT date, soil_moisture_28_to_100cm_m3m3 FROM Historical_Data;"
    try:
        df = pd.read_sql_query(query, engine)
        if df.empty:
            st.warning("No soil moisture data found.")
        return df
    except Exception as e:
        st.error(f"Error fetching soil moisture data: {str(e)}")
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

# Function to plot stacked bar chart for soil moisture and irrigation needs
def plot_stacked_bar_chart(soil_moisture_data, irrigation_needs_data):
    if 'date' not in soil_moisture_data.columns or 'soil_moisture_28_to_100cm_m3m3' not in soil_moisture_data.columns:
        st.error("The required columns 'date' and 'soil_moisture_28_to_100cm_m3m3' are not present in the soil moisture data.")
        return None

    if 'date' not in irrigation_needs_data.columns or 'irrigation_amount_mm' not in irrigation_needs_data.columns:
        st.error("The required columns 'date' and 'irrigation_amount_mm' are not present in the irrigation needs data.")
        return None

    # Merge the two dataframes on the 'date' column
    merged_data = pd.merge(soil_moisture_data, irrigation_needs_data, on='date')

    # Plot the stacked bar chart
    fig = go.Figure(data=[
        go.Bar(name='Soil Moisture', x=merged_data['date'], y=merged_data['soil_moisture_28_to_100cm_m3m3']),
        go.Bar(name='Irrigation Needs', x=merged_data['date'], y=merged_data['irrigation_amount_mm'])
    ])
    fig.update_layout(barmode='stack', title='Soil Moisture and Irrigation Needs Over Time', xaxis_title='Date', yaxis_title='Values', template='plotly_white')
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
    tab1, tab2 = st.tabs(["Data Visualization", "Crop Details"])

    with tab1:
        # Historical data visualization
        st.header('4 Years Historical Data')
        historical_data = get_historical_data(engine, feature_selected)
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

        # Future data visualization
        st.header('6 Months Data With Forecast')
        future_data = get_future_data(engine, feature_selected)
        if not future_data.empty:
            # Ensure the date column is datetime type
            future_data['date'] = pd.to_datetime(future_data['date'])

            # Sort data by date
            future_data = future_data.sort_values(by='date')

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

        # Irrigation needs visualization
        st.header('Irrigation Needs')
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

        # Stacked bar chart visualization
        st.header('Soil Moisture and Irrigation Needs')
        soil_moisture_data = get_soil_moisture_data(engine)
        if not soil_moisture_data.empty and not irrigation_needs.empty:
            fig_stacked_bar = plot_stacked_bar_chart(soil_moisture_data, irrigation_needs)
            if fig_stacked_bar:
                st.plotly_chart(fig_stacked_bar)

    with tab2:
        # Crop details
        st.header(f"{crop_selected} Crop Details")
        crop_details = get_crop_details(engine, crop_selected)
        if not crop_details.empty:
            st.dataframe(crop_details, width=1000)
        else:
            st.warning("No crop details available.")

# Run the Streamlit app
if __name__ == '__main__':
    main()
