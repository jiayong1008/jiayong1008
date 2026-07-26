import fs from "node:fs";

const apiKey = process.env.WAKATIME_API_KEY;
if (!apiKey) {
  console.error("WAKATIME_API_KEY is not set — skipping WakaTime update.");
  process.exit(1);
}

const EXCLUDED_PROJECTS = new Set(["jiayong1008"]); // this profile repo itself

// Real coding history on this account starts ~May 2026. Kept as a fixed
// anchor (rather than a rolling window) so "all-time" stays true all-time.
// WakaTime's free-tier API caps ranges at ~365 days, so this will need
// bumping forward once the account has been active for close to a year.
const ALL_TIME_START = "2026-05-01";

function formatDuration(totalSeconds) {
  const totalMinutes = Math.round(totalSeconds / 60);
  const hrs = Math.floor(totalMinutes / 60);
  const mins = totalMinutes % 60;
  if (hrs === 0) return `${mins} min${mins === 1 ? "" : "s"}`;
  if (mins === 0) return `${hrs} hr${hrs === 1 ? "" : "s"}`;
  return `${hrs} hr${hrs === 1 ? "" : "s"} ${mins} min${mins === 1 ? "" : "s"}`;
}

const auth = Buffer.from(apiKey).toString("base64");
const authHeaders = { Authorization: `Basic ${auth}` };

// The legacy /stats/:range endpoint returns empty data for accounts without
// a public WakaTime username, even when authenticated. /summaries is what
// the interactive dashboard itself uses and reliably has real data.
async function fetchSummaries(start, end) {
  const url = `https://wakatime.com/api/v1/users/current/summaries?start=${start}&end=${end}`;
  const res = await fetch(url, { headers: authHeaders });
  if (!res.ok) {
    throw new Error(`WakaTime API error ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

const end = new Date();
const toDateStr = (d) => d.toISOString().slice(0, 10);
const endStr = toDateStr(end);

const thirtyDaysAgo = new Date(end);
thirtyDaysAgo.setUTCDate(thirtyDaysAgo.getUTCDate() - 29);

const [last30, allTime] = await Promise.all([
  fetchSummaries(toDateStr(thirtyDaysAgo), endStr),
  fetchSummaries(ALL_TIME_START, endStr),
]);

// --- Project table (last 30 days) ---

const projectSeconds = new Map();
for (const day of last30.data ?? []) {
  for (const p of day.projects ?? []) {
    projectSeconds.set(p.name, (projectSeconds.get(p.name) ?? 0) + p.total_seconds);
  }
}

const projects = [...projectSeconds.entries()]
  .filter(([name, seconds]) => seconds > 60 && !EXCLUDED_PROJECTS.has(name))
  .sort((a, b) => b[1] - a[1])
  .slice(0, 6);

const projectRows = projects.map(([name, seconds]) => `| ${name} | ${formatDuration(seconds)} |`).join("\n");
const projectTable = [
  "| Project | Time |",
  "| :--- | :--- |",
  projectRows || "| _no activity in the last 30 days_ | |",
].join("\n");

// --- All-time stat strip ---

const allTimeDays = allTime.data ?? [];
const dailyTotals = allTimeDays.map((d) => ({ date: d.range.date, seconds: d.grand_total.total_seconds }));

let currentStreak = 0;
for (let i = dailyTotals.length - 1; i >= 0; i--) {
  if (dailyTotals[i].seconds > 0) currentStreak++;
  else break;
}

const bestDay = dailyTotals.reduce((a, b) => (b.seconds > a.seconds ? b : a), { seconds: 0, date: null });
const bestDayLabel = bestDay.date
  ? `${formatDuration(bestDay.seconds)} (${bestDay.date})`
  : "—";

const allTimeSeconds = allTime.cumulative_total?.seconds ?? 0;
const last30Seconds = last30.cumulative_total?.seconds ?? 0;
const last30Pct = allTimeSeconds > 0 ? Math.round((last30Seconds / allTimeSeconds) * 100) : 0;

const statStrip = [
  "| Metric | Value |",
  "| :--- | :--- |",
  `| Total time coded | ${allTime.cumulative_total?.text ?? "—"} |`,
  `| Current streak | ${currentStreak} day${currentStreak === 1 ? "" : "s"} |`,
  `| Best day | ${bestDayLabel} |`,
].join("\n");

const accelerationLine =
  last30Pct >= 50
    ? `<sub>${last30.cumulative_total?.text ?? "?"} of that (${last30Pct}%) happened in just the last 30 days.</sub>`
    : "";

// --- Write back into README ---

const readmePath = "README.md";
let readme = fs.readFileSync(readmePath, "utf8");

readme = readme.replace(
  /<!--WAKATIME:START-->[\s\S]*?<!--WAKATIME:END-->/,
  `<!--WAKATIME:START-->\n${projectTable}\n<!--WAKATIME:END-->`
);

readme = readme.replace(
  /<!--WAKATIME_ALLTIME:START-->[\s\S]*?<!--WAKATIME_ALLTIME:END-->/,
  `<!--WAKATIME_ALLTIME:START-->\n${statStrip}\n\n${accelerationLine}\n<!--WAKATIME_ALLTIME:END-->`
);

fs.writeFileSync(readmePath, readme);

console.log(
  `WakaTime: all-time ${allTime.cumulative_total?.text}, last 30d ${last30.cumulative_total?.text} (${last30Pct}%), streak ${currentStreak}d, best day ${bestDayLabel}, projects ${projects.length}`
);
