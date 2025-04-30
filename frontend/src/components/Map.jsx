// covered_walkways was filtered with
// [out:json][timeout:25];
// // within Singapore bounding box
// (
//   way["highway"="footway"]["covered"="yes"](1.22,103.77,1.47,104.05);
//   way["footway"="covered"](1.22,103.77,1.47,104.05);
// );
// out body;
// >;
// out skel qt;

// covered_walkways_west was filtered with
// [out:json][timeout:90];
// (
//   // Expanded Western Singapore (includes Woodlands, Kranji, Tuas, Jurong)
//   way["highway"="footway"]["covered"="yes"](1.25,103.60,1.45,103.80);
//   way["footway"="covered"](1.25,103.60,1.45,103.80);
//   way["roof"="yes"](1.25,103.60,1.45,103.80);
//   way["tunnel"="covered"](1.25,103.60,1.45,103.80);
// );
// out body;
// >;
// out skel qt;

import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  GeoJSON,
} from "react-leaflet";
import {
  Box,
  Button,
  MenuItem,
  Select,
  Stack,
  FormControl
} from "@mui/material";
import SearchBar from './SearchBar';
import { getRoute, getFloodPredictions } from "../utils/onemap";
import { loadCoveredWalkways } from "../utils/coveredWalkways";
import FloodRiskLegend from './FloodRiskLegend';
import { CircleMarker } from 'react-leaflet';

export default function Map() {
  const [startPoint, setStartPoint] = useState(null);
  const [endPoint, setEndPoint] = useState(null);
  const [startInput, setStartInput] = useState("");
  const [endInput, setEndInput] = useState("");
  const [routeData, setRouteData] = useState(null);
  const [alternateRoute, setAlternateRoute] = useState(null);
  const [routeMode, setRouteMode] = useState("walk");
  const [routePreference, setRoutePreference] = useState("fastest");
  const [coveredWalkways, setCoveredWalkways] = useState(null);
  const [floodRisks, setFloodRisks] = useState(null);

  useEffect(() => {
    loadCoveredWalkways().then(setCoveredWalkways);
  }, []);

  const handleStartSelect = (result) => {
    setStartPoint([parseFloat(result.LATITUDE), parseFloat(result.LONGITUDE)]);
  };

  const handleEndSelect = (result) => {
    setEndPoint([parseFloat(result.LATITUDE), parseFloat(result.LONGITUDE)]);
  };

  const testApiConnection = async () => {
    try {
      const testResponse = await fetch('http://localhost:8000/api/predict_flood_risk/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ route: [{ lat: 1.3521, lon: 103.8198 }] })
      });
      console.log("API connection test:", await testResponse.json());
    } catch (error) {
      console.error("API connection failed:", error);
    }
  };

  useEffect(() => {
    testApiConnection();
  }, []);

  const handleRoute = async () => {
    if (startPoint && endPoint) {
      const routeCoords = await getRoute(
        startPoint,
        endPoint,
        routeMode,
        routePreference,
        coveredWalkways,
        setRouteData,
        setAlternateRoute
      );
        
      if (routeCoords) {
        console.log("Sending coordinates to flood prediction:", routeCoords);
        const predictions = await getFloodPredictions(routeCoords);
        console.log("Flood predictions received:", predictions);
        setFloodRisks(predictions);
      }
    }
  };

  // useEffect(() => {
  //   const fetchFloodPredictions = async () => {
  //     if (routeData) {
  //       console.log("Route data:", routeData);
  //       const coordinates = routeData.features[0].geometry.coordinates;
  //       const predictions = await getFloodPredictions(coordinates);
  //       console.log("Flood predictions:", predictions);
  //       setFloodRisks(predictions);
  //     }
  //   };

  //   fetchFloodPredictions();
  // }, [routeData]);

  const renderFloodRiskMarkers = () => {
    if (!floodRisks || floodRisks.error) {
      console.log("No flood predictions available:", floodRisks?.error);
      return null;
    }
  
    const predictions = floodRisks.predictions || [];
    console.log(`Rendering ${predictions.length} flood risk markers`);
  
    return predictions.map((point, index) => {
      try {
        const lat = point.lat ?? point[0];
        const lon = point.lon ?? point[1];
        const risk = point.risk ?? point[2] ?? 0;
        
        if (typeof lat !== 'number' || typeof lon !== 'number' || typeof risk !== 'number') {
          console.warn("Invalid prediction point format:", point);
          return null;
        }
  
        if (risk <= 0.3) return null;
  
        const color = risk > 0.7 ? 'red' : risk > 0.5 ? 'orange' : 'yellow';
        
        return (
          <CircleMarker
            key={`flood-${index}-${lat}-${lon}`}
            center={[lat, lon]}
            radius={5 + (risk * 10)}
            pathOptions={{
              color: color,
              fillColor: color,
              fillOpacity: 0.8
            }}
          >
            <Popup>
              <div>
                <strong>Flood Risk</strong><br />
                Probability: {(risk * 100).toFixed(1)}%<br />
                Location: {lat.toFixed(6)}, {lon.toFixed(6)}
              </div>
            </Popup>
          </CircleMarker>
        );
      } catch (error) {
        console.error("Error rendering flood marker:", error, point);
        return null;
      }
    });
  };

  const swapPoints = () => {
    const tempPoint = startPoint;
    const tempInput = startInput;
    setStartPoint(endPoint);
    setEndPoint(tempPoint);
    setStartInput(endInput);
    setEndInput(tempInput);
  };

  return (
    <Box p={2}>
        <SearchBar
            label="Start Location"
            value={startInput}
            setValue={setStartInput}
            onSelect={handleStartSelect}
            onSwap={swapPoints}
        />
        <SearchBar
            label="End Location"
            value={endInput}
            setValue={setEndInput}
            onSelect={handleEndSelect}
        />

        <Stack direction="row" alignItems="center" paddingTop="20px" gap={2}>
            <FormControl size="small">
                <Select
                value={routeMode}
                fullWidth
                onChange={(e) => setRouteMode(e.target.value)}
                >
                    <MenuItem value="walk">Walk</MenuItem>
                    <MenuItem value="drive">Drive</MenuItem>
                    <MenuItem value="cycle">Cycle</MenuItem>
                </Select>   
            </FormControl>

            <FormControl size="small">
                {routeMode === "walk" && (
                    <Select
                    value={routePreference}
                    fullWidth
                    onChange={(e) => setRoutePreference(e.target.value)}
                    >
                    <MenuItem value="fastest">Fastest</MenuItem>
                    <MenuItem value="sheltered">Most Sheltered</MenuItem>
                    </Select>
                )}
            </FormControl>


            <FormControl size="small">
                <Button
                    variant="contained"
                    fullWidth
                    onClick={handleRoute}
                    disabled={!startPoint || !endPoint}
                    sx={{
                        "& .MuiOutlinedInput-root": {
                            "& fieldset": {
                            borderColor: "#007bff",
                            },
                            "&:hover fieldset": {
                            borderColor: "#0056b3",
                            },
                            "&.Mui-focused fieldset": {
                            borderColor: "#007bff",
                            },
                        },
                    }}
                    >
                    Get Route
                </Button>
            </FormControl>
        </Stack>

      <Box mt={3}>
        <MapContainer
          center={[1.3521, 103.8198]}
          zoom={13}
          style={{ height: "60vh", width: "70vw" }}
          maxZoom={19}
        >
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          {routeData && (
            <GeoJSON data={routeData} style={{ color: "green", weight: 4 }} />
          )}

          {alternateRoute && (
            <GeoJSON
              data={alternateRoute}
              style={{ color: "orange", weight: 4, dashArray: "4" }}
            />
          )}

          {coveredWalkways && (
            <GeoJSON
              data={coveredWalkways}
              style={{ color: "#007BFF", weight: 2, opacity: 1 }}
              onEachFeature={(feature, layer) => {
                const props = feature.properties;
                let label = `Covered walkway`;
                if (props.name) label = props.name;
                layer.bindPopup(label);
              }}
            />
          )}
          {renderFloodRiskMarkers()}
          <FloodRiskLegend />
        </MapContainer>
      </Box>
    </Box>
  );
}
