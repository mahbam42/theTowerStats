(() => {
  function initializeFoundation() {
    if (typeof window.$ === "undefined") {
      return;
    }

    if (typeof window.$(document).foundation !== "function") {
      return;
    }

    window.$(document).foundation();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeFoundation, { once: true });
    return;
  }

  initializeFoundation();
})();
