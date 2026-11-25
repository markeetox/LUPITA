import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const baseUrl = process.env.LUPITA_BASE_URL || "https://lupita.fuglymon.com";
const outputDir = process.env.SMOKE_OUTPUT_DIR || "artifacts/frontend-smoke";
fs.mkdirSync(outputDir, { recursive: true });

const failures = [];
const results = [];

async function runViewport(name, viewport, mobile = false) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport,
    isMobile: mobile,
    hasTouch: mobile,
    deviceScaleFactor: mobile ? 2 : 1
  });
  const page = await context.newPage();
  const pageErrors = [];
  const apiResponses = [];
  page.on("pageerror", error => pageErrors.push(error.message));
  page.on("response", response => {
    if (response.url().includes("/api/v1/") && response.status() >= 400) {
      apiResponses.push({ url: response.url(), status: response.status() });
    }
  });

  try {
    const response = await page.goto(baseUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
    if (!response || !response.ok()) throw new Error("Site navigation failed: " + (response && response.status()));
    // The species checklist is intentionally collapsed until its control is opened.
    await page.locator("#selectBtn").click();
    await page.waitForSelector("#checklist input[type='checkbox']", { state: "visible", timeout: 60000 });
    await page.waitForFunction(() => {
      const box = document.querySelector("#checklist");
      return box && box.querySelectorAll("input[type='checkbox']").length >= 100;
    }, { timeout: 60000 });

    const speciesCount = await page.locator("#checklist input[type='checkbox']").count();
    const initialRegion = await page.locator("#regionSelect").inputValue();
    await page.locator("#checklist .check-item").filter({ hasText: "Spanish mackerel" }).click();

    await page.waitForFunction(() => {
      const root = document.querySelector("#opportunityContent");
      return root && root.querySelectorAll(".opportunity-card").length > 0;
    }, { timeout: 30000 });

    const cards = page.locator("#opportunityContent .opportunity-card");
    const cardCount = await cards.count();
    if (cardCount < 1 || cardCount > 3) throw new Error("Expected 1-3 Spanish mackerel cards, got " + cardCount);

    const opportunityText = await page.locator("#opportunityContent").innerText();
    if (!opportunityText.toLowerCase().includes("spanish mackerel")) throw new Error("Species name missing from opportunity panel");
    if (!opportunityText.includes("Habitat match")) throw new Error("Habitat-match score label missing");
    if (!opportunityText.includes("Model confidence")) throw new Error("Model confidence label missing");
    if (!opportunityText.includes("Measured input at prediction")) throw new Error("Prediction-time measured buoy context missing");
    if (!opportunityText.includes("not a catch probability")) throw new Error("Habitat-match disclaimer missing");
    if (!opportunityText.includes("current nearby buoy readings are displayed separately")) throw new Error("Prediction-time/current buoy distinction missing");
    await page.screenshot({ path: path.join(outputDir, name + "-opportunities.png"), fullPage: false });

    const beforePan = await page.locator("#opportunityContent .opportunity-meta").allTextContents();
    await page.evaluate(() => map.jumpTo({ center: [-100, 35], zoom: 4 }));
    await page.waitForFunction(previous => {
      const current = Array.from(document.querySelectorAll("#opportunityContent .opportunity-meta")).map(node => node.textContent);
      return current.length > 0 && current.some((value, index) => value !== previous[index]);
    }, beforePan, { timeout: 10000 });
    const afterPan = await page.locator("#opportunityContent .opportunity-meta").allTextContents();

    await cards.first().click();
    await page.waitForFunction(() => {
      const sheet = document.querySelector("#sheet");
      return sheet && sheet.classList.contains("open") && document.querySelector("#sheetBody").textContent.trim().length > 0;
    }, { timeout: 10000 });
    const detailText = await page.locator("#sheetBody").innerText();
    if (!detailText.toLowerCase().includes("spanish mackerel")) throw new Error("Opportunity card did not open its species detail sheet");
    await page.screenshot({ path: path.join(outputDir, name + "-area-detail.png"), fullPage: false });
    await page.locator("#sheetClose").click();

    // Verify an explicitly no-favorable-areas species is reported honestly.
    await page.locator("#selectBtn").click();
    await page.locator("#checklist .check-item").filter({ hasText: "Spanish mackerel" }).click();
    await page.locator("#checklist .check-item").filter({ hasText: "Gopher rockfish" }).click();
    await page.waitForFunction(() => {
      const text = document.querySelector("#opportunityContent")?.innerText || "";
      return text.includes("No favorable areas in the current snapshot for: Gopher rockfish");
    }, { timeout: 30000 });

    // Confirm the mobile control sheet can scroll within the viewport.
    const layout = await page.evaluate(() => {
      const sheet = document.querySelector("#topsheet");
      const style = getComputedStyle(sheet);
      return {
        viewportHeight: window.innerHeight,
        sheetHeight: sheet.getBoundingClientRect().height,
        maxHeight: style.maxHeight,
        overflowY: style.overflowY,
        scrollHeight: sheet.scrollHeight,
        clientHeight: sheet.clientHeight
      };
    });
    if (mobile) {
      if (layout.sheetHeight > viewport.height * 0.9) throw new Error("Mobile control sheet exceeds 90% of viewport");
      if (!["auto", "scroll"].includes(layout.overflowY)) throw new Error("Mobile control sheet is not vertically scrollable: " + layout.overflowY);
    }

    await page.screenshot({ path: path.join(outputDir, name + ".png"), fullPage: false });
    if (pageErrors.length) throw new Error("Uncaught browser errors: " + pageErrors.join(" | "));
    if (apiResponses.length) throw new Error("API request failures: " + JSON.stringify(apiResponses));

    results.push({
      viewport: name,
      speciesCount,
      initialRegion,
      spanishMackerelCards: cardCount,
      measuredContextShown: true,
      mapPanRefreshesDistances: beforePan.some((value, index) => value !== afterPan[index]),
      cardOpensDetailSheet: true,
      gopherRockfishNoFavorableAreas: true,
      layout
    });
  } catch (error) {
    failures.push({ viewport: name, error: error.message, pageErrors, apiResponses });
    try { await page.screenshot({ path: path.join(outputDir, name + "-failure.png"), fullPage: false }); } catch {}
  } finally {
    await context.close();
    await browser.close();
  }
}

await runViewport("desktop", { width: 1440, height: 1000 }, false);
await runViewport("mobile", { width: 390, height: 844 }, true);

fs.writeFileSync(path.join(outputDir, "results.json"), JSON.stringify({ baseUrl, results, failures }, null, 2));
console.log(JSON.stringify({ baseUrl, results, failures }, null, 2));
if (failures.length) process.exit(1);
