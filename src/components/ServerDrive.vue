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
    case 'csv': return 'fa-file-csv';
    case 'xlsx': case 'xls': return 'fa-file-excel';
    case 'pdf': return 'fa-file-pdf';
    case 'txt': return 'fa-file-alt';
    case 'doc': case 'docx': return 'fa-file-word';
    case 'ppt': case 'pptx': return 'fa-file-powerpoint';
    case 'zip': case 'rar': return 'fa-file-archive';
    case 'jpg': case 'jpeg': case 'png': case 'gif': return 'fa-file-image';
    default: return 'fa-file';
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
          <i class="fas fa-server title-icon"></i>
          Server Drive
        </h1>
        <button @click="fetchServerData" class="refresh-button" :disabled="isLoading">
          <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-sync-alt"></i>
          <span>{{ isLoading ? 'Loading...' : 'Refresh' }}</span>
        </button>
      </div>
    </header>

    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-triangle error-icon"></i>
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="loading-animation">
        <i class="fas fa-spinner fa-spin loading-spinner"></i>
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
            <i class="fas folder-icon" 
               :class="expandedFolders.has(folderName) ? 'fa-folder-open' : 'fa-folder'"></i>
            <h3 class="folder-name">{{ folderName }}</h3>
            <span class="file-count">
              <i class="fas fa-file-alt"></i>
              {{ files.length }}
            </span>
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
              <i v-if="uploadingFiles.has(folderName)" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-upload"></i>
              <span>{{ uploadingFiles.has(folderName) ? 'Uploading...' : 'Upload' }}</span>
            </label>
            <button class="expand-button" :class="{ 'expanded': expandedFolders.has(folderName) }">
              <i class="fas" :class="expandedFolders.has(folderName) ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </button>
          </div>
        </div>

        <Transition name="folder-content">
          <div v-if="expandedFolders.has(folderName)" class="folder-content">
            <div v-if="files.length === 0" class="empty-folder">
              <i class="fas fa-inbox empty-icon"></i>
              <p>No files in this folder</p>
            </div>
            <div v-else class="files-grid">
              <div 
                v-for="fileName in files" 
                :key="fileName" 
                class="file-item"
              >
                <div class="file-info">
                  <i class="fas file-icon" :class="getFileIcon(fileName)"></i>
                  <div class="file-details">
                    <p class="file-name">{{ fileName }}</p>
                    <p class="file-meta">
                      <i class="fas fa-weight"></i>
                      {{ getFileSize() }}
                    </p>
                  </div>
                </div>
                <div class="file-actions">
                  <button 
                    @click="downloadFile(folderName, fileName)" 
                    class="action-button download-button"
                    title="Download file"
                  >
                    <i class="fas fa-download"></i>
                  </button>
                  <button 
                    @click="deleteFile(folderName, fileName)" 
                    class="action-button delete-button"
                    title="Delete file"
                  >
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <div v-if="Object.keys(serverData).length === 0" class="empty-drive">
        <div class="empty-content">
          <i class="fas fa-folder-open empty-icon"></i>
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
  background: #f8f9fa;
  padding: 1.5rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.drive-header {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drive-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
}

.title-icon {
  color: #3498db;
  font-size: 1.8rem;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.refresh-button:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
}

.refresh-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  background: #fff5f5;
  color: #e53e3e;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid #fed7d7;
}

.error-icon {
  color: #e53e3e;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-animation {
  text-align: center;
  color: #6c757d;
}

.loading-spinner {
  font-size: 2rem;
  color: #3498db;
  margin-bottom: 1rem;
}

.folders-container {
  display: grid;
  gap: 1.5rem;
}

.folder-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.folder-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.folder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border-bottom: 1px solid #f8f9fa;
}

.folder-header:hover {
  background: #f8f9fa;
}

.folder-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.folder-icon {
  font-size: 1.5rem;
  color: #3498db;
  width: 24px;
}

.folder-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.file-count {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
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
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  font-size: 0.875rem;
}

.upload-button:hover:not(.uploading) {
  background: #229954;
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(39, 174, 96, 0.3);
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
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #6c757d;
}

.expand-button:hover {
  background: #e9ecef;
  color: #495057;
}

.expand-button.expanded {
  background: #e3f2fd;
  color: #1976d2;
  border-color: #bbdefb;
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
  padding: 1.5rem 2rem 2rem;
  background: #fafbfc;
}

.empty-folder {
  text-align: center;
  padding: 3rem 1rem;
  color: #6c757d;
}

.empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
  color: #adb5bd;
}

.files-grid {
  display: grid;
  gap: 0.75rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.file-item:hover {
  border-color: #3498db;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.15);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-icon {
  font-size: 1.25rem;
  width: 20px;
  text-align: center;
}

.file-icon.fa-file-csv {
  color: #27ae60;
}

.file-icon.fa-file-excel {
  color: #2ecc71;
}

.file-icon.fa-file-pdf {
  color: #e74c3c;
}

.file-icon.fa-file-alt {
  color: #3498db;
}

.file-icon.fa-file-word {
  color: #2980b9;
}

.file-icon.fa-file-powerpoint {
  color: #e67e22;
}

.file-icon.fa-file-archive {
  color: #8e44ad;
}

.file-icon.fa-file-image {
  color: #f39c12;
}

.file-icon.fa-file {
  color: #7f8c8d;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  font-size: 0.875rem;
}

.file-meta {
  font-size: 0.75rem;
  color: #6c757d;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.file-actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  padding: 0.375rem 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.download-button {
  background: #3498db;
  color: white;
}

.download-button:hover {
  background: #2980b9;
  transform: translateY(-1px);
}

.delete-button {
  background: #e74c3c;
  color: white;
}

.delete-button:hover {
  background: #c0392b;
  transform: translateY(-1px);
}

.empty-drive {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.empty-content .empty-icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 1rem;
  color: #adb5bd;
}

.empty-content h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.empty-content p {
  font-size: 1rem;
  color: #6c757d;
}

@media (max-width: 768px) {
  .server-drive-container {
    padding: 1rem;
  }
  
  .drive-title {
    font-size: 1.5rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .folder-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .folder-info {
    justify-content: space-between;
  }
  
  .folder-actions {
    justify-content: space-between;
  }
  
  .file-item {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .file-info {
    justify-content: flex-start;
  }
  
  .file-actions {
    justify-content: center;
  }
}</style>