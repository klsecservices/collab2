<template>
  <div>
    <div class="header-actions">
      <h2>HTTP Response Editor ({{ domain.name }})</h2>
    </div>
    <PathEditor :paths="paths" @update="updatePath" @remove="deletePath" @add="createPath" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useDomainStore } from '../stores/domainStore';
import PathEditor from '@/components/PathEditor.vue';
import { showSuccess, showError, showWarning, showInfo } from '../stores/notifications';

const store = useDomainStore();
const router = useRouter();
const domain = store.getDomain(parseInt(router.currentRoute.value.params.id));

const paths = ref([]);

const goBack = () => {
  router.go(-1);
};

const fetchPaths = async () => {
  try {
    if (!domain) {
      showError({
        title: 'Domain not found'
      });
      return;
    }
    const response = await fetch('/api/getPatterns', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessKey: domain.accessKey })
    });
    if (!response.ok) {
      showError({
        title: 'Fetch error /api/getPatterns'
      });
      return;
    }
    const data = await response.json();
    paths.value = data.map(pattern => ({
      id: pattern.id,
      pattern: pattern.pattern,
      priority: pattern.priority,
      responsecode: pattern.responsecode,
      responsebody: atob(pattern.responsebody),
      responseheaders: pattern.responseheaders,
      externalHandler: pattern.externalHandler
    }));
  } catch (error) {
    showError({
      title: 'Fetch pattern error'
    });
  }
};

const updatePath = async (updatedPath) => {
  try {
    updatedPath.responsebody = btoa(updatedPath.responsebody);
    const response = await fetch('/api/updatePattern', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessKey: domain.accessKey, response: updatedPath })
    });
    if (!response.ok) {
      showError({
        title: 'Fetch error /api/updatePattern'
      });
      return;
    } else {
      showSuccess({
        title: 'HTTP response updated',
        message: 'HTTP response updated successfully.'
      });
    }
    fetchPaths();
  } catch (error) {
    showError({
      title: 'Update pattern error'
    });
  }
};

const createPath = async () => {
  try {
    const response = await fetch('/api/createPattern', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessKey: domain.accessKey })
    });
    if (!response.ok) {
      showError({
        title: 'Fetch error /api/createPattern'
      });
      return;
    } else {
      showSuccess({
        title: 'HTTP response created',
        message: 'HTTP response created successfully.'
      });
    }
    fetchPaths();
  } catch (error) {
    showError({
      title: 'Create pattern error'
    });
  }
};

const deletePath = async (id) => {
  try {
    const response = await fetch('/api/deletePattern', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessKey: domain.accessKey, id })
    });
    if (!response.ok) {
      showError({
        title: 'Fetch error /api/deletePattern'
      });
      return;
    } else {
      showSuccess({
        title: 'HTTP response deleted',
        message: 'HTTP response deleted successfully.'
      });
    }
    fetchPaths();
  } catch (error) {
    showError({
      title: 'Remove pattern error'
    });
  }
};

fetchPaths();
</script>