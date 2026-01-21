// Configuration de l'API
export const API_URL = `${window.location.protocol}//${window.location.host}`;

// État global de l'application
export const state = {
    currentUser: null,
    currentTrips: [],
    chart: null
};

// Getters/Setters
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