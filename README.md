# Smart Irrigation System Documentation

## Overview

This repository hosts data and codes for a Smart Irrigation System designed to optimize water usage in agricultural practices, specifically tailored for Punjab, India. The system utilizes environmental parameters and crop-specific factors to determine irrigation needs and schedules, aiming to enhance crop yield while conserving water resources.

## Features (Dataset Columns)

### Environmental Data

- **date**: Date of the recorded data.
- **temperature_2m (°C)**: Air temperature at 2 meters above ground level.
- **relative_humidity_2m (%)**: Relative humidity at 2 meters above ground level.
- **precipitation (mm)**: Precipitation amount.
- **ET₀ (mm)**: Reference evapotranspiration.
- **wind_speed_10m (km/h)**: Wind speed at 10 meters above ground level.
- **soil_temperature_28_to_100cm (°C)**: Soil temperature at depths of 28 to 100 cm.
- **soil_moisture_28_to_100cm (m³/m³)**: Soil moisture content at depths of 28 to 100 cm.
- **shortwave_radiation_instant (W/m²)**: Instantaneous shortwave radiation.

### Crop Data

- **crop**: Type of crop (e.g., Wheat, Maize, Rice).
- **Kc**: Crop coefficient, representing water needs relative to reference evapotranspiration.
- **ETc (mm)**: Crop evapotranspiration, calculated based on Kc and ET₀.
- **soil_deficit**: Soil water deficit, indicating the amount of water needed to reach optimal soil moisture.

### Irrigation Management

- **irrigation_need**: Boolean indicating whether irrigation is required based on soil moisture and deficit.
- **irrigation_amount**: Amount of irrigation water required (mm), calculated based on soil moisture levels and threshold.

## Water Resource Challenges in Punjab

Punjab faces several challenges related to water resources, influencing agricultural practices and necessitating efficient irrigation systems:

- **Depleting Groundwater**: Over-extraction of groundwater for irrigation has led to declining water tables in Punjab.
- **Water Quality Issues**: Increasing salinity and alkalinity in soil due to poor water quality and irrigation practices.
- **Seasonal Variability**: Monsoonal rainfall variability affects water availability, impacting crop growth and irrigation requirements.
- **Water-Intensive Crops**: Traditional crops like rice and wheat require significant water inputs, exacerbating water stress.

## Usage

1. **Data Collection**: The system collects real-time environmental data including temperature, humidity, precipitation, and soil conditions.
  
2. **Crop Monitoring**: Monitors crop-specific factors such as soil moisture, temperature, and growth stage to assess irrigation needs.

3. **Irrigation Decision**: Utilizes calculated ETc and soil moisture data to determine optimal irrigation schedules, aiming for water conservation and crop health.

4. **Optimization**: Implements strategies to optimize water usage, improve crop yield, and mitigate water resource challenges specific to Punjab.

## Future Work

- Expand crop types and geographic coverage to encompass diverse agricultural regions.
- Collaborate with local stakeholders and researchers to address region-specific water management challenges.



