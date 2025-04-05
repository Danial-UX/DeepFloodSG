import React, {useCallback, useEffect, useState} from 'react';
import {APIProvider, InfoWindow, Map} from '@vis.gl/react-google-maps';
import './Map.css'; // Import the CSS file

import {ClusteredMarkers} from './mapComponents/clustered-markers.tsx';

import ControlPanel from './control-panel.tsx';
import {loadDevicesGeojson, DevicesGeojson} from './devices.ts';

// import './style.css';
import {Feature, Point} from 'geojson';
import {InfoWindowContent} from './mapComponents/info-window-content.tsx';


const MapWindow = ({filteredFeatures, onVisibleFeaturesChange}) => {
    const center = { lat: 1.3908, lng: 103.8170 }; // set as singapore
    const zoom = 15; // original zoom level

    // const googleMapsApiKey = ""; // for dev
    // uncomment google maps api key for prod
    const googleMapsApiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || "";

    const [geojson, setGeojson] = useState<DevicesGeojson | null>(null);
    const [numClusters, setNumClusters] = useState(0);
  
    useEffect(() => {
      void loadDevicesGeojson().then(data => setGeojson(data));
    }, []);
  
    const [infowindowData, setInfowindowData] = useState<{
      anchor: google.maps.marker.AdvancedMarkerElement;
      features: Feature<Point>[];
    } | null>(null);
  
    const handleInfoWindowClose = useCallback(
      () => setInfowindowData(null),
      [setInfowindowData]
    );

    const handleBoundsChange = useCallback((map: google.maps.Map) => {
      const bounds = map.getBounds() || null;
      // console.log('bounds', bounds);
      // console.log('geojsonData', geojson);
      //console.log('filteredFeatures', filteredFeatures);
      if (geojson && bounds) {
        const visibleFeatures = geojson.features.filter(feature => {
          const coords = feature.geometry.coordinates;
          return bounds.contains({lat: coords[1], lng: coords[0]});
        });
        // console.log('visibleFeatures', visibleFeatures);
        onVisibleFeaturesChange(visibleFeatures);
      } else {
        // console.log('emptyVisibleFeatures', []);
        onVisibleFeaturesChange([]);
      }
    }, [onVisibleFeaturesChange]);

    return (
      <APIProvider apiKey={googleMapsApiKey} version={'beta'}>
      <Map
        mapId={'adb2f98d5d3ce48'}
        defaultCenter={center}
        defaultZoom={zoom}
        mapTypeId={'satellite'}
        gestureHandling={'greedy'}
        disableDefaultUI
        onClick={() => setInfowindowData(null)}
        className={'custom-marker-clustering-map'}
        onBoundsChanged={({map})=>handleBoundsChange(map)}>
        {geojson && (
          <ClusteredMarkers
            geojson={{type: 'FeatureCollection', features: filteredFeatures || []}}
            setNumClusters={setNumClusters}
            setInfowindowData={setInfowindowData}
          />
        )}

        {infowindowData && (
          <InfoWindow
            onCloseClick={handleInfoWindowClose}
            anchor={infowindowData.anchor}>
            <InfoWindowContent features={infowindowData.features} />
          </InfoWindow>
        )}
      </Map>

      <ControlPanel
        numClusters={numClusters}
        numFeatures={geojson?.features.length || 0}
      />
    </APIProvider>
    )
};

export default MapWindow;