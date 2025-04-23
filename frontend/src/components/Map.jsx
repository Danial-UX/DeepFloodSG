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
import { getRoute } from "../utils/onemap";
import { loadCoveredWalkways } from "../utils/coveredWalkways";

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

  useEffect(() => {
    loadCoveredWalkways().then(setCoveredWalkways);
  }, []);

  const handleStartSelect = (result) => {
    setStartPoint([parseFloat(result.LATITUDE), parseFloat(result.LONGITUDE)]);
  };

  const handleEndSelect = (result) => {
    setEndPoint([parseFloat(result.LATITUDE), parseFloat(result.LONGITUDE)]);
  };

  const handleRoute = () => {
    if (startPoint && endPoint) {
      getRoute(
        startPoint,
        endPoint,
        routeMode,
        routePreference,
        coveredWalkways,
        setRouteData,
        setAlternateRoute
      );
    }
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
        </MapContainer>
      </Box>
    </Box>
  );
}
