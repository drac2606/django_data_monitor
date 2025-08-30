/**
 * For usage, visit Chart.js docs https://www.chartjs.org/docs/latest/
 */

// Función para obtener datos del gráfico desde el backend
function getChartData() {
  // Obtener los datos del gráfico desde el contexto de Django
  // Estos datos se pasan desde la vista
  const chartData = window.chartData || [];
  
  if (chartData.length === 0) {
    return {
      labels: [],
      data: []
    };
  }
  
  const labels = chartData.map(item => item.date);
  const data = chartData.map(item => item.total_people);
  
  return { labels, data };
}

// Función para crear el gráfico
function createChart() {
  const chartInfo = getChartData();
  
  // Verificar que tenemos datos válidos
  if (chartInfo.labels.length === 0 || chartInfo.data.length === 0) {
    return;
  }
  
  const lineConfig = {
    type: 'line',
    data: {
      labels: chartInfo.labels,
      datasets: [
        {
          label: 'Cantidad de Personas por Día',
          /**
           * These colors come from Tailwind CSS palette
           * https://tailwindcss.com/docs/customizing-colors/#default-color-palette
           */
          backgroundColor: '#0694a2',
          borderColor: '#0694a2',
          data: chartInfo.data,
          fill: false,
          tension: 0.4,
          pointRadius: 6,
          pointHoverRadius: 8,
        },
      ],
    },
    options: {
      responsive: true,
      /**
       * Default legends are ugly and impossible to style.
       * See examples in charts.html to add your own legends
       *  */
      legend: {
        display: true,
        position: 'top',
        labels: {
          fontColor: '#6b7280',
          fontSize: 12,
          usePointStyle: true,
        }
      },
      tooltips: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: function(context) {
            return `Personas: ${context.parsed.y}`;
          }
        }
      },
      hover: {
        mode: 'nearest',
        intersect: true,
      },
      scales: {
        x: {
          display: true,
          scaleLabel: {
            display: true,
            labelString: 'Fecha',
            fontColor: '#6b7280',
            fontSize: 14,
          },
          ticks: {
            fontColor: '#6b7280',
            fontSize: 12,
          }
        },
        y: {
          display: true,
          scaleLabel: {
            display: true,
            labelString: 'Cantidad de Personas',
            fontColor: '#6b7280',
            fontSize: 14,
          },
          ticks: {
            fontColor: '#6b7280',
            fontSize: 12,
            callback: function(value) {
              return value + ' personas';
            }
          }
        },
      },
    },
  }

  // change this to the id of your chart element in HMTL
  const lineCtx = document.getElementById('line')
  if (lineCtx) {
    // Destruir gráfico existente si existe
    if (window.myLine) {
      window.myLine.destroy();
    }
    window.myLine = new Chart(lineCtx, lineConfig)
  }
}

// Esperar a que la página esté completamente cargada
document.addEventListener('DOMContentLoaded', function() {
  // Esperar un poco más para asegurar que los datos estén disponibles
  setTimeout(createChart, 200);
});

// También crear el gráfico cuando la ventana esté completamente cargada
window.addEventListener('load', createChart);
