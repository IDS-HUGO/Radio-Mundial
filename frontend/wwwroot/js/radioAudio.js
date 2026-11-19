/**
 * Radio-Mundial HTML5 Audio Bridge & Preferences Manager
 * Audio nativo sin interrupciones con recuperación de errores y persistencia.
 */
window.radioAudio = {
    audio: null,
    dotNetHelper: null,
    currentUrl: "",
    originalStreamUrl: "",
    canFallbackToHttp: false,

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
                // Si falló el intento sobre https, intentar fallback a la url original si era http
                if (this.canFallbackToHttp && this.originalStreamUrl && this.currentUrl !== this.originalStreamUrl) {
                    this.canFallbackToHttp = false;
                    console.info('[RadioAudio] Reintentando con stream original:', this.originalStreamUrl);
                    this.currentUrl = this.originalStreamUrl;
                    this.audio.src = this.originalStreamUrl;
                    this.audio.load();
                    this.audio.play().catch(err => {
                        console.warn('[RadioAudio] Fallback original también falló:', err);
                        if (this.dotNetHelper) {
                            this.dotNetHelper.invokeMethodAsync('OnNativeAudioError', 'Stream no disponible.');
                        }
                    });
                    return;
                }
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

            this.originalStreamUrl = streamUrl.trim();
            this.canFallbackToHttp = false;

            let candidateUrl = this.originalStreamUrl;
            // Si la página se carga sobre HTTPS y el stream es http://, intentar upgrade seguro a https:// si no es IP
            if (location.protocol === 'https:' && candidateUrl.startsWith('http://')) {
                const isIp = /^http:\/\/\d+\.\d+\.\d+\.\d+/.test(candidateUrl);
                if (!isIp) {
                    candidateUrl = candidateUrl.replace('http://', 'https://');
                    this.canFallbackToHttp = true;
                }
            }

            if (this.currentUrl !== candidateUrl) {
                this.audio.pause();
                this.currentUrl = candidateUrl;
                this.audio.src = candidateUrl;
                this.audio.load();
            }

            const playPromise = this.audio.play();
            if (playPromise !== undefined) {
                await playPromise;
            }
            return true;
        } catch (error) {
            console.warn('[RadioAudio] Reproducción inicial no completada:', error.message);
            if (this.canFallbackToHttp && this.originalStreamUrl && this.currentUrl !== this.originalStreamUrl) {
                this.canFallbackToHttp = false;
                try {
                    this.currentUrl = this.originalStreamUrl;
                    this.audio.src = this.originalStreamUrl;
                    this.audio.load();
                    const p = this.audio.play();
                    if (p !== undefined) await p;
                    return true;
                } catch (fallbackErr) {
                    console.warn('[RadioAudio] Fallback original también falló:', fallbackErr.message);
                }
            }
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

    initThemeWatcher: function () {
        try {
            const savedTheme = localStorage.getItem('rm_theme') || 'dark';
            this.applyTheme(savedTheme);

            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
                const current = localStorage.getItem('rm_theme') || 'system';
                if (current === 'system') {
                    this.applyTheme('system');
                }
            });
        } catch (e) {
            console.debug('[RadioAudio] Theme init handled:', e);
        }
    },

    applyTheme: function (themeName) {
        try {
            localStorage.setItem('rm_theme', themeName);
            let effective = themeName;
            if (themeName === 'system') {
                const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                effective = prefersDark ? 'dark' : 'light';
            }
            document.documentElement.setAttribute('data-theme', effective);
            const metaTheme = document.querySelector('meta[name="theme-color"]');
            if (metaTheme) {
                metaTheme.setAttribute('content', effective === 'dark' ? '#0E0B08' : '#F7F2EB');
            }
        } catch (e) {
            console.debug('[RadioAudio] Apply theme handled:', e);
        }
    },

    getCurrentThemePreference: function () {
        try {
            return localStorage.getItem('rm_theme') || 'dark';
        } catch (e) {
            return 'dark';
        }
    },

    setStoredLanguage: function (lang) {
        try {
            localStorage.setItem('rm_lang', lang);
            this.setCookie('rm_lang', lang, 365);
        } catch (e) {
            console.debug('[RadioAudio] Language storage handled:', e);
        }
    },

    getStoredLanguage: function () {
        try {
            return localStorage.getItem('rm_lang') || this.getCookie('rm_lang') || this.getBrowserLanguage();
        } catch (e) {
            return 'es';
        }
    },

    getBrowserLanguage: function () {
        try {
            const langs = (navigator.languages && navigator.languages.length)
                ? navigator.languages
                : [navigator.language || navigator.userLanguage || 'es'];
            for (let i = 0; i < langs.length; i++) {
                const l = (langs[i] || '').toLowerCase().trim();
                if (l.startsWith('es')) return 'es';
            }
            const primary = (langs[0] || '').toLowerCase().trim();
            return primary.startsWith('es') ? 'es' : 'en';
        } catch (e) {
            return 'es';
        }
    }
};
