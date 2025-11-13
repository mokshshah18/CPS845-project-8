import React, { useState, useRef, useEffect } from "react";
import {
    GoogleMap,
    LoadScript,
    Marker,
    DirectionsRenderer,
} from "@react-google-maps/api";
import { BrowserMultiFormatReader } from "@zxing/browser";
import UserDbDebug from "./components/UserDbDebug";
import "./CampusNavigator.css";

const CampusNavigator: React.FC = () => {
    const [currloc, setcurrloc] = useState<{ lat: number; lng: number } | null>(null);
    const [origin, setorigin] = useState("");
    const [destination, setdest] = useState("");
    const [dirs, setdirs] = useState<google.maps.DirectionsResult | null>(null);
    const [recent, setrecent] = useState<string[]>([]);
    const [scanning, setscanning] = useState(false);
    const [showDebug, setShowDebug] = useState(false);
    const [showIncidentMenu, setShowIncidentMenu] = useState(false);

    const videoRef = useRef<HTMLVideoElement | null>(null);
    const codeReaderRef = useRef<BrowserMultiFormatReader | null>(null);

    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_KEY;

    const gpshandle = () => {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const coords = { lat: pos.coords.latitude, lng: pos.coords.longitude };
                setcurrloc(coords);
                setorigin(`${coords.lat}, ${coords.lng}`);
            }
        );
    };

    const startscan = async () => {
        setscanning(true);
        codeReaderRef.current = new BrowserMultiFormatReader();

        const videoInputDevices = await BrowserMultiFormatReader.listVideoInputDevices();
        const deviceId = videoInputDevices[0].deviceId;
        const result = await codeReaderRef.current.decodeOnceFromVideoDevice(deviceId, videoRef.current!);
        setorigin(result.getText());
        setscanning(false);

        if (videoRef.current && videoRef.current.srcObject) {
            const stream = videoRef.current.srcObject as MediaStream;
            stream.getTracks().forEach((track) => track.stop());
            videoRef.current.srcObject = null;
        }
    };

    const getorigin = (): google.maps.LatLngLiteral | string => {
        if (origin.includes(",")) {
            const parts = origin.split(",").map((p) => parseFloat(p.trim()));
            if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
                return { lat: parts[0], lng: parts[1] };
            }
        }
        return origin;
    };

    useEffect(() => {
        const getdirs = async () => {
            if (!destination || (!origin && !currloc)) return;

            const service = new google.maps.DirectionsService();
            const result = await service.route({
                origin: getorigin(),
                destination: destination,
                travelMode: google.maps.TravelMode.WALKING,
            });
            setdirs(result);
        };
        getdirs();
    }, [origin, destination, currloc]);

    const navbutton = () => {
        if (!destination) return alert("Enter a destination!");
        if (!origin && !currloc) return alert("Origin unknown");

        setrecent((prev) =>
            [destination, ...prev.filter((d) => d !== destination)].slice(0, 5)
        );
    };

    return (
        <div className="full-container">
            {showDebug && <UserDbDebug onClose={() => setShowDebug(false)} />}

            <div className="top-bar">
                <div className="left-controls">
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <h1>Campus Navigator</h1>
                        <button
                            onClick={() => setShowDebug(true)}
                            className="debug-btn"
                            title="Open User DB Debug Panel"
                        >
                            Debug DB
                        </button>
                    </div>
                </div>

                <div className="right-controls">
                    <button className="top-btn">Saved Searches</button>
                    <button className="top-btn">Heatmap</button>
                    <button className="top-btn">View Notifications</button>
                    <button className="top-btn">Sync Schedule</button>

                    <div
                        className="incident-dropdown"
                        onMouseEnter={() => setShowIncidentMenu(true)}
                        onMouseLeave={() => setShowIncidentMenu(false)}
                    >
                        <button className="top-btn">Report Incidents ▾</button>
                        {showIncidentMenu && (
                        <div className="incident-menu">
                            <button onClick={() => (window.location.href = "/report-student.html")}>
                            Report Incident (Student)
                            </button>
                            <button onClick={() => (window.location.href = "/faculty-login.html")}>
                            Send Alert (Faculty)
                            </button>
                        </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="controls">
                <div className="gps-buttons">
                    <button className="gps" onClick={gpshandle}>
                        Use my Current Location
                    </button>
                    <button className="gps" onClick={startscan}>
                        Scan QR
                    </button>
                </div>

                <div className="inputs">
                    <input
                        type="text"
                        placeholder="Origin (Enter or click Use my Current Location)"
                        value={origin}
                        onChange={(e) => setorigin(e.target.value)}
                    />

                    <button
                        className="swap"
                        onClick={() => {
                            const temp = origin;
                            setorigin(destination);
                            setdest(temp);
                        }}
                        title="Swap Origin and Destination"
                    >
                        ⇄
                    </button>

                    <input
                        type="text"
                        placeholder="Destination"
                        value={destination}
                        onChange={(e) => setdest(e.target.value)}
                    />

                    <button className="navigate" onClick={navbutton}>
                        Navigate
                    </button>
                </div>

                {recent.length > 0 && (
                    <div>
                        <h3>Recent Searches</h3>
                        <ul>
                            {recent.map((s) => (
                                <li key={s} onClick={() => setdest(s)}>
                                    {s}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {scanning && (
                    <div className="scanner">
                        <p>Scanning QR code</p>
                        <video ref={videoRef} autoPlay />
                    </div>
                )}
            </div>

            <div className="map-wrapper">
                <LoadScript googleMapsApiKey={apiKey}>
                    <GoogleMap
                        mapContainerStyle={{ width: "100%", height: "100%" }}
                        center={currloc || { lat: 43.6577, lng: -79.3788 }}
                        zoom={17}
                        options={{
                            zoomControl: true,
                            scrollwheel: true,
                            draggable: true,
                        }}
                    >
                        {currloc && <Marker position={currloc} />}

                        {dirs && (
                            <DirectionsRenderer
                                directions={dirs}
                                options={{ preserveViewport: true }}
                            />
                        )}
                    </GoogleMap>
                </LoadScript>
            </div>
        </div>
    );
};

export default CampusNavigator;
