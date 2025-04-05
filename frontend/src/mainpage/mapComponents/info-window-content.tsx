import React, {memo} from 'react';
import {Feature, Point} from 'geojson';
import {DeviceFeatureProps} from '../devices.ts';

type InfowindowContentProps = {
  features: Feature<Point>[];
};

const numFmt = new Intl.NumberFormat();

export const InfoWindowContent = memo(({features}: InfowindowContentProps) => {
  if (features.length === 1) {
    const f = features[0];
    const props = f.properties! as DeviceFeatureProps;

    return (
      <div>
        <h4>{props.name}</h4>
        <p>
          Device ID: {props.id}
        </p>
      </div>
    );
  }

  return (
    <div>
      <h4>{numFmt.format(features.length)} devices. Zoom in to explore.</h4>

      <ul className="feature-list">
        {features.slice(0, 3).map(feature => {
          const props = feature.properties! as DeviceFeatureProps;

          return (
            <li key={feature.id} className="feature-list-item">
                {props.name}
            </li>
          );
        })}

        {features.length > 3 && (
          <li>and {numFmt.format(features.length - 3)} more.</li>
        )}
      </ul>
    </div>
  );
});