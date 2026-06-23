/* =========================================================================
   animations.js — all GSAP/ScrollTrigger + AOS driven motion.

   Shared timing/easing defaults live here so every animation feels
   consistent. Everything is guarded with existence checks, so the file is
   safe to load on pages that don't have a given section.
   ========================================================================= */
(function () {
  "use strict";

  const P = window.PORTFOLIO || { reducedMotion: false, refresh: function () {} };
  const hasGSAP = typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined";

  // -------------------------------------------------- Shared motion language
  const EASE = "power3.out";
  const DURATION = 0.9;
  const STAGGER = 0.12;

  // Hide preloader regardless of what else happens below.
  function hidePreloader() {
    const pre = document.getElementById("preloader");
    if (pre) pre.classList.add("is-hidden");
  }

  // If we can't / shouldn't animate, just show everything and bail early.
  if (!hasGSAP || P.reducedMotion) {
    window.addEventListener("load", hidePreloader);
    initAOS(); // AOS respects reduced motion via its own option below
    return;
  }

  gsap.registerPlugin(ScrollTrigger);
  gsap.defaults({ ease: EASE, duration: DURATION });

  // Mark root so CSS can pre-hide [data-anim] elements (avoids flash).
  document.documentElement.classList.add("anim-ready");

  document.addEventListener("DOMContentLoaded", run);
  if (document.readyState !== "loading") run();

  let started = false;
  function run() {
    if (started) return;
    started = true;

    heroIntro();
    typewriter();
    scrollReveals();
    skillBars();
    timeline();
    staggerGroups();
    projectFilter();
    pageTransitions();
    initAOS();

    window.addEventListener("load", function () {
      hidePreloader();
      P.refresh();
    });
    // Fallback: if `load` already fired, still hide the preloader.
    setTimeout(hidePreloader, 1500);
  }

  // --------------------------------------------------------------- Hero intro
  function heroIntro() {
    const items = gsap.utils.toArray("[data-hero]");
    if (!items.length) return;
    gsap.fromTo(
      items,
      { y: 40, opacity: 0 },
      { y: 0, opacity: 1, duration: 1, stagger: 0.15, delay: 0.2 }
    );
  }

  // ----------------------------------------------- Generic scroll-in reveals
  // Usage: <div data-anim="fade-up" data-anim-delay="0.2">
  const PRESETS = {
    fade: { opacity: 0 },
    "fade-up": { opacity: 0, y: 50 },
    "fade-down": { opacity: 0, y: -50 },
    "fade-left": { opacity: 0, x: -50 },
    "fade-right": { opacity: 0, x: 50 },
    zoom: { opacity: 0, scale: 0.9 },
  };

  function scrollReveals() {
    gsap.utils.toArray("[data-anim]").forEach(function (el) {
      const preset = PRESETS[el.dataset.anim] || PRESETS["fade-up"];
      const delay = parseFloat(el.dataset.animDelay || "0");
      gsap.fromTo(
        el,
        preset,
        {
          opacity: 1, x: 0, y: 0, scale: 1, delay: delay,
          scrollTrigger: { trigger: el, start: "top 85%" },
        }
      );
    });
  }

  // --------------------------------------------------------------- Skill bars
  // Usage: <div data-skill data-percent="85"><span class="skill-bar__fill"></span></div>
  function skillBars() {
    gsap.utils.toArray("[data-skill]").forEach(function (bar) {
      const fill = bar.querySelector(".skill-bar__fill");
      const pct = bar.dataset.percent || "0";
      if (!fill) return;
      ScrollTrigger.create({
        trigger: bar,
        start: "top 85%",
        once: true,
        onEnter: function () {
          fill.style.width = pct + "%";
          const label = bar.querySelector("[data-skill-count]");
          if (label) {
            const obj = { v: 0 };
            gsap.to(obj, {
              v: parseInt(pct, 10),
              duration: 1.2,
              ease: EASE,
              onUpdate: function () {
                label.textContent = Math.round(obj.v) + "%";
              },
            });
          }
        },
      });
    });
  }

  // ------------------------------------------------------- Experience timeline
  function timeline() {
    const line = document.querySelector("[data-timeline-line]");
    if (line) {
      gsap.to(line, {
        scaleY: 1,
        ease: "none",
        scrollTrigger: {
          trigger: line,
          start: "top 80%",
          end: "bottom 60%",
          scrub: true,
        },
      });
    }
    gsap.utils.toArray("[data-timeline-item]").forEach(function (item, i) {
      gsap.fromTo(
        item,
        { opacity: 0, y: 40 },
        {
          opacity: 1, y: 0,
          scrollTrigger: { trigger: item, start: "top 85%" },
        }
      );
    });
  }

  // ----------------------------------------- Staggered groups (icon/card grids)
  // Usage: <div data-stagger> ...children... </div>
  function staggerGroups() {
    gsap.utils.toArray("[data-stagger]").forEach(function (group) {
      const children = group.children;
      if (!children.length) return;
      gsap.fromTo(
        children,
        { opacity: 0, y: 40 },
        {
          opacity: 1, y: 0, stagger: STAGGER,
          scrollTrigger: { trigger: group, start: "top 80%" },
        }
      );
    });
  }

  // --------------------------------------------------- Project category filter
  // Usage: filter buttons [data-filter="slug"], cards [data-project]
  //        with data-category="slug" data-tech="a,b,c".
  function projectFilter() {
    const buttons = gsap.utils.toArray("[data-filter]");
    const cards = gsap.utils.toArray("[data-project]");
    if (!buttons.length || !cards.length) return;

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        const filter = btn.dataset.filter;
        buttons.forEach((b) => b.classList.remove("is-active", "bg-accent", "text-white"));
        btn.classList.add("is-active", "bg-accent", "text-white");

        cards.forEach(function (card) {
          const cat = card.dataset.category || "";
          const tech = (card.dataset.tech || "").split(",");
          const match = filter === "all" || cat === filter || tech.includes(filter);
          if (match) {
            card.style.display = "";
            gsap.fromTo(card, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4 });
          } else {
            card.style.display = "none";
          }
        });
        P.refresh();
      });
    });
  }

  // -------------------------------------------------------------- Typewriter
  // Usage: <span data-typewriter>Text to type</span>
  function typewriter() {
    gsap.utils.toArray("[data-typewriter]").forEach(function (el) {
      const full = el.textContent.trim();
      el.textContent = "";
      el.style.opacity = 1;
      let i = 0;
      const speed = 45;
      // Slight delay so it follows the hero intro.
      setTimeout(function tick() {
        if (i <= full.length) {
          el.textContent = full.slice(0, i);
          i++;
          setTimeout(tick, speed);
        }
      }, 600);
    });
  }

  // ---------------------------------------------------- Page-load transitions
  // Fade the page out before navigating to another internal page, for a
  // smooth "SPA-like" feel. Anchor (#) links are handled by scroll.js.
  function pageTransitions() {
    document.addEventListener("click", function (e) {
      const link = e.target.closest("a");
      if (!link) return;
      const href = link.getAttribute("href");
      if (
        !href ||
        href.startsWith("#") ||
        href.startsWith("mailto:") ||
        href.startsWith("tel:") ||
        link.target === "_blank" ||
        link.hasAttribute("download") ||
        link.hostname !== window.location.hostname ||
        link.hasAttribute("data-nav") // on-page anchor nav
      ) {
        return;
      }
      e.preventDefault();
      gsap.to("body", {
        opacity: 0,
        duration: 0.35,
        onComplete: function () {
          window.location.href = href;
        },
      });
    });

    // Fade back in when returning via back/forward cache.
    window.addEventListener("pageshow", function () {
      gsap.to("body", { opacity: 1, duration: 0.35 });
    });
  }

  // ---------------------------------------------------------------------- AOS
  function initAOS() {
    if (typeof AOS === "undefined") return;
    AOS.init({
      once: true,
      duration: 700,
      easing: "ease-out-cubic",
      offset: 80,
      disable: function () {
        return (
          window.matchMedia &&
          window.matchMedia("(prefers-reduced-motion: reduce)").matches
        );
      },
    });
    // Bridge: Locomotive uses transforms, so window 'scroll' doesn't fire.
    // Re-dispatch it (throttled by AOS internally) so AOS re-checks positions.
    if (P.loco) {
      P.loco.on("scroll", function () {
        window.dispatchEvent(new Event("scroll"));
      });
    }
  }
})();
