import axios from "axios";

const TOMTOM_API_KEY =  "jCpyeIRapGEyeJWrSt8fz2wyOYzMshBu";  

export const fetchTrafficData = async (lat, lon) => {
  const url = `https://api.tomtom.com/traffic/services/4/incidentDetails/s3/${lon},${lat},20/0/json?key=${TOMTOM_API_KEY}`;
  
  try {
    const response = await axios.get(url);
    return response.data.incidents;  
  } catch (error) {
    console.error("Error fetching traffic data:", error);
    return [];
  }
};
