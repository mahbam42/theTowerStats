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

  function initializeGlobalSearch() {
    const input = document.getElementById("global-search-input");
    const dropdown = document.getElementById("global-search-dropdown");
    if (!input || !dropdown) return;

    const endpoint = input.dataset.searchEndpoint;
    if (!endpoint) return;

    let activeIndex = -1;
    let activeResults = [];
    let debounceTimer = null;

    function clearResults() {
      dropdown.hidden = true;
      dropdown.innerHTML = "";
      activeResults = [];
      activeIndex = -1;
    }

    function renderResults(results) {
      activeResults = Array.isArray(results) ? results : [];
      activeIndex = -1;
      dropdown.innerHTML = "";

      if (!activeResults.length) {
        clearResults();
        return;
      }

      for (let idx = 0; idx < activeResults.length; idx += 1) {
        const row = activeResults[idx];
        const a = document.createElement("a");
        a.href = row.url;
        a.className = "search-item";
        a.setAttribute("role", "option");
        a.dataset.index = String(idx);
        if (row.external) {
          a.dataset.external = "1";
          a.target = "_blank";
          a.rel = "noopener noreferrer";
        }

        const title = document.createElement("div");
        title.className = "search-item-title";
        title.textContent = row.title || "";
        a.appendChild(title);

        if (row.subtitle) {
          const subtitle = document.createElement("div");
          subtitle.className = "search-item-subtitle";
          subtitle.textContent = row.subtitle;
          a.appendChild(subtitle);
        }

        a.addEventListener("mousemove", () => setActiveIndex(idx));
        dropdown.appendChild(a);
      }

      dropdown.hidden = false;
    }

    function setActiveIndex(nextIndex) {
      const max = activeResults.length - 1;
      const clamped = Math.max(-1, Math.min(max, nextIndex));
      activeIndex = clamped;
      for (const node of dropdown.querySelectorAll(".search-item")) {
        node.classList.remove("is-selected");
      }
      if (activeIndex >= 0) {
        const selected = dropdown.querySelector(`.search-item[data-index="${activeIndex}"]`);
        if (selected) selected.classList.add("is-selected");
      }
    }

    async function fetchResults(query) {
      const url = new URL(endpoint, window.location.origin);
      url.searchParams.set("q", query);
      const resp = await fetch(url.toString(), {
        method: "GET",
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!resp.ok) return [];
      const payload = await resp.json();
      return payload && Array.isArray(payload.results) ? payload.results : [];
    }

    function scheduleSearch() {
      const query = input.value.trim();
      if (debounceTimer) window.clearTimeout(debounceTimer);

      if (!query) {
        clearResults();
        return;
      }

      debounceTimer = window.setTimeout(async () => {
        try {
          const results = await fetchResults(query);
          renderResults(results);
        } catch (_err) {
          clearResults();
        }
      }, 150);
    }

    input.addEventListener("input", scheduleSearch);
    input.addEventListener("focus", scheduleSearch);
    document.addEventListener("click", (event) => {
      if (event.target === input) return;
      if (dropdown.contains(event.target)) return;
      clearResults();
    });

    input.addEventListener("keydown", (event) => {
      if (dropdown.hidden) return;
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveIndex(activeIndex + 1);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIndex(activeIndex - 1);
      } else if (event.key === "Enter") {
        if (activeIndex >= 0) {
          const selected = dropdown.querySelector(`.search-item[data-index="${activeIndex}"]`);
          if (selected) {
            event.preventDefault();
            if (selected.dataset.external === "1") {
              window.open(selected.href, "_blank", "noopener,noreferrer");
              clearResults();
              return;
            }
            window.location.href = selected.href;
          }
        }
      } else if (event.key === "Escape") {
        clearResults();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      () => {
        initializeFoundation();
        initializeGlobalSearch();
      },
      { once: true }
    );
    return;
  }

  initializeFoundation();
  initializeGlobalSearch();
})();
