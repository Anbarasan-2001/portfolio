/* =========================================================================
   carousel.js — auto-advancing testimonials carousel with dot navigation.
   Crossfades slides with GSAP when available, else toggles visibility.
   ========================================================================= */
(function () {
  "use strict";

  const carousel = document.querySelector("[data-carousel]");
  if (!carousel) return;

  const slides = Array.from(carousel.querySelectorAll("[data-carousel-slide]"));
  if (slides.length < 2) return;

  const dots = Array.from(document.querySelectorAll("[data-carousel-dot]"));
  const hasGSAP = typeof gsap !== "undefined";
  const INTERVAL = 6000;
  let current = 0;
  let timer;

  function show(index) {
    slides.forEach(function (slide, i) {
      if (i === index) {
        slide.classList.remove("hidden");
        if (hasGSAP) gsap.fromTo(slide, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.6 });
      } else {
        slide.classList.add("hidden");
      }
    });
    dots.forEach(function (dot, i) {
      dot.classList.toggle("bg-accent", i === index);
      dot.classList.toggle("bg-slate-300", i !== index);
      dot.classList.toggle("dark:bg-white/20", i !== index);
    });
    current = index;
  }

  function next() {
    show((current + 1) % slides.length);
  }

  function start() {
    stop();
    timer = setInterval(next, INTERVAL);
  }
  function stop() {
    if (timer) clearInterval(timer);
  }

  dots.forEach(function (dot, i) {
    dot.addEventListener("click", function () {
      show(i);
      start(); // reset timer on manual nav
    });
  });

  // Pause on hover for readability.
  carousel.addEventListener("mouseenter", stop);
  carousel.addEventListener("mouseleave", start);

  show(0);
  start();
})();
