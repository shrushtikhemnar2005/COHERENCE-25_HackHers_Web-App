import { useState, useEffect } from "react";
import AirQualityChart from "./AirQuality";
import TrafficMap from "./TrafficMap";

function Dashboard() {
  return (
    <div className="dashboard">
      <AirQualityChart />
      <TrafficMap />
    </div>
  );
}

export default Dashboard;
