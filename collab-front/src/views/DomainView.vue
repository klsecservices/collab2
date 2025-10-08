<template>
  <div>
    <h2>Requests to {{ domain.name }}
      <button @click="copyAccessKey()" :title="accessKeyTooltip">
        <span class="material-icons">share</span>
        <span v-if="showAccessKeyTooltip" class="tooltip">Copied!</span>
      </button>
      <button @click="copyDomain()" :title="domainTooltip">
        <span class="material-icons">content_copy</span>
        <span v-if="showDomainTooltip" class="tooltip">Copied!</span>
      </button>
    </h2>
    <button @click="editPaths">Edit custom HTTP responses</button>
    <button @click="editDnsRecords">Edit DNS records</button>
    <button @click="manualFetch">Refresh</button>
    
    <!-- Toggle buttons for HTTP/DNS/SMTP -->
    <div class="toggle-section">
      <button 
        @click="toggleHttp" 
        :class="{ active: showHttp }"
        class="toggle-btn"
      >
        HTTP {{ showHttp ? '✓' : '✗' }}
      </button>
      <button 
        @click="toggleDns" 
        :class="{ active: showDns }"
        class="toggle-btn"
      >
        DNS {{ showDns ? '✓' : '✗' }}
      </button>
      <button 
        @click="toggleSmtp" 
        :class="{ active: showSmtp }"
        class="toggle-btn"
      >
        SMTP {{ showSmtp ? '✓' : '✗' }}
      </button>
    </div>
    
    <div class="filter-section">
      <label for="pattern-select">Filter by pattern:</label>
      <select id="pattern-select" v-model="selectedPatternId" @change="filterByPattern">
        <option :value="null">All requests</option>
        <option v-for="pattern in patterns" :key="pattern.id" :value="pattern.id">
          {{ pattern.pattern }} (Priority: {{ pattern.priority }})
        </option>
      </select>
    </div>
 
   <div class="requests-container">
      <ul class="request-list">
        <li v-for="request in filteredRequests" :key="request.id" @click="selectRequest(request)">
          <span class="method" :data-method="request.displayMethod" :class="{ 'dns-method': request.type === 'dns', 'smtp-method': request.type === 'smtp' }">{{ request.displayMethod }}</span>
          <span class="path">{{ request.displayPath }}</span>
          <span class="datetime">{{ request.datetime }}</span>
          <span class="ip">{{ request.ip }}</span>
        </li>
      </ul>
      <div class="request-details" v-if="selectedRequest">
        <h3>Request details</h3>
        <template v-if="selectedRequest.type === 'http'">
          <p><strong>Method:</strong> {{ selectedRequest.method }}</p>
          <p><strong>Path:</strong> {{ selectedRequest.path }}</p>
          <p><strong>Timestamp:</strong> {{ selectedRequest.datetime }}</p>
          <p><strong>IP:</strong> {{ selectedRequest.ip }}</p>
          <h4>Raw request</h4>
          <pre class="message-content">{{ selectedRequest.raw }}</pre>
        </template>
        <template v-else-if="selectedRequest.type === 'dns'">
          <p><strong>Question Name:</strong> {{ selectedRequest.qname }}</p>
          <p><strong>Question Type:</strong> {{ selectedRequest.qtype }}</p>
          <p><strong>Timestamp:</strong> {{ selectedRequest.datetime }}</p>
          <p><strong>IP:</strong> {{ selectedRequest.ip }}</p>
        </template>
        <template v-else-if="selectedRequest.type === 'smtp'">
          <p><strong>From:</strong> {{ selectedRequest.from }}</p>
          <p><strong>To:</strong> {{ selectedRequest.to }}</p>
          <p><strong>Timestamp:</strong> {{ selectedRequest.datetime }}</p>
          <p><strong>IP:</strong> {{ selectedRequest.ip }}</p>
          <h4>Raw message</h4>
          <div class="message-container">
            <div class="message-header">
              <div class="message-actions">
                <button @click="downloadRawMessage" :title="downloadTooltip" class="action-btn">
                  <span class="material-icons">download</span>
                </button>
                <button @click="copyMessageContent()" :title="messageCopyTooltip" class="action-btn">
                  <span class="material-icons">content_copy</span>
                  <span v-if="showMessageCopyTooltip" class="tooltip">Copied!</span>
                </button>
              </div>
            </div>
            <pre class="message-content">{{ selectedRequest.data }}</pre>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useDomainStore } from '../stores/domainStore';
import { showSuccess, showError, showWarning, showInfo } from '../stores/notifications';

const store = useDomainStore();
const router = useRouter();
const selectedRequest = ref(null);
const requests = ref([]);
const dnsRequests = ref([]);
const smtpRequests = ref([]);
const patterns = ref([]);
const selectedPatternId = ref(null);
const domain = store.getDomain(parseInt(router.currentRoute.value.params.id));

const lastUpdate = ref(null);
const intervalId = ref(null);

// Tooltip states
const showAccessKeyTooltip = ref(false);
const showDomainTooltip = ref(false);
const showMessageCopyTooltip = ref(false);
const accessKeyTooltip = ref('Copy access key');
const domainTooltip = ref('Copy domain');
const messageCopyTooltip = ref('Copy message content');
const downloadTooltip = ref('Download message');

const showHttp = ref(true);
const showDns = ref(true);
const showSmtp = ref(true);

const sortedRequests = computed(() => {
  const allRequests = [
    ...requests.value.map(req => ({
      ...req,
      type: 'http',
      displayMethod: req.method,
      displayPath: req.path,
      id: `http_${req.timestamp}_${req.method}_${req.path}_${req.ip}`
    })),
    ...dnsRequests.value.map(req => ({
      ...req,
      type: 'dns',
      displayMethod: 'DNS',
      displayPath: req.qname + ' (' + req.qtype + ')',
      id: `dns_${req.timestamp}_${req.qname}_${req.qtype}_${req.ip}`
    })),
    ...smtpRequests.value.map(req => ({
      ...req,
      type: 'smtp',
      displayMethod: 'SMTP',
      displayPath: req.from + ' -> ' + req.to,
      id: `smtp_${req.timestamp}_${req.from}_${req.to}_${req.ip}`
    }))
  ];
  
  // Удаляем дубликаты по id
  const uniqueRequests = allRequests.filter((request, index, self) => 
    index === self.findIndex(r => r.id === request.id)
  );
  
  return uniqueRequests.sort((a, b) => {
    const dateA = new Date(a.datetime).getTime();
    const dateB = new Date(b.datetime).getTime();
    return dateB - dateA;
  });
});

const filteredRequests = computed(() => {
  return sortedRequests.value.filter(request => {
    if (showHttp.value && showDns.value) {
      return true;
    }
    if (showHttp.value && request.type === 'http') {
      return true;
    }
    if (showDns.value && request.type === 'dns') {
      return true;
    }
    if (showSmtp.value && request.type === 'smtp') {
      return true;
    }
    return false;
  });
});

const fetchPatterns = async () => {
  try {
    if (!domain) {
      showError({
        title: 'Domain not found',
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
        title: 'Fetch error /api/getPatterns',
      });
      return;
    }
    const data = await response.json();
    patterns.value = data.map(pattern => ({
      id: pattern.id,
      pattern: pattern.pattern,
      priority: pattern.priority
    }));
  } catch (error) {
    showError({
      title: 'Fetch patterns error'
    });
  }
};

const fetchRequests = async () => {
  try {
    if (!domain) {
      showError({
        title: 'Domain not found'
      });
      return;
    }
    const requestBody = { accessKey: domain.accessKey };
    
    if (selectedPatternId.value !== null) {
      requestBody.patternId = selectedPatternId.value;
    }
    
    if (lastUpdate.value !== null) {
      requestBody.after = lastUpdate.value;
    }
    
    // Fetch HTTP requests
    const httpResponse = await fetch('/api/getRequests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
    if (!httpResponse.ok) {
      showError({
        title: 'Fetch error'
      });
      return;
    }
    const httpData = await httpResponse.json();
    requests.value = [
      ...requests.value,
      ...httpData.map(request => ({
        method: request.method,
        path: request.path,
        raw: atob(request.rawrequest),
        datetime: new Date(request.timestamp * 1000).toLocaleString(),
        ip: request.userip,
        timestamp: request.timestamp,
      }))
    ];

    // Fetch DNS requests
    const dnsResponse = await fetch('/api/getDNSRequests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
    if (!dnsResponse.ok) {
      showError({
        title: 'Fetch error'
      });
      return;
    }
    const dnsData = await dnsResponse.json();
    dnsRequests.value = [
      ...dnsRequests.value,
      ...dnsData.map(request => ({
        qname: request.qname,
        qtype: request.qtype,
        datetime: new Date(request.timestamp * 1000).toLocaleString(),
        ip: request.userip,
        timestamp: request.timestamp,
      }))
    ];

    // Fetch SMTP requests
    const smtpResponse = await fetch('/api/getSMTPRequests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
    if (!smtpResponse.ok) {
      showError({
        title: 'Fetch error'
      });
      return;
    }
    const smtpData = await smtpResponse.json();
    smtpRequests.value = [
      ...smtpRequests.value,
      ...smtpData.map(request => ({
        from: request.from,
        to: request.to,
        data: atob(request.data),
        datetime: new Date(request.timestamp * 1000).toLocaleString(),
        ip: request.userip,
        timestamp: request.timestamp,
      }))
    ];

    lastUpdate.value = Math.floor(Date.now() / 1000);
  } catch (error) {
    showError({
      title: 'Fetch error'
    });
  }
};

const filterByPattern = () => {
  requests.value = [];
  dnsRequests.value = [];
  smtpRequests.value = [];
  lastUpdate.value = null;
  fetchRequests();
};

const manualFetch = () => {
  fetchRequests();
};

onMounted(() => {
  fetchPatterns();
  fetchRequests();
  intervalId.value = setInterval(fetchRequests, 5000);
});

onUnmounted(() => {
  if (intervalId.value) {
    clearInterval(intervalId.value);
  }
});

const selectRequest = (request) => {
  selectedRequest.value = request;
};

const copyAccessKey = async () => {
  try {
    if (domain) {
      await navigator.clipboard.writeText(domain.accessKey);
      showSuccess({
        title: 'Access Key copied',
        message: 'Access Key copied to clipboard.'
      });
    } else {
      showError({
        title: 'Domain not found'
      });
    }
  } catch (error) {
    showError({
      title: 'Access Key copy error'
    });
  }
};

const copyDomain = async () => {
  try {
    if (domain) {
      await navigator.clipboard.writeText(domain.name);
      showSuccess({
        title: 'Domain copied',
        message: 'Domain copied to clipboard.'
      });
    } else {
      showError({
        title: 'Domain not found'
      });
    }
  } catch (error) {
    showError({
      title: 'Domain copy error'
    });
  }
};

const downloadRawMessage = () => {
  const blob = new Blob([selectedRequest.value.data], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'message.eml';
  a.click();
  URL.revokeObjectURL(url);
};

const copyMessageContent = async () => {
  try {
    if (selectedRequest.value && selectedRequest.value.data) {
      await navigator.clipboard.writeText(selectedRequest.value.data);
      showMessageCopyTooltip.value = true;
      setTimeout(() => {
        showMessageCopyTooltip.value = false;
      }, 2000);
      showSuccess({
        title: 'Message content copied',
        message: 'Message content copied to clipboard.'
      });
    } else {
      showError({
        title: 'No message content',
        message: 'No message content to copy.'
      });
    }
  } catch (error) {
    showError({
      title: 'Copy error',
      message: 'Failed to copy message content to clipboard.'
    });
  }
};

const editPaths = () => {
  router.push(`/paths/${router.currentRoute.value.params.id}`);
};

const toggleHttp = () => {
  showHttp.value = !showHttp.value;
};

const toggleDns = () => {
  showDns.value = !showDns.value;
};

const toggleSmtp = () => {
  showSmtp.value = !showSmtp.value;
};

const editDnsRecords = () => {
  router.push(`/dns/${router.currentRoute.value.params.id}`);
};
</script>

<style scoped>
button {
  position: relative;
  margin-right: 10px;
}

button:last-of-type {
  margin-right: 0;
}
</style>