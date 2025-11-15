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
import { Incident, getIncidents } from "./api";

// Score how safe a route is based on distance to incidents
function computeRouteIncidentScore(
    route: google.maps.DirectionsRoute,
    incidentPoints: { lat: number; lng: number }[]
): { score: number; incidentsNearRoute: number; travelTimeMinutes: number } {
    // If geometry not available, just use travel time
    if (!window.google || !google.maps.geometry) {
        const totalDurationSec =
            route.legs?.reduce(
                (sum, leg) => sum + (leg.duration?.value || 0),
                0
            ) ?? 0;
        return {
            score: totalDurationSec,
            incidentsNearRoute: 0,
            travelTimeMinutes: totalDurationSec / 60,
        };
    }

    // Larger radius + big penalties to strongly prefer routes away from incidents
    const dangerRadiusMeters = 80;
    let incidentsNearRoute = 0;

    for (const leg of route.legs || []) {
        for (const step of leg.steps || []) {
            const path = step.path || [];
            for (const point of path) {
                for (const inc of incidentPoints) {
                    const d =
                        google.maps.geometry.spherical.computeDistanceBetween(
                            point,
                            new google.maps.LatLng(inc.lat, inc.lng)
                        );
                    if (d <= dangerRadiusMeters) {
                        incidentsNearRoute++;
                        break;
                    }
                }
            }
        }
    }

    const totalDurationSec =
        route.legs?.reduce(
            (sum, leg) => sum + (leg.duration?.value || 0),
            0
        ) ?? 0;

    const penaltySeconds = incidentsNearRoute * 15 * 60; 
    const score = totalDurationSec + penaltySeconds;

    return {
        score,
        incidentsNearRoute,
        travelTimeMinutes: totalDurationSec / 60,
    };
}

const CampusNavigator: React.FC = () => {
    const [currloc, setcurrloc] =
        useState<{ lat: number; lng: number } | null>(null);
    const [origin, setorigin] = useState("");
    const [destination, setdest] = useState("");
    const [dirs, setdirs] =
        useState<google.maps.DirectionsResult | null>(null);
    const [recent, setrecent] = useState<string[]>([]);
    const [scanning, setscanning] = useState(false);
    const [showDebug, setShowDebug] = useState(false);
    const [showIncidentMenu, setShowIncidentMenu] = useState(false);

    // === INCIDENT / SAFETY STATE ===
    const [incidents, setIncidents] = useState<Incident[]>([]);
    const [routeInfo, setRouteInfo] = useState<{
        incidentsNearRoute: number;
        travelTimeMinutes: number;
    } | null>(null);

    // === HEATMAP STATE ===
    const [heatmapVisible, setHeatmapVisible] = useState(false);
    const heatmapRef =
        useRef<google.maps.visualization.HeatmapLayer | null>(null);
    const mapRef = useRef<google.maps.Map | null>(null);

    const videoRef = useRef<HTMLVideoElement | null>(null);
    const codeReaderRef = useRef<BrowserMultiFormatReader | null>(null);

    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_KEY;

    const heatmapData = [
        { lat: 43.65788609751147, lng: -79.38116487168452, weight: 150 },
        { lat: 43.659168279937234, lng: -79.38098324697091, weight: 180 },
        { lat: 43.658559323798286, lng: -79.380842582807, weight: 120 },
        { lat: 43.658013883035, lng: -79.38062280446464, weight: 100 },
        { lat: 43.65803803550416, lng: -79.37991617534612, weight: 200 },
        { lat: 43.65814269606438, lng: -79.37905097201683, weight: 90 },
        { lat: 43.65838019435132, lng: -79.37823028075593, weight: 50 },
        { lat: 43.65900211338999, lng: -79.37854186523596, weight: 60 },
        { lat: 43.65955157048326, lng: -79.37875051555642, weight: 70 },
        { lat: 43.659410684530904, lng: -79.37954060477031, weight: 160 },
        { lat: 43.659241620951704, lng: -79.38041137210814, weight: 200 },
        { lat: 43.65856397504496, lng: -79.38009866326198, weight: 110 },
        { lat: 43.65878078168392, lng: -79.3793086030687, weight: 140 },
        { lat: 43.65982410503219, lng: -79.37814097538906, weight: 40 },
        { lat: 43.659830092306436, lng: -79.3776195882128, weight: 30 },
        { lat: 43.659634507705086, lng: -79.37714785695809, weight: 50 },
        { lat: 43.65938503662571, lng: -79.3770264758165, weight: 45 },
        { lat: 43.65951276594786, lng: -79.3779478690275, weight: 155 },
        { lat: 43.65923136192491, lng: -79.37793959304055, weight: 110 },
        { lat: 43.658770335448985, lng: -79.37699613050758, weight: 60 },
        { lat: 43.65853882298987, lng: -79.37760579487772, weight: 120 },
        { lat: 43.65802989158176, lng: -79.3774237231533, weight: 100 },
        { lat: 43.65730340949373, lng: -79.37712302896179, weight: 50 },
        { lat: 43.65718166300854, lng: -79.37772441734883, weight: 95 },
        { lat: 43.65789018416639, lng: -79.37801683556654, weight: 110 },
        { lat: 43.657622743359944, lng: -79.37849684280819, weight: 90 },
        { lat: 43.65786423846877, lng: -79.37872581177973, weight: 100 },
        { lat: 43.656891408678995, lng: -79.37818336085053, weight: 35 },
        { lat: 43.65665492945539, lng: -79.37881486675307, weight: 55 },
        { lat: 43.65701079589828, lng: -79.37894497600567, weight: 75 },
        { lat: 43.65746079174427, lng: -79.37918932752966, weight: 110 },
        { lat: 43.65731155880031, lng: -79.37960186908809, weight: 80 },
        { lat: 43.65692355142155, lng: -79.3794717598355, weight: 60 },
        { lat: 43.65717150908827, lng: -79.38029684291963, weight: 150 },
        { lat: 43.656655707080596, lng: -79.38142862996358, weight: 70 },
        { lat: 43.65574926681535, lng: -79.38288121741424, weight: 30 },
    ];

    // HEATMAP TOGGLE EFFECT
    useEffect(() => {
        if (!mapRef.current) return;

        if (heatmapVisible) {
            if (!heatmapRef.current) {
                heatmapRef.current =
                    new google.maps.visualization.HeatmapLayer({
                        data: heatmapData.map((d) => ({
                            location: new google.maps.LatLng(d.lat, d.lng),
                            weight: d.weight,
                        })),
                        radius: 35,
                    });
            }
            heatmapRef.current.setMap(mapRef.current);
        } else {
            if (heatmapRef.current) {
                heatmapRef.current.setMap(null);
            }
        }
    }, [heatmapVisible]);

    const gpshandle = () => {
        navigator.geolocation.getCurrentPosition((pos) => {
            const coords = {
                lat: pos.coords.latitude,
                lng: pos.coords.longitude,
            };
            setcurrloc(coords);
            setorigin(`${coords.lat}, ${coords.lng}`);
        });
    };

    const startscan = async () => {
        setscanning(true);
        codeReaderRef.current = new BrowserMultiFormatReader();

        const videoInputDevices =
            await BrowserMultiFormatReader.listVideoInputDevices();
        const deviceId = videoInputDevices[0]?.deviceId;
        if (!deviceId) {
            alert("No camera found");
            setscanning(false);
            return;
        }

        const result =
            await codeReaderRef.current.decodeOnceFromVideoDevice(
                deviceId,
                videoRef.current!
            );
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
            if (
                parts.length === 2 &&
                !isNaN(parts[0]) &&
                !isNaN(parts[1])
            ) {
                return { lat: parts[0], lng: parts[1] };
            }
        }
        return origin;
    };

    // Load incidents from backend
    useEffect(() => {
        const loadIncidents = async () => {
            try {
                const data = await getIncidents();
                setIncidents(data || []);
            } catch (err) {
                console.error("Failed to load incidents", err);
            }
        };
        loadIncidents();
    }, []);

    // Compute directions:
    // - if NO incidents then normal shortest route
    // - if incidents exist then choose safest alternative route
    useEffect(() => {
        const getdirs = async () => {
            if (!destination || (!origin && !currloc)) return;

            const service = new google.maps.DirectionsService();

            const activeIncidentPoints =
                incidents
                    .filter((inc) => inc.lat != null && inc.lng != null)
                    .map((inc) => ({
                        lat: inc.lat as number,
                        lng: inc.lng as number,
                    })) ?? [];

            const hasIncidents = activeIncidentPoints.length > 0;

            if (!hasIncidents) {
                const result = await service.route({
                    origin: getorigin(),
                    destination: destination,
                    travelMode: google.maps.TravelMode.WALKING,
                });
                setdirs(result);
                setRouteInfo(null); 
                return;
            }

            const result = await service.route({
                origin: getorigin(),
                destination: destination,
                travelMode: google.maps.TravelMode.WALKING,
                provideRouteAlternatives: true,
            });

            if (!result.routes || result.routes.length === 0) {
                setdirs(result);
                setRouteInfo(null);
                return;
            }

            let bestRoute = result.routes[0];
            let bestStats = computeRouteIncidentScore(
                bestRoute,
                activeIncidentPoints
            );

            for (const route of result.routes.slice(1)) {
                const stats = computeRouteIncidentScore(
                    route,
                    activeIncidentPoints
                );
                if (stats.score < bestStats.score) {
                    bestRoute = route;
                    bestStats = stats;
                }
            }

            const safeResult: google.maps.DirectionsResult = {
                ...result,
                routes: [bestRoute],
            };

            setdirs(safeResult);
            setRouteInfo(bestStats); 
        };

        getdirs();
    }, [origin, destination, currloc, incidents]);

    const navbutton = () => {
        if (!destination) return alert("Enter a destination!");
        if (!origin && !currloc) return alert("Origin unknown");

        setrecent((prev) =>
            [destination, ...prev.filter((d) => d !== destination)].slice(
                0,
                5
            )
        );
    };

    const mapCenter: google.maps.LatLngLiteral =
        currloc ||
        (incidents.length > 0 &&
        incidents[0].lat != null &&
        incidents[0].lng != null
            ? {
                  lat: incidents[0].lat as number,
                  lng: incidents[0].lng as number,
              }
            : { lat: 43.6577, lng: -79.3788 });

    return (
        <div className="full-container">
            {showDebug && (
                <UserDbDebug onClose={() => setShowDebug(false)} />
            )}

            <div className="top-bar">
                <div className="left-controls">
                    <h1>Campus Navigator</h1>
                </div>

                <div
                    className="right-controls"
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                    }}
                >
                    <button
                        onClick={() => setShowDebug(true)}
                        className="debug-btn"
                        title="Open User DB Debug Panel"
                    >
                        Debug DB
                    </button>

                    <button
                        className="top-btn"
                        onClick={() =>
                            setHeatmapVisible((prev) => !prev)
                        }
                    >
                        Heatmap
                    </button>

                    <div
                        className="incident-dropdown"
                        onMouseEnter={() => setShowIncidentMenu(true)}
                        onMouseLeave={() => setShowIncidentMenu(false)}
                    >
                        <button className="top-btn">
                            Report Incidents ▾
                        </button>
                        {showIncidentMenu && (
                            <div className="incident-menu">
                                <button
                                    onClick={() =>
                                        (window.location.href =
                                            "/report-student.html")
                                    }
                                >
                                    Report Incident (Student)
                                </button>
                                <button
                                    onClick={() =>
                                        (window.location.href =
                                            "/faculty-login.html")
                                    }
                                >
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

                {incidents.length > 0 && routeInfo && (
                    <div style={{ marginTop: "10px" }}>
                        <strong>Route Safety:</strong>{" "}
                        {routeInfo.incidentsNearRoute === 0 ? (
                            <span>
                                This route avoids all reported incidents.
                            </span>
                        ) : (
                            <span>
                                This route passes near{" "}
                                {routeInfo.incidentsNearRoute} reported
                                incident
                                {routeInfo.incidentsNearRoute > 1 ? "s" : ""}.
                            </span>
                        )}
                        <div>
                            Estimated travel time:{" "}
                            {routeInfo.travelTimeMinutes.toFixed(1)} minutes
                        </div>
                    </div>
                )}

                {scanning && (
                    <div className="scanner">
                        <p>Scanning QR code…</p>
                        <video ref={videoRef} autoPlay />
                    </div>
                )}
            </div>

            <div className="map-wrapper">
                <LoadScript
                    googleMapsApiKey={apiKey}
                    libraries={["geometry", "visualization"]}
                >
                    <GoogleMap
                        onLoad={(map) => {
                            mapRef.current = map;
                        }}
                        mapContainerStyle={{
                            width: "100%",
                            height: "100%",
                        }}
                        center={mapCenter}
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
