import {FeatureCollection, Point} from 'geojson';

export type DeviceFeatureProps = {
  name: string;
  id: string;
};

export type DevicesGeojson = FeatureCollection<Point, DeviceFeatureProps>;

export async function loadDevicesGeojson(): Promise<DevicesGeojson> {
  // const url = new URL('../../data/Devices.json', import.meta.url);

  return await fetch("http://localhost:8000/api/devices/getall/").then(res => res.json());
}
