document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('consumptionChart').getContext('2d');
    
    // Gradiente para el área debajo de la línea
    const gradientRequested = ctx.createLinearGradient(0, 0, 0, 400);
    gradientRequested.addColorStop(0, 'rgba(59, 130, 246, 0.5)');   // primary color
    gradientRequested.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
    
    const gradientAuthorized = ctx.createLinearGradient(0, 0, 0, 400);
    gradientAuthorized.addColorStop(0, 'rgba(16, 185, 129, 0.5)');  // success color
    gradientAuthorized.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

    // Datos simulados basados en tu archivo Maestro
    const data = {
        labels: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
        datasets: [
            {
                label: 'Solicitado (Lts)',
                data: [2500, 2100, 2400, 2800, 2200, 1500, 1080],
                borderColor: '#3b82f6',
                backgroundColor: gradientRequested,
                borderWidth: 3,
                pointBackgroundColor: '#0f172a',
                pointBorderColor: '#3b82f6',
                pointBorderWidth: 2,
                pointRadius: 4,
                fill: true,
                tension: 0.4
            },
            {
                label: 'Autorizado / Entregado (Lts)',
                data: [2200, 2100, 2000, 2300, 2000, 1000, 600],
                borderColor: '#10b981',
                backgroundColor: gradientAuthorized,
                borderWidth: 3,
                pointBackgroundColor: '#0f172a',
                pointBorderColor: '#10b981',
                pointBorderWidth: 2,
                pointRadius: 4,
                fill: true,
                tension: 0.4
            }
        ]
    };

    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#f8fafc',
                        font: {
                            family: 'Outfit',
                            size: 13
                        },
                        usePointStyle: true,
                        boxWidth: 8
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleFont: { family: 'Outfit', size: 14 },
                    bodyFont: { family: 'Outfit', size: 13 },
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: { family: 'Outfit' }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: { family: 'Outfit' }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index',
            },
        }
    };

    new Chart(ctx, config);
});
