export const playSound = async (soundFile = "/alarm.mp3", volume = 0.3) => {
    const audio = new Audio(soundFile);
    audio.volume = volume;
    try {
        audio.currentTime = 0;
        await audio.play();
    } catch (error) {
        console.error("Error playing audio:", error);
    }
};
