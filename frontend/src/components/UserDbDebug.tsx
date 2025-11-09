import React, { useState } from "react";
import {
  getSavedLocations,
  saveLocation,
  updateSavedLocation,
  deleteSavedLocation,
  getRecentSearches,
  addRecentSearch,
  deleteRecentSearch,
  getSchedule,
  addScheduleEntry,
  updateScheduleEntry,
  deleteScheduleEntry,
  getPreferences,
  updatePreferences,
  SavedLocation,
  RecentSearch,
  ScheduleEntry,
  UserPreferences,
} from "../api";

interface UserDbDebugProps {
  onClose: () => void;
}

const UserDbDebug: React.FC<UserDbDebugProps> = ({ onClose }) => {
  const [userId, setUserId] = useState<number>(1);
  const [activeTab, setActiveTab] = useState<"locations" | "searches" | "schedule" | "preferences">("locations");
  const [response, setResponse] = useState<string>("");
  const [loading, setLoading] = useState(false);
  
  // Data states for displaying fetched items
  const [locations, setLocations] = useState<SavedLocation[]>([]);
  const [searches, setSearches] = useState<RecentSearch[]>([]);
  const [schedule, setSchedule] = useState<ScheduleEntry[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);

  // Form states
  const [locationForm, setLocationForm] = useState<Partial<SavedLocation>>({
    location_name: "",
    building_name: "",
    room_number: "",
    floor_number: undefined,
    qr_code_id: "",
  });
  const [searchForm, setSearchForm] = useState<Partial<RecentSearch>>({
    search_term: "",
    resolved_location_id: undefined,
  });
  const [scheduleForm, setScheduleForm] = useState<Partial<ScheduleEntry>>({
    course_name: "",
    professor_name: "",
    building_name: "",
    room_number: "",
    event_start_time: "",
    event_end_time: "",
  });
  const [preferencesForm, setPreferencesForm] = useState<Partial<UserPreferences>>({
    sorting_preference: "name",
    route_preference: "shortest",
    calendar_sync_enabled: false,
    offline_mode_enabled: false,
  });

  const handleResponse = (data: any, error?: any) => {
    if (error) {
      setResponse(`Error: ${JSON.stringify(error, null, 2)}`);
    } else {
      setResponse(JSON.stringify(data, null, 2));
    }
  };

  // Saved Locations handlers
  const handleGetLocations = async () => {
    setLoading(true);
    try {
      const data = await getSavedLocations(userId);
      setLocations(data);
      handleResponse(data);
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
      setLocations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveLocation = async () => {
    setLoading(true);
    try {
      const data = await saveLocation({ ...locationForm, user_id: userId } as SavedLocation);
      handleResponse(data);
      setLocationForm({ location_name: "", building_name: "", room_number: "", floor_number: undefined, qr_code_id: "" });
      handleGetLocations(); // Refresh the list
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteLocation = async (id: number) => {
    setLoading(true);
    try {
      const data = await deleteSavedLocation(id);
      handleResponse(data);
      handleGetLocations();
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };

  // Recent Searches handlers
  const handleGetSearches = async () => {
    setLoading(true);
    try {
      const data = await getRecentSearches(userId);
      setSearches(data);
      handleResponse(data);
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
      setSearches([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSearch = async () => {
    setLoading(true);
    try {
      const data = await addRecentSearch({ ...searchForm, user_id: userId } as RecentSearch);
      handleResponse(data);
      setSearchForm({ search_term: "", resolved_location_id: undefined });
      handleGetSearches(); // Refresh the list
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSearch = async (id: number) => {
    setLoading(true);
    try {
      const data = await deleteRecentSearch(id);
      handleResponse(data);
      handleGetSearches();
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };

  // Schedule handlers
  const handleGetSchedule = async () => {
    setLoading(true);
    try {
      const data = await getSchedule(userId);
      setSchedule(data);
      handleResponse(data);
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
      setSchedule([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSchedule = async () => {
    setLoading(true);
    try {
      // Convert datetime-local format to ISO format
      const startTime = scheduleForm.event_start_time 
        ? new Date(scheduleForm.event_start_time).toISOString()
        : "";
      const endTime = scheduleForm.event_end_time 
        ? new Date(scheduleForm.event_end_time).toISOString()
        : "";
      
      const data = await addScheduleEntry({ 
        ...scheduleForm, 
        user_id: userId,
        event_start_time: startTime,
        event_end_time: endTime,
      } as ScheduleEntry);
      handleResponse(data);
      setScheduleForm({
        course_name: "",
        professor_name: "",
        building_name: "",
        room_number: "",
        event_start_time: "",
        event_end_time: "",
      });
      handleGetSchedule(); // Refresh the list
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSchedule = async (id: number) => {
    setLoading(true);
    try {
      const data = await deleteScheduleEntry(id);
      handleResponse(data);
      handleGetSchedule();
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };

  // Preferences handlers
  const handleGetPreferences = async () => {
    setLoading(true);
    try {
      const data = await getPreferences(userId);
      setPreferences(data);
      setPreferencesForm(data);
      handleResponse(data);
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
      setPreferences(null);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePreferences = async () => {
    setLoading(true);
    try {
      const data = await updatePreferences({ ...preferencesForm, user_id: userId });
      handleResponse(data);
    } catch (error: any) {
      handleResponse(null, error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(0, 0, 0, 0.8)",
      zIndex: 1000,
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      padding: "20px",
    }}>
      <div style={{
        backgroundColor: "white",
        borderRadius: "8px",
        padding: "20px",
        maxWidth: "900px",
        width: "100%",
        maxHeight: "90vh",
        overflow: "auto",
        boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <h2>User DB Debug Panel</h2>
          <button onClick={onClose} style={{ padding: "8px 16px", cursor: "pointer" }}>Close</button>
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label>
            User ID:{" "}
            <input
              type="number"
              value={userId}
              onChange={(e) => setUserId(parseInt(e.target.value) || 1)}
              style={{ padding: "4px", marginLeft: "8px" }}
            />
          </label>
        </div>

        <div style={{ display: "flex", gap: "10px", marginBottom: "20px", borderBottom: "1px solid #ccc" }}>
          <button
            onClick={() => setActiveTab("locations")}
            style={{
              padding: "8px 16px",
              cursor: "pointer",
              backgroundColor: activeTab === "locations" ? "#007bff" : "#f0f0f0",
              color: activeTab === "locations" ? "white" : "black",
              border: "none",
              borderRadius: "4px",
            }}
          >
            Saved Locations
          </button>
          <button
            onClick={() => setActiveTab("searches")}
            style={{
              padding: "8px 16px",
              cursor: "pointer",
              backgroundColor: activeTab === "searches" ? "#007bff" : "#f0f0f0",
              color: activeTab === "searches" ? "white" : "black",
              border: "none",
              borderRadius: "4px",
            }}
          >
            Recent Searches
          </button>
          <button
            onClick={() => setActiveTab("schedule")}
            style={{
              padding: "8px 16px",
              cursor: "pointer",
              backgroundColor: activeTab === "schedule" ? "#007bff" : "#f0f0f0",
              color: activeTab === "schedule" ? "white" : "black",
              border: "none",
              borderRadius: "4px",
            }}
          >
            Schedule
          </button>
          <button
            onClick={() => setActiveTab("preferences")}
            style={{
              padding: "8px 16px",
              cursor: "pointer",
              backgroundColor: activeTab === "preferences" ? "#007bff" : "#f0f0f0",
              color: activeTab === "preferences" ? "white" : "black",
              border: "none",
              borderRadius: "4px",
            }}
          >
            Preferences
          </button>
        </div>

        <div style={{ marginBottom: "20px" }}>
          {activeTab === "locations" && (
            <div>
              <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
                <button onClick={handleGetLocations} disabled={loading} style={{ padding: "8px 16px", cursor: "pointer" }}>
                  GET Locations
                </button>
                <button onClick={handleSaveLocation} disabled={loading} style={{ padding: "8px 16px", cursor: "pointer" }}>
                  POST Location
                </button>
              </div>
              <div style={{ display: "grid", gap: "10px", marginBottom: "20px" }}>
                <input
                  type="text"
                  placeholder="Location Name"
                  value={locationForm.location_name || ""}
                  onChange={(e) => setLocationForm({ ...locationForm, location_name: e.target.value })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="text"
                  placeholder="Building Name"
                  value={locationForm.building_name || ""}
                  onChange={(e) => setLocationForm({ ...locationForm, building_name: e.target.value })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="text"
                  placeholder="Room Number"
                  value={locationForm.room_number || ""}
                  onChange={(e) => setLocationForm({ ...locationForm, room_number: e.target.value })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="number"
                  placeholder="Floor Number"
                  value={locationForm.floor_number || ""}
                  onChange={(e) => setLocationForm({ ...locationForm, floor_number: parseInt(e.target.value) || undefined })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="text"
                  placeholder="QR Code ID"
                  value={locationForm.qr_code_id || ""}
                  onChange={(e) => setLocationForm({ ...locationForm, qr_code_id: e.target.value })}
                  style={{ padding: "8px" }}
                />
              </div>
              {locations.length > 0 && (
                <div style={{ marginTop: "20px", borderTop: "1px solid #ccc", paddingTop: "20px" }}>
                  <h3>Saved Locations ({locations.length})</h3>
                  {locations.map((loc) => (
                    <div
                      key={loc.id}
                      style={{
                        padding: "10px",
                        marginBottom: "10px",
                        backgroundColor: "#f9f9f9",
                        borderRadius: "4px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <div>
                        <strong>{loc.location_name}</strong>
                        {loc.building_name && <div>Building: {loc.building_name}</div>}
                        {loc.room_number && <div>Room: {loc.room_number}</div>}
                        {loc.floor_number && <div>Floor: {loc.floor_number}</div>}
                        {loc.qr_code_id && <div>QR: {loc.qr_code_id}</div>}
                      </div>
                      <button
                        onClick={() => loc.id && handleDeleteLocation(loc.id)}
                        disabled={loading}
                        style={{
                          padding: "6px 12px",
                          backgroundColor: "#dc3545",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "searches" && (
            <div>
              <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
                <button onClick={handleGetSearches} disabled={loading} style={{ padding: "8px 16px", cursor: "pointer" }}>
                  GET Searches
                </button>
                <button onClick={handleAddSearch} disabled={loading} style={{ padding: "8px 16px", cursor: "pointer" }}>
                  POST Search
                </button>
              </div>
              <div style={{ display: "grid", gap: "10px", marginBottom: "20px" }}>
                <input
                  type="text"
                  placeholder="Search Term"
                  value={searchForm.search_term || ""}
                  onChange={(e) => setSearchForm({ ...searchForm, search_term: e.target.value })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="number"
                  placeholder="Resolved Location ID (optional)"
                  value={searchForm.resolved_location_id || ""}
                  onChange={(e) => setSearchForm({ ...searchForm, resolved_location_id: parseInt(e.target.value) || undefined })}
                  style={{ padding: "8px" }}
                />
              </div>
              {searches.length > 0 && (
                <div style={{ marginTop: "20px", borderTop: "1px solid #ccc", paddingTop: "20px" }}>
                  <h3>Recent Searches ({searches.length})</h3>
                  {searches.map((search) => (
                    <div
                      key={search.id}
                      style={{
                        padding: "10px",
                        marginBottom: "10px",
                        backgroundColor: "#f9f9f9",
                        borderRadius: "4px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <div>
                        <strong>{search.search_term}</strong>
                        {search.location && <div>Location: {search.location.name}</div>}
                        {search.timestamp && <div>Time: {new Date(search.timestamp).toLocaleString()}</div>}
                      </div>
                      <button
                        onClick={() => search.id && handleDeleteSearch(search.id)}
                        disabled={loading}
                        style={{
                          padding: "6px 12px",
                          backgroundColor: "#dc3545",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "schedule" && (
            <div>
              <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
                <button onClick={handleGetSchedule} disabled={loading} style={{ padding: "8px 16px", cursor: "pointer" }}>
                  GET Schedule
                </button>
                <button onClick={handleAddSchedule} disabled={loading} style={{ padding: "8px 16px", cursor: "pointer" }}>
                  POST Schedule Entry
                </button>
              </div>
              <div style={{ display: "grid", gap: "10px", marginBottom: "20px" }}>
                <input
                  type="text"
                  placeholder="Course Name"
                  value={scheduleForm.course_name || ""}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, course_name: e.target.value })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="text"
                  placeholder="Professor Name"
                  value={scheduleForm.professor_name || ""}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, professor_name: e.target.value })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="text"
                  placeholder="Building Name"
                  value={scheduleForm.building_name || ""}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, building_name: e.target.value })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="text"
                  placeholder="Room Number"
                  value={scheduleForm.room_number || ""}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, room_number: e.target.value })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="datetime-local"
                  placeholder="Start Time"
                  value={scheduleForm.event_start_time ? scheduleForm.event_start_time.slice(0, 16) : ""}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, event_start_time: e.target.value })}
                  style={{ padding: "8px" }}
                />
                <input
                  type="datetime-local"
                  placeholder="End Time"
                  value={scheduleForm.event_end_time ? scheduleForm.event_end_time.slice(0, 16) : ""}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, event_end_time: e.target.value })}
                  style={{ padding: "8px" }}
                />
              </div>
              {schedule.length > 0 && (
                <div style={{ marginTop: "20px", borderTop: "1px solid #ccc", paddingTop: "20px" }}>
                  <h3>Schedule Entries ({schedule.length})</h3>
                  {schedule.map((entry) => (
                    <div
                      key={entry.id}
                      style={{
                        padding: "10px",
                        marginBottom: "10px",
                        backgroundColor: "#f9f9f9",
                        borderRadius: "4px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <div>
                        {entry.course_name && <strong>{entry.course_name}</strong>}
                        {entry.professor_name && <div>Professor: {entry.professor_name}</div>}
                        {entry.building_name && <div>Building: {entry.building_name}</div>}
                        {entry.room_number && <div>Room: {entry.room_number}</div>}
                        {entry.event_start_time && (
                          <div>
                            {new Date(entry.event_start_time).toLocaleString()} -{" "}
                            {entry.event_end_time && new Date(entry.event_end_time).toLocaleString()}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => entry.id && handleDeleteSchedule(entry.id)}
                        disabled={loading}
                        style={{
                          padding: "6px 12px",
                          backgroundColor: "#dc3545",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "preferences" && (
            <div>
              <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
                <button onClick={handleGetPreferences} disabled={loading} style={{ padding: "8px 16px", cursor: "pointer" }}>
                  GET Preferences
                </button>
                <button onClick={handleUpdatePreferences} disabled={loading} style={{ padding: "8px 16px", cursor: "pointer" }}>
                  PUT Preferences
                </button>
              </div>
              <div style={{ display: "grid", gap: "10px", marginBottom: "20px" }}>
                <select
                  value={preferencesForm.sorting_preference || "name"}
                  onChange={(e) => setPreferencesForm({ ...preferencesForm, sorting_preference: e.target.value })}
                  style={{ padding: "8px" }}
                >
                  <option value="name">Name</option>
                  <option value="professor">Professor</option>
                  <option value="course_code">Course Code</option>
                  <option value="created_at">Date Created</option>
                </select>
                <select
                  value={preferencesForm.route_preference || "shortest"}
                  onChange={(e) => setPreferencesForm({ ...preferencesForm, route_preference: e.target.value })}
                  style={{ padding: "8px" }}
                >
                  <option value="shortest">Shortest</option>
                  <option value="fastest">Fastest</option>
                  <option value="accessible">Accessible</option>
                </select>
                <label style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <input
                    type="checkbox"
                    checked={preferencesForm.calendar_sync_enabled || false}
                    onChange={(e) => setPreferencesForm({ ...preferencesForm, calendar_sync_enabled: e.target.checked })}
                  />
                  Calendar Sync Enabled
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <input
                    type="checkbox"
                    checked={preferencesForm.offline_mode_enabled || false}
                    onChange={(e) => setPreferencesForm({ ...preferencesForm, offline_mode_enabled: e.target.checked })}
                  />
                  Offline Mode Enabled
                </label>
              </div>
            </div>
          )}
        </div>

        {loading && <div style={{ padding: "10px", backgroundColor: "#f0f0f0", marginBottom: "10px" }}>Loading...</div>}

        {response && (
          <div style={{
            backgroundColor: "#f5f5f5",
            padding: "15px",
            borderRadius: "4px",
            maxHeight: "300px",
            overflow: "auto",
            fontFamily: "monospace",
            fontSize: "12px",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}>
            <strong>Response:</strong>
            <pre style={{ margin: "10px 0 0 0" }}>{response}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserDbDebug;

