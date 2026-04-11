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

  function formatExactNumber(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) return String(value);
    return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(num);
  }

  function formatCompactNumber(value) {
    const num = Number(value);
    const absValue = Math.abs(num);
    if (!Number.isFinite(absValue)) return String(value);
    const units = [
      { threshold: 1_000_000_000_000_000_000_000_000_000_000, suffix: "O" },
      { threshold: 1_000_000_000_000_000_000_000_000_000, suffix: "o" },
      { threshold: 1_000_000_000_000_000_000_000_000, suffix: "S" },
      { threshold: 1_000_000_000_000_000_000_000, suffix: "s" },
      { threshold: 1_000_000_000_000_000_000, suffix: "Q" },
      { threshold: 1_000_000_000_000_000, suffix: "q" },
      { threshold: 1_000_000_000_000, suffix: "T" },
      { threshold: 1_000_000_000, suffix: "B" },
      { threshold: 1_000_000, suffix: "M" },
      { threshold: 1_000, suffix: "K" },
    ];
    for (const unit of units) {
      if (absValue >= unit.threshold) {
        return `${(num / unit.threshold).toFixed(2)}${unit.suffix}`;
      }
    }
    return formatExactNumber(num);
  }

  function formatChartNumber(value, unit) {
    const unitLabel = String(unit || "").trim().toLowerCase();
    const noCompact = new Set(["%", "percent", "x", "multiplier", "seconds", "s"]);
    if (noCompact.has(unitLabel)) return formatExactNumber(value);
    return formatCompactNumber(value);
  }

  window.ttsFormatChartNumber = formatChartNumber;
  window.ttsFormatExactNumber = formatExactNumber;

  function initializeUnitFormatting() {
    const formatter = window.ttsFormatChartNumber || formatChartNumber;
    const nodes = document.querySelectorAll("[data-format='unit-value']");
    for (const node of nodes) {
      const rawValue = node.dataset.value;
      const unit = node.dataset.unit || "";
      const suffix = node.dataset.suffix || "";
      const numeric = Number(rawValue);
      if (!Number.isFinite(numeric)) {
        node.textContent = rawValue || "—";
        continue;
      }
      const formatted = formatter(numeric, unit);
      node.textContent = suffix ? `${formatted}${suffix}` : formatted;
    }
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
      const includeHidden = form && form.elements["include_hidden"] ? form.elements["include_hidden"].checked : null;
      const windowKind = getFormValue("window_kind");
      const windowN = getFormValue("window_n");
      const movingAverage = getFormValue("moving_average_window");
      const contextSnapshot = getFormValue("context_snapshot");
      if (granularity) url.searchParams.set("granularity", granularity);
      if (tier) url.searchParams.set("tier", tier);
      if (preset) url.searchParams.set("preset", preset);
      if (includeTournaments) url.searchParams.set("include_tournaments", "on");
      if (includeHidden) url.searchParams.set("include_hidden", "on");
      if (windowKind) url.searchParams.set("window_kind", windowKind);
      if (windowN) url.searchParams.set("window_n", windowN);
      if (movingAverage) url.searchParams.set("moving_average_window", movingAverage);
      if (contextSnapshot) url.searchParams.set("context_snapshot", contextSnapshot);
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
      const formatter = window.ttsFormatChartNumber || formatChartNumber;
      for (const metric of metrics || []) {
        const row = document.createElement("div");
        row.className = "battle-report-metric-row";

        const label = document.createElement("span");
        const value = document.createElement("span");
        value.className = "battle-report-metric-value";
        const numeric = metric.numeric_value;
        const unit = metric.unit || "";
        if (Number.isFinite(Number(numeric))) {
          const formatted = formatter(numeric, unit);
          value.textContent = unit ? `${formatted} ${unit}` : formatted;
        } else {
          value.textContent = metric.value || "—";
        }

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
          const label = new Date(report.battle_date).toLocaleString();
          if (report.battle_date_fallback) {
            titleParts.push(`${label} (Imported)`);
          } else {
            titleParts.push(label);
          }
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
    const battleHistoryNote =
      modal.dataset.contextNote || "Navigation follows the current Battle History sorting and filters.";
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

    const exploreRows = document.querySelectorAll(".explore-result-row");
    for (const row of exploreRows) {
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

  function initializeExploreModal() {
    const modal = document.getElementById("explore-modal");
    if (!modal) return;
    const openBtn = document.getElementById("open-explore-modal");
    const closeBtn = modal.querySelector("[data-close-modal]");
    const form = modal.querySelector("[data-explore-modal-form]");

    function openModal() {
      modal.classList.add("is-open");
      modal.setAttribute("aria-hidden", "false");
    }

    function closeModal() {
      modal.classList.remove("is-open");
      modal.setAttribute("aria-hidden", "true");
    }

    if (openBtn) openBtn.addEventListener("click", openModal);
    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    modal.addEventListener("click", (event) => {
      if (event.target === modal) closeModal();
    });
    window.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && modal.getAttribute("aria-hidden") === "false") {
        closeModal();
      }
    });

    if (!form) return;

    const statusEl = modal.querySelector("[data-explore-modal-status]");
    const summaryEl = modal.querySelector("[data-explore-modal-summary]");
    const tableWrap = modal.querySelector("[data-explore-modal-table]");
    const tableHead = modal.querySelector("[data-explore-modal-table-head]");
    const tableBody = modal.querySelector("[data-explore-modal-table-body]");
    const tableTotal = modal.querySelector("[data-explore-modal-table-total]");
    const emptyEl = modal.querySelector("[data-explore-modal-empty]");
    const chartWrap = modal.querySelector("[data-explore-modal-chart-wrap]");
    const chartCanvas = modal.querySelector("[data-explore-modal-chart]");
    const kpiEl = modal.querySelector("[data-explore-modal-kpi]");
    const kpiValueEl = modal.querySelector("[data-explore-modal-kpi-value]");
    const legendEl = modal.querySelector("[data-explore-modal-legend]");
    let chartInstance = null;

    const formatter = window.ttsFormatChartNumber || formatChartNumber;
    function getChartPalette() {
      const rootStyles = getComputedStyle(document.documentElement);
      const pick = (name, fallback) => rootStyles.getPropertyValue(name).trim() || fallback;
      return [
        pick("--tts-color-accent", "#2b7de9"),
        pick("--tts-color-success", "#3cb371"),
        pick("--tts-color-warning", "#f5b14c"),
        pick("--tts-color-danger", "#d35b52"),
        pick("--tts-color-link", "#7ab7ff"),
      ];
    }
    const chartPalette = getChartPalette();

    function clearPreview() {
      if (statusEl) statusEl.innerHTML = "";
      if (summaryEl) summaryEl.textContent = "Preview appears after running a query.";
      if (tableWrap) tableWrap.hidden = true;
      if (tableHead) tableHead.innerHTML = "";
      if (tableBody) tableBody.innerHTML = "";
      if (tableTotal) tableTotal.innerHTML = "";
      if (emptyEl) emptyEl.hidden = false;
      if (kpiEl) kpiEl.hidden = true;
      if (chartCanvas) chartCanvas.hidden = true;
      if (legendEl) legendEl.innerHTML = "";
      if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
      }
    }

    function renderStatus(errors, warnings) {
      if (!statusEl) return;
      statusEl.innerHTML = "";
      const renderCallout = (items, kind, title) => {
        if (!items || !items.length) return;
        const callout = document.createElement("div");
        callout.className = `callout ${kind}`;
        const heading = document.createElement("p");
        heading.className = "margin-0";
        heading.innerHTML = `<strong>${title}</strong>`;
        callout.appendChild(heading);
        const list = document.createElement("ul");
        list.className = "margin-0";
        for (const item of items) {
          const li = document.createElement("li");
          li.textContent = item;
          list.appendChild(li);
        }
        callout.appendChild(list);
        statusEl.appendChild(callout);
      };
      renderCallout(errors, "alert", "Explore validation");
      renderCallout(warnings, "warning", "Explore notes");
    }

    function renderTable(headers, rows, unit, totalValue, totalCount) {
      if (!tableWrap || !tableHead || !tableBody || !tableTotal) return;
      tableHead.innerHTML = "";
      const headerRow = document.createDocumentFragment();
      for (const header of headers || []) {
        const th = document.createElement("th");
        th.scope = "col";
        th.textContent = header;
        headerRow.appendChild(th);
      }
      const valueTh = document.createElement("th");
      valueTh.scope = "col";
      valueTh.textContent = "Value";
      headerRow.appendChild(valueTh);
      const countTh = document.createElement("th");
      countTh.scope = "col";
      countTh.textContent = "Runs counted";
      headerRow.appendChild(countTh);
      tableHead.appendChild(headerRow);

      tableBody.innerHTML = "";
      for (const row of rows || []) {
        const tr = document.createElement("tr");
        const breakdown = row.breakdown || [];
        for (const label of breakdown) {
          const td = document.createElement("td");
          td.textContent = label;
          tr.appendChild(td);
        }
        const valueTd = document.createElement("td");
        const value = row.value;
        if (Number.isFinite(Number(value))) {
          valueTd.textContent = unit ? `${formatter(value, unit)} ${unit}` : formatter(value, unit);
        } else {
          valueTd.textContent = "—";
        }
        tr.appendChild(valueTd);
        const countTd = document.createElement("td");
        countTd.textContent = row.sample_count ?? "—";
        tr.appendChild(countTd);
        tableBody.appendChild(tr);
      }
      tableTotal.innerHTML = "";
      const totalLabel = document.createElement("td");
      const labelSpan = (headers || []).length ? headers.length : 1;
      totalLabel.colSpan = labelSpan;
      totalLabel.textContent = "Total";
      tableTotal.appendChild(totalLabel);
      const totalValueCell = document.createElement("td");
      if (Number.isFinite(Number(totalValue))) {
        totalValueCell.textContent = unit ? `${formatter(totalValue, unit)} ${unit}` : formatter(totalValue, unit);
      } else {
        totalValueCell.textContent = "—";
      }
      tableTotal.appendChild(totalValueCell);
      const totalCountCell = document.createElement("td");
      totalCountCell.textContent = totalCount ?? "—";
      tableTotal.appendChild(totalCountCell);
      tableWrap.hidden = (rows || []).length === 0;
    }

    function renderChart(chart, visualization, unit, totalValue) {
      if (!chartCanvas || !chartWrap) return;
      if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
      }
      if (visualization === "kpi") {
        if (emptyEl) emptyEl.hidden = true;
        if (kpiEl && kpiValueEl) {
          kpiEl.hidden = false;
          kpiValueEl.textContent = Number.isFinite(Number(totalValue))
            ? (unit ? `${formatter(totalValue, unit)} ${unit}` : formatter(totalValue, unit))
            : "—";
        }
        if (chartCanvas) chartCanvas.hidden = true;
        return;
      }
      if (visualization !== "bar" && visualization !== "donut") {
        if (emptyEl) emptyEl.hidden = false;
        if (chartCanvas) chartCanvas.hidden = true;
        return;
      }
      if (emptyEl) emptyEl.hidden = true;
      if (!window.Chart) return;
      chartCanvas.hidden = false;
      const labels = (chart && chart.labels) || [];
      const values = (chart && chart.values) || [];
      const chartUnit = (chart && chart.unit) || unit || "";
      const chartType = visualization === "donut" ? "doughnut" : "bar";
      chartInstance = new Chart(chartCanvas.getContext("2d"), {
        type: chartType,
        data: {
          labels,
          datasets: [
            {
              label: chartUnit || "Value",
              data: values,
              backgroundColor: visualization === "donut" ? chartPalette : "#2a9d8f",
            },
          ],
        },
        options: {
          plugins: {
            legend: { display: visualization === "donut" },
          },
          scales: visualization === "donut" ? {} : {
            y: { beginAtZero: true },
          },
        },
      });
      if (legendEl) {
        legendEl.innerHTML = "";
        const legendLabels = labels.length ? labels : [chartUnit || "Value"];
        legendLabels.forEach((label, idx) => {
          const item = document.createElement("div");
          item.className = "explore-legend-item";
          const swatch = document.createElement("span");
          swatch.className = "explore-legend-swatch";
          swatch.style.backgroundColor = visualization === "donut" ? chartPalette[idx % chartPalette.length] : "#2a9d8f";
          const text = document.createElement("span");
          text.textContent = label;
          item.appendChild(swatch);
          item.appendChild(text);
          legendEl.appendChild(item);
        });
      }
    }

    async function runPreview() {
      if (!summaryEl) return;
      summaryEl.textContent = "Running query...";
      const formData = new FormData(form);
      formData.set("action", "run_explore_query");
      try {
        const response = await fetch(form.action, {
          method: "POST",
          credentials: "same-origin",
          headers: { "X-Requested-With": "XMLHttpRequest" },
          body: formData,
        });
        if (!response.ok) {
          throw new Error("Request failed");
        }
        const payload = await response.json();
        renderStatus(payload.errors || [], payload.warnings || []);
        if (!payload.results) {
          clearPreview();
          return;
        }
        const results = payload.results;
        if (summaryEl) {
          summaryEl.textContent = `${results.metric_label || "Metric"} • ${String(results.aggregation || "").toUpperCase()}`;
        }
        renderTable(
          results.breakdown_headers,
          results.rows,
          results.metric_unit,
          results.total_value,
          results.total_sample_count
        );
        renderChart(results.chart, results.visualization, results.metric_unit, results.total_value);
      } catch (_err) {
        clearPreview();
        renderStatus(["Unable to run the query preview."], []);
      }
    }

    form.addEventListener("submit", (event) => {
      if (!event.submitter || event.submitter.value !== "run_explore_query") return;
      event.preventDefault();
      clearPreview();
      runPreview();
    });
  }

  function initializeLifetimeStatsModal() {
    const modal = document.getElementById("lifetime-stats-modal");
    if (!modal) return;

    const endpoint = modal.dataset.endpoint;
    if (!endpoint) return;

    const openBtn = document.getElementById("open-lifetime-stats");
    const closeBtn = modal.querySelector("[data-close-modal]");
    const form = modal.querySelector("[data-lifetime-stats-form]");
    const rangeEl = modal.querySelector("[data-lifetime-stats-range]");
    const runCountEl = modal.querySelector("[data-lifetime-stats-run-count]");
    const groupsEl = modal.querySelector("[data-lifetime-stats-groups]");
    const statusEl = modal.querySelector("[data-lifetime-stats-status]");
    if (!form || !groupsEl) return;

    const rangeSelect = form.querySelector("[name='range_mode']");
    const startInput = form.querySelector("[name='start_date']");
    const endInput = form.querySelector("[name='end_date']");

    const formatter = window.ttsFormatChartNumber || formatChartNumber;

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

    function setStatus(message) {
      if (!statusEl) return;
      statusEl.hidden = false;
      statusEl.textContent = message;
    }

    function clearStatus() {
      if (!statusEl) return;
      statusEl.hidden = true;
      statusEl.textContent = "";
    }

    function setLoading() {
      clearStatus();
      if (groupsEl) groupsEl.innerHTML = "";
      if (runCountEl) runCountEl.textContent = "Loading…";
    }

    function setRangeInputs(mode) {
      const isCustom = mode === "custom";
      if (startInput) startInput.disabled = !isCustom;
      if (endInput) endInput.disabled = !isCustom;
    }

    function renderGroups(groups) {
      groupsEl.innerHTML = "";
      for (const group of groups || []) {
        const card = document.createElement("div");
        card.className = "card-shell lifetime-stats-group";

        const header = document.createElement("h5");
        header.textContent = group.label || "";
        card.appendChild(header);

        const grid = document.createElement("div");
        grid.className = "lifetime-stats-metrics";
        for (const metric of group.metrics || []) {
          const row = document.createElement("div");
          row.className = "lifetime-stats-row";

          const label = document.createElement("span");
          label.textContent = metric.label || "";

          const value = document.createElement("span");
          value.className = "lifetime-stats-value";
          const numeric = metric.numeric_value;
          const unit = metric.unit || "";
          if (Number.isFinite(Number(numeric))) {
            const formatted = formatter(numeric, unit);
            value.textContent = unit ? `${formatted} ${unit}` : formatted;
          } else {
            value.textContent = "—";
          }

          row.appendChild(label);
          row.appendChild(value);
          grid.appendChild(row);
        }

        card.appendChild(grid);
        groupsEl.appendChild(card);
      }
    }

    async function loadStats() {
      if (!endpoint) return;
      setLoading();
      const params = new URLSearchParams();
      const mode = rangeSelect ? rangeSelect.value : "";
      if (mode) params.set("range_mode", mode);
      if (startInput && startInput.value) params.set("start_date", startInput.value);
      if (endInput && endInput.value) params.set("end_date", endInput.value);
      const url = params.toString() ? `${endpoint}?${params.toString()}` : endpoint;

      try {
        const resp = await fetch(url, {
          method: "GET",
          credentials: "same-origin",
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const payload = await resp.json();
        if (!resp.ok || !payload.ok) {
          setStatus("Unable to load Lifetime Stats.");
          if (runCountEl) runCountEl.textContent = "";
          return;
        }
        clearStatus();
        const range = payload.range || {};
        if (rangeSelect && range.mode) rangeSelect.value = range.mode;
        setRangeInputs(range.mode || "");
        if (startInput && range.start_date) startInput.value = range.start_date;
        if (endInput && range.end_date) endInput.value = range.end_date;
        if (rangeEl) rangeEl.textContent = range.label || "";
        if (runCountEl) runCountEl.textContent = `Runs included: ${payload.run_count || 0}`;
        renderGroups(payload.groups || []);
      } catch (_err) {
        setStatus("Unable to load Lifetime Stats.");
        if (runCountEl) runCountEl.textContent = "";
      }
    }

    if (openBtn) {
      openBtn.addEventListener("click", () => {
        openModal();
        setRangeInputs(rangeSelect ? rangeSelect.value : "");
        loadStats();
      });
    }
    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    modal.addEventListener("click", (event) => {
      if (event.target === modal) closeModal();
    });
    window.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && modal.getAttribute("aria-hidden") === "false") {
        closeModal();
      }
    });
    if (rangeSelect) {
      rangeSelect.addEventListener("change", () => {
        setRangeInputs(rangeSelect.value);
      });
    }
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      loadStats();
    });
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
        initializeExploreModal();
        initializeLifetimeStatsModal();
        initializeUnitFormatting();
        initializeGuidedWalkthrough();
      },
      { once: true }
    );
    return;
  }

  initializeFoundation();
  initializeGlobalSearch();
  initializeBattleReportModal();
  initializeExploreModal();
  initializeLifetimeStatsModal();
  initializeUnitFormatting();
  initializeGuidedWalkthrough();
})();
