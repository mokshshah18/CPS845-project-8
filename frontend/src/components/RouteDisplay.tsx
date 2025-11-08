import React from "react";

export default function RouteDisplay({ route }: { route: any }) {
  return (
    <div className="route-display">
      <h3>Directions</h3>
      <ul>
        {route.steps.map((step: string, i: number) => (
          <li key={i}>{step}</li>
        ))}
      </ul>
    </div>
  );
}
