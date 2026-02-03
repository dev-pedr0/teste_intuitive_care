<template>
  <main class="stats-page">
    <StatsChart
      title="5 Operadoras com Maior Crescimento de Gastos"
      :labels="crescimentoLabels"
      :data="crescimentoData"
    />

    <StatsChart
      title="5 Estados com Maior Despesa Total"
      :labels="estadosLabels"
      :data="estadosData"
    />

    <StatsChart
      title="Valores de Operadoras Acima da Média de Gastos"
      :labels="acimaMediaLabels"
      :data="acimaMediaData"
    />
  </main>
</template>

<script setup lang="ts">
import StatsChart from '@/components/StatsChart.vue';
import axios from "axios";
import { ref, onMounted, computed } from "vue";

const crescimentoLabels = ref<string[]>([]);
const crescimentoData = ref<number[]>([]);

const estadosLabels = ref<string[]>([]);
const estadosData = ref<number[]>([]);

const acimaMediaLabels = ref<string[]>([]);
const acimaMediaData = ref<number[]>([]);

async function carregarEstatisticas() {
  const res = await axios.get("http://localhost:8000/api/estatisticas");

  // Crescimento de despesas (top 5 completos)
  const completos = res.data.crescimento_despesas.dados_completos;
  crescimentoLabels.value = completos.map((o: any) => o.razao_social);
  crescimentoData.value = completos.map((o: any) => o.crescimento_percentual);

  // Estados com maiores despesas
  estadosLabels.value = res.data.estados_maiores_despesas.map((e: any) => e.uf);
  estadosData.value = res.data.estados_maiores_despesas.map(
    (e: any) => parseFloat(e.total_despesas_uf)
  );

  // Operadoras acima da média
  acimaMediaLabels.value = res.data.operadoras_acima_media.lista
  .slice(0, 10)                              // limita aos 10 primeiros
  .map((o: any) => o.razao_social);

acimaMediaData.value = res.data.operadoras_acima_media.lista
  .slice(0, 10)                              // limita aos 10 primeiros
  .map((o: any) => parseFloat(o.trimestres_acima_da_media));
}

onMounted(() => {
  carregarEstatisticas();
});

</script>