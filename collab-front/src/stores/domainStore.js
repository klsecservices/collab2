import { defineStore } from 'pinia';

export const useDomainStore = defineStore('domain', {
  state: () => ({
    domains: JSON.parse(localStorage.getItem('domains')) || []
  }),
  actions: {
    addDomain(domain) {
      this.domains.push(domain);
      localStorage.setItem('domains', JSON.stringify(this.domains));
    },
    getDomain(index) {
      return this.domains[index];
    },
    removeDomain(index) {
      this.domains.splice(index, 1);
      localStorage.setItem('domains', JSON.stringify(this.domains));
    },
    getDomainIndex(domain) {
      return this.domains.findIndex(d => d.name === domain.name);
    }
  }
});