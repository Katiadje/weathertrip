import { initCsrf } from './config.js';
import { handleLogin, handleRegister, checkAuth, logout } from './auth.js';
import { showMainSection, showAuthSection, showTab, openDestinationModal, closeDestinationModal, setupModalCloseHandlers, openWeatherModal, closeWeatherModal } from './ui.js';
import { loadTrips, setupTripForm, deleteTrip } from './trips.js';
import { setupDestinationForm, deleteDestination } from './destinations.js';
import { getDestinationWeather } from './weather.js';

// ==================== FONCTIONS GLOBALES ====================
// Définir AVANT DOMContentLoaded pour que onclick fonctionne
window.logout = logout;
window.showTab = showTab;
window.closeDestinationModal = closeDestinationModal;
window.openDestinationModal = openDestinationModal;
window.deleteTrip = async (tripId) => {
    if (confirm('Supprimer ce voyage ?')) {
        try {
            await deleteTrip(tripId);
            await loadTrips();
        } catch (err) {
            alert('Erreur: ' + err.message);
        }
    }
};
window.deleteDestination = async (destinationId) => {
    if (confirm('Supprimer cette destination ?')) {
        try {
            await deleteDestination(destinationId);
            await loadTrips();
        } catch (err) {
            alert('Erreur: ' + err.message);
        }
    }
};

window.showWeather = async (destinationId, city, country) => {
    try {
        openWeatherModal();
        const weatherContent = document.getElementById('weather-content');
        weatherContent.innerHTML = '<div class="loading">Chargement de la météo...</div>';
        
        const data = await getDestinationWeather(destinationId);
        
        if (!data || !data.current_weather) {
            weatherContent.innerHTML = `
                <p style="text-align:center;color:#999;">❌ Météo non disponible pour ${city}, ${country}</p>
            `;
            return;
        }
        
        const w = data.current_weather;
        weatherContent.innerHTML = `
            <div style="text-align:center;">
                <h3 style="color:#667eea;margin-bottom:20px;">${city}, ${country}</h3>
                <div style="font-size:3em;margin-bottom:10px;">🌡️</div>
                <div style="font-size:2em;margin-bottom:20px;font-weight:bold;color:#764ba2;">
                    ${w.temperature}°C
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-bottom:20px;">
                    <div style="background:#f8f9ff;padding:15px;border-radius:8px;">
                        <div style="color:#666;font-size:0.9em;">Ressenti</div>
                        <div style="font-weight:bold;">${w.feels_like}°C</div>
                    </div>
                    <div style="background:#f8f9ff;padding:15px;border-radius:8px;">
                        <div style="color:#666;font-size:0.9em;">Humidité</div>
                        <div style="font-weight:bold;">${w.humidity}%</div>
                    </div>
                    <div style="background:#f8f9ff;padding:15px;border-radius:8px;">
                        <div style="color:#666;font-size:0.9em;">Vent</div>
                        <div style="font-weight:bold;">${w.wind_speed} m/s</div>
                    </div>
                    <div style="background:#f8f9ff;padding:15px;border-radius:8px;">
                        <div style="color:#666;font-size:0.9em;">Description</div>
                        <div style="font-weight:bold;">${w.description}</div>
                    </div>
                </div>
                <div style="color:#999;font-size:0.85em;">
                    Dernière mise à jour: ${new Date(data.last_updated).toLocaleString('fr-FR')}
                </div>
            </div>
        `;
    } catch (err) {
        console.error('Erreur météo:', err);
        document.getElementById('weather-content').innerHTML = `
            <p style="text-align:center;color:#dc3545;">❌ Erreur: ${err.message}</p>
        `;
    }
};

window.closeWeatherModal = closeWeatherModal;

// ==================== INITIALISATION ====================
document.addEventListener('DOMContentLoaded', async () => {
    await initCsrf();
    
    setupTripForm?.();
    setupDestinationForm?.();
    setupModalCloseHandlers?.();

    document.getElementById('login-form')?.addEventListener('submit', handleLogin);
    document.getElementById('register-form')?.addEventListener('submit', handleRegister);

    if (checkAuth()) {
        showMainSection();
        loadTrips();
    } else {
        showAuthSection();
    }
});