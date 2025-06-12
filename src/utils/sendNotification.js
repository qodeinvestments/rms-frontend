export const requestNotificationPermission = async () => {
    if (!("Notification" in window)) {
        console.log("This browser does not support notifications");
        return;
    }

    let permission = Notification.permission;
    
    if (permission === "default") {
        try {
            permission = await Notification.requestPermission();
        } catch (error) {
            console.error("Error requesting permission:", error);
        }
    }
    
    console.log("Notification permission:", permission);
    // if (permission !== "granted") {
    //     alert("Please enable notifications in your browser settings.");
    // }
};

export const sendNotification = async (title, message) => {
    if (!("Notification" in window) || Notification.permission !== "granted") {
        console.log("No notification permission");
        return;
    }

    if ("serviceWorker" in navigator) {
        navigator.serviceWorker.ready
            .then((reg) => {
                reg.showNotification(title, {
                    body: message,
                    icon: "/favicon.ico",
                    requireInteraction: true,
                    silent: true // No sound, only visual notification
                });
            })
            .catch((err) => console.error("Error showing notification:", err));
    }
};
