// Exports the 3 s animation frame by frame: Playwright seeks the GSAP timeline to each frame and screenshots it,
// ffmpeg builds the MP4 (H.264, yuv420p), the GIF and the last-frame PNG into output/.
// Run: npm install (once), then npm run render. Needs ffmpeg.
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const OUT = path.join(__dirname, "output");
const FRAMES = path.join(OUT, "frames");
const exe = fs.existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined; // preinstalled Chromium, if any

(async () => {
  fs.rmSync(FRAMES, { recursive: true, force: true });
  fs.mkdirSync(FRAMES, { recursive: true });
  const browser = await chromium.launch({ ...(exe ? { executablePath: exe } : {}), args: ["--disable-dev-shm-usage"] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  // fonts come from fonts/ (self-hosted copies of the Google Fonts); no network, so every export is identical
  await page.route(/^https?:/, (r) => r.abort());
  await page.goto("file://" + path.join(__dirname, "index.html") + "?render", { waitUntil: "load", timeout: 30000 });
  await page.evaluate(() => window.__ready.then(() => true));
  const { fps, duration } = await page.evaluate(() => window.CONFIG.size);
  const n = Math.round(fps * duration);
  for (let i = 0; i < n; i++) {
    await page.evaluate((t) => { window.__seek(t); return true; }, i / fps);
    await page.screenshot({ path: path.join(FRAMES, String(i).padStart(4, "0") + ".png"), timeout: 20000 });
  }
  await browser.close();

  const ff = (args) => execFileSync("ffmpeg", ["-v", "error", "-y", ...args], { stdio: "inherit" });
  const src = ["-framerate", String(fps), "-i", path.join(FRAMES, "%04d.png")];
  ff([...src, "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path.join(OUT, "mirro-try-now.mp4")]);
  // GIF: plays once (no loop), 540 px wide, 25 fps (GIF delays are in 1/100 s, so 25 fps keeps the length exactly 3.0 s)
  ff([...src, "-vf", "fps=25,scale=540:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=192:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a", "-loop", "-1", path.join(OUT, "mirro-try-now.gif")]);
  fs.copyFileSync(path.join(FRAMES, String(n - 1).padStart(4, "0") + ".png"), path.join(OUT, "mirro-try-now-last-frame.png"));
  console.log(`ok: ${n} frames -> output/`);
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
