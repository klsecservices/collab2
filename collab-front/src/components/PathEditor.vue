<template>
  <div class="paths-container">
    <ul class="path-list">
      <li v-for="path in paths" :key="path.id" @click="selectPath(path)">
        {{ path.pattern }} (Priority: {{ path.priority }})
      </li>
      <button @click="addPath" class="add-button">Add custom response</button>
    </ul>
    <div class="path-editor" v-if="selectedPath">
      <h3>Custom response editor</h3>
      <input v-model="selectedPath.id" type="hidden" />
      <label>Pattern (regex): <input v-model="selectedPath.pattern" /></label>
      <label>Priority: <input v-model.number="selectedPath.priority" type="number" /></label>
      
      <div class="mode-switcher">
        <label class="switch">
          <input type="checkbox" v-model="isExternalMode" />
          <span class="slider round"></span>
        </label>
        <span>External handler</span>
      </div>
      
      <div v-if="!isExternalMode">
        <label>Response code: <input v-model.number="selectedPath.responsecode" type="number" /></label>
        <label>Headers:
          <div v-for="(header, index) in selectedPath.responseheaders" :key="index" class="header-row">
            <input v-model="header.key" placeholder="Key" />
            <input v-model="header.value" placeholder="Value" />
            <button @click="removeHeader(index)">Remove</button>
          </div>
          <button class="full-width-button" @click="addHeader">Add header</button>
        </label>
        
        <div v-if="!isBinaryContent && !selectedFile">
          <label>Response body: <textarea v-model="responseText" class="response-textarea"></textarea></label>
        </div>
        <div v-else class="binary-content-notice">
          <p>{{ selectedFile ? 'File selected: ' + selectedFile.name : 'Binary content' }} ({{ formatFileSize(selectedFile ? selectedFile.size : responseBuffer ? responseBuffer.byteLength : 0) }})</p>
        </div>
        
        <div class="file-upload-container">
          <label class="file-upload-label">
            Upload file as response:
            <input type="file" @change="handleFileUpload" ref="fileInput" class="file-input" />
          </label>
          <div v-if="selectedFile" class="selected-file">
            Selected file: <a href="#" @click.prevent="downloadSelectedFile">{{ selectedFile.name }}</a> ({{ formatFileSize(selectedFile.size) }})
            <button class="remove-file-button" @click="removeFile">✕</button>
          </div>
        </div>
      </div>
      
      <div v-else>
        <label>External handler: <input v-model="selectedPath.externalHandler" class="full-width-input" /></label>
      </div>
      
      <div class="button-group">
        <button class="action-button" @click="savePath">Save</button>
        <button class="action-button remove-button" @click="removePath(selectedPath.id)">Remove</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, computed } from 'vue';

const props = defineProps({ paths: Array });
const emit = defineEmits(['update', 'remove', 'add']);
const selectedPath = ref(null);
const selectedFile = ref(null);
const fileInput = ref(null);
const responseBuffer = ref(null);
const isExternalMode = ref(false);

const responseText = computed({
  get: () => {
    if (!responseBuffer.value) return '';
    
    return arrayBufferToString(responseBuffer.value);
  },
  set: (value) => {
    responseBuffer.value = stringToArrayBuffer(value);
  }
});

const isBinaryContent = computed(() => {
  if (!responseBuffer.value) return false;
  return checkIsBinaryContent(responseBuffer.value);
});

const stringToArrayBuffer = (str) => {
  if (!str) return new ArrayBuffer(0);
  
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0; i < str.length; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
};

const arrayBufferToString = (buffer) => {
  if (!buffer) return '';
  
  const bytes = new Uint8Array(buffer);
  let result = '';
  for (let i = 0; i < bytes.length; i++) {
    result += String.fromCharCode(bytes[i]);
  }
  return result;
};

const selectPath = (path) => {
  selectedPath.value = { ...path };
  selectedFile.value = null;
  if (fileInput.value) fileInput.value.value = '';
  
  isExternalMode.value = selectedPath.value.externalHandler !== undefined;
  
  if (selectedPath.value.responsebody && !isExternalMode.value) {
    responseBuffer.value = stringToArrayBuffer(selectedPath.value.responsebody);
    
    const isBinary = checkIsBinaryContent(responseBuffer.value);
    
    if (isBinary) {
      createBlobFromBinaryContent();
    }
  } else {
    responseBuffer.value = new ArrayBuffer(0);
  }
};

const checkIsBinaryContent = (buffer) => {
  if (!buffer) return false;
  
  const content = arrayBufferToString(buffer);

  if (content.length > 4096) {
    return true;
  }

  for (let i = 0; i < Math.min(content.length, 1000); i++) {
    const charCode = content.charCodeAt(i);
    if ((charCode < 32 && ![9, 10, 13].includes(charCode)) || charCode === 0 || charCode === 127) {
      return true;
    }
  }
  
  return false;
};

const createBlobFromBinaryContent = () => {
  const contentType = 'application/octet-stream';
  const fileName = 'response-data';
  
  const blob = new Blob([responseBuffer.value], { type: contentType });
  selectedFile.value = new File([blob], fileName, { type: contentType });
};

const downloadSelectedFile = () => {
  if (!selectedFile.value) return;
  
  const url = URL.createObjectURL(selectedFile.value);
  const link = document.createElement('a');
  link.href = url;
  link.download = selectedFile.value.name;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
  }
};

const removeFile = () => {
  selectedFile.value = null;
  if (fileInput.value) fileInput.value.value = '';
  
  if (isBinaryContent.value) {
    responseBuffer.value = new ArrayBuffer(0);
  }
};

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' bytes';
  else if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' kb';
  else return (bytes / 1048576).toFixed(2) + ' mb';
};

const savePath = async () => {
  if (!isExternalMode.value) {
    if (selectedFile.value) {
      try {
        const buffer = await readFileAsArrayBuffer(selectedFile.value);
        responseBuffer.value = buffer;
      } catch (error) {
        console.error('Error reading file:', error);
      }
    }
    
    selectedPath.value.responsebody = arrayBufferToString(responseBuffer.value);
    
    if ('externalHandler' in selectedPath.value) {
      delete selectedPath.value.externalHandler;
    }
  } else {
    selectedPath.value.responsebody = '';
    selectedPath.value.responseheaders = [];
    selectedPath.value.responsecode = 200;
    
    if (!selectedPath.value.externalHandler) {
      selectedPath.value.externalHandler = '';
    }
  }
  
  emit('update', selectedPath.value);
};

const readFileAsArrayBuffer = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => resolve(event.target.result);
    reader.onerror = (error) => reject(error);
    reader.readAsArrayBuffer(file);
  });
};

const removePath = (id) => {
  emit('remove', id);
  selectedPath.value = null;
  selectedFile.value = null;
  responseBuffer.value = null;
};

const addPath = () => {
  emit('add');
};

const addHeader = () => {
  if (selectedPath.value) {
    if (selectedPath.value.responseheaders.push) {
      selectedPath.value.responseheaders.push({ key: '', value: '' });
    } else {
      selectedPath.value.responseheaders = [{ key: '', value: '' }];
    }
  }
};

const removeHeader = (index) => {
  if (selectedPath.value) {
    selectedPath.value.responseheaders.splice(index, 1);
  }
};
</script>