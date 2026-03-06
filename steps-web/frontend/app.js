const defaultSource = `step: main
    do:
        display "Hello from Steps Web"
`;

const editor = document.getElementById("editor");
const inputLines = document.getElementById("input-lines");
const output = document.getElementById("output");
const diagnostics = document.getElementById("diagnostics");
const exampleSelect = document.getElementById("example-select");
const tutorialSelect = document.getElementById("tutorial-select");
const runButton = document.getElementById("run-button");
const checkButton = document.getElementById("check-button");
const resetButton = document.getElementById("reset-button");
const clearOutputButton = document.getElementById("clear-output-button");
const requestStatus = document.getElementById("request-status");
const exampleNotes = document.getElementById("example-notes");
const tutorialNotes = document.getElementById("tutorial-notes");
const examplesById = new Map();
const tutorialsById = new Map();
const requestControls = [exampleSelect, tutorialSelect, runButton, checkButton, resetButton, clearOutputButton];
const EDITOR_STORAGE_KEY = "steps-web.editor-source";

let isRequestInFlight = false;

editor.value = loadStoredText(EDITOR_STORAGE_KEY) || defaultSource;

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed: ${url}`);
  return response.json();
}

function loadStoredText(key) {
  try {
    return window.localStorage.getItem(key) || "";
  } catch (_error) {
    return "";
  }
}

function saveStoredText(key, value) {
  try {
    window.localStorage.setItem(key, value);
  } catch (_error) {
    // Ignore browser storage failures and keep the playground usable.
  }
}

function persistEditorSource() {
  saveStoredText(EDITOR_STORAGE_KEY, editor.value);
}

async function loadContent() {
  setRequestState(true, "Loading starter content...");
  const hasSavedEditorSource = Boolean(loadStoredText(EDITOR_STORAGE_KEY));

  const [examples, tutorials] = await Promise.all([
    fetchJson("/api/examples"),
    fetchJson("/api/tutorials"),
  ]);

  for (const item of examples.items) {
    examplesById.set(item.id, item);
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.title;
    exampleSelect.append(option);
  }

  for (const item of tutorials.items) {
    tutorialsById.set(item.id, item);
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.title;
    tutorialSelect.append(option);
  }

  exampleSelect.addEventListener("change", () => syncExampleSelection(true));
  tutorialSelect.addEventListener("change", syncTutorialSelection);

  if (exampleSelect.options.length > 0) exampleSelect.selectedIndex = 0;
  if (tutorialSelect.options.length > 0) tutorialSelect.selectedIndex = 0;
  syncExampleSelection(true, hasSavedEditorSource);
  syncTutorialSelection();
  setRequestState(false, "Ready.");
}

function clearContainer(node) {
  node.replaceChildren();
}

function appendParagraph(container, text, className = "") {
  const element = document.createElement("p");
  if (className) element.className = className;
  element.textContent = text;
  container.append(element);
}

function appendList(container, items) {
  if (!Array.isArray(items) || items.length === 0) return;
  const list = document.createElement("ul");
  list.className = "meta-list";

  for (const item of items) {
    const entry = document.createElement("li");
    entry.textContent = item;
    list.append(entry);
  }

  container.append(list);
}

function appendLink(container, label, href) {
  if (!label || !href) return;
  const paragraph = document.createElement("p");
  paragraph.className = "inline-link";
  const link = document.createElement("a");
  link.href = href;
  link.textContent = label;
  if (href.startsWith("http")) {
    link.target = "_blank";
    link.rel = "noreferrer";
  }
  paragraph.append(link);
  container.append(paragraph);
}

function formatDiagnosticLocation(item) {
  const parts = [];
  if (item.file) parts.push(item.file);
  if (item.line) parts.push(`line ${item.line}`);
  return parts.join(" • ");
}

function renderDiagnostics(items, emptyMessage = "No diagnostics yet. Use Check or Run.") {
  clearContainer(diagnostics);

  if (!Array.isArray(items) || items.length === 0) {
    if (emptyMessage) appendParagraph(diagnostics, emptyMessage, "subtle");
    return;
  }

  for (const item of items) {
    const entry = document.createElement("article");
    entry.className = "diagnostic-item";

    const title = document.createElement("p");
    title.className = "diagnostic-title";
    title.textContent = item.code || "Diagnostic";
    entry.append(title);

    const message = document.createElement("p");
    message.className = "diagnostic-message";
    message.textContent = item.message || "Unknown diagnostic.";
    entry.append(message);

    const location = formatDiagnosticLocation(item);
    if (location) appendParagraph(entry, location, "diagnostic-meta");

    diagnostics.append(entry);
  }
}

function setRequestState(isBusy, statusMessage = "Ready.", activeButton = null) {
  isRequestInFlight = isBusy;
  requestStatus.textContent = statusMessage;
  output.setAttribute("aria-busy", String(isBusy));
  diagnostics.setAttribute("aria-busy", String(isBusy));

  for (const control of requestControls) {
    control.disabled = isBusy;
  }

  runButton.textContent = activeButton === runButton ? "Running..." : "Run";
  checkButton.textContent = activeButton === checkButton ? "Checking..." : "Check";
}

function syncExampleSelection(resetInput, preserveEditor = false) {
  const item = examplesById.get(exampleSelect.value);

  if (!preserveEditor) {
    editor.value = item?.step_source || defaultSource;
    persistEditorSource();
  }

  if (resetInput) {
    inputLines.value = Array.isArray(item?.input_lines) ? item.input_lines.join("\n") : "";
  }

  clearContainer(exampleNotes);
  if (!item) return;

  appendParagraph(exampleNotes, item.description || "Load a starter snippet and edit it.");
  appendList(exampleNotes, item.focus_points || []);

  if (Array.isArray(item.input_lines) && item.input_lines.length > 0) {
    appendParagraph(exampleNotes, "Suggested input has been preloaded in the Input panel.", "subtle");
  }
}

function syncTutorialSelection() {
  const item = tutorialsById.get(tutorialSelect.value);
  clearContainer(tutorialNotes);
  if (!item) return;

  appendParagraph(tutorialNotes, item.summary || "");
  appendList(tutorialNotes, item.checklist || []);

  if (item.recommended_example_id && examplesById.get(item.recommended_example_id)) {
    const recommended = examplesById.get(item.recommended_example_id);
    appendParagraph(tutorialNotes, `Try next: ${recommended.title}`, "subtle");
  }

  if (item.learn_more?.label && item.learn_more?.href) {
    appendLink(tutorialNotes, item.learn_more.label, item.learn_more.href);
  }
}

function requestPayload() {
  return {
    step_source: editor.value,
    input_lines: inputLines.value ? inputLines.value.split("\n") : [],
    include_wrapper: false,
  };
}

editor.addEventListener("input", persistEditorSource);

async function callApi(path, pendingLabel, activeButton) {
  if (isRequestInFlight) return;

  setRequestState(true, `${pendingLabel}...`, activeButton);
  output.textContent = `${pendingLabel}...`;
  renderDiagnostics([], "");

  try {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestPayload()),
    });
    if (!response.ok) throw new Error(`Request failed: ${path}`);

    const data = await response.json();
    output.textContent = data.output || "";
    renderDiagnostics(data.diagnostics || []);
  } catch (error) {
    output.textContent = "";
    renderDiagnostics([{ code: "WEB001", message: error.message }], "");
  } finally {
    setRequestState(false, "Ready.");
  }
}

runButton.addEventListener("click", () => callApi("/api/run", "Running", runButton));
checkButton.addEventListener("click", () => callApi("/api/check", "Checking", checkButton));
clearOutputButton.addEventListener("click", () => {
  output.textContent = "";
  renderDiagnostics();
  requestStatus.textContent = "Ready.";
});
resetButton.addEventListener("click", () => {
  syncExampleSelection(true);
  syncTutorialSelection();
  output.textContent = "";
  renderDiagnostics();
  requestStatus.textContent = "Ready.";
});

window.addEventListener("keydown", (event) => {
  if (event.ctrlKey && event.key === "Enter" && !isRequestInFlight) {
    event.preventDefault();
    callApi("/api/run", "Running", runButton);
  }
});

loadContent().catch((error) => {
  setRequestState(false, "Starter content unavailable.");
  renderDiagnostics([{ code: "WEB001", message: `Failed to load starter content: ${error.message}` }], "");
});