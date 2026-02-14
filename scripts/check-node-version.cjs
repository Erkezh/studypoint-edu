#!/usr/bin/env node

function parseVersion(v) {
  const parts = String(v).split(".").map((n) => Number.parseInt(n, 10));
  return [parts[0] || 0, parts[1] || 0, parts[2] || 0];
}

function isSupported(versionTuple) {
  const [major, minor] = versionTuple;

  if (major === 20) {
    return minor >= 19;
  }
  if (major === 22) {
    return minor >= 12;
  }
  return major > 22;
}

const current = process.versions.node;
const currentTuple = parseVersion(current);

if (!isSupported(currentTuple)) {
  // Keep message explicit for the vite/plugin-vue crypto.hash failure.
  console.error(
    [
      "",
      "Unsupported Node.js version detected:",
      `  current: v${current}`,
      "  required: ^20.19.0 OR >=22.12.0",
      "",
      "Reason:",
      "  Recent Vite/Vue tooling uses `crypto.hash`, which is missing in older Node versions.",
      "",
      "Fix:",
      "  Install Node 22.12+ (recommended) or 20.19+ and run `npm ci` again.",
      "",
    ].join("\n"),
  );
  process.exit(1);
}
