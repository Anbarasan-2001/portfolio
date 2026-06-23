/* =========================================================================
   theme.js — dark/light theme toggle, mobile menu, and small global helpers.
   Loaded first; sets up UI chrome that doesn't depend on GSAP/Locomotive.
   ========================================================================= */
(function () {
  "use strict";

  const root = document.documentElement;
  root.classList.add("js");

  // ----- Footer year -----
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ----- Theme toggle -----
  const toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      const isDark = root.classList.toggle("dark");
      try {
        localStorage.setItem("theme", isDark ? "dark" : "light");
      } catch (e) {}
      // Let other modules react (e.g. recolor canvas particles).
      document.dispatchEvent(
        new CustomEvent("themechange", { detail: { dark: isDark } })
      );
    });
  }

  // ----- Mobile menu -----
  const navToggle = document.getElementById("nav-toggle");
  const mobileMenu = document.getElementById("mobile-menu");
  if (navToggle && mobileMenu) {
    navToggle.addEventListener("click", function () {
      mobileMenu.classList.toggle("hidden");
    });
    // Close the menu when a link inside it is tapped.
    mobileMenu.querySelectorAll("[data-mobile-link]").forEach(function (link) {
      link.addEventListener("click", function () {
        mobileMenu.classList.add("hidden");
      });
    });
  }
})();
