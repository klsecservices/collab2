<template>
  <div class="home-container">
    <h2>Domains</h2>
    <div class="input-group">
      <div class="domain-input">
        <input v-model="newDomain" placeholder="Subdomain (leave blank for random)" /><span>.{{ baseDomain }}</span>
      </div>
      <button @click="createDomain">Create domain</button>
    </div>
    <div class="input-group">
      <input v-model="accessKeyInput" placeholder="Access Key" />
      <button @click="addDomain">Import domain</button>
    </div>
    
    <ul class="domain-list">
      <li v-for="(domain, index) in store.domains">
        <router-link :to="`/domain/${index}`">{{ domain.name }} (HTTP: {{ domain.requestCountHttp }}, DNS: {{ domain.requestCountDns }}, SMTP: {{ domain.requestCountSmtp }})</router-link>
        <button @click="deleteDomain(index)" class="domain-button"><span class="material-icons">delete</span></button>
        <button @click="copyDomain(index)" class="domain-button" :title="domainTooltip">
          <span class="material-icons">content_copy</span>
          <span v-if="showDomainTooltip === domain.index" class="tooltip">Copied!</span>
        </button>
        <button @click="copyAccessKey(index)" class="domain-button" :title="accessKeyTooltip">
          <span class="material-icons">share</span>
          <span v-if="showAccessKeyTooltip === index" class="tooltip">Copied!</span>
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useDomainStore } from '../stores/domainStore';
import { showSuccess, showError, showWarning, showInfo } from '../stores/notifications';

const store = useDomainStore();
const newDomain = ref('');
const accessKeyInput = ref('');
const baseDomain = ref(__BASE_DOMAIN__);

// Tooltip states
const showAccessKeyTooltip = ref(null);
const showDomainTooltip = ref(null);
const accessKeyTooltip = ref('Copy access key');
const domainTooltip = ref('Copy domain');

const fetchDomains = async () => {
  try {
    let to_remove = [];
    for (let i = 0; i < store.domains.length; i++) {
      const domain = store.domains[i];
      const response = await fetch('/api/getDomain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accessKey: domain.accessKey })
      });
      if (response.ok) {
        const data = await response.json();
        domain.name = data.host;
        domain.requestCountHttp = data.requestCountHttp;
        domain.requestCountDns = data.requestCountDns;
        domain.requestCountSmtp = data.requestCountSmtp;
      }
      if (response.status === 403) {
        to_remove.push(i);
      }
    }
    for (let i = to_remove.length - 1; i >= 0; i--) {
      store.removeDomain(to_remove[i]);
    }
  } catch (error) {
    console.error('Domain fetch error:', error);
  }
};

const createDomain = async () => {
  try {
    const response = await fetch('/api/createDomain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ host: newDomain.value })
    });
    if (!response.ok) {
      throw new Error('Fetch error /api/createDomain');
    }
    const data = await response.json();
    store.addDomain({
      name: data.host,
      accessKey: data.accessKey
    });
    newDomain.value = '';
    showSuccess({
      title: 'Domain created',
      message: `Domain ${data.host} created successfully`
    });
    fetchDomains();
  } catch (error) {
    console.error('Domain create error:', error);
    showError({
      title: 'Domain creation error',
      message: 'Failed to create domain. Please check the entered data.'
    });
  }
};

const addDomain = async () => {
  if (!accessKeyInput.value.trim()) {
    showWarning('Enter Access Key');
    return;
  }
  
  try {
    const response = await fetch('/api/getDomain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessKey: accessKeyInput.value })
    });
    if (!response.ok) {
      showError({
        title: 'Domain addition error',
        message: 'Failed to add domain. Please check the Access Key.'
      });
      return;
    }
    const domain = await response.json();
    store.addDomain({
      name: domain.host,
      accessKey: accessKeyInput.value
    });
    accessKeyInput.value = '';
    showSuccess({
      title: 'Domain added',
      message: `Domain ${domain.host} added successfully`
    });
    fetchDomains();
  } catch (error) {
    console.error('Domain add error:', error);
    showError({
      title: 'Domain addition error',
      message: 'Failed to add domain. Please check the Access Key.'
    });
  }
};

const copyAccessKey = async (index) => {
  try {
    const domain = store.getDomain(index);
    if (domain) {
      await navigator.clipboard.writeText(domain.accessKey);
      showAccessKeyTooltip.value = index;
      showSuccess('Access Key copied to clipboard');
      setTimeout(() => {
        showAccessKeyTooltip.value = null;
      }, 2000);
    } else {
      showError('Domain not found');
    }
  } catch (error) {
    console.error('Access Key copy error:', error);
    showError('Access Key copy error');
  }
};

const copyDomain = async (index) => {
  try {
    const domain = store.getDomain(index);
    if (domain) {
      await navigator.clipboard.writeText(domain.name);
      showDomainTooltip.value = index;
      showSuccess('Domain copied to clipboard');
      setTimeout(() => {
        showDomainTooltip.value = null;
      }, 2000);
    } else {
      showError('Domain not found');
    }
  } catch (error) {
    console.error('Domain copy error:', error);
    showError('Domain copy error');
  }
}; 

const deleteDomain = (index) => {
  const domain = store.getDomain(index);
  if (domain) {
    store.removeDomain(index);
    showInfo({
      title: 'Domain deleted',
      message: `Domain ${domain.name} removed from list`
    });
    fetchDomains();
  }
};

onMounted(fetchDomains);
</script>

<style scoped>
</style>