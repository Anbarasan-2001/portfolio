/* =========================================================================
   form.js — contact form: client-side validation + animated error/success
   states, submitted over fetch() to the Django view (see Milestone 6).
   ========================================================================= */
(function () {
  "use strict";

  const form = document.querySelector("[data-contact-form]");
  if (!form) return;

  const status = form.querySelector("[data-form-status]");
  const submitBtn = form.querySelector("[type=submit]");
  const hasGSAP = typeof gsap !== "undefined";

  function getCookie(name) {
    const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return m ? m.pop() : "";
  }

  function showError(field, message) {
    const wrap = field.closest("[data-field]") || field.parentElement;
    let err = wrap.querySelector("[data-field-error]");
    if (!err) {
      err = document.createElement("p");
      err.setAttribute("data-field-error", "");
      err.className = "mt-1 text-sm text-red-500";
      wrap.appendChild(err);
    }
    err.textContent = message;
    field.classList.add("border-red-500");
    if (hasGSAP) {
      gsap.fromTo(field, { x: -6 }, { x: 0, duration: 0.4, ease: "elastic.out(1, 0.4)" });
    }
  }

  function clearError(field) {
    const wrap = field.closest("[data-field]") || field.parentElement;
    const err = wrap.querySelector("[data-field-error]");
    if (err) err.textContent = "";
    field.classList.remove("border-red-500");
  }

  function validate() {
    let ok = true;
    form.querySelectorAll("[required]").forEach(function (field) {
      const val = (field.value || "").trim();
      if (!val) {
        showError(field, "This field is required.");
        ok = false;
      } else if (field.type === "email" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(val)) {
        showError(field, "Please enter a valid email address.");
        ok = false;
      } else {
        clearError(field);
      }
    });
    return ok;
  }

  // Clear field errors as the user fixes them.
  form.querySelectorAll("input, textarea").forEach(function (field) {
    field.addEventListener("input", function () {
      if (field.value.trim()) clearError(field);
    });
  });

  function setStatus(message, kind) {
    if (!status) return;
    status.textContent = message;
    status.className =
      "mt-4 text-sm font-medium " +
      (kind === "success" ? "text-emerald-500" : "text-red-500");
    if (hasGSAP) {
      gsap.fromTo(status, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.5 });
    }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!validate()) return;

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.dataset.label = submitBtn.textContent;
      submitBtn.textContent = "Sending...";
    }

    fetch(form.action, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new FormData(form),
    })
      .then((r) => r.json())
      .then(function (data) {
        if (data.success) {
          form.reset();
          setStatus(data.message || "Thanks! Your message has been sent.", "success");
          if (hasGSAP) {
            gsap.fromTo(
              form,
              { scale: 0.98 },
              { scale: 1, duration: 0.5, ease: "elastic.out(1, 0.5)" }
            );
          }
        } else {
          // Field-level errors from Django.
          if (data.errors) {
            Object.keys(data.errors).forEach(function (name) {
              const field = form.querySelector("[name=" + name + "]");
              if (field) showError(field, data.errors[name][0].message || data.errors[name][0]);
            });
          }
          setStatus(data.message || "Please fix the errors above.", "error");
        }
      })
      .catch(function () {
        setStatus("Something went wrong. Please try again later.", "error");
      })
      .finally(function () {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = submitBtn.dataset.label || "Send Message";
        }
      });
  });
})();
