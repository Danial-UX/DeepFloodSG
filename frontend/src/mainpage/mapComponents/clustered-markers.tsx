import React, {useCallback, useEffect} from 'react';
import Supercluster, {ClusterProperties} from 'supercluster';
import {FeaturesClusterMarker} from './features-cluster-marker.tsx';
import {FeatureMarker} from './feature-marker.tsx';
import {useSupercluster} from '../../hooks/use-supercluster.ts';
import {Feature, FeatureCollection, GeoJsonProperties, Point} from 'geojson';

type ClusteredMarkersProps = {
  geojson: FeatureCollection<Point>;
  setNumClusters: (n: number) => void;
  setInfowindowData: (
    data: {
      anchor: google.maps.marker.AdvancedMarkerElement;
      features: Feature<Point>[];
    } | null
  ) => void;
};

const superclusterOptions: Supercluster.Options<
  GeoJsonProperties,
  ClusterProperties
> = {
  extent: 256,
  radius: 50,
  maxZoom: 15
};

export const ClusteredMarkers = ({
  geojson,
  setNumClusters,
  setInfowindowData
}: ClusteredMarkersProps) => {
  const {clusters, getLeaves} = useSupercluster(geojson, superclusterOptions);

  useEffect(() => {
    setNumClusters(clusters.length);
  }, [setNumClusters, clusters.length]);

  const handleClusterClick = useCallback(
    (marker: google.maps.marker.AdvancedMarkerElement, clusterId: number) => {
      setInfowindowData(null); // Clear existing InfoWindow
      const leaves = getLeaves(clusterId);
      setTimeout(() => {
        setInfowindowData({anchor: marker, features: leaves});
      }, 0);
    },
    [getLeaves, setInfowindowData]
  );

  const handleMarkerClick = useCallback(
    (marker: google.maps.marker.AdvancedMarkerElement, featureId: string) => {
      setInfowindowData(null); // Clear existing InfoWindow
      const feature = clusters.find(
        feat => feat.id === featureId
      ) as Feature<Point>;
      setTimeout(() => {
        setInfowindowData({anchor: marker, features: [feature]});
      }, 0);
    },
    [clusters, setInfowindowData]
  );

  return (
    <>
      {clusters.map(feature => {
        const [lng, lat] = feature.geometry.coordinates;

        const clusterProperties = feature.properties as ClusterProperties;
        const isCluster: boolean = clusterProperties.cluster;

        return isCluster ? (
          <FeaturesClusterMarker
            key={feature.id}
            clusterId={clusterProperties.cluster_id}
            position={{lat, lng}}
            size={clusterProperties.point_count}
            sizeAsText={String(clusterProperties.point_count_abbreviated)}
            onMarkerClick={handleClusterClick}
          />
        ) : (
          <FeatureMarker
            key={feature.id}
            featureId={feature.id as string}
            position={{lat, lng}}
            onMarkerClick={handleMarkerClick}
            status={(feature.properties as {status: string}).status || 'inactive'}
          />
        );
      })}
    </>
  );
};
