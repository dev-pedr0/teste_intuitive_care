<template>
  <main class="expenses-page">
    <h2>Despesas da Operadora</h2>

    <table class="expenses-table" v-if="despesas.length">
      <thead>
        <tr>
          <th>Ano</th>
          <th>Trimestre</th>
          <th>Valor das Despesas</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in despesas" :key="index">
          <td>{{ item.ano }}</td>
          <td>{{ item.trimestre }}º</td>
          <td>{{ formatarMoeda(item.valor_despesas) }}</td>
        </tr>
        <tr class="total-row">
          <td colspan="2"><strong>Total</strong></td>
          <td><strong>{{ formatarMoeda(totalDespesas) }}</strong></td>
        </tr>
      </tbody>
    </table>

    <p v-else>Carregando despesas...</p>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

const route = useRoute();
const despesas = ref<any[]>([]);

// Função para formatar valores como "R$ 1.000.000,00"
function formatarMoeda(valor: number | string) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(valor));
}

// Chamada de API de despesas
async function carregarDespesas() {
  try {
    const cnpj = route.params.cnpj; // pega o cnpj da rota
    const res = await axios.get(`http://localhost:8000/api/operadoras/${cnpj}/despesas`);
    despesas.value = res.data.despesas;
  } catch (err) {
    console.error("Erro ao carregar despesas:", err);
  }
}

// Calcula total de despesas
const totalDespesas = computed(() =>
  despesas.value.reduce((acc, item) => acc + Number(item.valor_despesas), 0)
);

onMounted(() => {
  carregarDespesas();
});
</script>