import fs from "node:fs";

const apiKey = process.env.WAKATIME_API_KEY;
if (!apiKey) {
  console.error("WAKATIME_API_KEY is not set — skipping WakaTime update.");
  process.exit(1);
}

function formatDuration(totalSeconds) {
  const totalMinutes = Math.round(totalSeconds / 60);
  const hrs = Math.floor(totalMinutes / 60);
  const mins = totalMinutes % 60;
  if (hrs === 0) return `${mins} min${mins === 1 ? "" : "s"}`;
  if (mins === 0) return `${hrs} hr${hrs === 1 ? "" : "s"}`;
  return `${hrs} hr${hrs === 1 ? "" : "s"} ${mins} min${mins === 1 ? "" : "s"}`;
}

const auth = Buffer.from(apiKey).toString("base64");

// The legacy /stats/:range endpoint returns empty data for accounts without
// a public WakaTime username, even when authenticated. /summaries is what
// the interactive dashboard itself uses and reliably has real data.
const end = new Date();
const start = new Date(end);
start.setUTCDate(start.getUTCDate() - 6);
const toDateStr = (d) => d.toISOString().slice(0, 10);

const url = `https://wakatime.com/api/v1/users/current/summaries?start=${toDateStr(start)}&end=${toDateStr(end)}`;
const res = await fetch(url, {
  headers: { Authorization: `Basic ${auth}` },
});

if (!res.ok) {
  console.error(`WakaTime API error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const body = await res.json();
const days = body.data ?? [];

const projectSeconds = new Map();
for (const day of days) {
  for (const p of day.projects ?? []) {
    projectSeconds.set(p.name, (projectSeconds.get(p.name) ?? 0) + p.total_seconds);
  }
}

const projects = [...projectSeconds.entries()]
  .filter(([, seconds]) => seconds > 60)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 6);

const rows = projects.map(([name, seconds]) => `| ${name} | ${formatDuration(seconds)} |`).join("\n");
const table = [
  "| Project | Time |",
  "| :--- | :--- |",
  rows || "| _no activity in the last 7 days_ | |",
].join("\n");

const readmePath = "README.md";
const readme = fs.readFileSync(readmePath, "utf8");
const updated = readme.replace(
  /<!--WAKATIME:START-->[\s\S]*?<!--WAKATIME:END-->/,
  `<!--WAKATIME:START-->\n${table}\n<!--WAKATIME:END-->`
);

if (updated === readme) {
  console.log("README already up to date (or markers not found).");
} else {
  fs.writeFileSync(readmePath, updated);
}

console.log(`WakaTime total (7d): ${body.cumulative_total?.text}, projects: ${projects.length}`);
