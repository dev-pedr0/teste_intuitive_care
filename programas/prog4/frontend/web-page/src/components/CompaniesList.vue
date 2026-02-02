<template>
  <div class="operadoras">
    <div class="filtros">
      <div>
        <label>Busca: </label>
        <input
          v-model="busca"
          placeholder="Buscar por CNPJ ou razão social"
          @input="aplicarFiltros"
        />
      </div>
      

      <div>
        <label>Status: </label>
        <select v-model="statusFiltro" @change="aplicarFiltros">
          <option value="">Todos</option>
          <option value="Ativo">Ativo</option>
          <option value="Cancelado">Cancelado</option>
        </select>
      </div>
    </div>

    <ul v-if="operadoras.length">
      <li
        v-for="op in operadoras"
        :key="op.cnpj"
        class="operadora-item"
      >
        <div class="info">
          <strong>{{ op.razao_social }}</strong>
          <span
            class="status"
            :class="op.status_cadastro.toLowerCase()"
          >
            {{ op.status_cadastro }} - CNPJ: {{ op.cnpj }}
          </span>
        </div>

        <div class="acoes">
          <button @click="irParaDetalhes(op.cnpj)">
            Detalhes
          </button>
          <button @click="irParaDespesas(op.cnpj)">
            Despesas
          </button>
        </div>
      </li>
    </ul>

    <p v-else>Carregando operadoras...</p>

    <!-- Paginação -->
    <div class="paginacao">
      <button
        :disabled="page === 1"
        @click="paginaAnterior"
      >
        Anterior
      </button>

      <span>Página {{ page }} de {{ totalPaginas }}</span>

      <button
        :disabled="page === totalPaginas"
        @click="proximaPagina"
      >
        Próxima
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { ref, onMounted, computed } from "vue";
import axios from "axios";

// Tipagem de dados das operadoras
interface Operadora {
  cnpj: string;
  razao_social: string;
  status_cadastro: string;
}

const router = useRouter();
const operadoras = ref<Operadora[]>([]);
const page = ref(1);
const limit = ref(10);
const total = ref(0);

// Constantes de Filro
const statusFiltro = ref<string | null>(null);
const busca = ref("");

// Contagem do total de páginas
const totalPaginas = computed(() =>
  Math.ceil(total.value / limit.value)
);

// Busca dados na API
async function carregarOperadoras() {
  const params: any = {
    page: page.value,
    limit: limit.value
  };

  if (statusFiltro.value) {
    params.status = statusFiltro.value;
  }

  if (busca.value) {
    params.search = busca.value;
  }

  const response = await axios.get(
    "http://localhost:8000/api/operadoras",
    { params }
  );

  operadoras.value = response.data.data;
  total.value = response.data.total;
}

// Reset para filtragem
function aplicarFiltros() {
  page.value = 1;
  carregarOperadoras();
}


// Mudança de páginas
function paginaAnterior() {
  if (page.value > 1) {
    page.value--;
    carregarOperadoras();
  }
}

function proximaPagina() {
  if (page.value < totalPaginas.value) {
    page.value++;
    carregarOperadoras();
  }
}

// Função dos botões
function irParaDetalhes(id: string) {
  router.push(`/detalhes/${id}`);
}

function irParaDespesas(id: string) {
  router.push(`/despesas/${id}`);
}

// Ao montar a página carregaas operadoras
onMounted(() => {
  carregarOperadoras();
});
</script>