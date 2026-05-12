document.addEventListener('DOMContentLoaded', function () {
    if (typeof forecastData !== 'undefined' && forecastData.length > 0) {
        // Chart Initialization
        const ctx = document.getElementById('weatherChart').getContext('2d');
        const labels = forecastData.map(day => day.date);
        const temps = forecastData.map(day => day.temp);
        const rainProbs = forecastData.map(day => day.rain_prob);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Nhiệt độ (°C)',
                        data: temps,
                        borderColor: 'rgba(255, 206, 86, 1)',
                        backgroundColor: 'rgba(255, 206, 86, 0.2)',
                        tension: 0.4,
                        borderWidth: 3,
                        pointBackgroundColor: '#fff',
                        pointRadius: 5,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Xác suất mưa (%)',
                        data: rainProbs,
                        borderColor: 'rgba(54, 162, 235, 0.8)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        type: 'bar',
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: 'white' } }
                },
                scales: {
                    x: { ticks: { color: 'white' }, grid: { display: false } },
                    y: { type: 'linear', display: true, position: 'left', ticks: { color: 'white' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                    y1: { type: 'linear', display: true, position: 'right', min: 0, max: 100, grid: { display: false }, ticks: { color: 'rgba(54, 162, 235, 0.8)' } }
                }
            }
        });
    }
});

// Global function to update UI with selected day's details
function showDayDetails(index) {
    if (typeof forecastData === 'undefined' || !forecastData[index]) return;

    const data = forecastData[index];

    // Update DOM elements
    // Note: We use 'full_date' from the updated utils.py or construct it. 
    // utils.py now provides 'full_date'
    document.getElementById('current-date').innerText = data.full_date || (data.day_name + ", " + data.date);

    document.getElementById('current-temp').innerText = data.temp;
    document.getElementById('current-desc').innerText = data.description;

    // Update Icon
    if (data.icon_url) {
        document.getElementById('current-icon').src = data.icon_url;
    } else {
        const iconUrl = `http://openweathermap.org/img/wn/${data.icon}@4x.png`;
        document.getElementById('current-icon').src = iconUrl;
    }

    document.getElementById('current-rain-prob').innerText = data.rain_prob;
    document.getElementById('current-humidity').innerText = data.humidity;
    document.getElementById('current-wind').innerText = data.wind_speed;
    document.getElementById('current-visibility').innerText = data.visibility;
    document.getElementById('current-pressure').innerText = data.pressure;

    // Update Hourly Forecast (NEW)
    const hourlyContainer = document.getElementById('hourly-forecast-container');
    if (hourlyContainer && data.hourly_segments) {
        hourlyContainer.innerHTML = ''; // Clear previous
        data.hourly_segments.forEach(segment => {
            const div = document.createElement('div');
            div.className = 'text-center text-white';
            div.style.minWidth = '80px';
            div.innerHTML = `
                <p class="mb-0 small opacity-75">${segment.time}</p>
                <img src="http://openweathermap.org/img/wn/${segment.icon}.png" width="40" alt="icon">
                <h6 class="mb-0">${segment.temp}°</h6>
                <small class="text-info" style="font-size: 0.7rem;"><i class="fas fa-umbrella"></i> ${segment.rain_prob}%</small>
            `;
            hourlyContainer.appendChild(div);
        });
    }

    // Scroll to top to show changes
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// SEARCH HISTORY FILTER
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const historyItems = document.querySelectorAll('.history-item');

    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            const searchTerm = e.target.value.toLowerCase();

            historyItems.forEach(item => {
                const cityNameElement = item.querySelector('.history-city');
                const cityName = cityNameElement ? cityNameElement.textContent.toLowerCase() : item.textContent.toLowerCase();

                if (cityName.includes(searchTerm)) {
                    item.style.display = ''; // Show
                } else {
                    item.style.display = 'none'; // Hide
                }
            });
        });
    }
});
