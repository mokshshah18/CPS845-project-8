import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:5000/api",
});

// ============ Basic API Functions ============

export async function getLocations() {
  const res = await API.get("/locations/");
  return res.data;
}

export async function getRoute(start: string, end: string) {
  const res = await API.get(`/route?start=${start}&end=${end}`);
  return res.data;
}

// ============ User Saved Locations ============

export interface SavedLocation {
  id?: number;
  user_id: number;
  location_name: string;
  building_name?: string;
  room_number?: string;
  floor_number?: number;
  qr_code_id?: string;
  created_at?: string;
}

export async function getSavedLocations(userId: number): Promise<SavedLocation[]> {
  const res = await API.get(`/user/saved-locations?user_id=${userId}`);
  return res.data;
}

export async function saveLocation(location: SavedLocation): Promise<{ message: string; id: number }> {
  const res = await API.post("/user/saved-locations", location);
  return res.data;
}

export async function updateSavedLocation(
  locationId: number,
  location: Partial<SavedLocation>
): Promise<{ message: string }> {
  const res = await API.put(`/user/saved-locations/${locationId}`, location);
  return res.data;
}

export async function deleteSavedLocation(locationId: number): Promise<{ message: string }> {
  const res = await API.delete(`/user/saved-locations/${locationId}`);
  return res.data;
}

// ============ User Recent Searches ============

export interface RecentSearch {
  id?: number;
  user_id: number;
  search_term: string;
  resolved_location_id?: number;
  timestamp?: string;
  location?: {
    id: number;
    name: string;
    x: number;
    y: number;
  };
}

export async function getRecentSearches(
  userId: number,
  limit: number = 10
): Promise<RecentSearch[]> {
  const res = await API.get(`/user/recent-searches?user_id=${userId}&limit=${limit}`);
  return res.data;
}

export async function addRecentSearch(search: RecentSearch): Promise<{ message: string; id: number }> {
  const res = await API.post("/user/recent-searches", search);
  return res.data;
}

export async function deleteRecentSearch(searchId: number): Promise<{ message: string }> {
  const res = await API.delete(`/user/recent-searches/${searchId}`);
  return res.data;
}

// ============ User Schedule Entries ============

export interface ScheduleEntry {
  id?: number;
  user_id: number;
  course_name?: string;
  professor_name?: string;
  building_name?: string;
  room_number?: string;
  event_start_time: string; // ISO format
  event_end_time: string; // ISO format
  created_at?: string;
}

export async function getSchedule(
  userId: number,
  startDate?: string,
  endDate?: string
): Promise<ScheduleEntry[]> {
  let url = `/user/schedule?user_id=${userId}`;
  if (startDate) url += `&start_date=${startDate}`;
  if (endDate) url += `&end_date=${endDate}`;
  const res = await API.get(url);
  return res.data;
}

export async function addScheduleEntry(entry: ScheduleEntry): Promise<{ message: string; id: number }> {
  const res = await API.post("/user/schedule", entry);
  return res.data;
}

export async function updateScheduleEntry(
  entryId: number,
  entry: Partial<ScheduleEntry>
): Promise<{ message: string }> {
  const res = await API.put(`/user/schedule/${entryId}`, entry);
  return res.data;
}

export async function deleteScheduleEntry(entryId: number): Promise<{ message: string }> {
  const res = await API.delete(`/user/schedule/${entryId}`);
  return res.data;
}

// ============ User Preferences ============

export interface UserPreferences {
  id?: number;
  user_id: number;
  sorting_preference?: string;
  route_preference?: string;
  calendar_sync_enabled?: boolean;
  offline_mode_enabled?: boolean;
  created_at?: string;
  updated_at?: string;
}

export async function getPreferences(userId: number): Promise<UserPreferences> {
  const res = await API.get(`/user/preferences?user_id=${userId}`);
  return res.data;
}

export async function updatePreferences(
  preferences: Partial<UserPreferences> & { user_id: number }
): Promise<{ message: string }> {
  const res = await API.put("/user/preferences", preferences);
  return res.data;
}

// ============ Incident Reports ============

export interface Incident {
  id: number;
  category: string;
  title: string;
  building_name?: string;
  room_number?: string;
  lat: number | null;
  lng: number | null;
  description?: string;
  created_at?: string;
}

export async function getIncidents(): Promise<Incident[]> {
  const res = await API.get("/report-incidents/");
  return res.data;
}

