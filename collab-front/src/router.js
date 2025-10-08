import { createRouter, createWebHistory } from 'vue-router';
import HomeView from './views/HomeView.vue';
import DomainView from './views/DomainView.vue';
import PathsView from './views/PathsView.vue';
import DnsView from './views/DnsView.vue';

const routes = [
  { path: '/', component: HomeView },
  { path: '/domain/:id', component: DomainView },
  { path: '/paths/:id', component: PathsView },
  { path: '/dns/:id', component: DnsView }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;