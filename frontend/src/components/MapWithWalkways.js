import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
 import "leaflet/dist/leaflet.css";
 import { useEffect, useState } from "react";
 
 export default function MapWithWalkways() {
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