import React, { useEffect, useState } from "react";
import axios from "axios";

const AirQuality = ({ lat, lon }) => {
  const [airQuality, setAirQuality] = useState(null);
  const API_KEY = "4f2d48f8469a7ee7fd709829653ea6c4"; 

  useEffect(() => {
    const fetchAirQuality = async () => {
      try {
        const response = await axios.get(
          `http://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${API_KEY}`
        );
        setAirQuality(response.data);
      } catch (error) {
        console.error("Error fetching air quality data:", error);
      }
    };
    fetchAirQuality();
  }, [lat, lon]);

  return (
    <div>
      <h3>Air Quality Index (AQI):</h3>
      {airQuality ? (
        <p>{airQuality.list[0].main.aqi} (1=Good, 5=Very Poor)</p>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default AirQuality;
