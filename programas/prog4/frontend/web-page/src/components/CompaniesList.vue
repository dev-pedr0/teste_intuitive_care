<template>
  <ul>
    <li v-for="op in operadoras" :key="op.id">
      {{ op.nome }}
      <div>
        <button @click="irParaDetalhes(op.id)">Detalhes</button>
        <button @click="irParaDespesas(op.id)">Despesas</button>
      </div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

const operadoras = [
  { id: 1, nome: "Saúde Vida" },
  { id: 2, nome: "Plano Bem Estar" },
  { id: 3, nome: "Operadora Nacional" }
];

function irParaDetalhes(id: number) {
  router.push(`/detalhes/${id}`);
}

function irParaDespesas(id: number) {
  router.push(`/despesas/${id}`);
}
</script>