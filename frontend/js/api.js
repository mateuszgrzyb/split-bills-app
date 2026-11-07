const API_BASE_URL = "http://127.0.0.1:8000";

export async function getApiHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error(`API zwróciło status ${response.status}`);
  }
  return response.json();
}
