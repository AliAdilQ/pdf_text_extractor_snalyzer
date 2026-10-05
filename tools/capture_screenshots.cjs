/* Capture real UI screenshots and verify the local app. Run after seeding. */
const { chromium } = require("playwright");
const path = require("node:path");
const fs = require("node:fs/promises");
const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const readline = require("node:readline");
const root = path.resolve(__dirname, "..");
const base = process.env.APP_URL || "http://127.0.0.1:5000";

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.BROWSER_EXECUTABLE || undefined, channel: process.env.BROWSER_CHANNEL || undefined });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
  const page = await context.newPage();
  let bridge;
  let uploadFormData;
  if (process.env.APP_BROWSER_BRIDGE === "1") {
    bridge = spawn(process.env.PYTHON_EXECUTABLE || "python", [path.join(root, "tools/browser_bridge.py")], { cwd: root, stdio: ["pipe", "pipe", "inherit"], windowsHide: true });
    let nextId = 0;
    const pending = new Map();
    readline.createInterface({ input: bridge.stdout }).on("line", line => {
      const response = JSON.parse(line);
      pending.get(response.id)?.(response);
      pending.delete(response.id);
    });
    await page.route(`${base}/**`, async route => {
      const request = route.request();
      const id = nextId++;
      const result = new Promise(resolve => pending.set(id, resolve));
      const message = { id, url: request.url(), method: request.method(), headers: await request.allHeaders(), body: (request.postDataBuffer() || Buffer.alloc(0)).toString("base64") };
      if (request.method() === "POST" && new URL(request.url()).pathname === "/upload") {
        // Chromium's request metadata omits binary file parts; transport the
        // exact selected browser File and actual form fields separately.
        message.formdata = uploadFormData;
      }
      bridge.stdin.write(JSON.stringify(message) + "\n");
      const response = await result;
      if (response.status >= 300 && response.status < 400 && response.headers.Location) {
        // Route interception does not cover Chromium's internal redirect chain.
        // Preserve real cookies and issue a new navigation for the real redirect.
        const headers = { ...response.headers, "Content-Type": "text/html; charset=utf-8" };
        delete headers["Content-Length"];
        await route.fulfill({ status: 200, headers, body: `<!doctype html><script>location.replace(${JSON.stringify(response.headers.Location)})</script>` });
      } else {
        await route.fulfill({ status: response.status, headers: response.headers, body: Buffer.from(response.body, "base64") });
      }
    });
  }
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  page.on("response", response => { if (response.status() >= 500) errors.push(`${response.status()} ${response.url()}`); });
  await fs.mkdir(path.join(root, "screenshots"), { recursive: true });
  await fs.mkdir(path.join(root, "tmp", "browser"), { recursive: true });
  async function visit(route) {
    const response = await page.goto(base + route, { waitUntil: "networkidle" });
    assert.equal(response.status(), 200, `${route} should open`);
    await page.evaluate(() => document.fonts.ready);
  }
  async function capture(name) {
    await page.screenshot({ path: path.join(root, "screenshots", `${name}.png`), animations: "disabled", fullPage: ["dashboard", "analysis", "admin-dashboard"].includes(name) });
    console.log(`Captured screenshots/${name}.png`);
  }
  async function login(username, password) {
    await visit("/login");
    await page.getByLabel("Email or username").fill(username);
    await page.getByLabel("Password", { exact: true }).fill(password);
    await Promise.all([page.waitForURL("**/dashboard"), page.getByRole("button", { name: "Sign in", exact: true }).click()]);
  }
  try {
    await visit("/"); await capture("home");
    await visit("/login"); await capture("login");
    await login("demo", "Demo123!");
    await page.waitForLoadState("networkidle"); await capture("dashboard");
    await visit("/documents");
    await page.getByLabel("Search filenames").fill("Python");
    await page.getByRole("button", { name: "Apply" }).click();
    await page.waitForLoadState("networkidle");
    assert.equal(await page.locator("tbody tr").count(), 1);
    await visit("/upload"); await capture("upload");
    await page.locator("#pdf").setInputFiles(path.join(root, "sample_data", "Python Programming Guide.pdf"));
    if (bridge) uploadFormData = await page.evaluate(async () => {
      const entries = [];
      for (const [key, value] of new FormData(document.getElementById("upload-form"))) {
        if (value instanceof File) {
          const bytes = new Uint8Array(await value.arrayBuffer());
          let binary = "";
          for (const byte of bytes) binary += String.fromCharCode(byte);
          entries.push({ key, file: btoa(binary), filename: value.name, type: value.type });
        } else entries.push({ key, value });
      }
      return entries;
    });
    await page.getByRole("button", { name: "Extract & analyze" }).click();
    await page.waitForURL(/\/documents\/\d+$/);
    const uploadedUrl = page.url();
    await page.locator(".dismiss-alert").click();
    await page.waitForLoadState("networkidle"); await capture("analysis");
    assert.ok(await page.locator("#frequency-chart").evaluate(canvas => canvas.width > 0));
    await page.getByRole("tab", { name: "Extracted text" }).click();
    await page.getByLabel("Search extracted text").fill("Python");
    await page.getByRole("button", { name: "Search text" }).click();
    await page.waitForLoadState("networkidle");
    assert.ok(await page.locator(".full-text mark").count() > 0);
    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("link", { name: "Download TXT" }).click();
    const download = await downloadPromise;
    assert.ok(download.suggestedFilename().endsWith("_extracted.txt"));
    await download.saveAs(path.join(root, "tmp/browser/exported.txt"));
    assert.match(await fs.readFile(path.join(root, "tmp/browser/exported.txt"), "utf8"), /Python/);
    const denied = await page.goto(base + "/admin");
    assert.equal(denied.status(), 403);
    await visit("/dashboard");
    await page.getByRole("button", { name: "Switch to dark theme" }).click();
    assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
    await page.reload();
    assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
    await page.screenshot({ path: path.join(root, "tmp/browser/dashboard-dark.png") });
    await page.getByRole("button", { name: "Switch to light theme" }).click();
    await visit("/documents");
    const id = new URL(uploadedUrl).pathname.split("/").pop();
    await page.locator(`form[action='/documents/${id}/delete'] button`).click();
    await page.getByRole("button", { name: "Delete permanently" }).click();
    await page.waitForURL("**/documents");
    const deleted = await page.goto(uploadedUrl);
    assert.equal(deleted.status(), 404);
    await visit("/dashboard");
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, "Dashboard should fit mobile viewport");
    await page.getByRole("button", { name: "Toggle navigation" }).click();
    assert.ok(await page.locator("#sidebar").evaluate(el => el.classList.contains("open")));
    await page.keyboard.press("Escape");
    assert.ok(await page.locator("#sidebar").evaluate(el => !el.classList.contains("open")));
    await page.screenshot({ path: path.join(root, "tmp/browser/dashboard-mobile.png") });
    await visit("/upload");
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, "Upload should fit mobile viewport");
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.getByRole("button", { name: "Sign out" }).click();
    await login("admin", "Admin123!");
    await visit("/admin"); await capture("admin-dashboard");
    for (const route of ["/admin/users", "/admin/documents", "/admin/analyses", "/admin/users/2", "/profile"]) await visit(route);
    assert.deepEqual(errors, [], "No browser exceptions or server errors");
    console.log("Browser verification passed: login, upload, extraction, chart, search, export, deletion, access control, theme persistence and mobile layout.");
  } catch (error) {
    await page.screenshot({ path: path.join(root, "tmp/browser/failure.png"), fullPage: true });
    console.error((await page.locator("main").innerText()).slice(0, 1800));
    throw error;
  } finally { bridge?.kill(); await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
