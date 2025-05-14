let topSkillsChart, cityChart, trendChart, sentimentChart;

document.addEventListener('DOMContentLoaded', () => {
  renderInitialCharts(window.initialTopSkills, window.initialCityData);
  renderTrendChart(window.jobsByWeek);
  renderSentimentChart(window.sentimentByCity);

  document.getElementById('analytics-filters').addEventListener('change', () => {
    const filters = {
      city: document.getElementById('city').value,
      type: document.getElementById('type').value
    };
    updateCharts(filters);
  });

  document.getElementById('resetBtn').addEventListener('click', () => {
    document.getElementById('city').value = '';
    document.getElementById('type').value = '';
    updateCharts();
  });
});

function renderInitialCharts(topSkillsData, cityData) {
  const ctx1 = document.getElementById('topSkillsChart').getContext('2d');
  topSkillsChart = new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: Object.keys(topSkillsData),
      datasets: [{
        label: 'Top Skills',
        data: Object.values(topSkillsData),
        backgroundColor: '#007bff'
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } }
    }
  });

  const ctx2 = document.getElementById('cityChart').getContext('2d');
  cityChart = new Chart(ctx2, {
    type: 'doughnut',
    data: {
      labels: Object.keys(cityData),
      datasets: [{
        label: 'Jobs by City',
        data: Object.values(cityData),
        backgroundColor: ['#4caf50', '#2196f3', '#ff9800', '#e91e63', '#9c27b0']
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } }
    }
  });
}

function renderTrendChart(jobsByWeek) {
  const ctx = document.getElementById('trendChart').getContext('2d');
  if (trendChart) trendChart.destroy();
  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: Object.keys(jobsByWeek),
      datasets: [{
        label: 'Jobs per Week',
        data: Object.values(jobsByWeek),
        borderColor: '#007bff',
        fill: false
      }]
    },
    options: {
      responsive: true,
      scales: {
        x: { title: { display: true, text: 'Week' } },
        y: { title: { display: true, text: 'Jobs' } }
      }
    }
  });
}

function renderSentimentChart(sentimentData) {
  const ctx = document.getElementById('sentimentChart').getContext('2d');
  if (sentimentChart) sentimentChart.destroy();

  const labels = Object.keys(sentimentData);
  const values = Object.values(sentimentData);

  const backgroundColors = values.map(score => {
    if (score > 0.1) return '#4caf50';
    if (score < -0.1) return '#f44336';
    return '#ffc107';
  });

  sentimentChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Avg Sentiment by City',
        data: values,
        backgroundColor: backgroundColors
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `Sentiment: ${ctx.raw.toFixed(2)}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          min: -1,
          max: 1,
          title: { display: true, text: 'Polarity Score' }
        }
      }
    }
  });
}


function updateCharts(filters = {}) {
  fetch(`/analytics/data?city=${filters.city || ''}&type=${filters.type || ''}`)
    .then(res => res.json())
    .then(data => {
      console.log("📊 Fetched data:", data);

      if (!data.top_skills || !Object.keys(data.top_skills).length) {
        alert("⚠️ No matching jobs found for selected filters.");
      }

      // top skills chart
      topSkillsChart.data.labels = Object.keys(data.top_skills);
      topSkillsChart.data.datasets[0].data = Object.values(data.top_skills);
      topSkillsChart.update();

      // city chart
      cityChart.data.labels = Object.keys(data.jobs_by_city);
      cityChart.data.datasets[0].data = Object.values(data.jobs_by_city);
      cityChart.update();

      // trend and sentiment charts
      renderTrendChart(data.jobs_by_week);
      renderSentimentChart(data.sentiment_by_city);
    })
    .catch(err => {
      console.error("❌ Error loading chart data:", err);
    });
}

function downloadAllChartsAsImage() {
  const chartIds = ['topSkillsChart', 'cityChart', 'trendChart', 'sentimentChart'];
  const titles = ['Top Skills', 'Jobs by City', 'Jobs Per Week', 'Sentiment by City'];

  const chartWidth = 600;
  const chartHeight = 400;
  const padding = 20;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = chartWidth * 2 + padding * 3;
  canvas.height = chartHeight * 2 + padding * 3;

  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  chartIds.forEach((id, i) => {
    const chartCanvas = document.getElementById(id);
    const x = padding + (i % 2) * (chartWidth + padding);
    const y = padding + Math.floor(i / 2) * (chartHeight + padding);
    ctx.drawImage(chartCanvas, x, y, chartWidth, chartHeight);
    ctx.fillStyle = "#000";
    ctx.font = "16px Arial";
    ctx.fillText(titles[i], x + 10, y + 20);
  });

  const link = document.createElement('a');
  link.href = canvas.toDataURL('image/png');
  link.download = 'job-analytics.png';
  link.click();
}
function showSpinner() {
  document.getElementById('spinner').style.display = 'flex';
}

function hideSpinner() {
  document.getElementById('spinner').style.display = 'none';
}