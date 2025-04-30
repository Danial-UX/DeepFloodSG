import { buffer, booleanIntersects } from "@turf/turf";

export async function getOneMapToken() {
    const payload = {
      email: process.env.REACT_APP_ONEMAP_EMAIL,
      password: process.env.REACT_APP_ONEMAP_PASSWORD
    };
    
    const res = await fetch('https://www.onemap.gov.sg/api/auth/post/getToken', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  
    if (!res.ok) {
      const errorText = await res.text();  // Get the error response body for debugging
      console.error('Failed to fetch token, Status:', res.status);
      console.error('Error Response:', errorText);
      throw new Error(`Failed to fetch token, Status: ${res.status}`);
    }
  
    const data = await res.json();
    return `Bearer ${data.access_token}`;
}

export async function handleSearch(searchQuery, setSearchResults) {
    if (!searchQuery?.trim()) {
      setSearchResults([]);
      return;
    }
  
    const token = getOneMapToken();
    const url = `https://www.onemap.gov.sg/api/common/elastic/search?searchVal=${encodeURIComponent(searchQuery)}&returnGeom=Y&getAddrDetails=Y&pageNum=1`;
  
    try {
      const res = await fetch(url, {
        headers: { Authorization: token }
      });
      const data = await res.json();  
      setSearchResults(data?.results?.length ? data.results : []);
    } catch (error) {
      console.error("Search error:", error);
      setSearchResults([]);
    }
}

const decodePolyline = (encoded) => {
    let points = [];
    let index = 0, lat = 0, lng = 0;

    while (index < encoded.length) {
      let b, shift = 0, result = 0;
      do {
        b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      const deltaLat = (result & 1) ? ~(result >> 1) : result >> 1;
      lat += deltaLat;

      shift = 0;
      result = 0;
      do {
        b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      const deltaLng = (result & 1) ? ~(result >> 1) : result >> 1;
      lng += deltaLng;

      points.push([lat / 1e5, lng / 1e5]);
    }
    return points;
};

function convertToGeoJSON(coords) {
    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: {
            type: "LineString",
            coordinates: coords.map(([lat, lng]) => [lng, lat]), // GeoJSON uses [lng, lat]
          },
          properties: {},
        },
      ],
    };
}

function suggestAlternates(routeFeatures, coveredWalkways) {
    if (!routeFeatures || !coveredWalkways) return [];
  
    const routeLine = routeFeatures[0];
  
    // Create a small buffer around the route (e.g. 30 meters)
    const buffered = buffer(routeLine, 0.03, { units: "kilometers" });
  
    const nearbyWalkways = coveredWalkways.features.filter(walkway =>
      booleanIntersects(buffered, walkway)
    );
  
    return nearbyWalkways;
}
  
export async function getFloodPredictions(routeCoordinates) {
  try {
    // Sample coordinates (every 10th point)
    const sampledCoords = routeCoordinates
      .filter((_, i) => i % 10 === 0)
      .map(coord => ({ lat: coord[0], lon: coord[1] }));

    console.log("Sending coordinates:", sampledCoords.length, sampledCoords[0]);

    const response = await fetch('http://localhost:8000/api/predict_flood_risk/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ route: sampledCoords })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error);
    }

    const data = await response.json();
    console.log("Raw response:", data);

    // Handle different response formats
    const predictions = (
      Array.isArray(data) ? data :
      data.predictions ?? data.predictions ?? // Handle typos
      Object.values(data)
    ).filter(Boolean);

    return {
      predictions: predictions.map(p => ({
        lat: p.lat ?? p.latitude ?? p[0],
        lon: p.lon ?? p.longitude ?? p[1],
        risk: parseFloat(p.risk ?? p.probability ?? p[2] ?? 0)
      }))
    };

  } catch (error) {
    console.error('Flood prediction error:', error);
    return { error: error.message, predictions: [] };
  }
}

export async function getRoute(
    startPoint,
    endPoint,
    routeMode,
    routePreference,
    coveredWalkways,
    setRouteData,
    setAlternateRoute
  ) {
    if (!startPoint || !endPoint || !routeMode) return;
  
    const token = await getOneMapToken();
    const url = `https://www.onemap.gov.sg/api/public/routingsvc/route?start=${startPoint[0]},${startPoint[1]}&end=${endPoint[0]},${endPoint[1]}&routeType=${routeMode}`;

    try {
      const res = await fetch(url, {
        headers: { Authorization: token }
      });
  
      const data = await res.json();
      console.log("data:", data);
  
      if (!data?.route_geometry) {
        console.warn("No route found.");
        setRouteData(null);
        setAlternateRoute(null);
        return;
      }
  
      const decodedCoords = decodePolyline(data.route_geometry);
      //console.log("Decoded coordinates:", decodedCoords);
      const geoJSON = convertToGeoJSON(decodedCoords);
      //console.log("setting route data:", geoJSON);
      setRouteData(geoJSON);
  
      if (routeMode === "walk" && routePreference === "sheltered" && coveredWalkways) {
        const filtered = suggestAlternates(geoJSON.features, coveredWalkways);
        setAlternateRoute({
          type: "FeatureCollection",
          features: filtered
        });
      } else {
        setAlternateRoute(null);
      }
      return decodedCoords;
    } catch (error) {
      console.error("Error fetching route:", error);
      setRouteData(null);
      setAlternateRoute(null);
    }
}  