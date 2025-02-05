self.addEventListener("install", (event) => {
    console.log("Service Worker installed");
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    console.log("Service Worker activated");
    return self.clients.claim();
});

// Listen for push notifications
self.addEventListener("push", (event) => {
    const data = event.data ? event.data.json() : { title: "Default", body: "No data received" };
    console.log("Push Notification Received:", data); // ✅ Debugging log

    self.registration.showNotification(data.title, {
        body: data.body,
        icon: "/favicon.ico",
        tag: data.tag || "default-tag",
        requireInteraction: false,
    });
});