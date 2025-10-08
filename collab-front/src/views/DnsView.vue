<template>
  <div>
    <div class="header-actions">
      <h2>DNS Records Editor ({{ domain.name }})</h2>
    </div>
    <DnsEditor :records="records" @update="updateRecord" @remove="deleteRecord" @add="createRecord" />
    
    <ConfirmationDialog
      :visible="showConfirmation"
      title="Warning: Root Domain A Record"
      message="Setting an A record for the root domain (@) will override the fallback response and break HTTP functionality for this domain. Do you want to continue?"
      confirm-text="Continue"
      cancel-text="Cancel"
      @confirm="confirmUpdate"
      @cancel="cancelUpdate"
      @close="closeConfirmation"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useDomainStore } from '../stores/domainStore';
import DnsEditor from '@/components/DnsEditor.vue';
import ConfirmationDialog from '@/components/ConfirmationDialog.vue';
import { showSuccess, showError, showWarning, showInfo } from '../stores/notifications';

const store = useDomainStore();
const router = useRouter();
const domain = store.getDomain(parseInt(router.currentRoute.value.params.id));


const records = ref([]);
const showConfirmation = ref(false);
const pendingRecord = ref(null);

const goBack = () => {
  router.go(-1);
};

const fetchRecords = async () => {
  try {
    if (!domain) {
      showError({
        title: 'Domain not found'
      });
      return;
    }
    const response = await fetch('/api/getDnsRecords', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessKey: domain.accessKey })
    });
    if (!response.ok) {
      showError({
        title: 'Fetch error /api/getDnsRecords'
      });
      return;
    }
    const data = await response.json();
    records.value = data.map(record => ({
      id: record.id,
      name: record.name,
      type: record.type,
      value: record.value,
      ttl: record.ttl || 300,
      responsetype: record.responsetype || 'static',
      value1: record.value1,
      value2: record.value2
    }));
  } catch (error) {
    showError({
      title: 'Fetch DNS records error'
    });
  }
};

const updateRecord = async (updatedRecord) => {
  if (updatedRecord.name === '@' && updatedRecord.type === 'A') {
    pendingRecord.value = updatedRecord;
    showConfirmation.value = true;
    return;
  }
  await performUpdate(updatedRecord);
};

const confirmUpdate = async () => {
  if (pendingRecord.value) {
    await performUpdate(pendingRecord.value);
  }
};

const cancelUpdate = () => {
  pendingRecord.value = null;
};

const closeConfirmation = () => {
  showConfirmation.value = false;
  pendingRecord.value = null;
};

const performUpdate = async (updatedRecord) => {
  try {
    const response = await fetch('/api/updateDnsRecord', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessKey: domain.accessKey, record: updatedRecord })
    });
    if (!response.ok) {
      showError({
        title: 'Fetch error /api/updateDnsRecord'
      });
      return;
    } else {
      showSuccess({
        title: 'DNS record updated',
        message: 'DNS record updated successfully.'
      });
    }
    fetchRecords();
  } catch (error) {
    showError({
      title: 'Update DNS record error'
    });
  }
};

const createRecord = async () => {
  try {
    const response = await fetch('/api/createDnsRecord', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessKey: domain.accessKey })
    });
    if (!response.ok) {
      showError({
        title: 'Fetch error /api/createDnsRecord'
      });
      return;
    } else {
      showSuccess({
        title: 'DNS record created',
        message: 'DNS record created successfully.'
      });
    }
    fetchRecords();
  } catch (error) {
    showError({
      title: 'Create DNS record error'
    });
  }
};

const deleteRecord = async (id) => {
  try {
    const response = await fetch('/api/deleteDnsRecord', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessKey: domain.accessKey, id })
    });
    if (!response.ok) {
      showError({
        title: 'Fetch error /api/deleteDnsRecord'
      });
      return;
    } else {
      showSuccess({
        title: 'DNS record deleted',
        message: 'DNS record deleted successfully.'
      });
    }
    fetchRecords();
  } catch (error) {
    showError({
      title: 'Remove DNS record error'
    });
  }
};

fetchRecords();
</script>