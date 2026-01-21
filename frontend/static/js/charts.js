import { getCurrentTrips, getChart, setChart } from './config.js';

// Mettre à jour le graphique
export function updateChart() {
    const ctx = document.getElementById('trips-chart').getContext('2d');
    const trips = getCurrentTrips();
    
    // Détruire l'ancien graphique
    const oldChart = getChart();
    if (oldChart) {
        oldChart.destroy();
    }
    
    const labels = trips.map(trip => trip.name);
    const destinationsCount = trips.map(trip => trip.destinations ? trip.destinations.length : 0);
    
    const newChart = new Chart(ctx, {
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
                    ticks: { stepSize: 1 }
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
    
    setChart(newChart);
}