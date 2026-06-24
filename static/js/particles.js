/* =========================================================================
   particles.js — animated particle network covering the full hero section.
   Pauses when off-screen / reduced motion, and resizes robustly
   (measures its host element, and re-measures on load + resize). No deps.
   ========================================================================= */
(function () {
  "use strict";

  const canvas = document.getElementById("hero-particles");
  if (!canvas) return;

  const reduced =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) return;

  const ctx = canvas.getContext("2d");
  const host = canvas.parentElement || canvas; // the hero <section>
  const LINK_DIST = 150;
  let w = 0, h = 0, particles = [], raf = null, running = true;

  function accentColor() {
    return "rgba(96, 165, 250, "; /* blue-400 — site is dark-only */
  }

  // Size the canvas to its host element (the full hero), guarding against a
  // zero measurement (which would leave the default 300x150 canvas).
  function size() {
    const rect = host.getBoundingClientRect();
    w = Math.max(1, Math.round(rect.width || window.innerWidth));
    h = Math.max(1, Math.round(rect.height || window.innerHeight));
    canvas.width = w;
    canvas.height = h;
  }

  // Particle count scales with area so the network fills any screen size.
  function spawn() {
    const n = Math.max(40, Math.min(140, Math.round((w * h) / 14000)));
    particles = [];
    for (let i = 0; i < n; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        r: Math.random() * 2.2 + 1.1,
      });
    }
  }

  function init() {
    size();
    spawn();
  }

  function step() {
    if (!running) return;
    ctx.clearRect(0, 0, w, h);
    const base = accentColor();

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > w) p.vx *= -1;
      if (p.y < 0 || p.y > h) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = base + "1)";
      ctx.fill();

      for (let j = i + 1; j < particles.length; j++) {
        const q = particles[j];
        const dx = p.x - q.x, dy = p.y - q.y;
        const dist = dx * dx + dy * dy;
        if (dist < LINK_DIST * LINK_DIST) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(q.x, q.y);
          ctx.strokeStyle =
            base + (0.45 * (1 - dist / (LINK_DIST * LINK_DIST))).toFixed(3) + ")";
          ctx.lineWidth = 1.2;
          ctx.stroke();
        }
      }
    }
    raf = requestAnimationFrame(step);
  }

  function start() {
    if (raf) cancelAnimationFrame(raf);
    running = true;
    step();
  }

  // Pause when the hero scrolls out of view (saves CPU/battery).
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      running = entries[0].isIntersecting;
      if (running) start();
      else if (raf) cancelAnimationFrame(raf);
    }).observe(canvas);
  }

  // Re-measure when the host element changes size (fonts/layout settling).
  if ("ResizeObserver" in window) {
    new ResizeObserver(function () {
      init();
    }).observe(host);
  }

  window.addEventListener("resize", init);
  window.addEventListener("load", function () {
    init();
    start();
  });

  init();
  start();
})();
