// apps/core/static/core/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('wasteChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['فرع التحلية', 'فرع المطار', 'فرع الروابي', 'فرع البلد'],
            datasets: [{
                label: 'نسبة الهدر المتوقعة (%)',
                data: [12, 19, 3, 5],
                backgroundColor: [
                    'rgba(231, 76, 60, 0.7)',
                    'rgba(231, 76, 60, 0.7)',
                    'rgba(39, 174, 96, 0.7)',
                    'rgba(39, 174, 96, 0.7)'
                ],
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});