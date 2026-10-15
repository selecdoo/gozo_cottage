import { spawn } from "node:child_process";
import fs from "node:fs";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const port = 9333;
const ch = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${port}`, "--no-sandbox", "--hide-scrollbars", "--user-data-dir=/tmp/gc/chrome-prof", "about:blank"], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 2500));
const tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
const ws = new WebSocket(tabs.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map();
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => (await send("Runtime.evaluate", { expression: expr, returnByValue: true })).result.value;

const [, , url, width, tag] = process.argv;
const mobile = Number(width) < 600;
await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: Number(width), height: 900, deviceScaleFactor: 1, mobile });
await send("Page.navigate", { url });
await wait(2500);
// scroll through to trigger lazy images
const H = await ev("document.documentElement.scrollHeight");
for (let y = 0; y < H; y += 600) { await ev(`window.scrollTo(0,${y})`); await wait(300); }
await wait(1500);
await ev("window.scrollTo(0,0)"); await wait(400);
const info = await ev(`JSON.stringify({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,h:document.documentElement.scrollHeight,
 over:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.right>document.documentElement.clientWidth+1 && getComputedStyle(e).position!=='fixed' && !e.closest('.rail')}).slice(0,8).map(e=>e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().right)),
 pending:[...document.images].filter(i=>!i.complete).length,broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.src)})`);
console.log(tag, info);
const clips = JSON.parse(process.argv[5] || "[]");
for (const [name, y, h] of clips) {
  const r = await send("Page.captureScreenshot", { format: "jpeg", quality: 60, captureBeyondViewport: true, clip: { x: 0, y, width: Number(width), height: h, scale: 1 } });
  fs.writeFileSync(`/tmp/gc/shot-${tag}-${name}.jpg`, Buffer.from(r.data, "base64"));
}
ws.close(); ch.kill();
