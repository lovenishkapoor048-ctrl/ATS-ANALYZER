/* script.js
   Chart rendering for the result page and dashboard.
   Color tokens mirror the CSS custom properties in style.css. */

const COLORS = {
  ink: "#14213D",
  green: "#1F9D6C",
  amber: "#B9791A",
  coral: "#C43D2A",
  border: "#E3E7ED",
  slate: "#6B7280",
};

function renderResultCharts(data) {
  // --- Score donut ---
  const donutCtx = document.getElementById("scoreDonut");
  if (donutCtx) {
    new Chart(donutCtx, {
      type: "doughnut",
      data: {
        labels: data.score_donut.labels,
        datasets: [
          {
            data: data.score_donut.data,
            backgroundColor: [COLORS.green, COLORS.border],
            borderWidth: 0,
          },
        ],
      },
      options: {
        cutout: "78%",
        responsive: true,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        animation: { animateRotate: true, duration: 900 },
      },
    });
  }

  // --- Category bar chart ---
  const barCtx = document.getElementById("categoryBar");
  if (barCtx) {
    new Chart(barCtx, {
      type: "bar",
      data: {
        labels: data.category_bar.labels,
        datasets: [
          {
            label: "Score",
            data: data.category_bar.data,
            backgroundColor: COLORS.ink,
            borderRadius: 6,
            maxBarThickness: 46,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        scales: {
          x: { min: 0, max: 100, grid: { color: COLORS.border } },
          y: { grid: { display: false } },
        },
        plugins: { legend: { display: false } },
      },
    });
  }

  // --- Keyword coverage pie ---
  const pieCtx = document.getElementById("keywordPie");
  if (pieCtx) {
    new Chart(pieCtx, {
      type: "pie",
      data: {
        labels: data.keyword_pie.labels,
        datasets: [
          {
            data: data.keyword_pie.data,
            backgroundColor: [COLORS.green, COLORS.amber],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } },
      },
    });
  }
}

function renderTrendChart(trend) {
  const ctx = document.getElementById("trendChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "line",
    data: {
      labels: trend.labels,
      datasets: [
        {
          label: "ATS Score",
          data: trend.data,
          borderColor: COLORS.green,
          backgroundColor: "rgba(31, 157, 108, 0.1)",
          fill: true,
          tension: 0.35,
          pointRadius: 4,
          pointBackgroundColor: COLORS.green,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: { min: 0, max: 100, grid: { color: COLORS.border } },
        x: { grid: { display: false } },
      },
      plugins: { legend: { display: false } },
    },
  });
}
