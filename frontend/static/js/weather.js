import { API_URL } from './config.js';
import { openWeatherModal, closeWeatherModal } from './ui.js';

// Icônes météo
export function getWeatherIcon(weatherMain) {
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

// Voir la météo d'une destination
export async function viewWeather(destinationId) {
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

// Voir la météo d'un voyage
export async function viewTripWeather(tripId) {
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

// Afficher météo destination
function displayWeather(data) {
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
                <button class="btn btn-primary" onclick="window.loadForecast(${dest.id})" style="width: 100%; font-size: 1.1em;">
                    📅 Afficher les prévisions 5 jours
                </button>
            </div>
            
            <div id="forecast-container"></div>
        `;
    }
    
    openWeatherModal();
}

// Afficher météo voyage
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
    
    openWeatherModal();
}

// Charger prévisions
export async function loadForecast(destinationId) {
    const container = document.getElementById('forecast-container');
    container.innerHTML = '<div class="loading">⏳ Récupération des prévisions météo...</div>';
    
    try {
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

// Afficher prévisions
function displayForecast(forecasts) {
    const container = document.getElementById('forecast-container');

    if (!Array.isArray(forecasts) || forecasts.length === 0) {
        container.innerHTML = '<p style="padding: 20px; text-align: center;">Aucune prévision disponible</p>';
        return;
    }

    const parseDate = (value) => {
        if (!value) return null;
        let s = String(value).trim();
        if (/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}/.test(s)) {
            s = s.replace(' ', 'T');
        }
        const d = new Date(s);
        return isNaN(d.getTime()) ? null : d;
    };

    const toNumber = (v) => {
        const n = Number(v);
        return Number.isFinite(n) ? n : null;
    };

    const cleaned = forecasts
        .map(f => ({
            ...f,
            _date: parseDate(f.forecast_date),
            temperature: toNumber(f.temperature),
            temp_min: toNumber(f.temp_min),
            temp_max: toNumber(f.temp_max),
            humidity: toNumber(f.humidity),
            weather_description: f.weather_description ?? ''
        }))
        .filter(f => f._date);

    if (cleaned.length === 0) {
        container.innerHTML = '<p style="padding: 20px; text-align: center;">Aucune prévision exploitable</p>';
        return;
    }

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