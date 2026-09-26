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

    const context = ctx.getContext('2d');
    const gradient = context.createRadialGradient(
      ctx.width / 2, ctx.height / 2, 10,
      ctx.width / 2, ctx.height / 2, 180
    );
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.35)');
    gradient.addColorStop(0.7, 'rgba(99, 102, 241, 0.2)');
    gradient.addColorStop(1, 'rgba(147, 197, 253, 0.05)');

    radarChartInstance = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: topicLabels,
        datasets: [{
          label: 'Mastery Level (%)',
          data: scores,
          backgroundColor: gradient,
          borderColor: '#2563eb',
          pointBackgroundColor: '#2563eb',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointHoverBackgroundColor: '#1d4ed8',
          pointHoverBorderColor: '#ffffff',
          pointHoverBorderWidth: 3,
          borderWidth: 2.5,
          pointRadius: 4.5,
          pointHoverRadius: 6.5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 900,
          easing: 'easeOutQuart'
        },
        scales: {
          r: {
            angleLines: { color: 'rgba(226, 232, 240, 0.75)' },
            grid: { color: 'rgba(241, 245, 249, 0.9)' },
            pointLabels: {
              color: '#334155',
              font: { family: 'Plus Jakarta Sans, sans-serif', size: 11.5, weight: '600' }
            },
            ticks: {
              backdropColor: 'transparent',
              color: '#94a3b8',
              stepSize: 20,
              font: { family: 'JetBrains Mono, monospace', size: 10 }
            },
            min: 0,
            max: 100
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.92)',
            titleFont: { family: 'Plus Jakarta Sans, sans-serif', weight: '700', size: 12.5 },
            bodyFont: { family: 'Plus Jakarta Sans, sans-serif', size: 12 },
            padding: 12,
            cornerRadius: 10,
            boxPadding: 4,
            borderColor: 'rgba(255, 255, 255, 0.15)',
            borderWidth: 1,
            callbacks: {
              label: (context) => ` Live Mastery: ${context.raw}%`
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

    // Color code with luminous gradients
    const context = ctx.getContext('2d');
    const barColors = scores.map(s => {
      if (s >= 75) {
        const grad = context.createLinearGradient(0, 0, 300, 0);
        grad.addColorStop(0, '#10b981');
        grad.addColorStop(1, '#34d399');
        return grad;
      }
      if (s >= 50) {
        const grad = context.createLinearGradient(0, 0, 300, 0);
        grad.addColorStop(0, '#f59e0b');
        grad.addColorStop(1, '#fbbf24');
        return grad;
      }
      const grad = context.createLinearGradient(0, 0, 300, 0);
      grad.addColorStop(0, '#ef4444');
      grad.addColorStop(1, '#f43f5e');
      return grad;
    });

    barChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: topicLabels,
        datasets: [{
          label: 'Topic Mastery %',
          data: scores,
          backgroundColor: barColors,
          borderRadius: 8,
          borderSkipped: false,
          barPercentage: 0.65
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 900,
          easing: 'easeOutQuart'
        },
        scales: {
          x: {
            min: 0,
            max: 100,
            grid: { color: 'rgba(241, 245, 249, 0.9)' },
            ticks: { 
              color: '#94a3b8', 
              font: { family: 'JetBrains Mono, monospace', size: 10.5 },
              callback: (val) => `${val}%`
            }
          },
          y: {
            grid: { display: false },
            ticks: { 
              color: '#1e293b', 
              font: { family: 'Plus Jakarta Sans, sans-serif', size: 12, weight: '600' } 
            }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.92)',
            titleFont: { family: 'Plus Jakarta Sans, sans-serif', weight: '700', size: 12.5 },
            bodyFont: { family: 'Plus Jakarta Sans, sans-serif', size: 12 },
            padding: 12,
            cornerRadius: 10,
            borderColor: 'rgba(255, 255, 255, 0.15)',
            borderWidth: 1,
            callbacks: {
              label: (context) => {
                const score = context.raw;
                const status = score >= 75 ? 'Strong Proficiency' : (score >= 50 ? 'Average - Practice Recommended' : 'Critical Weak Spot');
                return ` Mastery: ${score}% • ${status}`;
              }
            }
          }
        }
      }
    });
  }
};
