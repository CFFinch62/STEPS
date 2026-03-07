window.registerStepsLanguage = function registerStepsLanguage(monaco) {
  monaco.languages.register({ id: "steps" })

  const structureKeywords = ["building:", "floor:", "step:", "riser:"]
  const clauseKeywords = ["belongs to:", "expects:", "returns:", "declare:", "do:", "attempt:", "if unsuccessful:", "then continue:"]
  const controlKeywords = ["otherwise if", "otherwise", "while", "repeat", "times", "for each", "exit", "in", "if"]
  const keywordWords = ["set", "to", "as", "fixed", "from", "iteration", "limit", "add", "remove"]
  const functionKeywords = ["storing result in", "call", "with", "return"]
  const builtins = ["clear console", "display", "indicate", "input"]
  const types = ["number", "text", "boolean", "list", "table"]
  const booleans = ["true", "false", "nothing"]
  const wordOperators = [
    "is greater than or equal to",
    "is less than or equal to",
    "is not equal to",
    "is greater than",
    "is less than",
    "is a boolean",
    "is a number",
    "is a table",
    "is a list",
    "is a text",
    "is equal to",
    "type of",
    "length of",
    "added to",
    "starts with",
    "ends with",
    "split by",
    "character at",
    "is in",
    "contains",
    "equals",
    "modulo",
    "and",
    "or",
    "not",
  ]

  const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  const joinAlternatives = (values) => [...values]
    .sort((left, right) => right.length - left.length)
    .map((value) => escapeRegExp(value).replace(/ /g, "\\s+"))
    .join("|")

  const structurePattern = new RegExp(`\\b(?:${joinAlternatives(structureKeywords)})`, "i")
  const clausePattern = new RegExp(`\\b(?:${joinAlternatives(clauseKeywords)})`, "i")
  const controlPattern = new RegExp(`\\b(?:${joinAlternatives(controlKeywords)})\\b`, "i")
  const keywordPattern = new RegExp(`\\b(?:${joinAlternatives(keywordWords)})\\b`, "i")
  const functionPattern = new RegExp(`\\b(?:${joinAlternatives(functionKeywords)})\\b`, "i")
  const builtinPattern = new RegExp(`\\b(?:${joinAlternatives(builtins)})\\b`, "i")
  const typePattern = new RegExp(`\\b(?:${joinAlternatives(types)})\\b`, "i")
  const booleanPattern = new RegExp(`\\b(?:${joinAlternatives(booleans)})\\b`, "i")
  const wordOperatorPattern = new RegExp(`\\b(?:${joinAlternatives(wordOperators)})\\b`, "i")

  const blockStarterPattern = /^\s*(?:building:.*|floor:.*|step:.*|riser:.*|belongs to:.*|expects:.*|returns:.*|declare:.*|do:.*|attempt:.*|if unsuccessful:.*|then continue:.*|if\b.*|otherwise\s+if\b.*|otherwise\b\s*|while\b.*|repeat\b.*|for each\b.*)$/i
  const outdentClausePattern = /^\s*(?:floor:.*|step:.*|riser:.*|belongs to:.*|expects:.*|returns:.*|declare:.*|do:.*|if unsuccessful:.*|then continue:.*|otherwise\s+if\b.*|otherwise\b\s*)$/i

  monaco.languages.setLanguageConfiguration("steps", {
    comments: {
      lineComment: "note:",
    },
    brackets: [
      ["(", ")"],
      ["[", "]"],
      ["{", "}"],
    ],
    autoClosingPairs: [
      { open: "(", close: ")" },
      { open: "[", close: "]" },
      { open: "{", close: "}" },
      { open: '"', close: '"', notIn: ["string", "comment"] },
    ],
    surroundingPairs: [
      { open: "(", close: ")" },
      { open: "[", close: "]" },
      { open: "{", close: "}" },
      { open: '"', close: '"' },
    ],
    indentationRules: {
      increaseIndentPattern: blockStarterPattern,
      decreaseIndentPattern: outdentClausePattern,
    },
    onEnterRules: [
      {
        beforeText: blockStarterPattern,
        action: { indentAction: monaco.languages.IndentAction.Indent },
      },
    ],
  })

  monaco.languages.setMonarchTokensProvider("steps", {
    defaultToken: "",
    tokenPostfix: ".steps",
    tokenizer: {
      root: [
        [/^[ \t]*note:.*$/, "comment"],
        [/"/, { token: "string.quote", next: "@string" }],
        [/-?\b\d+\.\d+\b/, "number.float"],
        [/-?\b\d+\b/, "number"],
        [wordOperatorPattern, "operator.word"],
        [structurePattern, "keyword.structure"],
        [clausePattern, "keyword.clause"],
        [functionPattern, "keyword.function"],
        [builtinPattern, "predefined"],
        [typePattern, "type"],
        [booleanPattern, "constant"],
        [controlPattern, "keyword.control"],
        [keywordPattern, "keyword"],
        [/[+\-*/=]/, "operator"],
        [/[()[\]{},.:]/, "delimiter"],
        [/[A-Za-z_][A-Za-z0-9_]*/, "identifier"],
        [/[ \t]+/, "white"],
      ],
      string: [
        [/[^"\\]+/, "string"],
        [/\\./, "string.escape"],
        [/"/, { token: "string.quote", next: "@pop" }],
      ],
    },
  })

  monaco.editor.defineTheme("steps-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "comment", foreground: "94a3b8", fontStyle: "italic" },
      { token: "keyword.structure", foreground: "60a5fa", fontStyle: "bold" },
      { token: "keyword.clause", foreground: "93c5fd" },
      { token: "keyword.control", foreground: "c084fc", fontStyle: "bold" },
      { token: "keyword.function", foreground: "f9a8d4" },
      { token: "keyword", foreground: "cbd5e1" },
      { token: "predefined", foreground: "34d399" },
      { token: "type", foreground: "fbbf24" },
      { token: "constant", foreground: "f59e0b" },
      { token: "string", foreground: "86efac" },
      { token: "string.quote", foreground: "86efac" },
      { token: "string.escape", foreground: "fdba74" },
      { token: "number", foreground: "fdba74" },
      { token: "number.float", foreground: "fdba74" },
      { token: "operator", foreground: "e2e8f0" },
      { token: "operator.word", foreground: "e879f9" },
      { token: "delimiter", foreground: "cbd5e1" },
      { token: "identifier", foreground: "e2e8f0" },
    ],
    colors: {
      "editor.background": "#020617",
      "editor.foreground": "#e2e8f0",
      "editorLineNumber.foreground": "#475569",
      "editorCursor.foreground": "#60a5fa",
      "editor.selectionBackground": "#1d4ed880",
      "editor.lineHighlightBackground": "#0f172a",
      "editorIndentGuide.background1": "#1e293b",
    },
  })
}