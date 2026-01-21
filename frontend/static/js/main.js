import { checkAuth } from './auth.js';
import { handleLogin, handleRegister, logout } from './auth.js';
import { handleCreateTrip, loadTrips, deleteTrip } from './trips.js';
import { handleAddDestination, deleteDestination } from './destinations.js';
import { viewWeather, viewTripWeather, loadForecast } from './weather.js';
import { showMainSection, showTab, setupModalCloseHandlers, openDestinationModal, closeDestinationModal, closeWeatherModal } from './ui.js';

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier auth
    if (checkAuth()) {
        showMainSection();
        loadTrips();
    }
    
    // Event listeners
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('trip-form').addEventListener('submit', handleCreateTrip);
    document.getElementById('destination-form').addEventListener('submit', handleAddDestination);
    
    // Setup modal handlers
    setupModalCloseHandlers();
});

// Exposer les fonctions globales pour les onclick HTML
window.showTab = showTab;
window.logout = logout;
window.openDestinationModal = openDestinationModal;
window.closeDestinationModal = closeDestinationModal;
window.closeWeatherModal = closeWeatherModal;
window.deleteTrip = deleteTrip;
window.deleteDestination = deleteDestination;
window.viewWeather = viewWeather;
window.viewTripWeather = viewTripWeather;
window.loadForecast = loadForecast;