<template>
  <div>
    <h3>{{ title }}</h3>
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from "chart.js";
import { computed } from "vue";

// Registrar elementos do Chart.js
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

// Props
const props = defineProps<{
  title: string;
  labels: string[];
  data: number[];
}>();

// Dados do gráfico
const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      label: props.title,
      backgroundColor: "#42A5F5",
      data: props.data
    }
  ]
}));

// Opções do gráfico
const chartOptions = computed(() => {
  const isOperadoras = props.title.includes("Operadoras"); // true para gráfico 1 e 3
  const showXLabels = !isOperadoras;

  return {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: {
          display: showXLabels,
          autoSkip: true,
          maxRotation: 90,
          minRotation: 45
        },
        grid: {
          display: true
        }
      },
      y: {
        beginAtZero: true,
        suggestedMax: Math.max(...(props.data || [0])) * 1.15,
        ticks: {
          precision: 0
        }
      }
    },
    plugins: {
      legend: {
        display: true,
        position: 'top' as const
      },
      tooltip: {
        enabled: true
      }
    }
  };
});
</script>

<style scoped>
div {
  width: 100%;
  max-width: 800px;
  margin-bottom: 2rem;
  height: 800px;
}
</style>