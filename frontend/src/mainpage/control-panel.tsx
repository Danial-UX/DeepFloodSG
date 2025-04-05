import * as React from 'react';

type ControlPanelProps = {
  numClusters: number;
  numFeatures: number;
};

const numberFormat = new Intl.NumberFormat();

function ControlPanel(props: ControlPanelProps) {
  return (
    <div className="control-panel custom-marker-clustering-control-panel">
      <ul>
        <li>
          <strong>{numberFormat.format(props.numFeatures)}</strong> Devices
          loaded
        </li>
        <li>
          <strong>{props.numClusters}</strong> Devices rendered
        </li>
      </ul>
    </div>
  );
}

export default React.memo(ControlPanel);
