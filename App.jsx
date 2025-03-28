import React from "react";
import TrafficMap from "./components/TrafficMap";
import AirQuality from "./components/AirQuality";
import Weather from "./components/weather";
//import WaterLevels from "./components/WaterLevels";
import Alerts from "./components/Alerts";

function App() {
  return (
    <div>
      <h1>Smart City Dashboard</h1>
      <TrafficMap />
      <Weather lat={28.7041} lon={77.1025} />
      <AirQuality lat={28.7041} lon={77.1025} />
      <Alerts lat={28.7041} lon={77.1025} />
    </div>
  );
}

export default App;
