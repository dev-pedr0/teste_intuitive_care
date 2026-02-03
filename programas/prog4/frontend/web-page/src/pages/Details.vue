<template>
  <main class="details-page">
    <h2>Detalhes da Operadora</h2>

    <div v-if="loading" class="loading">Carregando dados...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="details-list">
      <div class="detail-item">
        <span class="label">Status do Cadastro</span>
        <span class="value">{{ dados.status }}</span>
      </div>
      <div class="detail-item">
        <span class="label">Razão Social</span>
        <span class="value">{{ dados.razaoSocial }}</span>
      </div>
      <div class="detail-item">
        <span class="label">CNPJ</span>
        <span class="value">{{ dados.cnpj }}</span>
      </div>
      <div class="detail-item">
        <span class="label">Registro ANS</span>
        <span class="value">{{ dados.registroAns }}</span>
      </div>
      <div class="detail-item">
        <span class="label">UF</span>
        <span class="value">{{ dados.uf }}</span>
      </div>
      <div class="detail-item">
        <span class="label">Modalidade</span>
        <span class="value">{{ dados.modalidade }}</span>
      </div>

      <div class="detail-item separator">
        <span class="label">Total de Despesas</span>
        <span class="value">{{ formatarMoeda(dados.totalDespesas) }}</span>
      </div>

      <div class="detail-item">
        <span class="label">Média 1º Trimestre</span>
        <span class="value">{{ formatarMoeda(dados.mediaT1) }}</span>
      </div>
      <div class="detail-item">
        <span class="label">Média 2º Trimestre</span>
        <span class="value">{{ formatarMoeda(dados.mediaT2) }}</span>
      </div>
      <div class="detail-item">
        <span class="label">Média 3º Trimestre</span>
        <span class="value">{{ formatarMoeda(dados.mediaT3) }}</span>
      </div>

      <div class="detail-item separator">
        <span class="label">Desvio 1º Trimestre</span>
        <span class="value">{{ formatarMoeda(dados.desvioT1) }}</span>
      </div>
      <div class="detail-item">
        <span class="label">Desvio 2º Trimestre</span>
        <span class="value">{{ formatarMoeda(dados.desvioT2) }}</span>
      </div>
      <div class="detail-item">
        <span class="label">Desvio 3º Trimestre</span>
        <span class="value">{{ formatarMoeda(dados.desvioT3) }}</span>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const dados = ref<any>(null);
const loading = ref(true);
const error = ref<string | null>(null);

async function carregarDados() {
  const cnpj = route.params.cnpj as string;

  if (!cnpj) {
    error.value = 'CNPJ não informado na URL';
    loading.value = false;
    return;
  }

  try {
    const response = await axios.get(`http://localhost:8000/api/operadoras/${cnpj}`);
    dados.value = response.data;
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Erro ao carregar detalhes da operadora';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

// Formata valores numéricos para moeda brasileira (R$)
function formatarMoeda(valor: number | string | null): string {
  if (valor == null) return '—';
  const num = typeof valor === 'string' ? parseFloat(valor) : valor;
  if (isNaN(num)) return '—';
  return num.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

onMounted(() => {
  carregarDados();
});
</script>