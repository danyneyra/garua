import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { Icon } from "leaflet";
import "leaflet/dist/leaflet.css";
import markerIconPng from "@/assets/marker.png";

interface MiniMapProps {
  readonly latitude: number;
  readonly longitude: number;
  readonly zoom?: number;
  readonly markerText?: string;
}

const customIcon = new Icon({
  iconUrl: markerIconPng,
  iconSize: [41, 41],
  iconAnchor: [20, 10],
});

export default function MiniMap({ latitude, longitude, zoom=14, markerText="Estación Metereológica" }: MiniMapProps) {
  const position: [number, number] = [latitude, longitude];

  return (
    <div className="h-[180px] w-full md:w-[300px] md:h-[200px] z-20">
      <MapContainer
        center={position}
        zoom={zoom}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%", borderRadius: "12px" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <Marker position={position} icon={customIcon}>
          <Popup>
            {markerText}
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
