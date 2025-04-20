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

import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";

export default function Map() {
    const [data, setData] = useState(null);    

    useEffect(() => {
        // Load both GeoJSON files in parallel
        Promise.all([
            fetch("/data/covered_walkways.geojson").then(res => res.json()),
            fetch("/data/covered_walkways_west.geojson").then(res => res.json())
        ])
        .then(([originalData, westernData]) => {
            // Merge features from both files
            const mergedData = {
                type: "FeatureCollection",
                features: [
                    ...originalData.features,
                    ...westernData.features
                ]
            };
            setData(mergedData);
        })
        .catch(error => console.error("Error loading GeoJSON:", error));
    }, []);

    return (
        <MapContainer center={[1.3908, 103.8170]} zoom={13} style={{ height: "60vh", width: "80vw" }} maxZoom={19}>
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {!data && <p>Loading...</p>}
            {data && (
                <GeoJSON
                    data={data}
                    style={{
                        color: "#0000ff", 
                        weight: 2,
                        opacity: 1
                    }}
                    onEachFeature={(feature, layer) => {
                        const props = feature.properties;
                        let label = `Covered walkway`;
                        if (props.name) label = props.name;
                        layer.bindPopup(label);
                    }}
                />
            )}
        </MapContainer>
    );
}
