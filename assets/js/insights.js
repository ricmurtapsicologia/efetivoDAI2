/* DAI/2 — Camada gerencial 2.6.0. Somente agregados da base publica. */
(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  };
  const number = (value) => Number(value) || 0;
  const label = (org) => (window.DAI2_RUNTIME?.orgDisplay || {})[org] || org;
  const storeKey = "dai2_decision_checklist_v1";
  const readState = () => {
    try { const value = JSON.parse(localStorage.getItem(storeKey) || "{}"); return value && typeof value === "object" ? value : {}; }
    catch (_) { return {}; }
  };
  const saveState = (state) => {
    try { localStorage.setItem(storeKey, JSON.stringify(state)); }
    catch (_) { /* A lista continua funcional sem persistencia. */ }
  };
  const ageInDays = (text) => {
    const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(String(text || ""));
    if (!match) return null;
    const time = Date.UTC(+match[3], +match[2] - 1, +match[1]);
    if (new Date(time).toISOString().slice(0, 10) !== [match[3],match[2],match[1]].join("-")) return null;
    return Math.max(0, Math.floor((Date.now() - time) / 86400000));
  };
  const sum = (rows, field) => rows.reduce((acc, row) => acc + number(row[1][field]), 0);
  const currentRows = () => Object.entries(window.DAI2_RUNTIME?.metrics || {});
  const displayFeedback = (message) => { const node = $("#decisionFeedback"); if (node) node.textContent = message; };
  const source = () => window.DAI2_META || {};
  const tpb = () => window.DAI_TPB_META?.current || {};
  const sortedGaps = (rows) => rows.filter((entry) => number(entry[1].claro) > 0)
    .sort((a, b) => number(b[1].claro) - number(a[1].claro) || label(a[0]).localeCompare(label(b[0]), "pt-BR"));
  const actions = [
    { id: "base", title: "Conferir a ficha-mestre do efetivo e validar a data-base.", target: "dataCutoff" },
    { id: "claros", title: "Avaliar claros por posto/graduação, com decisão fundamentada.", target: "decisionPriorities" },
    { id: "excedentes", title: "Verificar excedentes por posto/graduação sem compensação indevida.", target: "decisionStats" },
    { id: "instrumentos", title: "Conferir atos e vigências dos instrumentos nas fontes oficiais.", target: "normasToggleBtn" }
  ];
  function render() {
    const rows = currentRows();
    const container = $("#decisionPanel");
    if (!container || !rows.length) return;
    const meta = source(), age = ageInDays(meta.dataCutoff);
    const totalPlanned = sum(rows, "planned"), totalExisting = sum(rows, "existing");
    const totalGap = sum(rows, "claro");
    const totalExcess = rows.reduce((acc, entry) => acc + (entry[0] === "SEMAD" ? 0 : number(entry[1].excess)), 0);
    const extra = rows.reduce((acc, entry) => acc + (entry[0] === "SEMAD" ? number(entry[1].existing) : 0), 0);
    const stats = $("#decisionStats");
    const cards = [
      ["Órgãos monitorados", rows.length, "Distribuição da base consultada"],
      ["Claros por P/G", totalGap, "Não equivalem à diferença global"],
      ["Excedentes por P/G", totalExcess, "Não compensam claros de outra P/G"],
      ["Extra-DDQOD", extra, "Implantação SEMAD"]
    ];
    stats.replaceChildren(...cards.map(([title, value, hint]) => {
      const card = element("div", "decision-stat");
      card.append(element("span", "decision-stat-title", title),
        element("strong", "decision-stat-value", value),
        element("span", "decision-stat-hint", hint));
      return card;
    }));
    const freshness = $("#decisionFreshness");
    freshness.className = "decision-freshness " + (age === null || age > 30 ? "needs-review" : "is-current");
    const freshnessMsg = age === null ? "Data-base não identificada: validar antes de decidir."
      : "Efetivo: " + meta.dataCutoff + " · " + age + (age === 1 ? " dia" : " dias") + " desde a referência" +
      (age > 30 ? " · Conferência recomendada" : " · Referência recente");
    freshness.textContent = freshnessMsg;
    const gaps = sortedGaps(rows), priorities = $("#decisionPriorities");
    priorities.replaceChildren();
    gaps.slice(0, 5).forEach(([org, metric]) => {
      const item = element("button", "decision-org");
      item.type = "button";
      const heading = element("span", "decision-org-name", label(org));
      const numbers = element("span", "decision-org-detail", "Claro " + number(metric.claro) + " · Previsto " + number(metric.planned) + " · Existente " + number(metric.existing));
      item.append(heading, numbers);
      item.addEventListener("click", () => {
        const block = Array.from(document.querySelectorAll(".block[data-orgao]")).find((node) => node.dataset.orgao === org);
        if (block) block.click();
      });
      priorities.append(item);
    });
    if (!gaps.length) priorities.append(element("p", "decision-empty", "Nenhum claro por P/G na base consultada."));
    const summary = $("#decisionPriorityNote");
    summary.textContent = "Ordenação exclusivamente quantitativa. Impacto operacional e prioridade administrativa dependem de análise da coordenação.";
    const governance = $("#decisionGovernance");
    const legalGroups = Object.values(window.DAI2_LEGAL || {});
    const legalCount = legalGroups.reduce((n, group) => n + (Array.isArray(group.items) ? group.items.length : 0), 0);
    governance.textContent = legalCount + " referência(s) documentais correlatas cadastradas. A página não atesta vigência: conferir o instrumento e o processo SEI antes de decidir. TPB: " +
      (tpb().asOf || "sem posição") + " (posição administrativa, não individualizada).";
    renderActions();
    $("#decisionLegalBtn")?.addEventListener("click", () => $("#normasToggleBtn")?.click());
    $("#decisionTpbBtn")?.addEventListener("click", () => $("#tpbToggleBtn")?.click());
    $("#decisionCopyBtn")?.addEventListener("click", () => copySummary({ rows, gaps, age, meta, totalPlanned, totalExisting, totalGap, totalExcess, extra }));
    const filter = $("#decisionFilterBtn");
    filter?.addEventListener("click", () => {
      const activated = filter.getAttribute("aria-pressed") !== "true";
      filter.setAttribute("aria-pressed", String(activated));
      filter.textContent = activated ? "Mostrar todos os órgãos" : "Exibir apenas órgãos com claro";
      document.querySelectorAll(".block[data-orgao]").forEach((block) => {
        const metric = (window.DAI2_RUNTIME?.metrics || {})[block.dataset.orgao];
        block.hidden = Boolean(activated && (!metric || number(metric.claro) === 0));
      });
      displayFeedback(activated ? "Filtro de claro aplicado. Os demais órgãos continuam na base." : "Todos os órgãos estão visíveis.");
    });
  }
  function renderActions() {
    const root = $("#decisionActions");
    if (!root) return;
    const state = readState();
    root.replaceChildren();
    actions.forEach((action) => {
      const row = element("label", "decision-action");
      const check = element("input");
      check.type = "checkbox";
      check.checked = state[action.id] === true;
      check.setAttribute("aria-label", action.title);
      check.addEventListener("change", () => {
        state[action.id] = check.checked;
        saveState(state);
        displayFeedback("Acompanhamento salvo somente neste navegador.");
      });
      row.append(check, element("span", "", action.title));
      root.append(row);
    });
  }
  function copySummary(info) {
    const top = info.gaps.slice(0, 5).map(([org, m]) => "• " + label(org) + ": " + number(m.claro) + " claro(s) P/G").join("\n");
    const text = [
      "DAI/2 — Síntese gerencial do efetivo",
      "Fonte do efetivo: " + (info.meta.dataCutoff || "sem data") + " (não equivale à posição atual)",
      "Fonte DDQOD: " + (info.meta.ddqodSource || "a conferir"),
      "Previsto: " + info.totalPlanned + " | Existente: " + info.totalExisting,
      "Claros por posto/graduação: " + info.totalGap + " | Excedentes DDQOD por P/G: " + info.totalExcess,
      "Extra-DDQOD (SEMAD): " + info.extra,
      "Maiores claros quantitativos:\n" + (top || "Nenhum na base consultada"),
      "TPB: posição administrativa de " + (tpb().asOf || "data não informada") + ".",
      "Validação das informações e priorização operacional dependem da coordenação DAI/2."
    ].join("\n");
    const fallback = () => {
      const textarea = element("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      document.body.append(textarea);
      textarea.select();
      let done = false;
      try { done = document.execCommand("copy"); } catch (_) { /* sem permissão */ }
      textarea.remove();
      displayFeedback(done ? "Síntese copiada." : "Cópia não autorizada pelo navegador.");
    };
    if (navigator.clipboard?.writeText && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(() => displayFeedback("Síntese copiada."), fallback);
    } else fallback();
  }
  document.addEventListener("DOMContentLoaded", render);
})();
