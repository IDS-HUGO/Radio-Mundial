/**
 * Radio-Mundial HTML5 Audio Bridge & Preferences Manager
 * Audio nativo sin interrupciones con recuperación de errores y persistencia.
 */
window.radioAudio = {
    audio: null,
    dotNetHelper: null,
    currentUrl: "",

    init: function (dotNetReference) {
        if (dotNetReference) {
            this.dotNetHelper = dotNetReference;
        }
        if (!this.audio) {
            this.audio = new Audio();
            this.audio.preload = 'none';

            this.audio.addEventListener('playing', () => {
                if (this.dotNetHelper) {
                    this.dotNetHelper.invokeMethodAsync('OnNativeAudioPlay');
                }
            });

            this.audio.addEventListener('pause', () => {
                if (this.dotNetHelper) {
                    this.dotNetHelper.invokeMethodAsync('OnNativeAudioPause');
                }
            });

            this.audio.addEventListener('error', (e) => {
                console.warn('[RadioAudio] Advertencia o desconexión en stream:', e);
                if (this.dotNetHelper) {
                    this.dotNetHelper.invokeMethodAsync('OnNativeAudioError', 'Stream no disponible.');
                }
            });
            this.initThemeWatcher();
        }
    },

    play: async function (streamUrl) {
        this.init();
        try {
            if (!streamUrl) return false;

            if (this.currentUrl !== streamUrl) {
                this.audio.pause();
                this.currentUrl = streamUrl;
                this.audio.src = streamUrl;
                this.audio.load();
            }

            const playPromise = this.audio.play();
            if (playPromise !== undefined) {
                await playPromise;
            }
            return true;
        } catch (error) {
            console.warn('[RadioAudio] Autoplay o cambio de stream gestionado:', error.message);
            if (this.dotNetHelper) {
                this.dotNetHelper.invokeMethodAsync('OnNativeAudioError', error.message || 'Stream no disponible');
            }
            return false;
        }
    },

    pause: function () {
        if (this.audio) {
            this.audio.pause();
        }
    },

    updateMediaMetadata: function (title, artist, album, artworkUrl) {
        if ('mediaSession' in navigator) {
            try {
                navigator.mediaSession.metadata = new MediaMetadata({
                    title: title || 'Radio Mundial',
                    artist: artist || 'Transmisión Global en Vivo',
                    album: album || 'Radio Mundial Hi-Fi',
                    artwork: artworkUrl ? [{ src: artworkUrl, sizes: '512x512', type: 'image/jpeg' }] : []
                });

                navigator.mediaSession.setActionHandler('play', () => {
                    if (this.dotNetHelper) this.dotNetHelper.invokeMethodAsync('TogglePlayAsync');
                });
                navigator.mediaSession.setActionHandler('pause', () => {
                    if (this.dotNetHelper) this.dotNetHelper.invokeMethodAsync('TogglePlayAsync');
                });
                navigator.mediaSession.setActionHandler('previoustrack', () => {
                    if (this.dotNetHelper) this.dotNetHelper.invokeMethodAsync('TunePreviousStationAsync');
                });
                navigator.mediaSession.setActionHandler('nexttrack', () => {
                    if (this.dotNetHelper) this.dotNetHelper.invokeMethodAsync('TuneNextStationAsync');
                });
            } catch (e) {
                console.debug('[RadioAudio] MediaSession metadata error:', e);
            }
        }
        if (title) {
            document.title = `${title} | Radio Mundial`;
        }
    },

    setVolume: function (volume) {
        this.init();
        const clamped = Math.max(0, Math.min(1, volume));
        if (this.audio) {
            this.audio.volume = clamped;
        }
    },

    setCookie: function (name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + encodeURIComponent(value || "") + expires + "; path=/; SameSite=Lax";
    },

    getCookie: function (name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
        }
        return null;
    },

    savePreferences: function (prefsJson) {
        try {
            localStorage.setItem("radio_mundial_preferences", prefsJson);
            this.setCookie("radio_prefs", prefsJson, 365);
        } catch (e) {
            console.warn('[RadioAudio] No se pudieron guardar preferencias:', e);
        }
    },

    loadPreferences: function () {
        try {
            const local = localStorage.getItem("radio_mundial_preferences");
            if (local) return local;

            const cookie = this.getCookie("radio_prefs");
            if (cookie) return cookie;
        } catch (e) {
            console.warn('[RadioAudio] Error al cargar preferencias:', e);
        }
        return null;
    },

    currentThemeMode: "system",

    initThemeWatcher: function () {
        const mq = window.matchMedia('(prefers-color-scheme: dark)');
        mq.addEventListener('change', (e) => {
            if (this.currentThemeMode === 'system') {
                this.applyTheme('system');
            }
        });
    },

    applyTheme: function (themeMode) {
        this.currentThemeMode = themeMode || "system";
        let resolved = "dark";
        if (this.currentThemeMode === "system") {
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            resolved = prefersDark ? "dark" : "light";
        } else {
            resolved = this.currentThemeMode;
        }
        document.documentElement.setAttribute('data-theme', resolved);
        document.body.setAttribute('data-theme', resolved);
        return resolved;
    }
};
