<!-- ServerDrive.vue -->
<script setup>
import { onMounted, ref, onUnmounted } from 'vue';

const serverData = ref({});
const isLoading = ref(false);
const error = ref(null);
const uploadingFiles = ref(new Set());
const expandedFolders = ref(new Set());

// Mock data for demonstration - replace with your actual API call
const mockServerData = {
  'Cash In Bank': ['Cash In Bank.csv', 'Position Table 1.xlsx'],
  'Gold Folder': ['Gold1.csv'],
  'Trading Records': ['trades_2024.xlsx', 'portfolio.csv', 'analysis.csv'],
  'Reports': ['monthly_report.pdf', 'quarterly.xlsx']
};




const fetchServerData = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('User not authenticated');
    const res = await fetch(`https://production2.swancapital.in/serverDrive`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    
    serverData.value = data || mockServerData;
  } catch (err) {
    console.error('Error fetching server data:', err);
    error.value = 'Failed to fetch server data. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

const toggleFolder = (folderName) => {
  if (expandedFolders.value.has(folderName)) {
    expandedFolders.value.delete(folderName);
  } else {
    expandedFolders.value.add(folderName);
  }
};

const handleFileUpload = async (folderName, event) => {
  const files = Array.from(event.target.files);
  if (files.length === 0) return;

  uploadingFiles.value.add(folderName);
  
  try {
        for (const file of files) {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("folder_name", folderName);

            const token = localStorage.getItem('access_token');
            const res = await fetch(`https://production2.swancapital.in/UploadserveDrive`, {
                method: 'POST',
                headers: {
                'Authorization': `Bearer ${token}`
                // DO NOT set Content-Type manually for FormData
                },
                body: formData
            });

            if (!res.ok) {
                const errorText = await res.text();
                throw new Error(errorText);
            }

            // Add file to UI only after successful upload
            if (!serverData.value[folderName]) {
                serverData.value[folderName] = [];
            }
            serverData.value[folderName].push(file.name);
        }
  } catch (err) {
    console.error('Upload error:', err);
    error.value = 'Failed to upload file(s). Please try again.';
  } finally {
    uploadingFiles.value.delete(folderName);
    // Reset file input
    event.target.value = '';
  }
};

const downloadFile = async (folderName, fileName) => {
  try {
    const token = localStorage.getItem('access_token');
    const url = new URL('https://production2.swancapital.in/DownloadServerDriveFile');
    url.searchParams.append('folder_name', folderName);
    url.searchParams.append('file_name', fileName);

    const response = await fetch(url, {
    headers: {
        'Authorization': `Bearer ${token}`
    }
    });

    if (!response.ok) {
    throw new Error('Failed to download file');
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = fileName;
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
    
    alert(`Downloading ${fileName} from ${folderName}`);
  } catch (err) {
    console.error('Download error:', err);
    error.value = 'Failed to download file. Please try again.';
  }
};

const deleteFile = async (folderName, fileName) => {
  if (!confirm(`Are you sure you want to delete ${fileName}?`)) return;
  
  try {
    const token = localStorage.getItem('access_token');
    const url = new URL('https://production2.swancapital.in/deleteFile');
    url.searchParams.append('folder_name', folderName);
    url.searchParams.append('file_name', fileName);

    const response = await fetch(url, {
    method: 'DELETE',
    headers: {
        'Authorization': `Bearer ${token}`
    }
    });

    if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText);
    }

    // Remove file from UI
    const folderFiles = serverData.value[folderName];
    const fileIndex = folderFiles.indexOf(fileName);
    if (fileIndex > -1) {
        folderFiles.splice(fileIndex, 1);
    }

  } catch (err) {
    console.error('Delete error:', err);
    error.value = 'Failed to delete file. Please try again.';
  }
};

const getFileIcon = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase();
  switch (extension) {
    case 'csv': return '📊';
    case 'xlsx': case 'xls': return '📈';
    case 'pdf': return '📄';
    case 'txt': return '📝';
    default: return '📁';
  }
};

const getFileSize = () => {
  // Mock file size - replace with actual file size from API
  return `${Math.floor(Math.random() * 1000) + 10}KB`;
};

onMounted(() => {
  document.title = 'Server Drive';
  fetchServerData();
});

onUnmounted(() => {
  document.title = 'Vite App';
});
</script>

<template>
  <div class="server-drive-container">
    <header class="drive-header">
      <div class="header-content">
        <h1 class="drive-title">
          <span class="title-icon">🗄️</span>
          Server Drive
        </h1>
        <button @click="fetchServerData" class="refresh-button" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          <span v-else class="refresh-icon">🔄</span>
          <span>{{ isLoading ? 'Loading...' : 'Refresh' }}</span>
        </button>
      </div>
    </header>

    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="loading-animation">
        <div class="loading-circle"></div>
        <p>Loading server data...</p>
      </div>
    </div>

    <div v-else class="folders-container">
      <div 
        v-for="(files, folderName) in serverData" 
        :key="folderName" 
        class="folder-card"
      >
        <div class="folder-header" @click="toggleFolder(folderName)">
          <div class="folder-info">
            <span class="folder-icon">
              {{ expandedFolders.has(folderName) ? '📂' : '📁' }}
            </span>
            <h3 class="folder-name">{{ folderName }}</h3>
            <span class="file-count">{{ files.length }} files</span>
          </div>
          <div class="folder-actions">
            <label class="upload-button" :class="{ 'uploading': uploadingFiles.has(folderName) }">
              <input 
                type="file" 
                multiple 
                accept=".csv,.xlsx,.xls,.pdf,.txt"
                @change="handleFileUpload(folderName, $event)"
                :disabled="uploadingFiles.has(folderName)"
              />
              <span v-if="uploadingFiles.has(folderName)" class="upload-spinner"></span>
              <span v-else>📤</span>
              <span>{{ uploadingFiles.has(folderName) ? 'Uploading...' : 'Upload' }}</span>
            </label>
            <button class="expand-button" :class="{ 'expanded': expandedFolders.has(folderName) }">
              <span>{{ expandedFolders.has(folderName) ? '▼' : '▶' }}</span>
            </button>
          </div>
        </div>

        <Transition name="folder-content">
          <div v-if="expandedFolders.has(folderName)" class="folder-content">
            <div v-if="files.length === 0" class="empty-folder">
              <span class="empty-icon">📭</span>
              <p>No files in this folder</p>
            </div>
            <div v-else class="files-grid">
              <div 
                v-for="fileName in files" 
                :key="fileName" 
                class="file-item"
              >
                <div class="file-info">
                  <span class="file-icon">{{ getFileIcon(fileName) }}</span>
                  <div class="file-details">
                    <p class="file-name">{{ fileName }}</p>
                    <p class="file-meta">{{ getFileSize() }}</p>
                  </div>
                </div>
                <div class="file-actions">
                  <button 
                    @click="downloadFile(folderName, fileName)" 
                    class="action-button download-button"
                    title="Download file"
                  >
                    <span>⬇️</span>
                  </button>
                  <button 
                    @click="deleteFile(folderName, fileName)" 
                    class="action-button delete-button"
                    title="Delete file"
                  >
                    <span>🗑️</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <div v-if="Object.keys(serverData).length === 0" class="empty-drive">
        <div class="empty-content">
          <span class="empty-icon">📂</span>
          <h3>No folders found</h3>
          <p>Your server drive appears to be empty</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.server-drive-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.drive-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drive-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
}

.title-icon {
  font-size: 2.5rem;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.refresh-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.refresh-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner, .upload-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-message {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-animation {
  text-align: center;
  color: white;
}

.loading-circle {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.folders-container {
  display: grid;
  gap: 1.5rem;
}

.folder-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.folder-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
}

.folder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.folder-header:hover {
  background: rgba(102, 126, 234, 0.05);
}

.folder-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.folder-icon {
  font-size: 2rem;
}

.folder-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.file-count {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.folder-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.upload-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #48bb78, #38a169);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.upload-button:hover:not(.uploading) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(72, 187, 120, 0.4);
}

.upload-button.uploading {
  opacity: 0.7;
  cursor: not-allowed;
}

.upload-button input[type="file"] {
  position: absolute;
  left: -9999px;
  opacity: 0;
}

.expand-button {
  background: rgba(102, 126, 234, 0.1);
  border: none;
  border-radius: 8px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #667eea;
  font-size: 1rem;
}

.expand-button:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.expand-button.expanded {
  background: rgba(102, 126, 234, 0.2);
}

.folder-content-enter-active,
.folder-content-leave-active {
  transition: all 0.3s ease;
}

.folder-content-enter-from,
.folder-content-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.folder-content {
  padding: 0 2rem 2rem;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
  background: rgba(102, 126, 234, 0.02);
}

.empty-folder {
  text-align: center;
  padding: 3rem 1rem;
  color: #718096;
}

.empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.files-grid {
  display: grid;
  gap: 1rem;
  margin-top: 1.5rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.file-item:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-icon {
  font-size: 1.5rem;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.file-meta {
  font-size: 0.875rem;
  color: #718096;
  margin: 0;
}

.file-actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  padding: 0.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.download-button {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
}

.download-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(66, 153, 225, 0.4);
}

.delete-button {
  background: linear-gradient(135deg, #f56565, #e53e3e);
  color: white;
}

.delete-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 101, 101, 0.4);
}

.empty-drive {
  text-align: center;
  padding: 4rem 2rem;
  color: white;
}

.empty-content .empty-icon {
  font-size: 5rem;
  display: block;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.empty-content h3 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.empty-content p {
  font-size: 1.125rem;
  opacity: 0.8;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .server-drive-container {
    padding: 1rem;
  }
  
  .drive-title {
    font-size: 2rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .folder-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .folder-actions {
    justify-content: space-between;
  }
  
  .file-item {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .file-actions {
    justify-content: center;
  }
}
</style>