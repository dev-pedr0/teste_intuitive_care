<template>
  <main class="details-page">
    <h2>Detalhes da Operadora</h2>

    <div class="details-grid">
      <p><strong>Status do Cadastro:</strong> {{ dados.status }}</p>
      <p><strong>Razão Social:</strong> {{ dados.razaoSocial }}</p>
      <p><strong>CNPJ:</strong> {{ dados.cnpj }}</p>
      <p><strong>Registro ANS:</strong> {{ dados.registroAns }}</p>
      <p><strong>UF:</strong> {{ dados.uf }}</p>
      <p><strong>Modalidade:</strong> {{ dados.modalidade }}</p>

      <p><strong>Total de Despesas:</strong> {{ dados.totalDespesas }}</p>

      <p><strong>Média 1º Trimestre:</strong> {{ dados.mediaT1 }}</p>
      <p><strong>Média 2º Trimestre:</strong> {{ dados.mediaT2 }}</p>
      <p><strong>Média 3º Trimestre:</strong> {{ dados.mediaT3 }}</p>

      <p><strong>Desvio 1º Trimestre:</strong> {{ dados.desvioT1 }}</p>
      <p><strong>Desvio 2º Trimestre:</strong> {{ dados.desvioT2 }}</p>
      <p><strong>Desvio 3º Trimestre:</strong> {{ dados.desvioT3 }}</p>
    </div>
  </main>
</template>

<script setup lang="ts">
const dados = {
  status: "Ativo",
  razaoSocial: "Operadora Saúde Vida S.A.",
  cnpj: "12.345.678/0001-90",
  registroAns: "123456",
  uf: "SP",
  modalidade: "Medicina de Grupo",
  totalDespesas: "R$ 12.500.000,00",
  mediaT1: "R$ 950.000,00",
  mediaT2: "R$ 1.050.000,00",
  mediaT3: "R$ 1.200.000,00",
  desvioT1: "R$ 120.000,00",
  desvioT2: "R$ 150.000,00",
  desvioT3: "R$ 180.000,00"
};
</script>