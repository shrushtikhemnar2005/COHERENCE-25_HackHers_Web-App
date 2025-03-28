import React, { useState, useEffect } from "react";
import axios from "axios";

const Alerts = ({ lat, lon }) => {
  const [alerts, setAlerts] = useState([]);

  const API_KEY = "4f2d48f8469a7ee7fd709829653ea6c4";
  const ALERTS_API = `https://api.openweathermap.org/data/2.5/onecall?lat=${lat}&lon=${lon}&exclude=current,minutely,hourly,daily&appid=${API_KEY}`;

  useEffect(() => {
    axios.get(ALERTS_API)
      .then(response => {
        console.log("Alerts Data:", response.data);
        setAlerts(response.data.alerts || []);
      })
      .catch(error => console.error("Error fetching alerts:", error));
  }, [lat, lon]);

  return (
    <div>
      <h2>Emergency Alerts</h2>
      {alerts.length > 0 ? (
        alerts.map((alert, index) => (
          <p key={index}>⚠️ {alert.event}: {alert.description}</p>
        ))
      ) : (
        <p>No active alerts</p>
      )}
    </div>
  );
};

export default Alerts;
