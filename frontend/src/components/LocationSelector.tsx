import React from "react";

interface Props {
  locations: any[];
  start: string;
  end: string;
  onStartChange: (v: string) => void;
  onEndChange: (v: string) => void;
  onSubmit: () => void;
}

export default function LocationSelector({
  locations,
  start,
  end,
  onStartChange,
  onEndChange,
  onSubmit,
}: Props) {
  return (
    <div className="selector">
      <select value={start} onChange={(e) => onStartChange(e.target.value)}>
        <option value="">Start</option>
        {locations.map((loc) => (
          <option key={loc.id} value={loc.id}>
            {loc.name}
          </option>
        ))}
      </select>

      <select value={end} onChange={(e) => onEndChange(e.target.value)}>
        <option value="">Destination</option>
        {locations.map((loc) => (
          <option key={loc.id} value={loc.id}>
            {loc.name}
          </option>
        ))}
      </select>

      <button onClick={onSubmit}>Get Route</button>
    </div>
  );
}
