import { API_URL, setCurrentUser, getCurrentUser, setCurrentTrips } from './config.js';
import { showMainSection, showAuthSection } from './ui.js';
import { loadTrips } from './trips.js';

// Connexion
export async function handleLogin(e) {
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
        
        // Stocker les informations
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userId', data.user_id);
        localStorage.setItem('username', data.username);
        
        setCurrentUser({ 
            id: data.user_id, 
            username: data.username, 
            token: data.access_token 
        });
        
        showMainSection();
        loadTrips();
        
        document.getElementById('login-form').reset();
    } catch (error) {
        alert('Erreur de connexion: ' + error.message);
    }
}

// Inscription
export async function handleRegister(e) {
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
        
        document.getElementById('register-form').reset();
    } catch (error) {
        alert('Erreur d\'inscription: ' + error.message);
    }
}

// Déconnexion
export function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    
    setCurrentUser(null);
    setCurrentTrips([]);
    
    showAuthSection();
}

// Vérifier si utilisateur connecté
export function checkAuth() {
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const username = localStorage.getItem('username');
    
    if (token && userId) {
        setCurrentUser({ id: parseInt(userId), username, token });
        return true;
    }
    return false;
}