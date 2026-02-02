<template>
  <main class="expenses-page">
    <h2>Despesas da Operadora</h2>

    <table class="expenses-table">
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
          <td>{{ item.trimestre }}</td>
          <td>{{ item.valor }}</td>
        </tr>
      </tbody>
    </table>
  </main>
</template>

<script setup lang="ts">
const despesas = [
  { ano: 2022, trimestre: "1º", valor: "R$ 820.000,00" },
  { ano: 2022, trimestre: "2º", valor: "R$ 910.000,00" },
  { ano: 2022, trimestre: "3º", valor: "R$ 1.050.000,00" },
  { ano: 2023, trimestre: "1º", valor: "R$ 1.120.000,00" }
];
</script>