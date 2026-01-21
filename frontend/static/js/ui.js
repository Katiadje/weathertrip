import { getCurrentUser } from './config.js';

// ==================== ONGLETS ====================
export function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const targetTab = document.getElementById(`${tabName}-tab`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        if ((tabName === 'login' && btn.textContent.includes('Connexion')) ||
            (tabName === 'register' && btn.textContent.includes('Inscription'))) {
            btn.classList.add('active');
        }
    });
}

// ==================== SECTIONS ====================
export function showMainSection() {
    document.getElementById('auth-section')?.classList.add('hidden');
    document.getElementById('main-section')?.classList.remove('hidden');
    document.getElementById('user-info')?.classList.remove('hidden');
    
    const user = getCurrentUser();
    if (user) {
        document.getElementById('username-display').textContent = `👤 ${user.username}`;
    }
}

export function showAuthSection() {
    document.getElementById('auth-section')?.classList.remove('hidden');
    document.getElementById('main-section')?.classList.add('hidden');
    document.getElementById('user-info')?.classList.add('hidden');
}

// ==================== MODALES ====================
export function openDestinationModal(tripId) {
    document.getElementById('modal-trip-id').value = tripId;
    document.getElementById('destination-modal').style.display = 'block';
}

export function closeDestinationModal() {
    document.getElementById('destination-modal').style.display = 'none';
    document.getElementById('destination-form')?.reset();
}

export function openWeatherModal() {
    document.getElementById('weather-modal').style.display = 'block';
}

export function closeWeatherModal() {
    document.getElementById('weather-modal').style.display = 'none';
}

export function setupModalCloseHandlers() {
    window.onclick = function(event) {
        const destModal = document.getElementById('destination-modal');
        const weatherModal = document.getElementById('weather-modal');
        
        if (event.target === destModal) closeDestinationModal();
        if (event.target === weatherModal) closeWeatherModal();
    };
}

// ==================== AFFICHAGE VOYAGES ====================
export function updateTripsUI(trips) {
    const tripsList = document.getElementById('trips-list');
    if (!tripsList) return;

    if (trips.length === 0) {
        tripsList.innerHTML = '<p class="empty-state">📭 Aucun voyage</p>';
        return;
    }

    tripsList.innerHTML = trips.map(trip => `
        <div class="trip-card">
            <div class="trip-header">
                <h3>${escapeHtml(trip.name)}</h3>
                <button onclick="deleteTrip(${trip.id})" class="btn btn-danger btn-sm">🗑️</button>
            </div>
            ${trip.description ? `<p class="trip-description">${escapeHtml(trip.description)}</p>` : ''}
            <div class="trip-dates">
                ${trip.start_date ? `📅 ${formatDate(trip.start_date)}` : ''}
                ${trip.end_date ? ` → ${formatDate(trip.end_date)}` : ''}
            </div>
            <div class="destinations-section">
                <h4>📍 Destinations (${trip.destinations?.length || 0})</h4>
                ${renderDestinations(trip.destinations || [])}
                <button onclick="openDestinationModal(${trip.id})" class="btn btn-secondary btn-sm">➕ Ajouter</button>
            </div>
        </div>
    `).join('');
}

function renderDestinations(destinations) {
    if (destinations.length === 0) {
        return '<p class="empty-destinations">Aucune destination</p>';
    }
    
    return `<ul class="destinations-list">
        ${destinations.map(dest => `
            <li>
                <span><strong>${escapeHtml(dest.city)}, ${escapeHtml(dest.country)}</strong></span>
                <div>
                    <button onclick="showWeather(${dest.id}, '${escapeHtml(dest.city)}', '${escapeHtml(dest.country)}')" class="btn-icon" title="Voir la météo">🌤️</button>
                    <button onclick="deleteDestination(${dest.id})" class="btn-icon" title="Supprimer">❌</button>
                </div>
            </li>
        `).join('')}
    </ul>`;
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}