import React, { useEffect, useState } from "react";
import { getLocations, getRoute } from "./api";
import LocationSelector from "./components/LocationSelector";
import RouteDisplay from "./components/RouteDisplay";
import MapView from "./components/MapView";

export default function App() {
  const [locations, setLocations] = useState<any[]>([]);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [route, setRoute] = useState<any>(null);

  useEffect(() => {
    getLocations().then(setLocations);
  }, []);

  async function handleGetRoute() {
    const res = await getRoute(start, end);
    setRoute(res.route);
  }

  return (
    <div className="container">
      <h1>Campus Navigator</h1>
      <LocationSelector
        locations={locations}
        start={start}
        end={end}
        onStartChange={setStart}
        onEndChange={setEnd}
        onSubmit={handleGetRoute}
      />
      {route && <RouteDisplay route={route} />}
      <MapView locations={locations} route={route} />
    </div>
  );
}
