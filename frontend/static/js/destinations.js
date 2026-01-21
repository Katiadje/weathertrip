import { API_URL } from './config.js';
import { closeDestinationModal } from './ui.js';
import { viewWeather } from './weather.js';

// Charger les destinations d'un voyage
export async function loadDestinations(tripId) {
    try {
        const response = await fetch(`${API_URL}/destinations/trip/${tripId}`);
        
        if (!response.ok) {
            throw new Error('Erreur lors du chargement des destinations');
        }
        
        const destinations = await response.json();
        const container = document.getElementById(`destinations-${tripId}`);
        
        if (destinations.length === 0) {
            container.innerHTML = '<p style="color: #999; padding: 10px;">Aucune destination pour ce voyage</p>';
            return;
        }
        
        container.innerHTML = destinations.map(dest => `
            <div class="destination-item">
                <div class="destination-info">
                    <div class="destination-name">📍 ${dest.city}, ${dest.country}</div>
                    <div class="destination-dates">
                        ${dest.arrival_date ? new Date(dest.arrival_date).toLocaleDateString('fr-FR') : '—'} 
                        → 
                        ${dest.departure_date ? new Date(dest.departure_date).toLocaleDateString('fr-FR') : '—'}
                    </div>
                </div>
                <div class="destination-actions">
                    <button class="btn btn-info" onclick="window.viewWeather(${dest.id})">🌤️</button>
                    <button class="btn btn-danger" onclick="window.deleteDestination(${dest.id}, ${tripId})">✕</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Ajouter une destination
export async function handleAddDestination(e) {
    e.preventDefault();

    const tripId = document.getElementById('modal-trip-id').value;
    const city = document.getElementById('destination-city').value;
    const country = document.getElementById('destination-country').value;
    const arrival = document.getElementById('destination-arrival').value;
    const departure = document.getElementById('destination-departure').value;

    const arrivalDateTime = arrival ? `${arrival}T00:00:00` : null;
    const departureDateTime = departure ? `${departure}T23:59:59` : null;

    try {
        const response = await fetch(`${API_URL}/destinations/?trip_id=${tripId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                city,
                country,
                arrival_date: arrivalDateTime,
                departure_date: departureDateTime
            })
        });

        if (!response.ok) {
            throw new Error("Erreur lors de l'ajout de la destination");
        }

        await loadDestinations(tripId);
        closeDestinationModal();
        alert('Destination ajoutée avec succès !');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Supprimer une destination
export async function deleteDestination(destinationId, tripId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette destination ?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/destinations/${destinationId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la suppression');
        }
        
        await loadDestinations(tripId);
        alert('Destination supprimée avec succès !');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}