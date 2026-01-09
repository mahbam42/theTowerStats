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

  function initializeBattleReportModal() {
    const modal = document.getElementById("battle-report-modal");
    if (!modal) return;

    const endpointTemplate = modal.dataset.endpointTemplate;
    const chartsUrl = modal.dataset.chartsUrl;
    if (!endpointTemplate) return;

    const titleEl = document.getElementById("battle-report-modal-title");
    const rawEl = document.getElementById("battle-report-raw");
    const metricsEl = document.getElementById("battle-report-metrics");
    const noteEl = document.getElementById("battle-report-order-note");
    const prevBtn = document.getElementById("battle-report-prev");
    const nextBtn = document.getElementById("battle-report-next");
    const closeBtn = document.getElementById("battle-report-close");

    const state = {
      order: [],
      index: -1,
      contextNote: "",
    };

    function buildEndpoint(runId) {
      return endpointTemplate.replace("/0/", `/${runId}/`);
    }

    function buildChartUrl(chartId) {
      if (!chartsUrl) return null;
      const url = new URL(chartsUrl, window.location.origin);
      const form = document.getElementById("chart-context-form");
      const getFormValue = (name) => {
        if (!form || !form.elements[name]) return null;
        const value = form.elements[name].value;
        return value === "" ? null : value;
      };
      url.searchParams.set("charts", chartId);
      url.searchParams.set("event_shift", "all");
      const granularity = getFormValue("granularity");
      const tier = getFormValue("tier");
      const preset = getFormValue("preset");
      const includeTournaments = form && form.elements["include_tournaments"] ? form.elements["include_tournaments"].checked : null;
      const windowKind = getFormValue("window_kind");
      const windowN = getFormValue("window_n");
      const movingAverage = getFormValue("moving_average_window");
      if (granularity) url.searchParams.set("granularity", granularity);
      if (tier) url.searchParams.set("tier", tier);
      if (preset) url.searchParams.set("preset", preset);
      if (includeTournaments) url.searchParams.set("include_tournaments", "on");
      if (windowKind) url.searchParams.set("window_kind", windowKind);
      if (windowN) url.searchParams.set("window_n", windowN);
      if (movingAverage) url.searchParams.set("moving_average_window", movingAverage);
      return url.toString();
    }

    function openModal() {
      modal.classList.add("is-open");
      modal.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
    }

    function closeModal() {
      modal.classList.remove("is-open");
      modal.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }

    function setNavState() {
      if (!prevBtn || !nextBtn) return;
      prevBtn.disabled = state.index <= 0;
      nextBtn.disabled = state.index < 0 || state.index >= state.order.length - 1;
    }

    function setLoading() {
      if (titleEl) titleEl.textContent = "Battle Report";
      if (rawEl) rawEl.textContent = "Loading...";
      if (metricsEl) metricsEl.innerHTML = "";
    }

    function setError(message) {
      if (rawEl) rawEl.textContent = message;
    }

    function renderMetrics(metrics) {
      if (!metricsEl) return;
      metricsEl.innerHTML = "";
      for (const metric of metrics || []) {
        const row = document.createElement("div");
        row.className = "battle-report-metric-row";

        const label = document.createElement("span");
        const value = document.createElement("span");
        value.className = "battle-report-metric-value";
        value.textContent = metric.value || "—";

        if (metric.chart_id) {
          const link = document.createElement("a");
          const href = buildChartUrl(metric.chart_id);
          link.href = href || "#";
          link.textContent = metric.label || "";
          link.className = "battle-report-metric-link";
          label.appendChild(link);
        } else {
          label.textContent = metric.label || "";
        }

        row.appendChild(label);
        row.appendChild(value);
        metricsEl.appendChild(row);
      }
    }

    async function loadRun(runId) {
      setLoading();
      try {
        const resp = await fetch(buildEndpoint(runId), {
          method: "GET",
          credentials: "same-origin",
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!resp.ok) {
          setError("Unable to load this Battle Report.");
          return;
        }
        const payload = await resp.json();
        if (!payload || !payload.ok || !payload.report) {
          setError("Unable to load this Battle Report.");
          return;
        }
        const report = payload.report;
        const titleParts = [];
        if (report.battle_date) {
          titleParts.push(new Date(report.battle_date).toLocaleString());
        } else if (report.parsed_at) {
          titleParts.push(new Date(report.parsed_at).toLocaleString());
        }
        const runLabel = Number.isInteger(report.run_number) ? report.run_number : report.id;
        titleParts.push(`Run ${runLabel}`);
        if (titleEl) titleEl.textContent = titleParts.join(" • ");
        if (rawEl) rawEl.textContent = report.raw_text || "";
        renderMetrics(report.metrics || []);
        if (noteEl) noteEl.textContent = state.contextNote || "";
      } catch (_err) {
        setError("Unable to load this Battle Report.");
      }
    }

    function setOrder(order, runId) {
      const cleaned = Array.isArray(order) ? order.filter((id) => Number.isInteger(id)) : [];
      state.order = cleaned;
      state.index = cleaned.indexOf(runId);
      if (state.index < 0) {
        state.order = [runId];
        state.index = 0;
      }
      setNavState();
    }

    function openForRun(runId, order, contextNote) {
      state.contextNote = contextNote || "";
      setOrder(order, runId);
      openModal();
      loadRun(runId);
    }

    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (modal) {
      modal.addEventListener("click", (event) => {
        if (event.target === modal) closeModal();
      });
    }
    document.addEventListener("keydown", (event) => {
      if (modal.getAttribute("aria-hidden") === "true") return;
      if (event.key === "Escape") closeModal();
    });

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        if (state.index <= 0) return;
        state.index -= 1;
        setNavState();
        loadRun(state.order[state.index]);
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        if (state.index < 0 || state.index >= state.order.length - 1) return;
        state.index += 1;
        setNavState();
        loadRun(state.order[state.index]);
      });
    }

    function readJsonScript(id) {
      const node = document.getElementById(id);
      if (!node) return null;
      try {
        return JSON.parse(node.textContent || "null");
      } catch (_err) {
        return null;
      }
    }

    const battleHistoryOrder = readJsonScript("battle-report-order");
    const battleHistoryNote = "Navigation follows the current Battle History sorting and filters.";
    const rows = document.querySelectorAll(".battle-report-row");
    for (const row of rows) {
      const runId = Number(row.dataset.runId);
      if (!Number.isInteger(runId)) continue;

      function shouldIgnore(target) {
        return Boolean(target.closest("a, button, input, select, textarea, label"));
      }

      row.addEventListener("click", (event) => {
        if (shouldIgnore(event.target)) return;
        openForRun(runId, battleHistoryOrder || [], battleHistoryNote);
      });

      row.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        if (shouldIgnore(event.target)) return;
        event.preventDefault();
        openForRun(runId, battleHistoryOrder || [], battleHistoryNote);
      });
    }

    window.openBattleReportModal = openForRun;
  }

  function initializeGuidedWalkthrough() {
    const container = document.getElementById("guided-walkthrough");
    if (!container) return;

    const trigger = document.getElementById("walkthrough-trigger");
    const overlay = container.querySelector(".walkthrough-overlay");
    const panel = container.querySelector(".walkthrough-panel");
    const progressEl = document.getElementById("walkthrough-progress");
    const titleEl = document.getElementById("walkthrough-title");
    const bodyEl = document.getElementById("walkthrough-body");
    const linkEl = document.getElementById("walkthrough-link");
    const backBtn = document.getElementById("walkthrough-back");
    const nextBtn = document.getElementById("walkthrough-next");
    const skipBtn = document.getElementById("walkthrough-skip");
    const dismissBtn = document.getElementById("walkthrough-dismiss");

    if (!trigger || !overlay || !panel || !progressEl || !titleEl || !bodyEl || !linkEl || !backBtn || !nextBtn || !skipBtn || !dismissBtn) {
      return;
    }

    const walkthroughEnabled = container.dataset.walkthroughEnabled === "true";
    const demoMode = container.dataset.demoMode === "true";
    const changelogUrl = container.dataset.changelogUrl || "";
    const dismissedKey = "tts_walkthrough_dismissed";
    const completedKey = "tts_walkthrough_completed_at";

    const steps = [
      {
        id: "charts-header",
        title: "Charts dashboard",
        body: "This dashboard shows how your runs change over time using your selected filters.",
        target: "[data-walkthrough-target='charts-header']",
      },
      {
        id: "context-menu",
        title: "More options",
        body: "More options lets you refine chart scope, grouping, and filters for focused views.",
        target: "[data-walkthrough-target='context-menu']",
        openDetails: "#charts-more-options",
      },
      {
        id: "demo-nav",
        title: "Demo windows",
        body: "These buttons switch between early, mid, and late demo windows so you can compare sample runs.",
        target: "[data-walkthrough-target='demo-nav']",
        requiresDemo: true,
      },
      {
        id: "top-nav",
        title: "Top navigation",
        body: "Use the top navigation to move between Battle History, Goals, and collection dashboards.",
        target: "[data-walkthrough-target='top-nav']",
      },
      {
        id: "docs-link",
        title: "Changelog",
        body: "View the Changelog to see what changed in recent updates.",
        target: "[data-walkthrough-target='docs-link']",
        linkUrl: changelogUrl,
        linkLabel: "Open Changelog",
      },
    ];

    const activeSteps = steps.filter((step) => {
      if (step.requiresDemo && !demoMode) return false;
      return Boolean(document.querySelector(step.target));
    });

    if (!walkthroughEnabled || activeSteps.length === 0) {
      trigger.hidden = true;
      return;
    }

    function readStorageFlag(key) {
      try {
        return window.localStorage.getItem(key) === "true";
      } catch (_err) {
        return false;
      }
    }

    function writeStorageFlag(key, value) {
      try {
        window.localStorage.setItem(key, value ? "true" : "false");
      } catch (_err) {
        return;
      }
    }

    function writeStorageValue(key, value) {
      try {
        window.localStorage.setItem(key, value);
      } catch (_err) {
        return;
      }
    }

    if (readStorageFlag(dismissedKey)) {
      trigger.hidden = true;
      return;
    }

    trigger.hidden = false;

    const state = {
      index: 0,
      steps: activeSteps,
      activeTarget: null,
      openDetails: null,
    };

    function clearHighlight() {
      if (state.activeTarget) {
        state.activeTarget.classList.remove("walkthrough-target");
      }
      state.activeTarget = null;
    }

    function restoreDetails() {
      if (!state.openDetails) return;
      if (!state.openDetails.wasOpen) {
        state.openDetails.node.removeAttribute("open");
      }
      state.openDetails = null;
    }

    function setActiveTarget(target) {
      clearHighlight();
      state.activeTarget = target;
      if (state.activeTarget) {
        state.activeTarget.classList.add("walkthrough-target");
      }
    }

    function positionPanel(target) {
      const margin = 12;
      const rect = target.getBoundingClientRect();
      const panelRect = panel.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      const spaces = {
        top: rect.top - margin,
        bottom: viewportHeight - rect.bottom - margin,
        left: rect.left - margin,
        right: viewportWidth - rect.right - margin,
      };
      const candidates = [
        {
          name: "right",
          fits: spaces.right >= panelRect.width,
          top: rect.top + (rect.height - panelRect.height) / 2,
          left: rect.right + margin,
        },
        {
          name: "left",
          fits: spaces.left >= panelRect.width,
          top: rect.top + (rect.height - panelRect.height) / 2,
          left: rect.left - panelRect.width - margin,
        },
        {
          name: "bottom",
          fits: spaces.bottom >= panelRect.height,
          top: rect.bottom + margin,
          left: rect.left + (rect.width - panelRect.width) / 2,
        },
        {
          name: "top",
          fits: spaces.top >= panelRect.height,
          top: rect.top - panelRect.height - margin,
          left: rect.left + (rect.width - panelRect.width) / 2,
        },
      ];
      const ordered = candidates.sort((a, b) => Number(b.fits) - Number(a.fits));
      const choice = ordered.find((item) => item.fits) || ordered[0];

      let top = choice.top;
      let left = choice.left;
      if (top + panelRect.height > viewportHeight - margin) {
        top = viewportHeight - panelRect.height - margin;
      }
      if (top < margin) top = margin;
      if (left + panelRect.width > viewportWidth - margin) {
        left = viewportWidth - panelRect.width - margin;
      }
      if (left < margin) left = margin;
      panel.style.top = `${Math.round(top)}px`;
      panel.style.left = `${Math.round(left)}px`;
    }

    function updateNavigation() {
      backBtn.disabled = state.index <= 0;
      nextBtn.textContent = state.index >= state.steps.length - 1 ? "Finish" : "Next";
      progressEl.textContent = `Step ${state.index + 1} of ${state.steps.length}`;
    }

    function showStep(index) {
      const step = state.steps[index];
      if (!step) return;
      state.index = index;

      restoreDetails();
      const target = document.querySelector(step.target);
      if (!target) return;

      if (step.openDetails) {
        const details = document.querySelector(step.openDetails);
        if (details) {
          const wasOpen = details.hasAttribute("open");
          details.setAttribute("open", "");
          state.openDetails = { node: details, wasOpen };
        }
      }

      target.scrollIntoView({ behavior: "smooth", block: "center" });
      setActiveTarget(target);
      titleEl.textContent = step.title;
      bodyEl.textContent = step.body;

      if (step.linkUrl) {
        linkEl.href = step.linkUrl;
        linkEl.textContent = step.linkLabel || "Open";
        linkEl.hidden = false;
      } else {
        linkEl.hidden = true;
      }

      updateNavigation();
      window.requestAnimationFrame(() => positionPanel(target));
    }

    function openWalkthrough() {
      container.classList.add("is-active");
      container.setAttribute("aria-hidden", "false");
      showStep(0);
    }

    function closeWalkthrough() {
      container.classList.remove("is-active");
      container.setAttribute("aria-hidden", "true");
      clearHighlight();
      restoreDetails();
    }

    trigger.addEventListener("click", openWalkthrough);
    overlay.addEventListener("click", closeWalkthrough);

    backBtn.addEventListener("click", () => {
      if (state.index <= 0) return;
      showStep(state.index - 1);
    });

    nextBtn.addEventListener("click", () => {
      if (state.index >= state.steps.length - 1) {
        writeStorageValue(completedKey, new Date().toISOString());
        closeWalkthrough();
        return;
      }
      showStep(state.index + 1);
    });

    skipBtn.addEventListener("click", closeWalkthrough);

    dismissBtn.addEventListener("click", () => {
      writeStorageFlag(dismissedKey, true);
      closeWalkthrough();
      trigger.hidden = true;
    });

    window.addEventListener("resize", () => {
      if (!state.activeTarget || !container.classList.contains("is-active")) return;
      positionPanel(state.activeTarget);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      () => {
        initializeFoundation();
        initializeGlobalSearch();
        initializeBattleReportModal();
        initializeGuidedWalkthrough();
      },
      { once: true }
    );
    return;
  }

  initializeFoundation();
  initializeGlobalSearch();
  initializeBattleReportModal();
  initializeGuidedWalkthrough();
})();
