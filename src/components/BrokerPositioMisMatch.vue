<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
    createColumnHelper,
} from '@tanstack/vue-table'
import TanStackTestTable from './TanStackTestTable.vue'
import * as XLSX from 'xlsx'  // Add this import


const defaultData = {}



// Add these refs near other ref declarations
const fileInput = ref(null)

// Add these refs for loading states
const isUploading = ref(false)
const isDownloading = ref(false)
const isAllDownloading = ref(false)

const handleFileUpload = async (event) => {
    try {
        isUploading.value = true  // Start loading
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('User not authenticated');
        }

        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('https://production2.swancapital.in/UpdateBrokerPositionMismatch', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            console.log('Upload successful:', data);
            alert('File uploaded successfully!');
        }
    } catch (error) {
        console.error('Upload failed:', error);
        alert(`Error: ${error.message}`);
    } finally {
        isUploading.value = false  // End loading
    }
}

const downloadCSV = async (type) => {
    try {
        
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('User not authenticated');
        }

        let url = "DownloadBrokerPositionMismatch";
        if (type === 'ALL') {
            isAllDownloading.value=true
            url = 'DownloadALLBrokerPositionMismatch';
        }
        else isDownloading.value = true  // Start loading

        const response = await fetch(`https://production2.swancapital.in/${url}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const jsonResponse = await response.json();

        if (!response.ok) {
            throw new Error(jsonResponse.detail || jsonResponse.message || 'An error occurred');
        }

        // Download Excel file
        const download = (data, title) => {
            try {
                if (!data || !Array.isArray(data.data)) {
                    throw new Error('Invalid data format received');
                }
                
                const currentDate = new Date();
                const formattedDate = currentDate.toLocaleString('en-US', {
                    year: 'numeric',
                    month: '2-digit', 
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                }).replace(/[/:]/g, '_');

                const file_name = `broker_position_mismatch_${formattedDate}.xlsx`;
                
                const wb = XLSX.utils.book_new();
                const ws = XLSX.utils.json_to_sheet(data.data, { header: data.columns });
                XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
                XLSX.writeFile(wb, file_name);
            } catch (error) {
                console.error('Download error:', error);
                throw error;
            }
        };

        if (jsonResponse.dataframe) {
            download(jsonResponse.dataframe, "broker_position_mismatch");
            alert("File downloaded successfully!");
        } else {
            throw new Error('No data received from server');
        }
    } catch (error) {
        console.error('Download failed:', error);
        alert(`Error: ${error.message}`);
    } finally {
        isDownloading.value = false  // End loading
        isAllDownloading.value=false
    }
}
const data = ref(defaultData)
const columnHelper = createColumnHelper()

import { h } from 'vue'
// ... existing imports ...

const columns = [
    columnHelper.accessor(row => row.Symbol, {
        id: 'Symbol',
        cell: info => info.getValue(),
        header: () => 'Symbol',
    }),
    columnHelper.accessor(row => row.Quantity, {
        id: 'Difference Quantity',
        cell: info => info.getValue(),
        header: () => 'Quantity',
    }),
    columnHelper.accessor(row => row.Checked, {
    id: 'Checked',
    cell: info => h('div', {
        innerHTML: info.getValue()
            ? '<span style="color: #22c55e; font-size: 1.2em;">✓</span>'  // Unicode checkmark
            : '<span style="color: #ef4444; font-size: 1.2em;">✗</span>', // Unicode X
        style: {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
        }
    }),
    header: () => 'Checked',
    enableSorting: true
})
]




const client_BackendData = ref({})
const connection_BackendData = ref({})

const time = ref([])
const checkBackendConnection = ref(false)
const Latency = ref(0)
const max_latency = ref(0);
const past_time = ref(0);
let socket = null
let reconnectAttempts = 0
const users = ref([])
const user = ref('')
const fulldata = ref()
const posdata=ref()




const handleMessage = (message) => {
    client_BackendData.value = message.client_data
    connection_BackendData.value = message.connection_data
    if (message.connection_data) {
        fulldata.value = message.connection_data.broker_Position_Mismatch;
        posdata.value=message.connection_data.position_broker_Mismatch;
        users.value=Object.keys(fulldata.value);
    }
   

}




const connectWebSocket = () => {
    const token = localStorage.getItem('access_token'); // Retrieve the access token
    if (!token) {
        alert('User not authenticated');
        return;
    }
    const socket = new WebSocket('wss://production2.swancapital.in/ws');

    socket.onopen = () => {
        console.log('WebSocket connection opened')
        const authMessage = JSON.stringify({ token });
        socket.send(authMessage);
        checkBackendConnection.value = true
        reconnectAttempts = 0
  
    }

    socket.onmessage = (event) => {
        if (event.data === 'ping') {
            socket.send('pong')
        } else {

            const message = JSON.parse(event.data);
            let ar2 = message.time;
            if (past_time.value === 0) past_time.value = ar2;
            let date1 = new Date(past_time.value.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let date2 = new Date(ar2.replace(/(\d{2})-(\d{2})-(\d{4})/, '$3-$2-$1'));
            let diffInMs = date2 - date1;
            let diffInSeconds = diffInMs / 1000;
            Latency.value = diffInSeconds;
            max_latency.value = Math.max(max_latency.value, Latency.value)
            past_time.value = ar2;
            handleMessage(message)
        }
    }

    socket.onclose = (event) => {
        console.log('WebSocket connection closed:', event.reason)
        checkBackendConnection.value = false
  
    }


    socket.onerror = (error) => {
        console.error('WebSocket error:', error)
        checkBackendConnection.value = false
    }
}


const givecolor = (option) => {
    if (fulldata.value[option]) {
        // Check if any item in the array has Checked = false
        const hasUncheckedItems = fulldata.value[option].some(item => item.Checked === false);
        if (hasUncheckedItems) {
            return 'negativecolor';
        }
    }
    if (posdata.value[option]) {
        // Check if any item in the array has Checked = false
        const hasUncheckedItems = posdata.value[option].some(item => item.Checked === false);
        if (hasUncheckedItems) {
            return 'negativecolor';
        }
    }
    return '';
}







onMounted(() => {
    connectWebSocket()
})

onUnmounted(() => {
    if (socket) {
        socket.close()
    }
})
</script>



<template>
    <div class="homePage_Container bg-[#efefef]/30">
       
        <div class="button-container">
            <input
                type="file"
                ref="fileInput"
                @change="handleFileUpload"
                accept=".csv,.xlsx,.xls"
                style="display: none"
            />
            <button 
                class="action-button" 
                @click="$refs.fileInput.click()"
                :disabled="isUploading"
            >
                <span v-if="isUploading" class="loader"></span>
                {{ isUploading ? 'Uploading...' : 'Upload File' }}
            </button>
            <button 
                class="action-button" 
                @click="downloadCSV('ALL')"
                :disabled="isAllDownloading"
            >
                <span v-if="isAllDownloading" class="loader"></span>
                {{ isAllDownloading ? 'Downloading...' : 'Download All CSV' }}
            </button>
            <button 
                class="action-button" 
                @click="downloadCSV('ONE')"
                :disabled="isDownloading"
            >
                <span v-if="isDownloading" class="loader"></span>
                {{ isDownloading ? 'Downloading...' : 'Download Current CSV' }}
            </button>
        </div>
        <div class="userSelectContainer" v-if="users">
            <label class="table-heading" for="options">Select an User:</label>
            <select class="table-heading" id="options" v-model="user">
                <option v-for="option in [...users].sort()" :key="option" :value="option"
                    :class="givecolor(option)">
                    {{ option }}
                </option>
            </select>
        </div>
       
        <div v-if="user === ''" class="mx-auto py-8 negative">
            <p class="table-heading">Select User !</p>
        </div>
        <div v-else-if="Object.keys(fulldata[user]).length > 0 || Object.keys(posdata[user]).length > 0" class="mx-auto px-8 py-8 flex flex-col gap-8">
            <!-- <p class="table-heading">Position MisMatch : {{ user }}</p> -->
             <div v-if="Object.keys(fulldata[user]).length > 0">
                <TanStackTestTable title="Broker Position MisMatch" :data="fulldata[user]" :columns="columns" :hasColor="[]" :navigateTo="{}"
                :showPagination="true" :hasRowcolor="{}"  :defaultSortFirstColumn="true"/>

             </div>
             <div v-if="Object.keys(posdata[user]).length > 0">

                <TanStackTestTable title="Position Broker MisMatch" :data="posdata[user]" :columns="columns" :hasColor="[]" :navigateTo="{}"
                :showPagination="true" :hasRowcolor="{}"  :defaultSortFirstColumn="true"/>

             </div>
           
           
        </div>

        <div v-else class="mx-auto px-8 py-8">
            <p class="table-heading">No Data</p>
        </div>
    </div>
</template>


<style>
html {
    font-size: 14px;
}


.action-button {
    padding: 8px 16px;
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 120px;
    justify-content: center;
}

.action-button:disabled {
    background-color: #a0a0a0;
    cursor: not-allowed;
}

.loader {
    width: 16px;
    height: 16px;
    border: 2px solid #ffffff;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
    animation: rotation 1s linear infinite;
}

@keyframes rotation {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

.button-container {
    display: flex;
    gap: 1rem;
    margin: 20px 30px;
}

.action-button {
    padding: 8px 16px;
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
}

.action-button:hover {
    background-color: #357abd;
}

.userSelectContainer {
    margin-top: 30px;
}

.table-heading {
    font-size: 22px;
    font-weight: 600;
    margin-left: 30px;
}

.negativecolor {
    color: #d95858 !important;
}
</style>