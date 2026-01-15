import {
  EditorState,
  EditorView,
  StreamLanguage,
  autocompletion,
  completeFromList,
  lineNumbers,
  syntaxHighlighting,
  defaultHighlightStyle,
} from "../vendor/codemirror/explore.bundle.mjs";

const textarea = document.getElementById("explore-dsl-input");
const editorHost = document.querySelector("[data-explore-dsl-editor]");

if (textarea && editorHost) {
  const autocompleteEl = document.getElementById("explore-dsl-autocomplete");
  const fallbackPayload = autocompleteEl ? JSON.parse(autocompleteEl.textContent || "{}") : {};
  const autocompleteEndpoint = editorHost.dataset.exploreAutocompleteUrl || "";
  const errorsEl = document.getElementById("explore-dsl-errors");
  const warningsEl = document.getElementById("explore-dsl-warnings");

  const CACHE_KEY = "ttsExploreAutocomplete";
  const CACHE_TTL_MS = 1000 * 60 * 60 * 24 * 2;

  function readCache() {
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const cached = JSON.parse(raw);
      if (!cached || typeof cached !== "object") return null;
      if (!cached.timestamp || !cached.payload) return null;
      if (Date.now() - cached.timestamp > CACHE_TTL_MS) return null;
      return cached.payload;
    } catch {
      return null;
    }
  }

  function writeCache(payload) {
    try {
      localStorage.setItem(
        CACHE_KEY,
        JSON.stringify({ timestamp: Date.now(), payload })
      );
    } catch {
      // Ignore cache failures.
    }
  }

  async function fetchAutocomplete() {
    if (!autocompleteEndpoint) return null;
    try {
      const resp = await fetch(autocompleteEndpoint, {
        method: "GET",
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!resp.ok) return null;
      const data = await resp.json();
      if (data && data.autocomplete) {
        writeCache(data.autocomplete);
        return data.autocomplete;
      }
    } catch {
      return null;
    }
    return null;
  }

  function buildCompletions(payload) {
    const keywordEntries = payload.keywords || [];
    const metricEntries = payload.metrics || [];
    const breakdownEntries = payload.breakdowns || [];
    const presetEntries = payload.presets || [];

    const completions = [...keywordEntries, ...metricEntries, ...breakdownEntries, ...presetEntries]
      .filter((entry) => entry && entry.label)
      .map((entry) => ({
        label: entry.label,
        detail: entry.detail || "",
        type: entry.type || "text",
      }));

    return {
      completions,
      keywordSet: new Set(keywordEntries.map((entry) => String(entry.label).toLowerCase())),
      metricSet: new Set(metricEntries.map((entry) => String(entry.label).toLowerCase())),
      breakdownSet: new Set(breakdownEntries.map((entry) => String(entry.label).toLowerCase())),
      presetSet: new Set(presetEntries.map((entry) => String(entry.label).toLowerCase())),
    };
  }

  function getCsrfToken() {
    const tokenInput = document.querySelector("input[name='csrfmiddlewaretoken']");
    if (tokenInput && tokenInput.value) return tokenInput.value;
    return "";
  }

  function renderValidation({ errors = [], warnings = [] } = {}) {
    function renderList(container, items) {
      if (!container) return;
      const list = container.querySelector("ul");
      if (!list) return;
      list.innerHTML = "";
      items.forEach((msg) => {
        const row = document.createElement("li");
        row.textContent = msg;
        list.appendChild(row);
      });
      container.hidden = !items.length;
    }

    renderList(errorsEl, errors);
    renderList(warningsEl, warnings);
  }

  async function runValidation(text) {
    if (!autocompleteEndpoint) return;
    if (!text.trim()) {
      renderValidation({ errors: [], warnings: [] });
      return;
    }

    try {
      const resp = await fetch(autocompleteEndpoint, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCsrfToken(),
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ dsl: text }),
      });
      if (!resp.ok) return;
      const data = await resp.json();
      renderValidation(data.validation || {});
    } catch {
      // Ignore validation fetch failures.
    }
  }

  async function initializeEditor() {
    const cachedPayload = readCache();
    const fetchedPayload = cachedPayload ? null : await fetchAutocomplete();
    const payload = cachedPayload || fetchedPayload || fallbackPayload || {};

    const { completions, keywordSet, metricSet, breakdownSet, presetSet } = buildCompletions(payload);

    const dslLanguage = StreamLanguage.define({
      token(stream) {
        if (stream.eatSpace()) return null;
        if (stream.match(/#[^\n]*/, true)) return "comment";
        if (stream.match(/\[[^\]]+\]/, true)) return "meta";
        if (stream.match(/"(?:[^"\\]|\\.)*"/, true)) return "string";
        if (stream.match(/>=|<=|!=|=|\.\./, true)) return "operator";
        if (stream.match(/\*/, true)) return "operator";
        if (stream.match(/\d+/, true)) return "number";
        if (stream.match(/[A-Za-z_][A-Za-z0-9_]*/, true)) {
          const word = stream.current().toLowerCase();
          if (keywordSet.has(word)) return "keyword";
          if (metricSet.has(word)) return "variableName";
          if (breakdownSet.has(word)) return "typeName";
          if (presetSet.has(word)) return "atom";
          return "variableName";
        }
        stream.next();
        return null;
      },
    });

    const editorTheme = EditorView.theme(
      {
        "&": {
          backgroundColor: "var(--tts-color-surface)",
          border: "1px solid var(--tts-color-border)",
          borderRadius: "var(--tts-radius-2)",
          fontFamily:
            "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
          fontSize: "0.95rem",
        },
        ".cm-content": {
          padding: "1rem",
          minHeight: "16rem",
        },
        ".cm-gutters": {
          backgroundColor: "transparent",
          borderRight: "1px solid var(--tts-color-border)",
          color: "var(--tts-color-text-muted)",
        },
        ".cm-line": {
          paddingLeft: "0.4rem",
        },
      },
      { dark: true }
    );

    let validationTimer = null;
    const updateListener = EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        const text = update.state.doc.toString();
        textarea.value = text;
        if (validationTimer) window.clearTimeout(validationTimer);
        validationTimer = window.setTimeout(() => runValidation(text), 500);
      }
    });

    const startState = EditorState.create({
      doc: textarea.value || "",
      extensions: [
        lineNumbers(),
        dslLanguage,
        syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
        autocompletion({ override: [completeFromList(completions)] }),
        editorTheme,
        updateListener,
        EditorView.lineWrapping,
      ],
    });

    textarea.style.display = "none";
    const view = new EditorView({
      state: startState,
      parent: editorHost,
    });

    const form = document.querySelector("[data-explore-dsl-form]");
    if (form) {
      form.addEventListener("submit", () => {
        textarea.value = view.state.doc.toString();
      });
    }

    renderValidation({ errors: [], warnings: [] });
    runValidation(view.state.doc.toString());
  }

  initializeEditor();
}
