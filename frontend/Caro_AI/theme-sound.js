// CaroAI Theme & Sound Engine — Refined Tabletop
(function () {
  const THEME_KEY = "caroai_theme";
  const SOUND_KEY = "caroai_sound_enabled";

  function applyTheme(theme) {
    if (theme === "dark" || theme === "light") {
      document.documentElement.setAttribute("data-theme", theme);
      document.documentElement.style.colorScheme = theme;
    } else {
      document.documentElement.removeAttribute("data-theme");
      const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      document.documentElement.style.colorScheme = prefersDark ? "dark" : "light";
    }
    updateThemeToggleUI();
  }

  function getStoredTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch (_) { return null; }
  }

  function setStoredTheme(theme) {
    try {
      if (theme) localStorage.setItem(THEME_KEY, theme);
      else localStorage.removeItem(THEME_KEY);
    } catch (_) {}
  }

  function isDark() {
    const attr = document.documentElement.getAttribute("data-theme");
    if (attr === "dark") return true;
    if (attr === "light") return false;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function toggleTheme() {
    const next = isDark() ? "light" : "dark";
    setStoredTheme(next);
    applyTheme(next);
  }

  function updateThemeToggleUI() {
    const btn = document.getElementById("themeToggleBtn");
    if (!btn) return;
    const dark = isDark();
    btn.setAttribute("aria-label", dark ? "Chuyển sang giao diện sáng" : "Chuyển sang giao diện tối");
    btn.setAttribute("title", dark ? "Chuyển sang giao diện sáng" : "Chuyển sang giao diện tối");
    btn.innerHTML = dark
      ? '<svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18" aria-hidden="true"><path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"/></svg><span class="sr-only">Giao diện sáng</span>'
      : '<svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18" aria-hidden="true"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/></svg><span class="sr-only">Giao diện tối</span>';
  }

  // Sound Engine (Web Audio API synthesis, OFF by default)
  let audioCtx = null;
  function isSoundEnabled() {
    try { return localStorage.getItem(SOUND_KEY) === "true"; } catch (_) { return false; }
  }

  function setSoundEnabled(enabled) {
    try { localStorage.setItem(SOUND_KEY, enabled ? "true" : "false"); } catch (_) {}
    updateSoundToggleUI();
  }

  function toggleSound() {
    const next = !isSoundEnabled();
    setSoundEnabled(next);
    if (next) playMoveSound();
  }

  function updateSoundToggleUI() {
    const btn = document.getElementById("soundToggleBtn");
    if (!btn) return;
    const enabled = isSoundEnabled();
    btn.setAttribute("aria-label", enabled ? "Tắt âm thanh bàn cờ" : "Bật âm thanh bàn cờ");
    btn.setAttribute("title", enabled ? "Tắt âm thanh bàn cờ" : "Bật âm thanh bàn cờ");
    btn.setAttribute("aria-pressed", String(enabled));
    btn.innerHTML = enabled
      ? '<svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18" aria-hidden="true"><path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.776L4.828 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.828l3.555-3.776a1 1 0 011.006-.148zM14.657 5.343a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 4.657 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.829 1 1 0 010-1.414z" clip-rule="evenodd"/></svg><span class="sr-only">Âm thanh: Bật</span>'
      : '<svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18" aria-hidden="true"><path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.776L4.828 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.828l3.555-3.776a1 1 0 011.006-.148zM12.293 7.293a1 1 0 011.414 0L15 8.586l1.293-1.293a1 1 0 111.414 1.414L16.414 10l1.293 1.293a1 1 0 01-1.414 1.414L15 11.414l-1.293 1.293a1 1 0 01-1.414-1.414L13.586 10l-1.293-1.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg><span class="sr-only">Âm thanh: Tắt</span>';
  }

  function getAudioContext() {
    if (!audioCtx && (window.AudioContext || window.webkitAudioContext)) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx && audioCtx.state === "suspended") {
      audioCtx.resume();
    }
    return audioCtx;
  }

  function playMoveSound() {
    if (!isSoundEnabled()) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const now = ctx.currentTime;
      osc.type = "sine";
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.exponentialRampToValueAtTime(200, now + 0.045);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.045);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.045);
    } catch (_) {}
  }

  function playVictorySound() {
    if (!isSoundEnabled()) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const now = ctx.currentTime;
      [523.25, 659.25, 783.99].forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const t = now + idx * 0.07;
        osc.type = "triangle";
        osc.frequency.setValueAtTime(freq, t);
        gain.gain.setValueAtTime(0.09, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.22);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.22);
      });
    } catch (_) {}
  }

  window.CaroAI = window.CaroAI || {};
  window.CaroAI.theme = {
    apply: applyTheme,
    toggle: toggleTheme,
    isDark: isDark,
    updateUI: updateThemeToggleUI
  };
  window.CaroAI.sound = {
    isEnabled: isSoundEnabled,
    toggle: toggleSound,
    updateUI: updateSoundToggleUI,
    playMove: playMoveSound,
    playVictory: playVictorySound
  };

  // Immediate theme application to eliminate flash of wrong theme
  applyTheme(getStoredTheme());

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      updateThemeToggleUI();
      updateSoundToggleUI();
      const themeBtn = document.getElementById("themeToggleBtn");
      if (themeBtn) themeBtn.addEventListener("click", toggleTheme);
      const soundBtn = document.getElementById("soundToggleBtn");
      if (soundBtn) soundBtn.addEventListener("click", toggleSound);
    });
  } else {
    updateThemeToggleUI();
    updateSoundToggleUI();
    const themeBtn = document.getElementById("themeToggleBtn");
    if (themeBtn) themeBtn.addEventListener("click", toggleTheme);
    const soundBtn = document.getElementById("soundToggleBtn");
    if (soundBtn) soundBtn.addEventListener("click", toggleSound);
  }
})();
