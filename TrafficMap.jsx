import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { fetchTrafficData } from "../api/fetchTrafficData"; 

const TrafficMap = () => {
  const [trafficIncidents, setTrafficIncidents] = useState([]);

  const lat = 28.7041;  // Delhi Latitude
  const lon = 77.1025;  // Delhi Longitude

  useEffect(() => {
    const getTrafficData = async () => {
      const incidents = await fetchTrafficData(lat, lon);
      setTrafficIncidents(incidents);
    };
    getTrafficData();
  }, []);

  return (
    <div>
      <h2>Real-Time Traffic Map</h2>
      <MapContainer center={[lat, lon]} zoom={12} style={{ height: "500px", width: "100%" }}>
        {/* Base Map */}
        <TileLayer 
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        {/* TomTom Traffic Layer */}
        <TileLayer 
          url={`https://{s}.api.tomtom.com/map/1/tile/traffic/relative0/{z}/{x}/{y}.png?key="jCpyeIRapGEyeJWrSt8fz2wyOYzMshBu"`}
          attribution="&copy; TomTom Traffic API"
        />

        {/* Show Traffic Incidents */}
        {trafficIncidents.map((incident, index) => (
          <Marker key={index} position={[incident.latitude, incident.longitude]}>
            <Popup>
              <b>{incident.type}</b> <br />
              {incident.delaySeconds ? `Delay: ${incident.delaySeconds} sec` : "No delay data"}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default TrafficMap;
