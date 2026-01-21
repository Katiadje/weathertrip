import { apiFetch } from './config.js';
import { loadTrips } from './trips.js';

export async function addDestination(destinationData) {
    const response = await apiFetch(`/destinations/`, {
        method: 'POST',
        body: JSON.stringify(destinationData)
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Erreur ajout destination');
    }

    return response.json();
}

export async function deleteDestination(destinationId) {
    const response = await apiFetch(`/destinations/${destinationId}`, {
        method: 'DELETE'
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Erreur suppression destination');
    }
}

export function openDestinationModal(tripId) {
    document.getElementById('modal-trip-id').value = tripId;
    document.getElementById('destination-modal').style.display = 'block';
}

export function closeDestinationModal() {
    document.getElementById('destination-modal').style.display = 'none';
    document.getElementById('destination-form')?.reset();
}

export function setupDestinationForm() {
    const form = document.getElementById('destination-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const trip_id = parseInt(document.getElementById('modal-trip-id').value);
        const city = document.getElementById('destination-city').value;
        const country = document.getElementById('destination-country').value;
        const arrival_date = document.getElementById('destination-arrival').value || null;
        const departure_date = document.getElementById('destination-departure').value || null;

        try {
            await addDestination({ trip_id, city, country, arrival_date, departure_date });
            closeDestinationModal();
            await loadTrips();
        } catch (err) {
            alert(err.message);
        }
    });
}
