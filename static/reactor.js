/**
 * J.A.R.V.I.S. Arc Reactor Visualizer & Talking Model Engine
 * 60FPS Canvas Animation with Audio-Reactive Pulse & State Machine
 */

class ArcReactor {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.state = 'STANDBY'; // STANDBY | LISTENING | THINKING | SPEAKING
    
    // Rotation angles
    this.angle1 = 0;
    this.angle2 = 0;
    this.angle3 = 0;
    
    // Audio analysis data
    this.audioData = new Uint8Array(64);
    this.audioLevel = 0;
    this.smoothedLevel = 0;

    // Pulse timing
    this.pulseTime = 0;
    
    // DPR handling
    this.resize();
    window.addEventListener('resize', () => this.resize());
    
    // Animation loop
    this.render = this.render.bind(this);
    requestAnimationFrame(this.render);
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.width = rect.width;
    this.height = rect.height;
    this.cx = this.width / 2;
    this.cy = this.height / 2;
    this.baseRadius = Math.min(this.width, this.height) * 0.38;
  }

  setState(newState) {
    this.state = newState;
  }

  updateAudioData(analyser) {
    if (!analyser) {
      this.audioLevel = 0;
      return;
    }
    analyser.getByteFrequencyData(this.audioData);
    let sum = 0;
    for (let i = 0; i < this.audioData.length; i++) {
      sum += this.audioData[i];
    }
    this.audioLevel = (sum / this.audioData.length) / 255;
  }

  render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    // Smooth audio reactivity
    this.smoothedLevel += (this.audioLevel - this.smoothedLevel) * 0.25;
    this.pulseTime += 0.03;

    // Determine colors based on state
    let primaryColor = '#00f0ff';
    let glowColor = 'rgba(0, 240, 255, ';
    let speedMult = 1.0;

    if (this.state === 'LISTENING') {
      primaryColor = '#ffaa00';
      glowColor = 'rgba(255, 170, 0, ';
      speedMult = 1.6;
    } else if (this.state === 'THINKING') {
      primaryColor = '#00d4ff';
      glowColor = 'rgba(0, 212, 255, ';
      speedMult = 3.5;
    } else if (this.state === 'SPEAKING') {
      primaryColor = '#00ffcc';
      glowColor = 'rgba(0, 255, 204, ';
      speedMult = 2.0;
    }

    // Update rotation speeds
    this.angle1 += 0.008 * speedMult;
    this.angle2 -= 0.012 * speedMult;
    this.angle3 += 0.005 * speedMult;

    const pulse = Math.sin(this.pulseTime) * 0.05 + 1;
    const dynamicLevel = Math.max(this.smoothedLevel, (this.state === 'SPEAKING' ? 0.35 : 0.05));
    const responsiveRadius = this.baseRadius * (1 + dynamicLevel * 0.25);

    ctx.save();
    ctx.translate(this.cx, this.cy);

    // 1. Outer Holographic Equalizer / Wave Bars
    this.drawEqualizerRings(ctx, responsiveRadius, glowColor, primaryColor);

    // 2. Outer Concentric Tech Rings
    this.drawOuterRing(ctx, this.baseRadius * 1.15, this.angle1, primaryColor, glowColor);
    this.drawNotchedRing(ctx, this.baseRadius * 0.95, this.angle2, primaryColor, glowColor);

    // 3. Triangle / Geometric Arc Core Structure
    this.drawCoreHousing(ctx, this.baseRadius * 0.72, this.angle3, primaryColor, glowColor);

    // 4. Inner Glowing Arc Reactor Core
    this.drawReactorCore(ctx, this.baseRadius * 0.45 * pulse, dynamicLevel, primaryColor, glowColor);

    ctx.restore();

    requestAnimationFrame(this.render);
  }

  drawOuterRing(ctx, radius, angle, primaryColor, glowColor) {
    ctx.save();
    ctx.rotate(angle);

    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    ctx.strokeStyle = glowColor + '0.25)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Segmented arcs
    const segments = 12;
    const segAngle = (Math.PI * 2) / segments;
    for (let i = 0; i < segments; i++) {
      ctx.beginPath();
      ctx.arc(0, 0, radius, i * segAngle, i * segAngle + segAngle * 0.45);
      ctx.strokeStyle = primaryColor;
      ctx.lineWidth = 4;
      ctx.shadowColor = primaryColor;
      ctx.shadowBlur = 10;
      ctx.stroke();
    }
    ctx.restore();
  }

  drawNotchedRing(ctx, radius, angle, primaryColor, glowColor) {
    ctx.save();
    ctx.rotate(angle);

    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    ctx.strokeStyle = glowColor + '0.4)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Notches & tick marks
    const ticks = 48;
    for (let i = 0; i < ticks; i++) {
      const a = (i * Math.PI * 2) / ticks;
      const len = (i % 4 === 0) ? 10 : 4;
      ctx.beginPath();
      ctx.moveTo(Math.cos(a) * (radius - len), Math.sin(a) * (radius - len));
      ctx.lineTo(Math.cos(a) * radius, Math.sin(a) * radius);
      ctx.strokeStyle = (i % 4 === 0) ? primaryColor : glowColor + '0.4)';
      ctx.lineWidth = (i % 4 === 0) ? 2 : 1;
      ctx.stroke();
    }
    ctx.restore();
  }

  drawCoreHousing(ctx, radius, angle, primaryColor, glowColor) {
    ctx.save();
    ctx.rotate(angle);

    // Outer octagon / polygon
    const points = 10;
    ctx.beginPath();
    for (let i = 0; i < points; i++) {
      const a = (i * Math.PI * 2) / points;
      const x = Math.cos(a) * radius;
      const y = Math.sin(a) * radius;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.strokeStyle = primaryColor;
    ctx.lineWidth = 2.5;
    ctx.shadowColor = primaryColor;
    ctx.shadowBlur = 8;
    ctx.stroke();

    // Coils around the reactor
    for (let i = 0; i < points; i++) {
      const a = (i * Math.PI * 2) / points;
      const cx = Math.cos(a) * (radius * 0.85);
      const cy = Math.sin(a) * (radius * 0.85);

      ctx.beginPath();
      ctx.arc(cx, cy, 6, 0, Math.PI * 2);
      ctx.fillStyle = primaryColor;
      ctx.shadowColor = primaryColor;
      ctx.shadowBlur = 12;
      ctx.fill();
    }
    ctx.restore();
  }

  drawEqualizerRings(ctx, baseR, glowColor, primaryColor) {
    const barCount = 32;
    const startR = baseR * 1.05;

    for (let i = 0; i < barCount; i++) {
      const a = (i * Math.PI * 2) / barCount;
      const freqIdx = i % this.audioData.length;
      const freqVal = this.audioData[freqIdx] || 0;
      
      let barLen = 6 + (freqVal / 255) * 45;
      if (this.state === 'STANDBY') {
        barLen = 4 + Math.sin(this.pulseTime * 2 + i) * 3;
      }

      const x1 = Math.cos(a) * startR;
      const y1 = Math.sin(a) * startR;
      const x2 = Math.cos(a) * (startR + barLen);
      const y2 = Math.sin(a) * (startR + barLen);

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = (freqVal > 140 || this.state === 'SPEAKING') ? primaryColor : glowColor + '0.5)';
      ctx.lineWidth = 3;
      ctx.stroke();
    }
  }

  drawReactorCore(ctx, radius, intensity, primaryColor, glowColor) {
    // Glowing Core Radial Gradient
    const grad = ctx.createRadialGradient(0, 0, 2, 0, 0, radius);
    grad.addColorStop(0, '#ffffff');
    grad.addColorStop(0.3, primaryColor);
    grad.addColorStop(0.7, glowColor + '0.5)');
    grad.addColorStop(1, 'transparent');

    ctx.beginPath();
    ctx.arc(0, 0, radius * (1 + intensity * 0.4), 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.shadowColor = primaryColor;
    ctx.shadowBlur = 25 + intensity * 40;
    ctx.fill();

    // Central Stark Core emblem
    ctx.beginPath();
    ctx.arc(0, 0, radius * 0.35, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = '#ffffff';
    ctx.shadowBlur = 15;
    ctx.fill();
  }
}

window.ArcReactor = ArcReactor;
