import { API_URL, getCurrentUser, setCurrentTrips, getCurrentTrips } from './config.js';
import { loadDestinations } from './destinations.js';
import { updateChart } from './charts.js';
import { viewTripWeather } from './weather.js';

// Créer un voyage
export async function handleCreateTrip(e) {
    e.preventDefault();
    
    const name = document.getElementById('trip-name').value;
    const description = document.getElementById('trip-description').value;
    const startDate = document.getElementById('trip-start').value;
    const endDate = document.getElementById('trip-end').value;

    const startDateTime = startDate ? `${startDate}T00:00:00` : null;
    const endDateTime = endDate ? `${endDate}T23:59:59` : null;

    try {
        const user = getCurrentUser();
        const response = await fetch(`${API_URL}/trips/?user_id=${user.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                description,
                start_date: startDateTime,
                end_date: endDateTime
            })
        });

        if (!response.ok) {
            throw new Error('Erreur lors de la création du voyage');
        }
        
        await loadTrips();
        document.getElementById('trip-form').reset();
        alert('Voyage créé avec succès !');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Charger les voyages
export async function loadTrips() {
    try {
        const user = getCurrentUser();
        const response = await fetch(`${API_URL}/trips/?user_id=${user.id}`);
        
        if (!response.ok) {
            throw new Error('Erreur lors du chargement des voyages');
        }
        
        const trips = await response.json();
        setCurrentTrips(trips);
        displayTrips();
        updateChart();
    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('trips-list').innerHTML = 
            '<p class="empty-state">Erreur lors du chargement des voyages</p>';
    }
}

// Afficher les voyages
export function displayTrips() {
    const container = document.getElementById('trips-list');
    const trips = getCurrentTrips();
    
    if (trips.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">✈️</div>
                <p>Aucun voyage pour le moment. Créez votre premier voyage ci-dessus !</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = trips.map(trip => `
        <div class="trip-item">
            <div class="trip-header">
                <div>
                    <div class="trip-title">${trip.name}</div>
                    <div class="trip-dates">
                        ${trip.start_date ? new Date(trip.start_date).toLocaleDateString('fr-FR') : '—'} 
                        → 
                        ${trip.end_date ? new Date(trip.end_date).toLocaleDateString('fr-FR') : '—'}
                    </div>
                    ${trip.description ? `<p>${trip.description}</p>` : ''}
                </div>
            </div>
            <div class="trip-actions">
                <button class="btn btn-success" onclick="window.openDestinationModal(${trip.id})">+ Destination</button>
                <button class="btn btn-info" onclick="window.viewTripWeather(${trip.id})">🌤️ Météo</button>
                <button class="btn btn-danger" onclick="window.deleteTrip(${trip.id})">Supprimer</button>
            </div>
            <div class="destinations-list" id="destinations-${trip.id}">
                <div class="loading">Chargement des destinations...</div>
            </div>
        </div>
    `).join('');
    
    trips.forEach(trip => loadDestinations(trip.id));
}

// Supprimer un voyage
export async function deleteTrip(tripId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce voyage ?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/trips/${tripId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la suppression');
        }
        
        await loadTrips();
        alert('Voyage supprimé avec succès !');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}