import React from "react";

interface Props {
  locations: any[];
  route: any;
}

export default function MapView({ locations, route }: Props) {
  return (
    <div
      className="map"
      style={{
        width: "100%",
        height: "400px",
        background: "url('/campus-map.png') center/contain no-repeat",
        border: "1px solid #ccc",
      }}
    >
      {/* later: overlay markers and route lines */}
    </div>
  );
}
