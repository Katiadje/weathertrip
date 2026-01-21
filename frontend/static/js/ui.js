import { getCurrentUser } from './config.js';

// Gestion des onglets
export function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
        if ((tabName === 'login' && btn.textContent.includes('Connexion')) ||
            (tabName === 'register' && btn.textContent.includes('Inscription'))) {
            btn.classList.add('active');
        }
    });
}

// Afficher section principale
export function showMainSection() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('main-section').classList.remove('hidden');
    document.getElementById('user-info').classList.remove('hidden');
    
    const user = getCurrentUser();
    if (user) {
        document.getElementById('username-display').textContent = user.username;
    }
}

// Afficher section auth
export function showAuthSection() {
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('main-section').classList.add('hidden');
    document.getElementById('user-info').classList.add('hidden');
}

// Modal destination
export function openDestinationModal(tripId) {
    document.getElementById('modal-trip-id').value = tripId;
    document.getElementById('destination-modal').style.display = 'block';
}

export function closeDestinationModal() {
    document.getElementById('destination-modal').style.display = 'none';
    document.getElementById('destination-form').reset();
}

// Modal météo
export function openWeatherModal() {
    document.getElementById('weather-modal').style.display = 'block';
}

export function closeWeatherModal() {
    document.getElementById('weather-modal').style.display = 'none';
}

// Click outside to close
export function setupModalCloseHandlers() {
    window.onclick = function(event) {
        const destModal = document.getElementById('destination-modal');
        const weatherModal = document.getElementById('weather-modal');
        
        if (event.target === destModal) {
            closeDestinationModal();
        }
        if (event.target === weatherModal) {
            closeWeatherModal();
        }
    };
}