const API_URL = import.meta.env.VITE_API_URL;

export async function getHealth() {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error(`Error ${response.status} al consultar /health`);
  }

  return response.json();
}
