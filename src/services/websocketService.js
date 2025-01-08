import { ref } from 'vue';

class WebSocketService {
  constructor() {
    this.connections = {}; // Store WebSocket connections for different endpoints
    this.messageListeners = {}; // Store listeners for each endpoint
  }

  connect(endpoint, url) {
    if (this.connections[endpoint]) {
      console.log(`WebSocket for ${endpoint} is already connected.`);
      return;
    }

    const socket = new WebSocket(url);

    // Initialize message listeners array for this endpoint
    if (!this.messageListeners[endpoint]) {
      this.messageListeners[endpoint] = [];
    }

    socket.onopen = () => {
      console.log(`WebSocket connection for ${endpoint} opened.`);
      const token = localStorage.getItem('access_token');
      if (token) {
        const authMessage = JSON.stringify({ token });
        socket.send(authMessage);
      }
    };

    socket.onmessage = (event) => {
      if (event.data === 'ping') {
        socket.send('pong');
      } else {
        const message = JSON.parse(event.data);
        this.messageListeners[endpoint].forEach((listener) => listener(message));
      }
    };

    socket.onclose = (event) => {
      console.log(`WebSocket connection for ${endpoint} closed:`, event.reason);
      delete this.connections[endpoint];
    };

    socket.onerror = (error) => {
      console.error(`WebSocket error for ${endpoint}:`, error);
    };

    this.connections[endpoint] = socket; // Store the connection
  }

  disconnect(endpoint) {
    const socket = this.connections[endpoint];
    if (socket) {
      socket.close();
      delete this.connections[endpoint];
      delete this.messageListeners[endpoint];
    }
  }

  sendMessage(endpoint, message) {
    const socket = this.connections[endpoint];
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    } else {
      console.error(`WebSocket for ${endpoint} is not connected.`);
    }
  }

  addMessageListener(endpoint, callback) {
    if (!this.messageListeners[endpoint]) {
      this.messageListeners[endpoint] = [];
    }
    if (typeof callback === 'function') {
      this.messageListeners[endpoint].push(callback);
    }
  }

  removeMessageListener(endpoint, callback) {
    if (this.messageListeners[endpoint]) {
      this.messageListeners[endpoint] = this.messageListeners[endpoint].filter((listener) => listener !== callback);
    }
  }
}

const webSocketService = new WebSocketService();
export default webSocketService;
