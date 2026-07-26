import fs from "node:fs";

const apiKey = process.env.WAKATIME_API_KEY;
if (!apiKey) {
  console.error("WAKATIME_API_KEY is not set — skipping WakaTime update.");
  process.exit(1);
}

const auth = Buffer.from(apiKey).toString("base64");
const res = await fetch("https://wakatime.com/api/v1/users/current/stats/last_7_days", {
  headers: { Authorization: `Basic ${auth}` },
});

if (!res.ok) {
  console.error(`WakaTime API error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const { data } = await res.json();

const projects = (data.projects ?? [])
  .filter((p) => p.total_seconds > 60)
  .sort((a, b) => b.total_seconds - a.total_seconds)
  .slice(0, 6);

const rows = projects.map((p) => `| ${p.name} | ${p.text} |`).join("\n");
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

console.log(`WakaTime total (7d): ${data.human_readable_total}, projects: ${projects.length}`);
