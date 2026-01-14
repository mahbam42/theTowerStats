import { EditorState, EditorView, basicSetup } from "../vendor/codemirror/basic-setup.bundle.mjs";
import { StreamLanguage } from "../vendor/codemirror/language.bundle.mjs";
import { autocompletion, completeFromList } from "../vendor/codemirror/autocomplete.bundle.mjs";

const textarea = document.getElementById("explore-dsl-input");
const editorHost = document.querySelector("[data-explore-dsl-editor]");

if (textarea && editorHost) {
  const autocompleteEl = document.getElementById("explore-dsl-autocomplete");
  const autocompletePayload = autocompleteEl ? JSON.parse(autocompleteEl.textContent || "{}") : {};
  const keywordEntries = autocompletePayload.keywords || [];
  const metricEntries = autocompletePayload.metrics || [];
  const breakdownEntries = autocompletePayload.breakdowns || [];

  const completions = [...keywordEntries, ...metricEntries, ...breakdownEntries]
    .filter((entry) => entry && entry.label)
    .map((entry) => ({
      label: entry.label,
      detail: entry.detail || "",
      type: entry.type || "text",
    }));

  const keywordSet = new Set(keywordEntries.map((entry) => String(entry.label).toLowerCase()));
  const metricSet = new Set(metricEntries.map((entry) => String(entry.label).toLowerCase()));
  const breakdownSet = new Set(breakdownEntries.map((entry) => String(entry.label).toLowerCase()));

  const dslLanguage = StreamLanguage.define({
    token(stream) {
      if (stream.eatSpace()) return null;
      if (stream.match(/#[^\n]*/, true)) return "comment";
      if (stream.match(/\[[^\]]+\]/, true)) return "placeholder";
      if (stream.match(/"(?:[^"\\]|\\.)*"/, true)) return "string";
      if (stream.match(/>=|<=|!=|=|\.\./, true)) return "operator";
      if (stream.match(/\d+/, true)) return "number";
      if (stream.match(/[A-Za-z_][A-Za-z0-9_]*/, true)) {
        const word = stream.current().toLowerCase();
        if (keywordSet.has(word)) return "keyword";
        if (metricSet.has(word)) return "variableName";
        if (breakdownSet.has(word)) return "typeName";
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
        fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
        fontSize: "0.95rem",
      },
      ".cm-content": {
        padding: "1rem",
        minHeight: "10rem",
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

  const updateListener = EditorView.updateListener.of((update) => {
    if (update.docChanged) {
      textarea.value = update.state.doc.toString();
    }
  });

  const startState = EditorState.create({
    doc: textarea.value || "",
    extensions: [
      basicSetup,
      dslLanguage,
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
}
