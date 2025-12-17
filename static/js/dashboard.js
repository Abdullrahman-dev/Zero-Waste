// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', function () {
    console.log("🚀 Dashboard JS Loaded Successfully!"); // رسالة تأكيد في الكونسول

    const ctx = document.getElementById('wasteChart');

    if (ctx) {
        console.log("📊 Found Chart Canvas, fetching data...");
        
        // جلب البيانات من الـ API
        fetch('/api/chart-data/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log("✅ Data received:", data); // لرؤية البيانات في الكونسول

                // إعداد الرسم البياني
                new Chart(ctx, {
                    type: 'bar', // نوع الرسم
                    data: {
                        labels: data.labels, 
                        datasets: [{
                            label: 'قيمة الهدر المتوقع (ر.س)',
                            data: data.values,
                            backgroundColor: '#e74c3c', // لون أحمر
                            borderRadius: 6, // حواف ناعمة للأعمدة
                            barPercentage: 0.6, // عرض العمود
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }, // إخفاء العنوان
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
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
    } else {
        console.warn("⚠️ Chart Canvas element not found on this page.");
    }
});