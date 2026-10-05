"use strict";
document.addEventListener("DOMContentLoaded", () => {
  let chart;
  const getColor = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const updateThemeIcon = () => document.querySelectorAll(".theme-toggle").forEach(button => {
    const dark = document.documentElement.dataset.theme === "dark";
    button.innerHTML = `<i class="bi bi-${dark ? "sun" : "moon"}" aria-hidden="true"></i>`;
    button.setAttribute("aria-label", `Switch to ${dark ? "light" : "dark"} theme`);
  });
  updateThemeIcon();
  document.querySelectorAll(".theme-toggle").forEach(button => button.addEventListener("click", () => {
    const theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem("pdf-theme", theme); } catch (_) { /* Theme still works without storage. */ }
    updateThemeIcon();
    if (chart) {
      chart.options.scales.x.ticks.color = getColor("--muted");
      chart.options.scales.y.ticks.color = getColor("--muted");
      chart.options.scales.x.grid.color = getColor("--border");
      chart.update();
    }
  }));
  const menu = document.querySelector(".menu-toggle");
  menu?.addEventListener("click", () => {
    const open = document.getElementById("sidebar").classList.toggle("open");
    menu.setAttribute("aria-expanded", String(open));
  });
  document.querySelector(".sidebar-close")?.addEventListener("click", () => {
    document.getElementById("sidebar").classList.remove("open");
    menu?.setAttribute("aria-expanded", "false");
    menu?.focus();
  });
  document.addEventListener("click", event => {
    const sidebar = document.getElementById("sidebar");
    if (sidebar?.classList.contains("open") && !sidebar.contains(event.target) && !menu.contains(event.target)) {
      sidebar.classList.remove("open"); menu.setAttribute("aria-expanded", "false");
    }
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      document.getElementById("sidebar")?.classList.remove("open");
      menu?.setAttribute("aria-expanded", "false");
    }
  });
  document.querySelectorAll(".dismiss-alert").forEach(button => button.addEventListener("click", () => button.closest(".alert").remove()));
  const dialog = document.getElementById("confirm-dialog");
  let pendingForm;
  document.querySelectorAll("form[data-confirm]").forEach(form => form.addEventListener("submit", event => {
    if (form.dataset.confirmed) return;
    event.preventDefault();
    pendingForm = form;
    document.getElementById("confirm-message").textContent = form.dataset.confirm;
    dialog.showModal();
  }));
  dialog?.addEventListener("close", () => {
    if (dialog.returnValue === "confirm" && pendingForm) {
      pendingForm.dataset.confirmed = "true";
      pendingForm.requestSubmit();
    }
    pendingForm = null;
  });
  const tabs = Array.from(document.querySelectorAll(".analysis-tab"));
  const selectTab = id => {
    tabs.forEach(button => {
      const selected = button.dataset.tab === id;
      button.classList.toggle("active", selected);
      button.setAttribute("aria-selected", String(selected));
      button.tabIndex = selected ? 0 : -1;
    });
    document.querySelectorAll(".tab-panel").forEach(panel => { panel.hidden = panel.id !== `panel-${id}`; });
    if (id === "overview") chart?.resize();
  };
  tabs.forEach((button, index) => {
    button.tabIndex = button.classList.contains("active") ? 0 : -1;
    button.addEventListener("click", () => selectTab(button.dataset.tab));
    button.addEventListener("keydown", event => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); selectTab(tabs[next].dataset.tab); tabs[next].focus(); }
    });
  });
  document.querySelectorAll(".tab-link").forEach(button => button.addEventListener("click", () => selectTab(button.dataset.tab)));
  const fullText = document.querySelector(".full-text");
  const query = fullText?.dataset.searchQuery;
  if (query) {
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(escaped, "gi");
    fullText.querySelectorAll(".page-text").forEach(page => {
      const text = page.textContent;
      const fragment = document.createDocumentFragment();
      let cursor = 0;
      for (const match of text.matchAll(pattern)) {
        fragment.append(document.createTextNode(text.slice(cursor, match.index)));
        const mark = document.createElement("mark"); mark.textContent = match[0]; fragment.append(mark);
        cursor = match.index + match[0].length;
      }
      fragment.append(document.createTextNode(text.slice(cursor)));
      page.replaceChildren(fragment);
    });
  }
  const chartData = document.getElementById("chart-data");
  if (chartData && document.getElementById("frequency-chart") && window.Chart) {
    const data = JSON.parse(chartData.textContent);
    chart = new Chart(document.getElementById("frequency-chart"), {
      type: "bar", data: { labels: data.map(item => item.word), datasets: [{ label: "Occurrences", data: data.map(item => item.count), backgroundColor: ["#8370d4", "#9382dc", "#a294e3", "#b0a3e9", "#bdb2ed", "#c7bdf1", "#d0c7f4", "#d8d0f7", "#ded8f9", "#e5e0fb"], borderRadius: 4, barThickness: 14 }] },
      options: { indexAxis: "y", maintainAspectRatio: false, responsive: true, plugins: { legend: { display: false }, tooltip: { padding: 12, displayColors: false } }, scales: { x: { beginAtZero: true, ticks: { color: getColor("--muted"), font: { size: 9 }, precision: 0 }, grid: { color: getColor("--border") }, border: { display: false } }, y: { ticks: { color: getColor("--muted"), font: { size: 10 } }, grid: { display: false }, border: { display: false } } } }
    });
  }
  const uploadForm = document.getElementById("upload-form");
  if (uploadForm) {
    const input = document.getElementById("pdf");
    const zone = document.getElementById("drop-zone");
    const feedback = document.getElementById("file-feedback");
    const button = document.getElementById("analyze-button");
    const defaultButtonContent = button.innerHTML;
    let validFile = false;
    const updateFile = () => {
      const file = input.files[0]; feedback.textContent = ""; validFile = false;
      document.getElementById("selected-file").hidden = !file;
      if (!file) return;
      document.getElementById("selected-name").textContent = file.name;
      document.getElementById("selected-size").textContent = `${(file.size / 1024).toFixed(1)} KB · PDF document`;
      let error;
      if (!file.name.toLowerCase().endsWith(".pdf")) error = "Please choose a PDF file.";
      else if (!file.size) error = "This file is empty. Please choose another PDF.";
      else if (file.size > Number(uploadForm.dataset.maxBytes)) error = "This file exceeds the upload size limit.";
      if (error) { feedback.className = "text-danger small mt-3"; feedback.textContent = error; }
      else validFile = true;
    };
    input.addEventListener("change", updateFile);
    ["dragenter", "dragover"].forEach(type => zone.addEventListener(type, event => { event.preventDefault(); zone.classList.add("drag-over"); }));
    ["dragleave", "drop"].forEach(type => zone.addEventListener(type, event => { event.preventDefault(); zone.classList.remove("drag-over"); }));
    zone.addEventListener("drop", event => {
      if (event.dataTransfer.files.length !== 1) { feedback.className = "text-danger small mt-3"; feedback.textContent = "Please upload one PDF at a time."; return; }
      input.files = event.dataTransfer.files; updateFile();
    });
    document.getElementById("remove-file").addEventListener("click", () => { input.value = ""; updateFile(); input.focus(); });
    uploadForm.addEventListener("submit", event => {
      updateFile();
      if (!validFile) { event.preventDefault(); if (!input.files.length) { feedback.className = "text-danger small mt-3"; feedback.textContent = "Choose a PDF before starting your analysis."; } return; }
      button.disabled = true; document.getElementById("processing-feedback").hidden = false;
      button.textContent = "Analyzing your document…";
    });
    window.addEventListener("pageshow", () => { button.disabled = false; button.innerHTML = defaultButtonContent; document.getElementById("processing-feedback").hidden = true; });
  }
});
