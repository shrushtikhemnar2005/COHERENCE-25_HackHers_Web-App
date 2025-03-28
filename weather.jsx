import React, { useEffect, useState } from "react";
import axios from "axios";

const Weather = ({ lat, lon }) => {
  const [weather, setWeather] = useState(null);
  const API_KEY = "4f2d48f8469a7ee7fd709829653ea6c4";
  const WEATHER_API = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${API_KEY}`;

  useEffect(() => {
    axios.get(WEATHER_API)
      .then(response => {
        console.log("Weather Data:", response.data);
        setWeather(response.data);
      })
      .catch(error => console.error("Error fetching weather data:", error));
  }, [lat, lon]);

  return (
    <div>
      <h2>Current Weather</h2>
      {weather ? (
        <p>
          🌡️ Temperature: {weather.main.temp}°C <br />
          💦 Humidity: {weather.main.humidity}% <br />
          🌬️ Wind Speed: {weather.wind.speed} m/s <br />
          🌤️ Condition: {weather.weather[0].description}
        </p>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default Weather;
