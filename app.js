/**
 * J.A.R.V.I.S. Core Frontend Controller
 * Coordinates WebSockets, Web Audio API, Speech Recognition, and HUD Telemetry.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const reactor = new ArcReactor('reactorCanvas');
  const micBtn = document.getElementById('micBtn');
  const micLabel = document.getElementById('micLabel');
  const stateBadge = document.getElementById('stateBadge');
  const stateText = document.getElementById('stateText');
  const speechContent = document.getElementById('speechContent');
  const speechTag = document.getElementById('speechTag');
  const terminalFeed = document.getElementById('terminalFeed');
  const clearLogBtn = document.getElementById('clearLogBtn');
  const commandForm = document.getElementById('commandForm');
  const textInput = document.getElementById('textInput');
  const hudClock = document.getElementById('hudClock');
  const connStatus = document.getElementById('connStatus');
  const jarvisAudio = document.getElementById('jarvisAudio');
  const volumeSlider = document.getElementById('volumeSlider');

  // Telemetry Elements
  const cpuVal = document.getElementById('cpuVal');
  const cpuBar = document.getElementById('cpuBar');
  const cpuSub = document.getElementById('cpuSub');
  const ramVal = document.getElementById('ramVal');
  const ramBar = document.getElementById('ramBar');
  const ramSub = document.getElementById('ramSub');
  const diskVal = document.getElementById('diskVal');
  const diskBar = document.getElementById('diskBar');
  const diskSub = document.getElementById('diskSub');
  const batVal = document.getElementById('batVal');
  const batBar = document.getElementById('batBar');
  const batSub = document.getElementById('batSub');
  const uptimeVal = document.getElementById('uptimeVal');
  const procVal = document.getElementById('procVal');

  // Audio Context & Analyser Setup
  let audioCtx = null;
  let audioAnalyser = null;
  let micAnalyser = null;
  let micStream = null;
  let isListening = false;
  let recognition = null;
  let ws = null;

  function initAudioContext() {
    if (audioCtx) return;
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContext();
      
      // Connect Output Audio
      audioAnalyser = audioCtx.createAnalyser();
      audioAnalyser.fftSize = 128;
      const audioSource = audioCtx.createMediaElementSource(jarvisAudio);
      audioSource.connect(audioAnalyser);
      audioAnalyser.connect(audioCtx.destination);

      // Animation frame hook for visualizer
      function audioLoop() {
        if (jarvisAudio && !jarvisAudio.paused) {
          reactor.updateAudioData(audioAnalyser);
        } else if (isListening && micAnalyser) {
          reactor.updateAudioData(micAnalyser);
        } else {
          reactor.updateAudioData(null);
        }
        requestAnimationFrame(audioLoop);
      }
      audioLoop();
    } catch (e) {
      console.warn("Audio Context init deferred:", e);
    }
  }

  // Futuristic Sound FX synthesized with Web Audio API
  function playSoundFX(type) {
    if (!audioCtx) initAudioContext();
    if (!audioCtx) return;

    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);

      const now = audioCtx.currentTime;
      if (type === 'activate') {
        // High dual chirp
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(1400, now + 0.12);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.15);
        osc.start(now);
        osc.stop(now + 0.15);
      } else if (type === 'ack') {
        // Tech acknowledgment blip
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(1200, now);
        osc.frequency.setValueAtTime(1600, now + 0.06);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.12);
        osc.start(now);
        osc.stop(now + 0.12);
      }
    } catch (e) {
      // Audio not yet unlocked
    }
  }

  // Clock Update
  function updateClock() {
    const now = new Date();
    hudClock.textContent = now.toLocaleTimeString();
  }
  setInterval(updateClock, 1000);
  updateClock();

  // State Management
  function setUIState(state) {
    reactor.setState(state);
    stateBadge.className = 'reactor-state-badge ' + state.toLowerCase();
    stateText.textContent = state;
  }

  // Terminal Log
  function addLog(text, sender = 'system') {
    const entry = document.createElement('div');
    entry.className = `feed-entry ${sender}`;
    const time = new Date().toLocaleTimeString().split(' ')[0];
    
    if (sender === 'user') {
      entry.innerHTML = `<span class="time">[${time}]</span> <span class="speaker">YOU:</span> "${text}"`;
    } else if (sender === 'jarvis') {
      entry.innerHTML = `<span class="time">[${time}]</span> <span class="speaker">JARVIS:</span> "${text}"`;
    } else {
      entry.innerHTML = `<span class="time">[${time}]</span> ${text}`;
    }
    
    terminalFeed.appendChild(entry);
    terminalFeed.scrollTop = terminalFeed.scrollHeight;
  }

  clearLogBtn.addEventListener('click', () => {
    terminalFeed.innerHTML = '';
    addLog('MISSION LOG BUFFER PURGED.', 'system');
  });

  // Update Telemetry Displays
  function updateTelemetry(data) {
    if (!data) return;
    
    // CPU
    cpuVal.textContent = `${data.cpu_percent}%`;
    cpuBar.style.width = `${Math.min(100, data.cpu_percent)}%`;
    cpuSub.textContent = `Cores: ${data.cpu_count} Threads`;

    // RAM
    ramVal.textContent = `${data.ram_percent}%`;
    ramBar.style.width = `${data.ram_percent}%`;
    ramSub.textContent = `Used: ${data.ram_used_gb} / ${data.ram_total_gb} GB`;

    // Disk
    diskVal.textContent = `${data.disk_percent}%`;
    diskBar.style.width = `${data.disk_percent}%`;
    diskSub.textContent = `Storage: ${data.disk_free_gb} GB Free`;

    // Battery
    if (data.battery) {
      batVal.textContent = `${data.battery.percent}%`;
      batBar.style.width = `${data.battery.percent}%`;
      batSub.textContent = data.battery.has_battery
        ? (data.battery.power_plugged ? 'Status: Charging AC' : 'Status: On Battery')
        : 'Status: Continuous AC';
    }

    // System Meta
    uptimeVal.textContent = data.uptime || '0:00:00';
    procVal.textContent = data.active_processes || '0';
  }

  // Play JARVIS Voice Audio
  async function speakJarvisResponse(text, audioUrl) {
    speechTag.textContent = 'J.A.R.V.I.S.';
    speechContent.textContent = `"${text}"`;
    addLog(text, 'jarvis');

    if (!audioUrl) {
      // Fallback to browser synthesis if backend audio generation had an issue
      fallbackBrowserSpeech(text);
      return;
    }

    try {
      initAudioContext();
      if (audioCtx && audioCtx.state === 'suspended') {
        await audioCtx.resume();
      }
      
      setUIState('SPEAKING');
      jarvisAudio.src = audioUrl;
      jarvisAudio.volume = parseFloat(volumeSlider.value);
      await jarvisAudio.play();

      jarvisAudio.onended = () => {
        setUIState('STANDBY');
      };
      jarvisAudio.onerror = () => {
        console.warn("Audio file playback issue, attempting browser speech fallback.");
        fallbackBrowserSpeech(text);
      };
    } catch (e) {
      console.warn("Playback error:", e);
      fallbackBrowserSpeech(text);
    }
  }

  function fallbackBrowserSpeech(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.rate = 1.05;
      utter.pitch = 0.95;
      
      // Try to find a British English voice
      const voices = window.speechSynthesis.getVoices();
      const british = voices.find(v => v.lang.includes('en-GB') || v.name.includes('British') || v.name.includes('UK'));
      if (british) utter.voice = british;

      utter.onstart = () => setUIState('SPEAKING');
      utter.onend = () => setUIState('STANDBY');
      utter.onerror = () => setUIState('STANDBY');
      window.speechSynthesis.speak(utter);
    } else {
      setUIState('STANDBY');
    }
  }

  // Hardware System Bridge Management
  const bridgeBadge = document.getElementById('bridgeBadge');
  const bridgeText = document.getElementById('bridgeText');
  const bridgeConfigBtn = document.getElementById('bridgeConfigBtn');
  const bridgeModal = document.getElementById('bridgeModal');
  const closeBridgeModal = document.getElementById('closeBridgeModal');
  const bridgeUrlInput = document.getElementById('bridgeUrlInput');
  const saveBridgeBtn = document.getElementById('saveBridgeBtn');
  const testBridgeBtn = document.getElementById('testBridgeBtn');
  const resetBridgeBtn = document.getElementById('resetBridgeBtn');
  const bridgeTestResult = document.getElementById('bridgeTestResult');

  let bridgeUrl = localStorage.getItem('jarvis_bridge_url') || (
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      ? window.location.origin
      : 'http://localhost:8000'
  );
  bridgeUrlInput.value = bridgeUrl;

  function getBridgeWsUrl() {
    let clean = bridgeUrl.trim().replace(/\/+$/, '');
    if (clean.startsWith('https://')) {
      return clean.replace('https://', 'wss://') + '/ws';
    } else if (clean.startsWith('http://')) {
      return clean.replace('http://', 'ws://') + '/ws';
    }
    return `ws://${clean}/ws`;
  }

  async function checkBridgeStatus() {
    try {
      const clean = bridgeUrl.trim().replace(/\/+$/, '');
      const resp = await fetch(`${clean}/api/bridge/ping`, { mode: 'cors' });
      if (resp.ok) {
        bridgeText.textContent = 'ONLINE (LOCAL)';
        bridgeText.className = 'bridge-status-text connected';
        return true;
      }
    } catch (e) {
      // Bridge not reachable
    }
    bridgeText.textContent = 'OFFLINE';
    bridgeText.className = 'bridge-status-text disconnected';
    return false;
  }

  // Modal Handlers
  if (bridgeConfigBtn) {
    bridgeConfigBtn.addEventListener('click', () => {
      bridgeModal.style.display = 'flex';
      bridgeTestResult.textContent = '';
    });
  }
  if (closeBridgeModal) {
    closeBridgeModal.addEventListener('click', () => {
      bridgeModal.style.display = 'none';
    });
  }
  if (resetBridgeBtn) {
    resetBridgeBtn.addEventListener('click', () => {
      bridgeUrl = 'http://localhost:8000';
      bridgeUrlInput.value = bridgeUrl;
      localStorage.removeItem('jarvis_bridge_url');
      bridgeTestResult.textContent = 'Reset to default: http://localhost:8000';
      bridgeTestResult.style.color = '#00f0ff';
      connectWebSocket();
    });
  }
  if (saveBridgeBtn) {
    saveBridgeBtn.addEventListener('click', () => {
      bridgeUrl = bridgeUrlInput.value.trim().replace(/\/+$/, '');
      localStorage.setItem('jarvis_bridge_url', bridgeUrl);
      bridgeModal.style.display = 'none';
      addLog(`BRIDGE CONFIGURATION SAVED: ${bridgeUrl}`, 'system');
      connectWebSocket();
    });
  }
  if (testBridgeBtn) {
    testBridgeBtn.addEventListener('click', async () => {
      bridgeTestResult.textContent = 'Testing link to local system...';
      bridgeTestResult.style.color = '#ffaa00';
      const target = bridgeUrlInput.value.trim().replace(/\/+$/, '');
      try {
        const resp = await fetch(`${target}/api/bridge/ping`, { mode: 'cors' });
        if (resp.ok) {
          bridgeTestResult.textContent = '✅ Success: Connected to JARVIS Hardware Bridge!';
          bridgeTestResult.style.color = '#00ffaa';
        } else {
          bridgeTestResult.textContent = `❌ Bridge returned error: ${resp.status}`;
          bridgeTestResult.style.color = '#ff3344';
        }
      } catch (err) {
        bridgeTestResult.textContent = '❌ Failed to reach bridge. Is python start.py running on your PC?';
        bridgeTestResult.style.color = '#ff3344';
      }
    });
  }

  // WebSocket Connection
  function connectWebSocket() {
    if (ws) {
      try { ws.close(); } catch(e) {}
    }

    const wsUrl = getBridgeWsUrl();
    checkBridgeStatus();

    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        connStatus.textContent = 'SYNCHRONIZED';
        connStatus.style.color = '#00f0ff';
        bridgeText.textContent = 'ONLINE (LOCAL)';
        bridgeText.className = 'bridge-status-text connected';
        addLog(`TELEMETRY LINK ESTABLISHED WITH LOCAL MACHINE [${bridgeUrl}]`, 'system');
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'telemetry' || msg.type === 'init') {
            updateTelemetry(msg.data || msg.telemetry);
          } else if (msg.type === 'status') {
            setUIState(msg.state);
          } else if (msg.type === 'response') {
            let audio = msg.audio_url;
            if (audio && !audio.startsWith('http')) {
              audio = `${bridgeUrl.replace(/\/+$/, '')}${audio}`;
            }
            speakJarvisResponse(msg.response_text, audio);
          }
        } catch (e) {
          console.error("WS Parse error:", e);
        }
      };

      ws.onclose = () => {
        connStatus.textContent = 'STANDALONE';
        connStatus.style.color = '#ffaa00';
        setTimeout(connectWebSocket, 5000);
      };

      ws.onerror = () => {
        connStatus.textContent = 'CLOUD ONLY';
        connStatus.style.color = '#ffaa00';
        bridgeText.textContent = 'NOT CONNECTED';
        bridgeText.className = 'bridge-status-text disconnected';
      };
    } catch (e) {
      console.warn("WebSocket init error:", e);
    }
  }

  connectWebSocket();

  // Send Command to Backend
  async function executeCommand(text) {
    if (!text || !text.trim()) return;
    initAudioContext();
    playSoundFX('ack');

    addLog(text, 'user');
    speechTag.textContent = 'DIRECTIVE DETECTED';
    speechContent.textContent = `"${text}"`;
    setUIState('THINKING');

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'command', text: text.trim() }));
    } else {
      // REST Fallback directly to local bridge
      try {
        const clean = bridgeUrl.trim().replace(/\/+$/, '');
        const resp = await fetch(`${clean}/api/command`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: text.trim() }),
          mode: 'cors'
        });
        const data = await resp.json();
        let audio = data.audio_url;
        if (audio && !audio.startsWith('http')) {
          audio = `${clean}${audio}`;
        }
        speakJarvisResponse(data.response_text, audio);
      } catch (e) {
        addLog(`BRIDGE DISPATCH ERROR: Local PC bridge unreachable. Ensure 'run_jarvis.bat' is active on your machine.`, 'system');
        speakJarvisResponse("I am unable to reach your local system bridge at this moment, Sir. Please ensure the JARVIS local core is active on your computer.", null);
        setUIState('STANDBY');
      }
    }
  }

  // Handle Form Submission
  commandForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = textInput.value;
    textInput.value = '';
    executeCommand(query);
  });

  // Rapid Protocol Buttons
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.getAttribute('data-cmd');
      executeCommand(cmd);
    });
  });

  // Wake Word & Continuous Voice Handling
  const wakeWordBtn = document.getElementById('wakeWordBtn');
  const wakeStatusText = document.getElementById('wakeStatusText');
  let wakeWordEnabled = false;
  let isSpeaking = false;

  jarvisAudio.addEventListener('play', () => {
    isSpeaking = true;
  });

  jarvisAudio.addEventListener('ended', () => {
    isSpeaking = false;
    setUIState('STANDBY');
    if (wakeWordEnabled) {
      setTimeout(() => {
        if (!isListening && !isSpeaking) startListening();
      }, 400);
    }
  });

  // Speech Recognition Setup
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      isListening = true;
      micBtn.classList.add('active');
      micLabel.textContent = wakeWordEnabled ? 'WAKE ACTIVE' : 'LISTENING...';
      setUIState('LISTENING');
      if (!wakeWordEnabled) playSoundFX('activate');

      // Connect mic stream to analyser if available
      navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        micStream = stream;
        if (audioCtx) {
          micAnalyser = audioCtx.createAnalyser();
          micAnalyser.fftSize = 128;
          const micSource = audioCtx.createMediaStreamSource(stream);
          micSource.connect(micAnalyser);
        }
      }).catch(() => {});
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      addLog(`SPEECH RECOGNIZED: "${transcript}"`, 'system');

      if (wakeWordEnabled) {
        // Check if wake word present
        const hasWakeWord = /\b(jarvis|hey jarvis|ok jarvis|hello jarvis)\b/i.test(transcript);
        if (hasWakeWord) {
          playSoundFX('activate');
          executeCommand(transcript);
        } else {
          // If in hands-free mode and heard speech without wake word, notify in log and resume
          addLog(`Ignored non-wake phrase: "${transcript}"`, 'system');
          stopListening();
        }
      } else {
        executeCommand(transcript);
      }
    };

    recognition.onerror = (event) => {
      console.warn("Speech error:", event.error);
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
      if (wakeWordEnabled && !isSpeaking) {
        setTimeout(() => {
          if (wakeWordEnabled && !isListening && !isSpeaking) {
            startListening();
          }
        }, 500);
      }
    };
  } else {
    micLabel.textContent = 'MIC (NOT SUPPORTED)';
    micBtn.disabled = true;
    if (wakeWordBtn) wakeWordBtn.disabled = true;
  }

  function startListening() {
    if (!recognition || isListening) return;
    initAudioContext();
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    if (jarvisAudio && !jarvisAudio.paused) {
      jarvisAudio.pause();
    }
    try {
      recognition.start();
    } catch (e) {
      // Already active
    }
  }

  function stopListening() {
    isListening = false;
    micBtn.classList.remove('active');
    micLabel.textContent = wakeWordEnabled ? 'WAKE ACTIVE' : 'PRESS TO SPEAK';
    if (stateText.textContent === 'LISTENING') {
      setUIState('STANDBY');
    }
    if (micStream) {
      micStream.getTracks().forEach(track => track.stop());
      micStream = null;
    }
  }

  micBtn.addEventListener('click', () => {
    if (isListening) {
      if (recognition) recognition.stop();
      stopListening();
    } else {
      startListening();
    }
  });

  if (wakeWordBtn) {
    wakeWordBtn.addEventListener('click', () => {
      wakeWordEnabled = !wakeWordEnabled;
      if (wakeWordEnabled) {
        wakeWordBtn.classList.add('active');
        wakeStatusText.textContent = 'WAKE WORD: ACTIVE';
        addLog('HANDS-FREE WAKE WORD DETECTOR ENGAGED (Say "Jarvis" or "Hey Jarvis").', 'system');
        startListening();
      } else {
        wakeWordBtn.classList.remove('active');
        wakeStatusText.textContent = 'WAKE WORD: OFF';
        addLog('HANDS-FREE WAKE WORD DETECTOR DISENGAGED.', 'system');
        stopListening();
      }
    });
  }

  // Keyboard shortcut: Spacebar toggles voice
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && document.activeElement !== textInput) {
      e.preventDefault();
      if (!isListening) {
        startListening();
      }
    }
  });

  // Volume slider
  volumeSlider.addEventListener('input', (e) => {
    jarvisAudio.volume = parseFloat(e.target.value);
  });
});
