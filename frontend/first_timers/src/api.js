const API_BASE = process.env.REACT_APP_API_BASE || "https://localhost:8000/api";
// Environmental variable for the API base, allows for easy switching between development and production

async function fetchJson(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) {
            throw new Error(`HTTP error status: ${res.status}`);
        }
        return await res.json();
    } catch (error) {
        console.error("API fetch error:", error);
        throw error;
    }
}
// Error handling

export async function getTradeData(hsCode, year) {
    return fetchJson(`${API_BASE}/trade-data?hs_code=${hsCode}&year=${year}`);
}
// TODO: Check if this changes, delete comment later
export async function getRiskScore(hsCode, year) {
    return fetchJson(`${API_BASE}/risk-score?hs_code=${hsCode}&year=${year}`);
}
// TODO: Check if this changes, delete comment later
export async function getBrief(hsCode, year) {
    return fetchJson(`${API_BASE}/brief?hs_code=${hsCode}&year=${year}`);
}
// TODO: Check if this changes, delete comment later