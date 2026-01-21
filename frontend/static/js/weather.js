import { apiFetch } from './config.js';

export async function getCityWeather(city, country = "") {
    const response = await apiFetch(`/weather/city/${encodeURIComponent(city)}?country=${encodeURIComponent(country)}`, {
        method: 'GET'
    });

    if (!response.ok) return null;
    return response.json();
}

export async function getDestinationWeather(destinationId, force_refresh = false) {
    const response = await apiFetch(`/weather/destination/${destinationId}?force_refresh=${force_refresh}`, {
        method: 'GET'
    });

    if (!response.ok) return null;
    return response.json();
}

export async function fetchForecast(destinationId) {
    const response = await apiFetch(`/weather/destination/${destinationId}/forecast`, {
        method: 'POST'
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Erreur récupération prévisions');
    }

    return response.json();
}
