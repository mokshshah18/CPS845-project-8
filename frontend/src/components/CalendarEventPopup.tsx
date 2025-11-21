import React from "react";
import { UpcomingEvent } from "../api";

interface Props {
  event: UpcomingEvent;
  onSetDestination: () => void;
  onClose: () => void;
}

const CalendarEventPopup: React.FC<Props> = ({
  event,
  onSetDestination,
  onClose,
}) => {
  // Format the time for display
  const formatTime = (timeString: string) => {
    try {
      const date = new Date(timeString);
      return date.toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
    } catch {
      return timeString;
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.6)",
        zIndex: 1000,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "20px",
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "24px",
          maxWidth: "400px",
          width: "100%",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
          position: "relative",
        }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          style={{
            position: "absolute",
            top: "12px",
            right: "12px",
            background: "none",
            border: "none",
            fontSize: "24px",
            cursor: "pointer",
            color: "#666",
            padding: "4px 8px",
            lineHeight: "1",
          }}
          title="Close"
        >
          ×
        </button>

        {/* Event name */}
        <h3
          style={{
            margin: "0 0 12px 0",
            fontSize: "20px",
            fontWeight: "600",
            color: "#333",
          }}
        >
          {event.name}
        </h3>

        {/* Event time */}
        <p
          style={{
            margin: "0 0 8px 0",
            fontSize: "16px",
            color: "#666",
          }}
        >
          {formatTime(event.start_time)}
        </p>

        {/* Event location (if available) */}
        {event.location && (
          <p
            style={{
              margin: "8px 0 20px 0",
              fontSize: "14px",
              color: "#888",
              fontStyle: "italic",
            }}
          >
            📍 {event.location}
          </p>
        )}

        {/* Set Destination button */}
        <button
          onClick={onSetDestination}
          style={{
            width: "100%",
            padding: "12px 24px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "6px",
            fontSize: "16px",
            fontWeight: "500",
            cursor: "pointer",
            transition: "background-color 0.2s",
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = "#0056b3";
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = "#007bff";
          }}
        >
          Set Destination
        </button>
      </div>
    </div>
  );
};

export default CalendarEventPopup;

