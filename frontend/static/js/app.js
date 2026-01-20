// Configuration de l'API
const API_URL = 'http://localhost:8000';

// État de l'application
let currentUser = null;
let currentTrips = [];
let chart = null;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si l'utilisateur est connecté
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const username = localStorage.getItem('username');
    
    if (token && userId) {
        currentUser = { id: parseInt(userId), username, token };
        showMainSection();
        loadTrips();
    }
    
    // Gestionnaires d'événements
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('trip-form').addEventListener('submit', handleCreateTrip);
    document.getElementById('destination-form').addEventListener('submit', handleAddDestination);
});

// Gestion des onglets
function showTab(tabName) {
    // Cacher tous les onglets
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Afficher l'onglet sélectionné
    document.getElementById(`${tabName}-tab`).classList.add('active');
    // Activer le bouton correspondant
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
        if ((tabName === 'login' && btn.textContent.includes('Connexion')) ||
            (tabName === 'register' && btn.textContent.includes('Inscription'))) {
            btn.classList.add('active');
        }
    });
}

// Authentification - Connexion
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_URL}/users/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            throw new Error('Identifiants incorrects');
        }
        
        const data = await response.json();
        
        // Stocker les informations de connexion
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userId', data.user_id);
        localStorage.setItem('username', data.username);
        
        currentUser = { id: data.user_id, username: data.username, token: data.access_token };
        
        showMainSection();
        loadTrips();
        
        // Réinitialiser le formulaire
        document.getElementById('login-form').reset();
    } catch (error) {
        alert('Erreur de connexion: ' + error.message);
    }
}

// Authentification - Inscription
async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch(`${API_URL}/users/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur lors de l\'inscription');
        }
        
        alert('Inscription réussie ! Vous pouvez maintenant vous connecter.');
        showTab('login');
        
        // Réinitialiser le formulaire
        document.getElementById('register-form').reset();
    } catch (error) {
        alert('Erreur d\'inscription: ' + error.message);
    }
}

// Déconnexion
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    currentUser = null;
    currentTrips = [];
    
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('main-section').classList.add('hidden');
    document.getElementById('user-info').classList.add('hidden');
}

// Afficher la section principale
function showMainSection() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('main-section').classList.remove('hidden');
    document.getElementById('user-info').classList.remove('hidden');
    document.getElementById('username-display').textContent = currentUser.username;
}

// Créer un voyage
async function handleCreateTrip(e) {
    e.preventDefault();
    
    const name = document.getElementById('trip-name').value;
    const description = document.getElementById('trip-description').value;


   const startDate = document.getElementById('trip-start').value;
    const endDate = document.getElementById('trip-end').value;

    // Convertir les dates au format ISO datetime
    const startDateTime = startDate ? `${startDate}T00:00:00` : null;
    const endDateTime = endDate ? `${endDate}T23:59:59` : null;

    try {
        const response = await fetch(`${API_URL}/trips/?user_id=${currentUser.id}`, {
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
        
        // Recharger la liste des voyages
        await loadTrips();
        
        // Réinitialiser le formulaire
        document.getElementById('trip-form').reset();
        
        alert('Voyage créé avec succès !');
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Charger les voyages
async function loadTrips() {
    try {
        const response = await fetch(`${API_URL}/trips/?user_id=${currentUser.id}`);
        
        if (!response.ok) {
            throw new Error('Erreur lors du chargement des voyages');
        }
        
        currentTrips = await response.json();
        displayTrips();
        updateChart();
    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('trips-list').innerHTML = '<p class="empty-state">Erreur lors du chargement des voyages</p>';
    }
}

// Afficher les voyages
function displayTrips() {
    const container = document.getElementById('trips-list');
    
    if (currentTrips.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">✈️</div><p>Aucun voyage pour le moment. Créez votre premier voyage ci-dessus !</p></div>';
        return;
    }
    
    container.innerHTML = currentTrips.map(trip => `
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
                <button class="btn btn-success" onclick="openDestinationModal(${trip.id})">+ Destination</button>
                <button class="btn btn-info" onclick="viewTripWeather(${trip.id})">🌤️ Météo</button>
                <button class="btn btn-danger" onclick="deleteTrip(${trip.id})">Supprimer</button>
            </div>
            <div class="destinations-list" id="destinations-${trip.id}">
                <div class="loading">Chargement des destinations...</div>
            </div>
        </div>
    `).join('');
    
    // Charger les destinations pour chaque voyage
    currentTrips.forEach(trip => loadDestinations(trip.id));
}

// Charger les destinations d'un voyage
async function loadDestinations(tripId) {
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
                    <button class="btn btn-info" onclick="viewWeather(${dest.id})">🌤️</button>
                    <button class="btn btn-danger" onclick="deleteDestination(${dest.id}, ${tripId})">✕</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Ouvrir le modal d'ajout de destination
function openDestinationModal(tripId) {
    document.getElementById('modal-trip-id').value = tripId;
    document.getElementById('destination-modal').style.display = 'block';
}

// Fermer le modal de destination
function closeDestinationModal() {
    document.getElementById('destination-modal').style.display = 'none';
    document.getElementById('destination-form').reset();
}

// Ajouter une destination
// Ajouter une destination
async function handleAddDestination(e) {
    e.preventDefault();

    const tripId = document.getElementById('modal-trip-id').value;
    const city = document.getElementById('destination-city').value;
    const country = document.getElementById('destination-country').value;

    const arrival = document.getElementById('destination-arrival').value;     // YYYY-MM-DD
    const departure = document.getElementById('destination-departure').value; // YYYY-MM-DD

    // ✅ Convertir en datetime ISO comme pour Trip
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


// Voir la météo d'une destination
async function viewWeather(destinationId) {
    try {
        const response = await fetch(`${API_URL}/weather/destination/${destinationId}`);
        
        if (!response.ok) {
            throw new Error('Erreur lors de la récupération de la météo');
        }
        
        const data = await response.json();
        displayWeather(data);
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Voir la météo de toutes les destinations d'un voyage
async function viewTripWeather(tripId) {
    try {
        const response = await fetch(`${API_URL}/weather/trip/${tripId}`);
        
        if (!response.ok) {
            throw new Error('Erreur lors de la récupération de la météo');
        }
        
        const data = await response.json();
        displayTripWeather(data);
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Afficher la météo dans le modal
// Afficher la météo dans le modal
async function displayWeather(data) {
    const content = document.getElementById('weather-content');
    
    const weather = data.current_weather;
    const dest = data.destination;
    
    if (!weather) {
        content.innerHTML = '<p>Météo non disponible pour cette destination</p>';
    } else {
        content.innerHTML = `
            <h3>${dest.city}, ${dest.country}</h3>
            
            <div class="weather-current">
                <div class="weather-card">
                    <div class="weather-icon">${getWeatherIcon(weather.weather_main)}</div>
                    <div class="weather-temp">${Math.round(weather.temperature)}°C</div>
                    <div class="weather-description">${weather.weather_description || ''}</div>
                    <div class="weather-details">
                        <div>💨 Ressenti: ${Math.round(weather.feels_like)}°C</div>
                        <div>💧 Humidité: ${weather.humidity}%</div>
                        <div>🌡️ Min: ${Math.round(weather.temp_min)}°C</div>
                        <div>🌡️ Max: ${Math.round(weather.temp_max)}°C</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 25px; text-align: center;">
                <button class="btn btn-primary" onclick="loadForecast(${dest.id})" style="width: 100%; font-size: 1.1em;">
                    📅 Afficher les prévisions 5 jours
                </button>
            </div>
            
            <div id="forecast-container"></div>
        `;
    }
    
    document.getElementById('weather-modal').style.display = 'block';
}
// Afficher la météo de tout le voyage
function displayTripWeather(data) {
    const content = document.getElementById('weather-content');
    
    content.innerHTML = `
        <h3>${data.trip.name}</h3>
        <div class="weather-display">
            ${data.destinations_weather.map(item => {
                const weather = item.current_weather;
                const dest = item.destination;
                
                if (!weather) {
                    return `<div class="weather-card"><p>${dest.city}: Météo non disponible</p></div>`;
                }
                
                return `
                    <div class="weather-card">
                        <h4>${dest.city}</h4>
                        <div class="weather-temp">${Math.round(weather.temperature)}°C</div>
                        <div class="weather-description">${weather.weather_description || ''}</div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    document.getElementById('weather-modal').style.display = 'block';
}

// Fermer le modal météo
function closeWeatherModal() {
    document.getElementById('weather-modal').style.display = 'none';
}

// Supprimer un voyage
async function deleteTrip(tripId) {
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

// Supprimer une destination
async function deleteDestination(destinationId, tripId) {
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

// Mettre à jour le graphique avec Chart.js
function updateChart() {
    const ctx = document.getElementById('trips-chart').getContext('2d');
    
    // Détruire l'ancien graphique s'il existe
    if (chart) {
        chart.destroy();
    }
    
    // Préparer les données
    const labels = currentTrips.map(trip => trip.name);
    const destinationsCount = currentTrips.map(trip => trip.destinations ? trip.destinations.length : 0);
    
    // Créer le graphique
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nombre de destinations',
                data: destinationsCount,
                backgroundColor: 'rgba(102, 126, 234, 0.6)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

// Fermer les modals en cliquant à l'extérieur
window.onclick = function(event) {
    const destModal = document.getElementById('destination-modal');
    const weatherModal = document.getElementById('weather-modal');
    
    if (event.target === destModal) {
        closeDestinationModal();
    }
    if (event.target === weatherModal) {
        closeWeatherModal();
    }
}
// NOUVELLE FONCTION - Charger les prévisions météo
async function loadForecast(destinationId) {
    const container = document.getElementById('forecast-container');
    container.innerHTML = '<div class="loading">⏳ Récupération des prévisions météo...</div>';
    
    try {
        // Appel à l'API pour récupérer et sauvegarder les prévisions
        const response = await fetch(`${API_URL}/weather/destination/${destinationId}/forecast`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la récupération des prévisions');
        }
        
        const data = await response.json();
        displayForecast(data.forecasts);
    } catch (error) {
        container.innerHTML = '<p style="color: #ef4444; padding: 20px;">❌ Impossible de charger les prévisions</p>';
        console.error('Erreur:', error);
    }
}


function parseApiDate(value) {
    if (!value) return null;

    let s = String(value).trim();

    // "YYYY-MM-DD HH:mm:ss" -> "YYYY-MM-DDT HH:mm:ss" (format ISO)
    if (/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}/.test(s)) {
        s = s.replace(' ', 'T');
    }

    const d = new Date(s);
    return isNaN(d.getTime()) ? null : d;
}

function toNumberOrNull(v) {
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
}

// NOUVELLE FONCTION - Afficher les prévisions
function displayForecast(forecasts) {
    const container = document.getElementById('forecast-container');

    if (!Array.isArray(forecasts) || forecasts.length === 0) {
        container.innerHTML = '<p style="padding: 20px; text-align: center;">Aucune prévision disponible</p>';
        return;
    }

    // Nettoyage
    const cleaned = forecasts
        .map(f => {
            const d = parseApiDate(f.forecast_date);
            return {
                ...f,
                _date: d,
                temperature: toNumberOrNull(f.temperature),
                temp_min: toNumberOrNull(f.temp_min),
                temp_max: toNumberOrNull(f.temp_max),
                humidity: toNumberOrNull(f.humidity),
                weather_description: f.weather_description ?? ''
            };
        })
        .filter(f => f._date); // garde uniquement les dates valides

    if (cleaned.length === 0) {
        container.innerHTML = '<p style="padding: 20px; text-align: center;">Aucune prévision exploitable (dates invalides)</p>';
        return;
    }

    // Group by day
    const forecastsByDay = {};
    cleaned.forEach(f => {
        const dateKey = f._date.toLocaleDateString('fr-FR', {
            weekday: 'short',
            day: 'numeric',
            month: 'short'
        });
        (forecastsByDay[dateKey] ||= []).push(f);
    });

    let html = '<div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e0e0e0;">';
    html += '<h3 style="margin-bottom: 20px; color: #667eea; font-size: 1.5em;">📊 Prévisions sur 5 jours</h3>';
    html += '<div class="forecast-grid">';

    Object.entries(forecastsByDay).slice(0, 5).forEach(([day, dayForecasts]) => {
        const temps = dayForecasts.map(x => x.temperature).filter(v => v !== null);
        const mins = dayForecasts.map(x => x.temp_min).filter(v => v !== null);
        const maxs = dayForecasts.map(x => x.temp_max).filter(v => v !== null);
        const hums = dayForecasts.map(x => x.humidity).filter(v => v !== null);

        const avgTemp = temps.length ? temps.reduce((a, b) => a + b, 0) / temps.length : null;
        const minTemp = mins.length ? Math.min(...mins) : null;
        const maxTemp = maxs.length ? Math.max(...maxs) : null;
        const humidity = hums.length ? Math.round(hums.reduce((a, b) => a + b, 0) / hums.length) : null;

        const mainWeather = dayForecasts[0].weather_main;
        const description = dayForecasts[0].weather_description || '—';
        const icon = getWeatherIcon(mainWeather);

        html += `
            <div class="forecast-day">
                <div class="forecast-day-name">${day}</div>
                <div class="forecast-icon">${icon}</div>
                <div class="forecast-temp-main">${avgTemp !== null ? Math.round(avgTemp) + '°C' : '—'}</div>
                <div class="forecast-minmax">
                    <span style="color: #3b82f6;">❄️ ${minTemp !== null ? Math.round(minTemp) + '°' : '—'}</span>
                    <span style="color: #ef4444;">🔥 ${maxTemp !== null ? Math.round(maxTemp) + '°' : '—'}</span>
                </div>
                <div class="forecast-desc">${description}</div>
                <div class="forecast-humidity">💧 ${humidity !== null ? humidity + '%' : '—'}</div>
            </div>
        `;
    });

    html += '</div></div>';
    container.innerHTML = html;
}

// NOUVELLE FONCTION - Icônes météo selon les conditions
function getWeatherIcon(weatherMain) {
    const icons = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Fog': '🌫️',
        'Haze': '🌫️'
    };
    return icons[weatherMain] || '🌤️';
}
