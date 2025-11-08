import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:5000/api",
});

export async function getLocations() {
  const res = await API.get("/locations/");
  return res.data;
}

export async function getRoute(start: string, end: string) {
  const res = await API.get(`/route?start=${start}&end=${end}`);
  return res.data;
}
