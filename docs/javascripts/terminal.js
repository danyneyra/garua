(function () {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function wait(ms) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
  }

  function optionNumber(element, name, fallback) {
    const value = Number(element.dataset[name]);
    return Number.isFinite(value) ? value : fallback;
  }

  function lineType(text) {
    if (text.startsWith("$ ")) {
      return "input";
    }

    if (/^[\s+:\-]*[█░]+[\s\d%]*$/.test(text)) {
      return "progress";
    }

    if (text.startsWith("INFO:")) {
      return "info";
    }

    return "output";
  }

  function lineText(text) {
    return text.startsWith("$ ") ? text.slice(2) : text;
  }

  function outputType(text) {
    if (/^[\s+:\-]*[█░]+[\s\d%]*$/m.test(text) && !text.includes("\n")) {
      return "progress";
    }

    if (text.startsWith("INFO:")) {
      return "info";
    }

    return "output";
  }

  function normalizeCodeText(text) {
    const lines = text.replace(/\r/g, "").split("\n");

    while (lines.length && lines[0].trim() === "") {
      lines.shift();
    }

    while (lines.length && lines[lines.length - 1].trim() === "") {
      lines.pop();
    }

    return lines;
  }

  function appendLine(codeElement, text, type) {
    const line = document.createElement("span");

    line.dataset.line = "";
    line.dataset.type = type;
    line.dataset.original = text;

    renderLine(line, text);

    if (type === "progress") {
      const blocks = (text.match(/[█░]/g) || []).length;
      line.dataset.progressBlocks = String(blocks || 32);
      line.dataset.progressLabel = text.split(/[█░]/)[0].trimEnd();
    }

    codeElement.append(line);
  }

  function renderLine(line, text) {
    line.textContent = "";

    if (!text) {
      line.textContent = " ";
      return;
    }

    if (!text.includes("\n")) {
      line.textContent = text;
      return;
    }

    text.split("\n").forEach((part, index) => {
      if (index > 0) {
        line.append(document.createElement("br"));
      }

      line.append(document.createTextNode(part || " "));
    });
  }

  function appendOutputBlock(codeElement, outputLines) {
    if (!outputLines.length) {
      return;
    }

    const text = outputLines.join("\n");
    appendLine(codeElement, text, outputType(text));
  }

  function ensureChrome(terminal) {
    if (!terminal.querySelector(".garua-terminal__bar")) {
      const bar = document.createElement("div");
      bar.className = "garua-terminal__bar";
      bar.innerHTML = [
        '<span class="garua-terminal__dot" aria-hidden="true"></span>',
        '<span class="garua-terminal__dot" aria-hidden="true"></span>',
        '<span class="garua-terminal__dot" aria-hidden="true"></span>',
        '<span class="garua-terminal__title">bash</span>',
      ].join("");
      terminal.prepend(bar);
    }

    if (!terminal.querySelector("[data-terminal-copy]")) {
      const copy = document.createElement("button");
      copy.className = "garua-terminal__copy";
      copy.type = "button";
      copy.dataset.terminalCopy = "";
      copy.setAttribute("aria-label", "Copiar comandos");
      copy.textContent = "copiar";
      terminal.querySelector(".garua-terminal__bar").append(copy);
    }

    if (!terminal.querySelector("[data-terminal-replay]")) {
      const replay = document.createElement("button");
      replay.className = "garua-terminal__replay";
      replay.type = "button";
      replay.dataset.terminalReplay = "";
      replay.setAttribute("aria-label", "Reiniciar animación");
      replay.textContent = "reiniciar ↻";
      terminal.append(replay);
    }
  }

  function hydrateCodeBlock(terminal) {
    if (terminal.querySelector("[data-line]")) {
      return;
    }

    const code = terminal.querySelector("pre code, pre");

    if (!code) {
      return;
    }

    const lines = normalizeCodeText(code.textContent);
    const codeElement = document.createElement("div");
    codeElement.className = "garua-terminal__screen";
    const outputMode = terminal.dataset.outputMode || "block";

    if (outputMode === "line") {
      lines.forEach((text) => {
        appendLine(codeElement, lineText(text), lineType(text));
      });
    } else {
      let outputLines = [];

      for (const text of lines) {
        if (text.startsWith("$ ")) {
          appendOutputBlock(codeElement, outputLines);
          outputLines = [];
          appendLine(codeElement, lineText(text), "input");
        } else {
          outputLines.push(text);
        }
      }

      appendOutputBlock(codeElement, outputLines);
    }

    const highlight = terminal.querySelector(".highlight");
    if (highlight) {
      highlight.replaceWith(codeElement);
      return;
    }

    const pre = terminal.querySelector("pre");
    if (pre) {
      pre.replaceWith(codeElement);
    } else {
      terminal.append(codeElement);
    }
  }

  async function typeLine(line, text, terminal, runId) {
    const speed = optionNumber(line, "speed", optionNumber(terminal, "typeSpeed", 26));
    line.textContent = "";
    line.classList.add("is-typing");

    for (const char of text) {
      if (terminal.dataset.runId !== runId) {
        line.classList.remove("is-typing");
        return false;
      }

      line.textContent += char;
      await wait(speed);
    }

    line.classList.remove("is-typing");
    return true;
  }

  async function progressLine(line, terminal, runId) {
    const blocks = Number(line.dataset.progressBlocks || 32);
    const label = line.dataset.progressLabel || "+:";
    const speed = optionNumber(
      line,
      "speed",
      optionNumber(terminal, "progressSpeed", 18),
    );

    line.textContent = "";

    for (let step = 0; step <= blocks; step += 1) {
      if (terminal.dataset.runId !== runId) {
        return false;
      }

      const percent = Math.round((step / blocks) * 100);
      const done = "█".repeat(step);
      const pending = "░".repeat(blocks - step);

      line.textContent = `${label} ${done}${pending} ${percent}%`;
      await wait(speed);
    }

    return true;
  }

  function prepareLines(lines) {
    lines.forEach((line) => {
      if (!line.dataset.original) {
        line.dataset.original = line.textContent;
      }
    });
  }

  function resetLines(terminal, lines) {
    terminal.classList.remove("is-complete");

    lines.forEach((line) => {
      line.textContent = "";
      line.classList.remove("is-visible", "is-typing");
    });
  }

  async function animateTerminal(terminal, options = {}) {
    const lines = Array.from(terminal.querySelectorAll("[data-line]"));
    const replay = terminal.querySelector("[data-terminal-replay]");
    const force = options.force === true;

    if (!force && terminal.dataset.hasAnimated === "true") {
      return;
    }

    if (!force && terminal.dataset.running === "true") {
      return;
    }

    prepareLines(lines);
    const runId = String((Number(terminal.dataset.runId || 0) + 1));
    terminal.dataset.runId = runId;
    terminal.dataset.hasAnimated = "true";
    terminal.dataset.running = "true";
    terminal.classList.remove("is-complete");
    replay && (replay.disabled = true);

    if (reducedMotion) {
      terminal.classList.add("is-ready");
      lines.forEach((line) => {
        renderLine(line, line.dataset.original);
        line.classList.add("is-visible");
      });
      terminal.classList.add("is-complete");
      terminal.dataset.running = "false";
      replay && (replay.disabled = false);
      return;
    }

    resetLines(terminal, lines);
    await wait(80);

    terminal.classList.add("is-ready");
    replay && replay.setAttribute("aria-busy", "true");

    for (const line of lines) {
      const text = line.dataset.original;
      const delay = optionNumber(line, "delay", optionNumber(terminal, "lineDelay", 220));

      await wait(delay);
      if (terminal.dataset.runId !== runId) {
        return;
      }

      line.classList.add("is-visible");

      if (line.dataset.type === "input") {
        const completed = await typeLine(line, text, terminal, runId);
        if (!completed) {
          replay && replay.removeAttribute("aria-busy");
          return;
        }
      } else if (line.dataset.type === "progress") {
        const completed = await progressLine(line, terminal, runId);
        if (!completed) {
          replay && replay.removeAttribute("aria-busy");
          return;
        }
      } else {
        renderLine(line, text);
      }
    }

    terminal.classList.add("is-complete");
    terminal.dataset.running = "false";
    replay && (replay.disabled = false);
    replay && replay.removeAttribute("aria-busy");
  }

  function restartTerminal(terminal) {
    const lines = Array.from(terminal.querySelectorAll("[data-line]"));

    terminal.dataset.runId = String((Number(terminal.dataset.runId || 0) + 1));
    resetLines(terminal, lines);
    window.setTimeout(() => animateTerminal(terminal, { force: true }), 80);
  }

  function bindReplay(terminal) {
    const replay = terminal.querySelector("[data-terminal-replay]");

    if (!replay || replay.dataset.bound === "true") {
      return;
    }

    replay.dataset.bound = "true";
    replay.addEventListener("click", () => {
      restartTerminal(terminal);
    });
  }

  function copyText(terminal) {
    if (terminal.dataset.copyText) {
      return terminal.dataset.copyText;
    }

    const lines = Array.from(terminal.querySelectorAll("[data-line]"));
    const mode = terminal.dataset.copyMode || "input";

    if (mode === "all") {
      return lines.map((line) => line.dataset.original || "").join("\n").trim();
    }

    return lines
      .filter((line) => line.dataset.type === "input")
      .map((line) => line.dataset.original || "")
      .join("\n")
      .trim();
  }

  async function writeClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }

    const input = document.createElement("textarea");
    input.value = text;
    input.setAttribute("readonly", "");
    input.style.position = "absolute";
    input.style.left = "-9999px";
    document.body.append(input);
    input.select();
    document.execCommand("copy");
    input.remove();
  }

  function bindCopy(terminal) {
    const copy = terminal.querySelector("[data-terminal-copy]");

    if (!copy || copy.dataset.bound === "true") {
      return;
    }

    copy.dataset.bound = "true";
    copy.addEventListener("click", async () => {
      const text = copyText(terminal);

      if (!text) {
        return;
      }

      await writeClipboard(text);
      copy.textContent = "copiado";
      window.setTimeout(() => {
        copy.textContent = "copiar";
      }, 1400);
    });
  }

  function init() {
    document.querySelectorAll("[data-garua-terminal]").forEach((terminal) => {
      ensureChrome(terminal);
      hydrateCodeBlock(terminal);
      bindCopy(terminal);
      bindReplay(terminal);
      animateTerminal(terminal);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  }
})();
