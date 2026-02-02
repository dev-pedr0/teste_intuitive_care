import { createRouter, createWebHistory } from "vue-router";
import Companies from "../pages/Companies.vue";
import Statistics from "../pages/Statistics.vue";
import Details from "@/pages/Details.vue";
import Costs from "@/pages/Costs.vue";

const routes = [
  { path: "/", component: Companies },
  { path: "/estatisticas", component: Statistics },
  { path: "/detalhes/:id", component: Details },
  { path: "/despesas/:id", component: Costs },
];

export default createRouter({
  history: createWebHistory(),
  routes
});