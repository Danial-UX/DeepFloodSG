import React, {useCallback} from 'react';
import {
  AdvancedMarker,
  AdvancedMarkerAnchorPoint,
  useAdvancedMarkerRef
} from '@vis.gl/react-google-maps';
import {DeviceSvg} from './device-svg.tsx';

type TreeMarkerProps = {
  position: google.maps.LatLngLiteral;
  featureId: string;
  onMarkerClick?: (
    marker: google.maps.marker.AdvancedMarkerElement,
    featureId: string
  ) => void;
  status: string;
};

export const FeatureMarker = ({
  position,
  featureId,
  onMarkerClick,
  status
}: TreeMarkerProps) => {
  const [markerRef, marker] = useAdvancedMarkerRef();
  const handleClick = useCallback(
    () => onMarkerClick && onMarkerClick(marker!, featureId),
    [onMarkerClick, marker, featureId]
  );
  const markerColor = status === 'active' ? '#00FF00' : '#FF3131';

  return (
    <AdvancedMarker
      ref={markerRef}
      position={position}
      onClick={handleClick}
      anchorPoint={AdvancedMarkerAnchorPoint.CENTER}
      className={'marker feature'}
      style={{color: markerColor}}>
      <DeviceSvg />
    </AdvancedMarker>
  );
};
