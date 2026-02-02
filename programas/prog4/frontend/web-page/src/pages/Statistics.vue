<template>
  <main class="stats-page">
    <section>
      <h2>5 Operadoras com Maior Crescimento de Gastos</h2>
      <ul class="stats-list">
        <li v-for="op in crescimento" :key="op">
          {{ op }}
        </li>
      </ul>
    </section>

    <section>
      <h2>5 Estados com Maior Despesa Total</h2>
      <ul class="stats-list">
        <li v-for="estado in estados" :key="estado">
          {{ estado }}
        </li>
      </ul>
    </section>

    <section>
      <h2>Operadoras Acima da Média de Gastos</h2>
      <ul class="stats-list">
        <li v-for="op in acimaMedia" :key="op">
          {{ op }}
        </li>
      </ul>
    </section>
  </main>
</template>

<script setup lang="ts">
const crescimento = [
  "Saúde Vida",
  "Plano Bem Estar",
  "Operadora Nacional",
  "Vida Total",
  "Mais Saúde"
];

const estados = ["SP", "RJ", "MG", "RS", "PR"];

const acimaMedia = [
  "Saúde Vida",
  "Operadora Nacional"
];
</script>