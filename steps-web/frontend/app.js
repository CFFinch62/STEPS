const defaultSource = `step: main
    do:
        display "Hello from Steps Web"
`;

const DEFAULT_CONSOLE_TEXT = "Ready. Use Run or Check to try the current code.";
const MODE_LABELS = {
  examples: "Choose example",
  tutorials: "Choose tutorial",
};
const NOTES_TITLES = {
  examples: "Example Notes",
  tutorials: "Tutorial Notes",
};

const editorElement = document.getElementById("editor");
const inputLines = document.getElementById("input-lines");
const output = document.getElementById("output");
const lessonSelect = document.getElementById("lesson-select");
const lessonLabel = document.getElementById("lesson-label");
const notesTitle = document.getElementById("notes-title");
const learningNotes = document.getElementById("learning-notes");
const modeButtons = Array.from(document.querySelectorAll(".mode-button"));
const aboutPlaygroundButton = document.getElementById("about-playground-button");
const aboutPlaygroundDialog = document.getElementById("about-playground-dialog");
const aboutPlaygroundClose = document.getElementById("about-playground-close");
const runButton = document.getElementById("run-button");
const checkButton = document.getElementById("check-button");
const resetButton = document.getElementById("reset-button");
const clearOutputButton = document.getElementById("clear-output-button");
const requestStatus = document.getElementById("request-status");
const examplesById = new Map();
const tutorialsById = new Map();
const requestControls = [lessonSelect, ...modeButtons, runButton, checkButton, resetButton, clearOutputButton];
const EDITOR_STORAGE_KEY = "steps-web.editor-source";

let isRequestInFlight = false;
let currentMode = "examples";
let exampleItems = [];
let tutorialItems = [];
let currentSelections = {
  examples: "",
  tutorials: "",
};
let editor = null;
const initialEditorSource = loadStoredText(EDITOR_STORAGE_KEY) || defaultSource;

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

function getEditorValue() {
  return editor ? editor.getValue() : initialEditorSource;
}

function setEditorValue(value) {
  if (editor) editor.setValue(value || "");
}

function persistEditorSource() {
  saveStoredText(EDITOR_STORAGE_KEY, getEditorValue());
}

function clearContainer(node) {
  node.replaceChildren();
}

function appendParagraph(container, text, className = "") {
  if (!text) return;
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

function getItemsForMode(mode = currentMode) {
  return mode === "tutorials" ? tutorialItems : exampleItems;
}

function getSelectedItem(mode = currentMode) {
  const selectionId = currentSelections[mode];
  if (!selectionId) return null;
  return mode === "tutorials" ? tutorialsById.get(selectionId) : examplesById.get(selectionId);
}

function getStarterExample(mode = currentMode) {
  if (mode === "examples") return getSelectedItem("examples");

  const tutorial = getSelectedItem("tutorials");
  if (!tutorial?.recommended_example_id) return null;
  return examplesById.get(tutorial.recommended_example_id) || null;
}

function populateLessonSelect() {
  clearContainer(lessonSelect);

  const items = getItemsForMode();
  const validSelection = items.some((item) => item.id === currentSelections[currentMode]);
  currentSelections[currentMode] = validSelection ? currentSelections[currentMode] : items[0]?.id || "";

  for (const item of items) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.title;
    lessonSelect.append(option);
  }

  lessonSelect.value = currentSelections[currentMode];
}

function updateModeButtons() {
  for (const button of modeButtons) {
    const isActive = button.dataset.mode === currentMode;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  }
}

function renderLearningNotes() {
  clearContainer(learningNotes);

  if (currentMode === "examples") {
    const item = getSelectedItem("examples");
    if (!item) return;

    appendParagraph(learningNotes, item.description || "Load a starter snippet and edit it.");
    appendList(learningNotes, item.focus_points || []);

    if (Array.isArray(item.input_lines) && item.input_lines.length > 0) {
      appendParagraph(learningNotes, "Suggested input has been preloaded below the console.", "subtle");
    }
    return;
  }

  const tutorial = getSelectedItem("tutorials");
  const starter = getStarterExample("tutorials");
  if (!tutorial) return;

  appendParagraph(learningNotes, tutorial.summary || "");
  appendList(learningNotes, tutorial.checklist || []);

  if (starter?.title) {
    appendParagraph(learningNotes, `Starter code loaded: ${starter.title}.`, "subtle");
  }

  if (Array.isArray(starter?.input_lines) && starter.input_lines.length > 0) {
    appendParagraph(learningNotes, "Suggested input has been preloaded below the console.", "subtle");
  }
}

function syncCurrentSelection(resetInput, preserveEditor = false) {
  currentSelections[currentMode] = lessonSelect.value || currentSelections[currentMode];
  const starter = getStarterExample();

  if (!preserveEditor) {
    setEditorValue(starter?.step_source || defaultSource);
    persistEditorSource();
  }

  if (resetInput) {
    inputLines.value = Array.isArray(starter?.input_lines) ? starter.input_lines.join("\n") : "";
  }

  renderLearningNotes();
}

function renderModeView(options = {}) {
  const { resetInput = false, preserveEditor = false } = options;
  lessonLabel.textContent = MODE_LABELS[currentMode];
  notesTitle.textContent = NOTES_TITLES[currentMode];
  populateLessonSelect();
  updateModeButtons();
  syncCurrentSelection(resetInput, preserveEditor);
}

function switchMode(mode) {
  if (!mode || mode === currentMode) return;
  currentSelections[currentMode] = lessonSelect.value || currentSelections[currentMode];
  currentMode = mode;
  renderModeView({ resetInput: true });
  requestStatus.textContent = "Ready.";
}

function formatDiagnosticLocation(item) {
  const parts = [];
  if (item.file) parts.push(item.file);
  if (item.line) parts.push(`line ${item.line}`);
  return parts.join(" • ");
}

function formatDiagnosticsText(items) {
  return items.map((item) => {
    const headline = item.code ? `[${item.code}] ${item.message || "Unknown problem."}` : item.message || "Unknown problem.";
    const location = formatDiagnosticLocation(item);
    return location ? `${headline}\nat ${location}` : headline;
  }).join("\n\n");
}

function renderConsole({ outputText = "", diagnostics = [], successMessage = "" } = {}) {
  const blocks = [];
  const trimmedOutput = outputText ? outputText.replace(/\s+$/, "") : "";

  if (trimmedOutput) blocks.push(trimmedOutput);

  if (Array.isArray(diagnostics) && diagnostics.length > 0) {
    blocks.push(`Problems:\n${formatDiagnosticsText(diagnostics)}`);
  }

  if (blocks.length === 0 && successMessage) blocks.push(successMessage);
  output.textContent = blocks.join("\n\n");
}

function setRequestState(isBusy, statusMessage = "Ready.", activeButton = null) {
  isRequestInFlight = isBusy;
  requestStatus.textContent = statusMessage;
  output.setAttribute("aria-busy", String(isBusy));

  for (const control of requestControls) {
    control.disabled = isBusy;
  }

  runButton.textContent = activeButton === runButton ? "Running..." : "Run";
  checkButton.textContent = activeButton === checkButton ? "Checking..." : "Check";
}

function requestPayload() {
  return {
    step_source: getEditorValue(),
    input_lines: inputLines.value ? inputLines.value.split("\n") : [],
    include_wrapper: false,
  };
}

function openAboutPlaygroundDialog() {
  if (!aboutPlaygroundDialog) return;

  if (typeof aboutPlaygroundDialog.showModal === "function") {
    aboutPlaygroundDialog.showModal();
    return;
  }

  aboutPlaygroundDialog.setAttribute("open", "open");
}

function closeAboutPlaygroundDialog() {
  if (!aboutPlaygroundDialog) return;

  if (typeof aboutPlaygroundDialog.close === "function") {
    aboutPlaygroundDialog.close();
    return;
  }

  aboutPlaygroundDialog.removeAttribute("open");
}

lessonSelect.addEventListener("change", () => syncCurrentSelection(true));

for (const button of modeButtons) {
  button.addEventListener("click", () => switchMode(button.dataset.mode));
}

if (aboutPlaygroundButton) {
  aboutPlaygroundButton.addEventListener("click", openAboutPlaygroundDialog);
}

if (aboutPlaygroundClose) {
  aboutPlaygroundClose.addEventListener("click", closeAboutPlaygroundDialog);
}

if (aboutPlaygroundDialog) {
  aboutPlaygroundDialog.addEventListener("click", (event) => {
    const bounds = aboutPlaygroundDialog.getBoundingClientRect();
    const clickedInside = (
      event.clientX >= bounds.left &&
      event.clientX <= bounds.right &&
      event.clientY >= bounds.top &&
      event.clientY <= bounds.bottom
    );

    if (!clickedInside) {
      closeAboutPlaygroundDialog();
    }
  });
}

async function callApi(path, pendingLabel, activeButton, successMessage) {
  if (isRequestInFlight) return;

  setRequestState(true, `${pendingLabel}...`, activeButton);
  output.textContent = `${pendingLabel}...`;

  try {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestPayload()),
    });
    if (!response.ok) throw new Error(`Request failed: ${path}`);

    const data = await response.json();
    renderConsole({
      outputText: data.output || "",
      diagnostics: data.diagnostics || [],
      successMessage,
    });
  } catch (error) {
    renderConsole({ diagnostics: [{ code: "WEB001", message: error.message }] });
  } finally {
    setRequestState(false, "Ready.");
  }
}

runButton.addEventListener("click", () => callApi("/api/run", "Running", runButton, "Program finished with no output."));
checkButton.addEventListener("click", () => callApi("/api/check", "Checking", checkButton, "No problems found."));
clearOutputButton.addEventListener("click", () => {
  output.textContent = "";
  requestStatus.textContent = "Ready.";
});
resetButton.addEventListener("click", () => {
  syncCurrentSelection(true);
  output.textContent = DEFAULT_CONSOLE_TEXT;
  requestStatus.textContent = "Ready.";
});

window.addEventListener("keydown", (event) => {
  if (event.ctrlKey && event.key === "Enter" && !isRequestInFlight) {
    event.preventDefault();
    callApi("/api/run", "Running", runButton, "Program finished with no output.");
  }
});

async function loadContent() {
  setRequestState(true, "Loading starter content...");
  const hasSavedEditorSource = Boolean(loadStoredText(EDITOR_STORAGE_KEY));

  const [examples, tutorials] = await Promise.all([
    fetchJson("/api/examples"),
    fetchJson("/api/tutorials"),
  ]);

  exampleItems = Array.isArray(examples.items) ? examples.items : [];
  tutorialItems = Array.isArray(tutorials.items)
    ? tutorials.items.filter((item) => item.id !== "next-step-full-product")
    : [];

  for (const item of exampleItems) {
    examplesById.set(item.id, item);
  }

  for (const item of tutorialItems) {
    tutorialsById.set(item.id, item);
  }

  currentSelections.examples = exampleItems[0]?.id || "";
  currentSelections.tutorials = tutorialItems[0]?.id || "";

  renderModeView({ resetInput: true, preserveEditor: hasSavedEditorSource });
  setRequestState(false, "Ready.");
}

setRequestState(true, "Loading editor...");

window.initApp = async function initApp(monaco) {
  if (typeof window.registerStepsLanguage !== "function") {
    throw new Error("Steps language definition did not load.");
  }

  window.registerStepsLanguage(monaco);
  editor = monaco.editor.create(editorElement, {
    value: initialEditorSource,
    language: "steps",
    theme: "steps-dark",
    autoIndent: "full",
    fontSize: 14,
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace",
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    lineNumbers: "on",
    tabSize: 4,
    insertSpaces: true,
    wordWrap: "off",
    wrappingIndent: "none",
    renderLineHighlight: "line",
  });

  editor.onDidChangeModelContent(persistEditorSource);
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
    if (!isRequestInFlight) {
      callApi("/api/run", "Running", runButton, "Program finished with no output.");
    }
  });

  try {
    await loadContent();
  } catch (error) {
    setRequestState(false, "Starter content unavailable.");
    renderConsole({ diagnostics: [{ code: "WEB001", message: `Failed to load starter content: ${error.message}` }] });
  }
};