<template>
  <div class="dns-container">
    <ul class="dns-list">
      <li v-for="record in records" :key="record.id" @click="selectRecord(record)">
        {{ record.name }} ({{ record.type }}) - {{ record.responsetype === 'rebind' ? record.value1 + ' / ' + record.value2 : record.value }}
      </li>
      <button @click="addRecord" class="add-button">Add DNS Record</button>
    </ul>
    <div class="dns-editor" v-if="selectedRecord">
      <h3>DNS Record Editor</h3>
      <input v-model="selectedRecord.id" type="hidden" />
      
      <label>Response type:</label>
      <select v-model="selectedRecord.responsetype">
        <option value="static">Static record</option>
        <option value="rebind">DNS rebinding</option>
      </select>

      <!-- Static record form -->
      <div v-if="selectedRecord.responsetype === 'static'">
        <label>Name: 
          <div class="domain-input">
            <input v-model="selectedRecord.name" /><span>.{{ domain.name }}</span>
          </div>
        </label>
        
        <label>Type: 
          <select v-model="selectedRecord.type">
            <option value="A">A (IPv4)</option>
            <option value="AAAA">AAAA (IPv6)</option>
            <option value="CNAME">CNAME</option>
            <option value="MX">MX</option>
            <option value="TXT">TXT</option>
            <option value="NS">NS</option>
            <option value="PTR">PTR</option>
          </select>
        </label>
        
        <label>Value: <input v-model="selectedRecord.value" /></label>
        
        <label>TTL: <input v-model.number="selectedRecord.ttl" type="number" min="0" /></label>
      </div>

      <!-- DNS rebinding form -->
      <div v-if="selectedRecord.responsetype === 'rebind'">
        <label>Name: 
          <div class="domain-input">
            <input v-model="selectedRecord.name" /><span>.{{ domain.name }}</span>
          </div>
        </label>
        
        <label>Type: 
          <select v-model="selectedRecord.type">
            <option value="A">A (IPv4)</option>
            <option value="AAAA">AAAA (IPv6)</option>
            <option value="CNAME">CNAME</option>
            <option value="MX">MX</option>
            <option value="TXT">TXT</option>
            <option value="NS">NS</option>
            <option value="PTR">PTR</option>
          </select>
        </label>
        
        <label>Value 1: <input v-model="selectedRecord.value1" /></label>
        
        <label>Value 2: <input v-model="selectedRecord.value2" /></label>
      </div>
      
      <div class="button-group">
        <button class="action-button" @click="saveRecord">Save</button>
        <button class="action-button remove-button" @click="removeRecord(selectedRecord.id)">Remove</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import { useDomainStore } from '../stores/domainStore';
import { useRouter } from 'vue-router';

const store = useDomainStore();
const router = useRouter();
const domain = store.getDomain(parseInt(router.currentRoute.value.params.id));

const props = defineProps({ records: Array });
const emit = defineEmits(['update', 'remove', 'add']);
const selectedRecord = ref(null);

const selectRecord = (record) => {
  selectedRecord.value = { ...record };
};

const saveRecord = async () => {
  emit('update', selectedRecord.value);
};

const removeRecord = (id) => {
  emit('remove', id);
  selectedRecord.value = null;
};

const addRecord = () => {
  emit('add');
};
</script>