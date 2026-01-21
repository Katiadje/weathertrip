import { apiFetch, setCurrentTrips, getCurrentTrips } from './config.js';
import { updateTripsUI } from './ui.js';
import { updateChart } from './charts.js';

// Charger les voyages
export async function loadTrips() {
    try {
        const response = await apiFetch(`/trips/`, { method: 'GET' });

        if (!response.ok) {
            throw new Error('Erreur lors du chargement des voyages');
        }

        const trips = await response.json();
        setCurrentTrips(trips);

        updateTripsUI(trips);
        updateChart(trips);

    } catch (error) {
        console.error(error);
        updateTripsUI([]);
    }
}

// Créer un voyage
export async function createTrip(tripData) {
    const response = await apiFetch(`/trips/`, {
        method: 'POST',
        body: JSON.stringify(tripData)
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Erreur création voyage');
    }

    return response.json();
}

// Supprimer un voyage
export async function deleteTrip(tripId) {
    const response = await apiFetch(`/trips/${tripId}`, {
        method: 'DELETE'
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Erreur suppression voyage');
    }
}

// Init formulaire création voyage
export function setupTripForm() {
    const form = document.getElementById('trip-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('trip-name').value;
        const start_date = document.getElementById('trip-start').value || null;
        const end_date = document.getElementById('trip-end').value || null;
        const description = document.getElementById('trip-description').value || null;

        try {
            await createTrip({ name, start_date, end_date, description });
            form.reset();
            await loadTrips();
        } catch (err) {
            alert(err.message);
        }
    });
}
