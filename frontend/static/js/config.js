// ==================== Configuration API ====================
export const API_URL = `${window.location.protocol}//${window.location.host}`;

// ==================== État global ====================
export const state = {
    currentUser: null,
    currentTrips: [],
    chart: null,
    csrfToken: null
};

// ==================== Getters / Setters ====================
export function setCurrentUser(user) {
    state.currentUser = user;
}

export function getCurrentUser() {
    return state.currentUser;
}

export function setCurrentTrips(trips) {
    state.currentTrips = trips;
}

export function getCurrentTrips() {
    return state.currentTrips;
}

export function setChart(chart) {
    state.chart = chart;
}

export function getChart() {
    return state.chart;
}

// ==================== CSRF ====================
export function setCsrfToken(token) {
    state.csrfToken = token;
}

export function getCsrfToken() {
    return state.csrfToken;
}

// ==================== Fetch sécurisé ====================
/**
 * apiFetch :
 * - ajoute automatiquement JWT si présent
 * - ajoute automatiquement X-CSRF-Token pour POST/PUT/DELETE
 * - récupère et stocke le CSRF token depuis la réponse
 */
export async function apiFetch(path, options = {}) {
    const url = `${API_URL}${path}`;
    const method = (options.method || "GET").toUpperCase();

    const headers = new Headers(options.headers || {});
    headers.set("Content-Type", headers.get("Content-Type") || "application/json");

    // JWT
    const token = localStorage.getItem("token");
    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    // CSRF (méthodes non safe)
    if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
        if (state.csrfToken) {
            headers.set("X-CSRF-Token", state.csrfToken);
        }
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    // Récupération du CSRF token depuis la réponse
    const newCsrfToken = response.headers.get("X-CSRF-Token");
    if (newCsrfToken) {
        setCsrfToken(newCsrfToken);
    }

    return response;
}

// ==================== Initialisation CSRF ====================
/**
 * Appelé au chargement de l'app
 * Permet de récupérer un CSRF token initial
 */
export async function initCsrf() {
    try {
        const response = await apiFetch("/", { method: "GET" });
        return response.ok;
    } catch (e) {
        console.error("Erreur initialisation CSRF", e);
        return false;
    }
}
