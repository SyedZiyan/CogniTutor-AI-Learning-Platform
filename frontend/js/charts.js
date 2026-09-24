// Chart visualizations for CogniTutor AI Learning Platform
let radarChartInstance = null;
let barChartInstance = null;

const chartManager = {
  renderCompetencyRadar(canvasId, topicLabels, scores) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (radarChartInstance) {
      radarChartInstance.destroy();
    }

    radarChartInstance = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: topicLabels,
        datasets: [{
          label: 'Mastery Level (%)',
          data: scores,
          backgroundColor: 'rgba(37, 99, 235, 0.12)',
          borderColor: '#2563eb',
          pointBackgroundColor: '#2563eb',
          pointBorderColor: '#ffffff',
          pointHoverBackgroundColor: '#1d4ed8',
          pointHoverBorderColor: '#ffffff',
          borderWidth: 2,
          pointRadius: 3.5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: '#e2e8f0' },
            grid: { color: '#f1f5f9' },
            pointLabels: {
              color: '#334155',
              font: { family: 'Inter', size: 11, weight: '500' }
            },
            ticks: {
              backdropColor: 'transparent',
              color: '#94a3b8',
              stepSize: 20
            },
            min: 0,
            max: 100
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            titleFont: { family: 'Inter', weight: 'bold', size: 12 },
            bodyFont: { family: 'Inter', size: 12 },
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: (context) => `Mastery: ${context.raw}%`
            }
          }
        }
      }
    });
  },

  renderMasteryBars(canvasId, topicLabels, scores) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (barChartInstance) {
      barChartInstance.destroy();
    }

    // Color code: green if >= 75, amber if >= 50, rose if < 50
    const barColors = scores.map(s => {
      if (s >= 75) return '#10b981';
      if (s >= 50) return '#f59e0b';
      return '#f43f5e';
    });

    barChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: topicLabels,
        datasets: [{
          label: 'Topic Mastery %',
          data: scores,
          backgroundColor: barColors,
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            min: 0,
            max: 100,
            grid: { color: '#f1f5f9' },
            ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
          },
          y: {
            grid: { display: false },
            ticks: { color: '#334155', font: { family: 'Inter', size: 11, weight: '500' } }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: (context) => {
                const score = context.raw;
                const status = score >= 75 ? 'Strong' : (score >= 50 ? 'Average' : 'Needs Work');
                return `${score}% (${status})`;
              }
            }
          }
        }
      }
    });
  }
};
