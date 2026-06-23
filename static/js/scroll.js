/* =========================================================================
   scroll.js — Locomotive Scroll <-> GSAP ScrollTrigger integration, plus
   navbar scroll state, scroll-progress bar, active-section highlighting, and
   smooth anchor navigation.

   Exposes a small global API on `window.PORTFOLIO`:
     .loco          -> the Locomotive Scroll instance (or null)
     .reducedMotion -> boolean
     .scrollTo(el)  -> smooth-scroll to an element/selector
     .refresh()     -> recompute Locomotive + ScrollTrigger (call after DOM/img
                       changes, e.g. project filtering)
   ========================================================================= */
(function () {
  "use strict";

  const reducedMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const scrollEl = document.querySelector("[data-scroll-container]");
  const hasGSAP = typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined";
  const hasLoco = typeof LocomotiveScroll !== "undefined";

  const api = {
    loco: null,
    reducedMotion: reducedMotion,
    scrollTo: function (target) {
      const el = typeof target === "string" ? document.querySelector(target) : target;
      if (!el) return;
      if (api.loco) {
        api.loco.scrollTo(el);
      } else {
        el.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
      }
    },
    refresh: function () {
      if (api.loco) api.loco.update();
      if (hasGSAP) ScrollTrigger.refresh();
    },
  };
  window.PORTFOLIO = api;

  if (hasGSAP) gsap.registerPlugin(ScrollTrigger);

  // ---------------------------------------------------------------- Locomotive
  // Smooth scrolling is disabled when motion is reduced or on touch devices,
  // where it tends to feel laggy — the page then scrolls natively.
  if (hasLoco && scrollEl && !reducedMotion) {
    api.loco = new LocomotiveScroll({
      el: scrollEl,
      smooth: true,
      lerp: 0.08,
      multiplier: 1,
      smartphone: { smooth: false },
      tablet: { smooth: false },
    });

    // Keep ScrollTrigger in sync with Locomotive's virtual scroll.
    if (hasGSAP) {
      api.loco.on("scroll", ScrollTrigger.update);

      ScrollTrigger.scrollerProxy(scrollEl, {
        scrollTop(value) {
          return arguments.length
            ? api.loco.scrollTo(value, { duration: 0, disableLerp: true })
            : api.loco.scroll.instance.scroll.y;
        },
        getBoundingClientRect() {
          return {
            top: 0,
            left: 0,
            width: window.innerWidth,
            height: window.innerHeight,
          };
        },
        pinType: scrollEl.style.transform ? "transform" : "fixed",
      });

      // All ScrollTrigger animations should use Locomotive's container.
      ScrollTrigger.defaults({ scroller: scrollEl });
      ScrollTrigger.addEventListener("refresh", () => api.loco.update());
      ScrollTrigger.refresh();
    }
  }

  // ------------------------------------------------------- Scroll-driven chrome
  const navbar = document.getElementById("navbar");
  const progress = document.getElementById("scroll-progress");
  const navLinks = Array.from(document.querySelectorAll("[data-nav-link]"));
  const sections = navLinks
    .map((l) => document.getElementById(l.dataset.navLink))
    .filter(Boolean);

  // The navbar already has a glass background; on scroll we just add depth.
  const NAV_SCROLLED_CLASSES = ["shadow-lg", "shadow-black/5"];

  function onScroll(y) {
    // Navbar style change after a little scrolling.
    if (navbar) {
      if (y > 40) navbar.classList.add(...NAV_SCROLLED_CLASSES);
      else navbar.classList.remove(...NAV_SCROLLED_CLASSES);
    }
    // Progress bar.
    if (progress) {
      const doc = document.documentElement;
      const max = (scrollEl ? scrollEl.scrollHeight : doc.scrollHeight) - window.innerHeight;
      const pct = max > 0 ? Math.min(100, (y / max) * 100) : 0;
      progress.style.width = pct + "%";
    }
    // Active section highlight.
    if (sections.length) {
      const mid = y + window.innerHeight * 0.35;
      let activeId = sections[0].id;
      for (const sec of sections) {
        if (sec.offsetTop <= mid) activeId = sec.id;
      }
      navLinks.forEach((link) => {
        link.classList.toggle("text-accent", link.dataset.navLink === activeId);
      });
    }
  }

  // Drive `onScroll` from Locomotive when present, otherwise native scroll.
  if (api.loco) {
    api.loco.on("scroll", (obj) => onScroll(obj.scroll.y));
  } else {
    window.addEventListener("scroll", () => onScroll(window.scrollY), { passive: true });
    onScroll(window.scrollY);
  }

  // ---------------------------------------------------------- Anchor navigation
  document.querySelectorAll("[data-nav]").forEach(function (link) {
    link.addEventListener("click", function (e) {
      const href = link.getAttribute("href") || "";
      const hashIndex = href.indexOf("#");
      if (hashIndex === -1) return;
      const id = href.slice(hashIndex + 1);
      const target = id ? document.getElementById(id) : null;
      // Only hijack if the target exists on THIS page; otherwise let the
      // browser navigate (e.g. from a detail page back to the homepage).
      if (target) {
        e.preventDefault();
        api.scrollTo(target);
      }
    });
  });

  // Recompute once everything (fonts/images) has loaded.
  window.addEventListener("load", api.refresh);
})();
