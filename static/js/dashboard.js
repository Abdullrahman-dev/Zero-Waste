// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', function () {
    console.log("🚀 Dashboard JS Loaded Successfully!");

    const ctx = document.getElementById('wasteChart');

    if (ctx) {
        console.log("📊 Found Chart Canvas, fetching data...");

        fetch('/api/chart-data/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log("✅ Data received:", data);

                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'قيمة الهدر المتوقع (ر.س)',
                            data: data.values,
                            backgroundColor: '#e74c3c',
                            borderRadius: 6,
                            barPercentage: 0.6,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        return context.raw + ' ر.س';
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: '#f0f0f0', borderDash: [5, 5] }
                            },
                            x: {
                                grid: { display: false }
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('❌ Error loading chart:', error);
            });
    }

    // --- Theme Toggle Logic ---
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const currentTheme = localStorage.getItem('theme') || 'light';

        // Apply saved theme on load
        if (currentTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            themeToggle.checked = true;
        }

        themeToggle.addEventListener('change', function () {
            if (this.checked) {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
            }
        });
    }
});