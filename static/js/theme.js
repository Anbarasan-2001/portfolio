/* =========================================================================
   theme.js — mobile menu and small global helpers.
   Loaded first; sets up UI chrome that doesn't depend on GSAP/Locomotive.
   The site is dark-only; the `dark` class is set on <html> in the template.
   ========================================================================= */
(function () {
  "use strict";

  const root = document.documentElement;
  root.classList.add("js");

  // ----- Footer year -----
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

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
