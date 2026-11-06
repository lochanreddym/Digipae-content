// DigiPae investor deck generator (pptxgenjs). Builds the 13-slide deck + appendix and the 7-slide YC-style cut.
// Usage: NODE_PATH=<dir with pptxgenjs, react-icons, react, react-dom, sharp> node build_deck.cjs <outDir>
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const Fi = require("react-icons/fi");

const OUT = process.argv[2] || path.join(__dirname, "..");
const LOGO = path.join(__dirname, "digipae-icon.png");
const SKILL = process.env.PPTX_SKILL_DIR;

// ---------- design system ----------
const COL = {
  navy: "081522", deep: "10263B", deep2: "153452", cyan: "37D5E8", white: "FFFFFF", gray: "A4B4C3",
  teal: "2BB5A0", line: "2A4560", light: "F4F7FA", lightCard: "FFFFFF", ink: "081522", inkSoft: "4A6075", amber: "E9B44C",
};
const THEME = {
  name: "DigiPae",
  headFontFace: "Inter",
  bodyFontFace: "Inter",
  colors: {
    dk1: COL.navy, lt1: COL.white, dk2: COL.deep, lt2: COL.light,
    accent1: COL.cyan, accent2: COL.teal, accent3: COL.gray, accent4: COL.deep2, accent5: COL.line, accent6: COL.amber,
    hlink: COL.cyan, folHlink: COL.gray,
  },
};
const W = 13.333, H = 7.5, MX = 0.7;
const FOOT = "DigiPae  ·  Confidential draft  ·  November 2026";

// ---------- icons ----------
const iconCache = {};
async function icon(name, color, size = 256) {
  const key = `${name}-${color}`;
  if (iconCache[key]) return iconCache[key];
  const svg = renderToStaticMarkup(React.createElement(Fi[name], { color: `#${color}`, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).resize(size, size).png().toBuffer();
  return (iconCache[key] = "image/png;base64," + buf.toString("base64"));
}
const ICONS = ["FiUser", "FiUsers", "FiFileText", "FiGlobe", "FiCheckSquare", "FiRepeat", "FiShield", "FiKey", "FiCode",
  "FiDatabase", "FiLock", "FiLayers", "FiSearch", "FiClock", "FiBriefcase", "FiHeart", "FiHome", "FiTrendingUp", "FiTarget",
  "FiMail", "FiCheckCircle", "FiLoader", "FiFlag", "FiLink", "FiCpu", "FiActivity", "FiArrowRight", "FiGrid", "FiServer"];

// ---------- helpers ----------
function makeDeck(title) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "DigiPae";
  pres.company = "CEIVIS LLC";
  pres.title = title;
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  for (const [name, bg, fg, sub] of [["DARK", COL.navy, COL.white, COL.gray], ["LIGHT", COL.light, COL.ink, COL.inkSoft]]) {
    pres.defineSlideMaster({
      title: name,
      background: { color: bg },
      objects: [
        { text: { text: FOOT, options: { x: MX, y: 6.95, w: 8, h: 0.3, fontSize: 10, color: sub, margin: 0 } } },
      ],
      slideNumber: { x: W - MX - 0.6, y: 6.95, w: 0.6, h: 0.3, fontSize: 10, color: sub, align: "right" },
      placeholders: undefined,
    });
    pres.defineSlideMaster({
      title: `${name}_T`,
      background: { color: bg },
      objects: [
        { text: { text: FOOT, options: { x: MX, y: 6.95, w: 8, h: 0.3, fontSize: 10, color: sub, margin: 0 } } },
        { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.95, w: W - 2 * MX, h: 1.2, fontSize: 32, bold: true,
            color: fg, valign: "top", align: "left", margin: 0, fontFace: "Inter" }, text: "" } },
      ],
      slideNumber: { x: W - MX - 0.6, y: 6.95, w: 0.6, h: 0.3, fontSize: 10, color: sub, align: "right" },
    });
  }
  return pres;
}
const T = (slide, text, o) => slide.addText(text, { isTextBox: true, margin: 0, valign: "top", fontFace: "Inter", ...o });
function kicker(slide, text, dark = true) {
  T(slide, text.toUpperCase(), { x: MX, y: 0.55, w: 9, h: 0.3, fontSize: 12, bold: true, color: dark ? COL.cyan : "0F7F8F", charSpacing: 3 });
}
function titled(pres, sec, master, kick, title) {
  const s = pres.addSlide({ masterName: `${master}_T`, sectionTitle: sec });
  kicker(s, kick, master === "DARK");
  s.addText(title, { placeholder: "title" });
  return s;
}
const card = (s, x, y, w, h, fill, line, name, radius = 0.12) =>
  s.addShape("roundRect", { x, y, w, h, fill: { color: fill }, line: line ? { color: line, width: 1 } : { type: "none" }, rectRadius: radius, objectName: name });
async function pill(s, text, x, y, kind) {
  const st = { dev: [COL.cyan, COL.navy], proto: [COL.teal, COL.white], plan: [COL.deep2, COL.gray], confirm: [COL.amber, COL.navy], illus: ["DCE6EE", COL.inkSoft] }[kind];
  const w = 0.3 + text.length * 0.095;
  s.addShape("roundRect", { x, y, w, h: 0.26, fill: { color: st[0] }, line: { type: "none" }, rectRadius: 0.13 });
  T(s, text, { x, y: y + 0.045, w, h: 0.2, fontSize: 9, bold: true, color: st[1], align: "center" });
  return w;
}
async function ic(s, name, color, x, y, size) { s.addImage({ data: await icon(name, color), x, y, w: size, h: size, altText: name.replace(/^Fi/, "") + " icon" }); }
async function iconDot(s, name, x, y, d, bg, fg) {
  s.addShape("ellipse", { x, y, w: d, h: d, fill: { color: bg }, line: { type: "none" } });
  await ic(s, name, fg, x + d * 0.24, y + d * 0.24, d * 0.52);
}
const line = (s, x1, y1, x2, y2, color, width = 1.25, dash) =>
  s.addShape("line", { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.0001, h: Math.abs(y2 - y1) || 0.0001,
    flipH: x2 < x1, flipV: y2 < y1, line: { color, width, dashType: dash || "solid" } });
const arrow = (s, x1, y1, x2, y2, color, width = 1.5) =>
  s.addShape("line", { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.0001, h: Math.abs(y2 - y1) || 0.0001,
    flipH: x2 < x1, flipV: y2 < y1, line: { color, width, endArrowType: "triangle" } });
function networkMotif(s, ox, oy, scale = 1, alpha = 70) {
  const P = [[0.4, 0.6], [1.9, 0.2], [3.3, 0.9], [4.6, 0.3], [0.9, 2.0], [2.5, 1.7], [3.9, 2.2], [1.6, 3.3], [3.2, 3.4], [4.7, 3.6], [0.5, 4.5], [2.4, 4.8], [4.0, 4.9]];
  const E = [[0, 1], [1, 2], [2, 3], [0, 4], [1, 5], [2, 5], [2, 6], [3, 6], [4, 5], [5, 6], [4, 7], [5, 8], [6, 8], [6, 9], [7, 8], [8, 9], [7, 10], [7, 11], [8, 11], [8, 12], [9, 12], [10, 11], [11, 12]];
  for (const [a, b] of E) { const [x1, y1] = P[a], [x2, y2] = P[b]; line(s, ox + x1 * scale, oy + y1 * scale, ox + x2 * scale, oy + y2 * scale, COL.line, 1); }
  P.forEach(([x, y], i) => {
    const d = (i % 4 === 0 ? 0.22 : 0.14) * scale;
    s.addShape("ellipse", { x: ox + x * scale - d / 2, y: oy + y * scale - d / 2, w: d, h: d,
      fill: { color: i % 3 === 0 ? COL.cyan : COL.gray, transparency: i % 3 === 0 ? alpha - 40 : alpha }, line: { type: "none" } });
  });
}

// ---------- slide builders ----------
const S = {};

S.cover = async (pres, sec) => {
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: sec });
  networkMotif(s, 7.7, 1.0, 1.05, 55);
  s.addImage({ path: LOGO, x: MX, y: 0.75, w: 0.62, h: 0.63 , altText: "DigiPae logo" });
  T(s, "DigiPae", { x: MX + 0.8, y: 0.83, w: 3, h: 0.5, fontSize: 24, bold: true, color: COL.white });
  T(s, "The Connectivity Layer for Government Services", { x: MX, y: 2.05, w: 7.0, h: 2.7, fontSize: 46, bold: true, color: COL.white, lineSpacingMultiple: 0.95 });
  T(s, "Simplifying government document access, eligibility workflows, and verification through consent-based infrastructure.",
    { x: MX, y: 4.75, w: 6.6, h: 1.0, fontSize: 17, color: COL.gray, lineSpacingMultiple: 1.15 });
  T(s, [
    { text: "Pre-seed  ·  2026", options: { color: COL.white, bold: true } },
    { text: "      digipae.com", options: { color: COL.cyan } },
    { text: "      Operated by CEIVIS LLC", options: { color: COL.gray } },
  ], { x: MX, y: 6.1, w: 9, h: 0.35, fontSize: 13 });
  s.addNotes(NOTES.cover);
  return s;
};

S.problem = async (pres, sec, k = "02 · Problem") => {
  const s = titled(pres, sec, "DARK", k, "Government Services Are Connected by Paperwork, Not Infrastructure");
  // hub-and-spoke of disconnected touchpoints around one person
  const cx = 4.2, cy = 4.45;
  const nodes = [
    ["FiGlobe", "Portal A", 1.05, 2.55], ["FiGlobe", "Portal B", 5.4, 2.55], ["FiFileText", "Documents", 0.7, 4.15],
    ["FiCheckSquare", "Eligibility rules", 5.9, 4.15], ["FiUsers", "Service organization", 1.05, 5.75], ["FiGlobe", "Portal C", 5.4, 5.75],
  ];
  for (const [, , x, y] of nodes) line(s, cx, cy, x + 1.05, y + 0.3, COL.line, 1.5, "dash");
  for (const [name, label, x, y] of nodes) {
    card(s, x, y, 2.1, 0.6, COL.deep, COL.line, `node-${label}`, 0.1);
    await ic(s, name, COL.gray, x + 0.14, y + 0.17, 0.26);
    T(s, label, { x: x + 0.48, y: y + 0.18, w: 1.58, h: 0.3, fontSize: 12, color: COL.white });
  }
  s.addShape("ellipse", { x: cx - 0.62, y: cy - 0.62, w: 1.24, h: 1.24, fill: { color: COL.cyan }, line: { type: "none" } });
  await ic(s, "FiUser", COL.navy, cx - 0.27, cy - 0.38, 0.54);
  T(s, "Applicant", { x: cx - 0.6, y: cy + 0.18, w: 1.2, h: 0.25, fontSize: 11, bold: true, color: COL.navy, align: "center" });
  // repeated-step markers on the spokes
  for (const [x, y] of nodes.map(([, , nx, ny]) => [cx + (nx + 1.05 - cx) * 0.52, cy + (ny + 0.3 - cy) * 0.52])) {
    s.addShape("ellipse", { x: x - 0.16, y: y - 0.16, w: 0.32, h: 0.32, fill: { color: COL.navy }, line: { color: COL.amber, width: 1 } });
    await ic(s, "FiRepeat", COL.amber, x - 0.1, y - 0.1, 0.2);
  }
  // takeaways
  const tx = 8.6;
  const rows = [
    ["FiGlobe", "Many portals, different rules", "Each program has its own site, account, and eligibility logic."],
    ["FiRepeat", "The same facts, entered again", "Identity, address, income, and household details are re-collected per program."],
    ["FiFileText", "Documents handled by hand", "Records are found, uploaded, and checked manually — by applicants and caseworkers."],
  ];
  let y = 2.5;
  for (const [n, h, b] of rows) {
    await iconDot(s, n, tx, y, 0.5, COL.deep, COL.cyan);
    T(s, h, { x: tx + 0.7, y: y - 0.02, w: 3.9, h: 0.35, fontSize: 16, bold: true, color: COL.white });
    T(s, b, { x: tx + 0.7, y: y + 0.38, w: 3.9, h: 0.75, fontSize: 13, color: COL.gray, lineSpacingMultiple: 1.1 });
    y += 1.35;
  }
  T(s, [{ text: "↻", options: { color: COL.amber, bold: true } }, { text: "  repeated manual step", options: { color: COL.gray } }],
    { x: MX, y: 6.5, w: 4, h: 0.3, fontSize: 11 });
  s.addNotes(NOTES.problem);
  return s;
};

S.impact = async (pres, sec, k = "03 · Why it matters") => {
  const s = titled(pres, sec, "LIGHT", k, "Fragmentation Creates Friction for Everyone");
  const cols = [
    ["FiUser", "Individuals", "≈ 2 in 3", "Medicaid disenrollments in the final month of the 2023–24 unwinding were for procedural or paperwork reasons — not a finding of ineligibility.", "KFF, 2024"],
    ["FiBriefcase", "Organizations", "Similar data", "Federally funded benefit programs require similar types of information about individuals to determine eligibility — gathered program by program.", "GAO/HEHS-00-119"],
    ["FiServer", "Agencies & the public", "10.5B hours", "Estimated public burden from federal information collections in FY2023 — forms, records, and verification across government.", "OMB FY2023, via CEI"],
  ];
  const cw = 3.82, gap = 0.22;
  for (let i = 0; i < 3; i++) {
    const [n, label, stat, body, src] = cols[i];
    const x = MX + i * (cw + gap);
    s.addShape("roundRect", { x, y: 2.3, w: cw, h: 3.85, fill: { color: COL.white }, line: { color: "DCE4EC", width: 1 }, rectRadius: 0.12,
      shadow: { type: "outer", color: "081522", opacity: 0.08, blur: 8, offset: 2, angle: 90 } });
    await iconDot(s, n, x + 0.3, 2.55, 0.5, "E6F7FA", "0F7F8F");
    T(s, label, { x: x + 0.95, y: 2.65, w: cw - 1.1, h: 0.3, fontSize: 14, bold: true, color: COL.inkSoft });
    T(s, stat, { x: x + 0.3, y: 3.25, w: cw - 0.6, h: 0.8, fontSize: 38, bold: true, color: COL.ink });
    T(s, body, { x: x + 0.3, y: 4.15, w: cw - 0.6, h: 1.45, fontSize: 13, color: COL.inkSoft, lineSpacingMultiple: 1.1 });
    T(s, src, { x: x + 0.3, y: 5.72, w: cw - 0.6, h: 0.25, fontSize: 10, color: "6B8095" });
  }
  T(s, "Reach also remains incomplete: WIC served an estimated 53.5% of eligible people in 2022 (USDA FNS). Full citations in the appendix.",
    { x: MX, y: 6.38, w: W - 2 * MX, h: 0.3, fontSize: 11, color: COL.inkSoft });
  s.addNotes(NOTES.impact);
  return s;
};

S.solution = async (pres, sec, k = "04 · Solution") => {
  const s = titled(pres, sec, "DARK", k, "One Consent-Based Connection. Multiple Government Workflows.");
  const left = [["FiGlobe", "Government portals & records*"], ["FiFileText", "Document issuers & records"], ["FiShield", "Identity verification providers"]];
  const right = [["FiUsers", "Benefits-navigation platforms"], ["FiHeart", "Nonprofits & health centers"], ["FiCode", "Apps built on government workflows"]];
  const hub = { x: 5.1, y: 2.55, w: 3.13, h: 3.55 };
  const ys = [2.6, 3.85, 5.1];
  T(s, "AUTHORIZED SOURCES", { x: MX, y: 2.27, w: 3.4, h: 0.25, fontSize: 10, bold: true, color: COL.gray, charSpacing: 2 });
  T(s, "ORGANIZATIONS & APPLICATIONS", { x: 9.23, y: 2.27, w: 3.4, h: 0.25, fontSize: 10, bold: true, color: COL.gray, charSpacing: 2 });
  for (let i = 0; i < 3; i++) {
    line(s, MX + 3.4, ys[i] + 0.45, hub.x, hub.y + hub.h / 2, COL.cyan, 1.25);
    line(s, hub.x + hub.w, hub.y + hub.h / 2, 9.23, ys[i] + 0.45, COL.cyan, 1.25);
  }
  for (let i = 0; i < 3; i++) {
    for (const [arr, x] of [[left, MX], [right, 9.23]]) {
      card(s, x, ys[i], 3.4, 0.9, COL.deep, COL.line, `src-${i}-${x}`, 0.1);
      await ic(s, arr[i][0], COL.cyan, x + 0.22, ys[i] + 0.3, 0.3);
      T(s, arr[i][1], { x: x + 0.68, y: ys[i] + 0.2, w: 2.6, h: 0.55, fontSize: 13, bold: true, color: COL.white, valign: "middle" });
    }
  }
  s.addShape("roundRect", { x: hub.x, y: hub.y, w: hub.w, h: hub.h, fill: { color: COL.deep2 }, line: { color: COL.cyan, width: 1.75 }, rectRadius: 0.16 });
  s.addImage({ path: LOGO, x: hub.x + 0.3, y: hub.y + 0.3, w: 0.5, h: 0.5 , altText: "DigiPae logo" });
  T(s, "DigiPae", { x: hub.x + 0.92, y: hub.y + 0.36, w: 2, h: 0.4, fontSize: 20, bold: true, color: COL.white });
  const caps = ["Consent & authorization", "Document retrieval", "Verification workflows", "Normalized data & APIs"];
  caps.forEach((c, i) => {
    s.addShape("ellipse", { x: hub.x + 0.34, y: hub.y + 1.17 + i * 0.55, w: 0.14, h: 0.14, fill: { color: COL.cyan }, line: { type: "none" } });
    T(s, c, { x: hub.x + 0.62, y: hub.y + 1.08 + i * 0.55, w: 2.4, h: 0.3, fontSize: 13, color: COL.white });
  });
  T(s, "* Only where access is legally permitted and an integration path exists. A user's consent alone does not create a right to access government data.",
    { x: MX, y: 6.35, w: W - 2 * MX, h: 0.3, fontSize: 11, color: COL.gray });
  s.addNotes(NOTES.solution);
  return s;
};

S.experience = async (pres, sec) => {
  const s = titled(pres, sec, "LIGHT", "05 · Product experience", "From Repeated Applications to Reusable Information");
  const lanes = [
    ["Today", ["Repeated forms", "Manual document collection", "Verification delays", "Service application"], "FFFFFF", COL.ink, "DCE4EC", 2.3],
    ["With DigiPae", ["User authorization", "Permitted data or document retrieval", "Structured verification & workflow", "Faster application preparation*"], COL.deep, COL.white, COL.cyan, 4.2],
  ];
  for (const [label, steps, fill, fg, border, y] of lanes) {
    T(s, label, { x: MX, y: y + 0.52, w: 1.7, h: 0.4, fontSize: 16, bold: true, color: label === "Today" ? COL.inkSoft : "0F7F8F" });
    const x0 = 2.55, sw = 2.3, gap = 0.27;
    for (let i = 0; i < 4; i++) {
      const x = x0 + i * (sw + gap);
      s.addShape("roundRect", { x, y, w: sw, h: 1.45, fill: { color: fill }, line: { color: border, width: 1.25 }, rectRadius: 0.12 });
      T(s, `${i + 1}`, { x: x + 0.2, y: y + 0.17, w: 0.4, h: 0.3, fontSize: 12, bold: true, color: label === "Today" ? "8A9CAE" : COL.cyan });
      T(s, steps[i], { x: x + 0.2, y: y + 0.5, w: sw - 0.35, h: 0.85, fontSize: 14, bold: true, color: fg, lineSpacingMultiple: 1.05 });
      if (i < 3) arrow(s, x + sw + 0.03, y + 0.72, x + sw + gap - 0.03, y + 0.72, label === "Today" ? "A4B4C3" : "0F7F8F", 1.5);
    }
  }
  T(s, "* Intended benefit, not a measured result. Time saved and completion rates will be measured with design partners before any claim is made.",
    { x: MX, y: 6.05, w: W - 2 * MX, h: 0.3, fontSize: 11, color: COL.inkSoft });
  s.addNotes(NOTES.experience);
  return s;
};

S.architecture = async (pres, sec) => {
  const s = titled(pres, sec, "DARK", "06 · Product architecture", "One Integration for Documents, Verification, and Eligibility");
  const hub = { x: 5.2, y: 3.75, w: 2.93, h: 1.05 };
  const mods = [
    ["FiKey", "Consent & authorization management", "proto", "Prototype", MX, 2.3],
    ["FiFileText", "Document retrieval & processing", "proto", "Prototype", MX, 3.75],
    ["FiShield", "Identity verification integration", "dev", "In development", MX, 5.2],
    ["FiDatabase", "Data normalization", "plan", "Planned", 9.13, 2.3],
    ["FiCheckSquare", "Eligibility workflow support", "dev", "In development", 9.13, 3.75],
    ["FiCode", "Developer APIs & webhooks", "plan", "Planned", 9.13, 5.2],
  ];
  for (const [, , , , x, y] of mods) line(s, x < 5 ? x + 3.5 : x, y + 0.52, x < 5 ? hub.x : hub.x + hub.w, hub.y + hub.h / 2, COL.line, 1.5);
  line(s, hub.x + hub.w / 2, hub.y + hub.h, hub.x + hub.w / 2, 5.32, COL.line, 1.5);
  for (const [n, label, kind, status, x, y] of mods) {
    card(s, x, y, 3.5, 1.05, COL.deep, COL.line, `mod-${label}`, 0.1);
    await ic(s, n, COL.cyan, x + 0.22, y + 0.2, 0.32);
    T(s, label, { x: x + 0.7, y: y + 0.17, w: 2.7, h: 0.5, fontSize: 13, bold: true, color: COL.white });
    await pill(s, status.toUpperCase(), x + 0.7, y + 0.68, kind);
  }
  // security spans the platform
  card(s, 4.55, 5.32, 4.23, 0.95, COL.deep, COL.line, "mod-security", 0.1);
  await ic(s, "FiLock", COL.cyan, 4.77, 5.5, 0.32);
  T(s, "Audit logs, access control & security", { x: 5.25, y: 5.47, w: 3.4, h: 0.3, fontSize: 13, bold: true, color: COL.white });
  await pill(s, "IN DEVELOPMENT", 5.25, 5.86, "dev");
  s.addShape("roundRect", { x: hub.x, y: hub.y, w: hub.w, h: hub.h, fill: { color: COL.cyan }, line: { type: "none" }, rectRadius: 0.14 });
  T(s, "DigiPae platform", { x: hub.x, y: hub.y + 0.18, w: hub.w, h: 0.4, fontSize: 18, bold: true, color: COL.navy, align: "center" });
  T(s, "one integration for customers", { x: hub.x, y: hub.y + 0.58, w: hub.w, h: 0.3, fontSize: 12, color: COL.navy, align: "center" });
  T(s, "Status as reported by the founding team — to confirm before external use. No live government integrations today.",
    { x: 4.3, y: 2.4, w: 4.73, h: 0.9, fontSize: 11, color: COL.gray, align: "center" });
  s.addNotes(NOTES.architecture);
  return s;
};

S.gtm = async (pres, sec) => {
  const s = titled(pres, sec, "DARK", "07 · Go-to-market", "Start With Benefits. Expand Into Government Connectivity.");
  const stages = [
    ["1", "Start", "Benefits workflows", ["Benefits-technology providers", "Navigation & nonprofit assistance organizations"],
      "Use case: reduce repeated document collection and manual case preparation."],
    ["2", "Expand", "Health & social services", ["Community health centers", "Medicaid health plans", "Community action agencies"],
      "Same consent, document, and verification layer — new customer segments."],
    ["3", "Extend", "Adjacent workflows", ["Other regulated and government-service workflows"],
      "Only where verified integration paths and customer demand exist."],
  ];
  const cw = 3.7, gap = 0.4;
  for (let i = 0; i < 3; i++) {
    const [num, phase, head, list, foot] = stages[i];
    const x = MX + i * (cw + gap), y = 2.35;
    s.addShape("roundRect", { x, y, w: cw, h: 3.55, fill: { color: i === 0 ? COL.deep2 : COL.deep }, line: { color: i === 0 ? COL.cyan : COL.line, width: i === 0 ? 1.5 : 1 }, rectRadius: 0.14 });
    s.addShape("ellipse", { x: x + 0.3, y: y + 0.3, w: 0.5, h: 0.5, fill: { color: i === 0 ? COL.cyan : COL.line }, line: { type: "none" } });
    T(s, num, { x: x + 0.3, y: y + 0.4, w: 0.5, h: 0.3, fontSize: 14, bold: true, color: i === 0 ? COL.navy : COL.white, align: "center" });
    T(s, phase.toUpperCase(), { x: x + 0.95, y: y + 0.42, w: 2.5, h: 0.3, fontSize: 11, bold: true, color: COL.cyan, charSpacing: 2 });
    T(s, head, { x: x + 0.3, y: y + 1.0, w: cw - 0.6, h: 0.4, fontSize: 18, bold: true, color: COL.white });
    T(s, list.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < list.length - 1 } })),
      { x: x + 0.3, y: y + 1.55, w: cw - 0.6, h: 1.1, fontSize: 13, color: COL.white, paraSpaceAfter: 4 });
    T(s, foot, { x: x + 0.3, y: y + 2.75, w: cw - 0.6, h: 0.65, fontSize: 12, color: COL.gray, lineSpacingMultiple: 1.05 });
    if (i < 2) arrow(s, x + cw + 0.05, y + 1.75, x + cw + gap - 0.05, y + 1.75, COL.cyan, 1.75);
  }
  T(s, [{ text: "Proposed motion  ", options: { bold: true, color: COL.white } },
    { text: "Founder-led design partnerships  →  paid pilots  →  developer self-serve onboarding", options: { color: COL.gray } }],
  { x: MX, y: 6.2, w: W - 2 * MX, h: 0.35, fontSize: 13 });
  s.addNotes(NOTES.gtm);
  return s;
};

S.model = async (pres, sec) => {
  const s = titled(pres, sec, "LIGHT", "08 · Business model", "Developer-First Infrastructure With Recurring Revenue Potential");
  const streams = [
    ["FiActivity", "Usage-based API", "Priced per authorized retrieval or verification call."],
    ["FiLayers", "Platform subscription", "Monthly platform fee by tier, with included usage."],
    ["FiBriefcase", "Enterprise integration", "Annual contracts for custom workflows, security, and support."],
  ];
  const cw = 3.82, gap = 0.22;
  for (let i = 0; i < 3; i++) {
    const [n, h, b] = streams[i];
    const x = MX + i * (cw + gap);
    s.addShape("roundRect", { x, y: 2.3, w: cw, h: 1.55, fill: { color: COL.white }, line: { color: "DCE4EC", width: 1 }, rectRadius: 0.12 });
    await iconDot(s, n, x + 0.25, 2.5, 0.48, "E6F7FA", "0F7F8F");
    T(s, h, { x: x + 0.88, y: 2.6, w: cw - 1.0, h: 0.35, fontSize: 16, bold: true, color: COL.ink });
    T(s, b, { x: x + 0.25, y: 3.12, w: cw - 0.5, h: 0.6, fontSize: 13, color: COL.inkSoft });
  }
  T(s, "ILLUSTRATIVE PRICING ARCHITECTURE", { x: MX, y: 4.1, w: 6, h: 0.25, fontSize: 10, bold: true, color: COL.inkSoft, charSpacing: 2 });
  const hdr = (t) => ({ text: t, options: { bold: true, color: COL.white, fill: { color: COL.deep } } });
  const cell = (t, o = {}) => ({ text: t, options: { color: COL.ink, ...o } });
  const tbc = (t) => cell(t, { color: "9A6B12", italic: true });
  s.addTable([
    [hdr(""), hdr("Starter"), hdr("Growth"), hdr("Enterprise")],
    [cell("Typical customer", { bold: true }), cell("Small nonprofit or pilot team"), cell("Benefits-tech platform"), cell("Health plan or multi-site network")],
    [cell("Platform fee", { bold: true }), tbc("$ / month — to confirm"), tbc("$ / month — to confirm"), tbc("Annual contract — to confirm")],
    [cell("Usage", { bold: true }), cell("Included calls, then per call"), cell("Volume-tiered per call"), cell("Committed volume")],
    [cell("Support & security", { bold: true }), cell("Standard"), cell("Priority"), cell("Custom integration, review & SLA")],
  ], { x: MX, y: 4.42, w: W - 2 * MX, colW: [2.6, 3.1, 3.1, 3.13], fontSize: 12, fontFace: "Inter", rowH: 0.36,
    border: { type: "solid", color: "DCE4EC", pt: 0.75 }, fill: { color: COL.white }, valign: "middle", margin: [0, 0.12, 0, 0.12] });
  T(s, "Illustrative structure only. DigiPae has no published pricing, contracted customers, or revenue to date.",
    { x: MX, y: 6.38, w: W - 2 * MX, h: 0.3, fontSize: 11, color: COL.inkSoft });
  s.addNotes(NOTES.model);
  return s;
};

S.market = async (pres, sec, k = "09 · Market opportunity") => {
  const s = titled(pres, sec, "LIGHT", k, "The Opportunity Extends Beyond Benefits");
  const hdr = (t, al = "left") => ({ text: t, options: { bold: true, color: COL.white, fill: { color: COL.deep }, align: al } });
  const c = (t, al = "left", o = {}) => ({ text: t, options: { color: COL.ink, align: al, ...o } });
  const rows = [
    ["Community health centers", "1,359", "HRSA UDS, 2024", "$24K", "$32.6M"],
    ["Medicaid health plans (MCOs)", "291", "KFF, Jul 2024", "$150K", "$43.7M"],
    ["Community action agencies", "~1,000", "Comm. Action Partnership", "$12K", "$12.0M"],
    ["211 referral agencies", "200+", "211.org", "$12K", "$2.4M"],
    ["LSC legal aid programs", "131", "LSC, 2023", "$12K", "$1.6M"],
    ["Benefits-tech platforms", "To confirm", "Customer research", "To confirm", "To confirm"],
  ];
  const data = [[hdr("Segment (US)"), hdr("Orgs", "right"), hdr("Count source"), hdr("ACV*", "right"), hdr("TAM", "right")]];
  for (const r of rows) {
    const tbd = r[1] === "To confirm";
    data.push([c(r[0]), c(r[1], "right", tbd ? { color: "9A6B12", italic: true } : {}), c(r[2], "left", { color: COL.inkSoft }),
      c(r[3], "right", tbd ? { color: "9A6B12", italic: true } : {}), c(r[4], "right", tbd ? { color: "9A6B12", italic: true } : { bold: true })]);
  }
  s.addTable(data, { x: MX, y: 2.3, w: 7.85, colW: [2.55, 1.05, 2.1, 1.05, 1.1], fontSize: 11, fontFace: "Inter", rowH: 0.4,
    border: { type: "solid", color: "DCE4EC", pt: 0.75 }, fill: { color: COL.white }, valign: "middle", margin: [0, 0.1, 0, 0.1] });
  const boxes = [
    ["TAM", "$92M", "Identified initial segments × illustrative ACV", COL.deep, COL.white],
    ["SAM", "$49M", "Nonprofit, community & health-center segments (2,690 orgs)", "E6F7FA", COL.ink],
    ["SOM", "$0.9M ARR", "50 customers in 36 months × $18K blended ACV (assumption)", COL.white, COL.ink],
  ];
  let y = 2.3;
  for (const [lab, val, sub, fill, fg] of boxes) {
    s.addShape("roundRect", { x: 8.85, y, w: 3.78, h: 1.2, fill: { color: fill }, line: { color: fill === COL.white ? "DCE4EC" : fill, width: 1 }, rectRadius: 0.12 });
    T(s, lab, { x: 9.1, y: y + 0.17, w: 0.9, h: 0.3, fontSize: 12, bold: true, color: fill === COL.deep ? COL.cyan : "0F7F8F" });
    T(s, val, { x: 9.95, y: y + 0.1, w: 2.55, h: 0.45, fontSize: 22, bold: true, color: fg, align: "right" });
    T(s, sub, { x: 9.1, y: y + 0.6, w: 3.4, h: 0.5, fontSize: 11, color: fill === COL.deep ? COL.gray : COL.inkSoft });
    y += 1.35;
  }
  T(s, "* ACVs are illustrative assumptions to validate in customer discovery, not observed prices. Beyond benefits, adjacent regulated and government-service workflows are not yet sized.",
    { x: MX, y: 5.35, w: 7.85, h: 0.7, fontSize: 11, color: COL.inkSoft, lineSpacingMultiple: 1.1 });
  T(s, "Bottom-up: TAM = segment organizations × ACV · SAM = reachable initial scope × ACV · SOM = obtainable customers × ACV. Calculation detail in the appendix.",
    { x: MX, y: 6.25, w: W - 2 * MX, h: 0.45, fontSize: 11, color: COL.inkSoft });
  s.addNotes(NOTES.market);
  return s;
};

S.competition = async (pres, sec) => {
  const s = titled(pres, sec, "DARK", "10 · Competitive landscape", "DigiPae Is Building the Connectivity Layer");
  const hdr = (t) => ({ text: t, options: { bold: true, color: COL.cyan, fill: { color: COL.deep2 } } });
  const c = (t, o = {}) => ({ text: t, options: { color: COL.white, fill: { color: COL.deep }, ...o } });
  const g = (t) => c(t, { color: COL.gray });
  const rows = [
    ["Digital identity", "Login.gov (GSA), ID.me", "Sign-in and identity verification for government services"],
    ["Identity verification", "Socure, Persona", "Identity verification for businesses and platforms"],
    ["Income & employment verification", "Equifax The Work Number, Truv", "Income and employment verification, including for benefits eligibility"],
    ["Benefits technology", "Propel, Code for America", "Consumer benefits tools; government-partnered benefits services"],
    ["Government digital services", "Nava PBC", "Builds digital services for government agencies"],
    ["Data connectivity", "Plaid", "Consumer-permissioned connectivity to financial accounts"],
  ];
  const data = [[hdr("Category"), hdr("Examples"), hdr("Documented focus")]];
  for (const r of rows) data.push([c(r[0], { bold: true }), c(r[1]), g(r[2])]);
  data.push([
    { text: "DigiPae (proposed)", options: { bold: true, color: COL.navy, fill: { color: COL.cyan } } },
    { text: "Infrastructure for organizations", options: { color: COL.navy, fill: { color: COL.cyan } } },
    { text: "Consent-based connectivity for government documents and eligibility workflows, delivered as developer APIs", options: { color: COL.navy, fill: { color: COL.cyan }, bold: true } },
  ]);
  s.addTable(data, { x: MX, y: 2.3, w: W - 2 * MX, colW: [2.9, 3.3, 5.73], fontSize: 12, fontFace: "Inter", rowH: 0.47,
    border: { type: "solid", color: COL.navy, pt: 2 }, valign: "middle", margin: [0, 0.14, 0, 0.14] });
  T(s, "Focus descriptions summarize each company's public materials; they are not claims about what these companies lack. Several are potential partners rather than competitors.",
    { x: MX, y: 6.2, w: W - 2 * MX, h: 0.5, fontSize: 11, color: COL.gray });
  s.addNotes(NOTES.competition);
  return s;
};

S.progress = async (pres, sec, k = "11 · Progress & roadmap") => {
  const s = titled(pres, sec, "DARK", k, "Building the Infrastructure, Validating the Demand");
  const cols = [
    ["FiCheckCircle", "Done", COL.teal, ["DigiPae brand, product design, and app prototype screens", "Earlier digital-payments exploration (now secondary)", "Product positioning and launch content"]],
    ["FiLoader", "In progress", COL.cyan, ["Identity verification integration", "Government benefits product development", "Staging environment and prototype", "Customer discovery and outreach"]],
    ["FiFlag", "Next 6–12 months", COL.gray, ["Design-partner agreements (target: to confirm)", "First permitted data-source integration", "Security and privacy baseline", "Paid pilot with defined success metrics"]],
  ];
  const cw = 3.82, gap = 0.22;
  for (let i = 0; i < 3; i++) {
    const [n, head, color, items] = cols[i];
    const x = MX + i * (cw + gap);
    s.addShape("roundRect", { x, y: 2.3, w: cw, h: 2.75, fill: { color: COL.deep }, line: { color: COL.line, width: 1 }, rectRadius: 0.12 });
    await ic(s, n, color, x + 0.28, 2.52, 0.34);
    T(s, head, { x: x + 0.75, y: 2.53, w: cw - 1, h: 0.35, fontSize: 16, bold: true, color: COL.white });
    T(s, items.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < items.length - 1 } })),
      { x: x + 0.28, y: 3.08, w: cw - 0.5, h: 1.85, fontSize: 13, color: COL.gray, paraSpaceAfter: 5 });
  }
  T(s, "TRACTION — TO CONFIRM", { x: MX, y: 5.3, w: 6, h: 0.25, fontSize: 10, bold: true, color: COL.amber, charSpacing: 2 });
  const metrics = ["Discovery conversations", "Design partners / LOIs", "Prototype users", "Waitlist sign-ups"];
  const mw = 2.86, mg = 0.16;
  metrics.forEach((m, i) => {
    const x = MX + i * (mw + mg);
    s.addShape("roundRect", { x, y: 5.62, w: mw, h: 0.95, fill: { color: COL.navy }, line: { color: COL.amber, width: 1, dashType: "dash" }, rectRadius: 0.1 });
    T(s, "[ # ]", { x: x + 0.2, y: 5.7, w: mw - 0.4, h: 0.4, fontSize: 18, bold: true, color: COL.amber });
    T(s, m, { x: x + 0.2, y: 6.12, w: mw - 0.4, h: 0.3, fontSize: 12, color: COL.gray });
  });
  s.addNotes(NOTES.progress);
  return s;
};

S.team = async (pres, sec, k = "12 · Team") => {
  const s = titled(pres, sec, "DARK", k, "Building the Team for Government Connectivity");
  const people = [
    ["Lochan Reddy", "Founder · role to confirm", "Relevant technical and business experience — to confirm"],
    ["[Cofounder name]", "Cofounder · role to confirm", "Relevant experience — to confirm"],
  ];
  let y = 2.3;
  for (const [nm, role, exp] of people) {
    s.addShape("roundRect", { x: MX, y, w: 6.0, h: 1.55, fill: { color: COL.deep }, line: { color: COL.line, width: 1 }, rectRadius: 0.12 });
    s.addShape("ellipse", { x: MX + 0.3, y: y + 0.3, w: 0.95, h: 0.95, fill: { color: COL.deep2 }, line: { color: COL.cyan, width: 1.25 } });
    await ic(s, "FiUser", COL.cyan, MX + 0.55, y + 0.55, 0.45);
    T(s, nm, { x: MX + 1.5, y: y + 0.28, w: 4.3, h: 0.4, fontSize: 18, bold: true, color: nm.startsWith("[") ? COL.amber : COL.white });
    T(s, role, { x: MX + 1.5, y: y + 0.7, w: 4.3, h: 0.3, fontSize: 13, color: COL.cyan });
    T(s, exp, { x: MX + 1.5, y: y + 1.05, w: 4.3, h: 0.3, fontSize: 12, color: COL.amber, italic: true });
    y += 1.8;
  }
  const rx = 7.1;
  T(s, "Why this team", { x: rx, y: 2.3, w: 5.5, h: 0.35, fontSize: 16, bold: true, color: COL.white });
  T(s, ["Firsthand view of repeated documentation and verification friction — to confirm with the founders' own story",
    "Has already shipped DigiPae brand, product design, and prototype work"].map((t, j, a) => ({ text: t, options: { bullet: true, breakLine: j < a.length - 1 } })),
  { x: rx, y: 2.75, w: 5.5, h: 1.3, fontSize: 13, color: COL.gray, paraSpaceAfter: 5 });
  T(s, "Planned hires & advisers", { x: rx, y: 4.2, w: 5.5, h: 0.35, fontSize: 16, bold: true, color: COL.white });
  const hires = [["FiCpu", "Founding engineer — integrations & security"], ["FiShield", "Privacy & compliance adviser"], ["FiHome", "Government benefits policy adviser"]];
  let hy = 4.65;
  for (const [n, t] of hires) {
    await iconDot(s, n, rx, hy, 0.4, COL.deep, COL.cyan);
    T(s, t, { x: rx + 0.55, y: hy + 0.07, w: 5, h: 0.3, fontSize: 13, color: COL.white });
    hy += 0.55;
  }
  s.addNotes(NOTES.team);
  return s;
};

S.ask = async (pres, sec, k = "13 · Vision & ask") => {
  const s = titled(pres, sec, "DARK", k, "Making Government Services Easier to Access and Integrate");
  T(s, "“Government services should be easier to connect to, easier to navigate, and easier to build upon.”",
    { x: MX, y: 2.2, w: 11.5, h: 0.9, fontSize: 22, italic: true, color: COL.cyan, lineSpacingMultiple: 1.1 });
  const cols = [
    ["Near-term milestones", ["Sign design partners in benefits workflows", "Ship the first permitted integration", "Run a measured pilot", "Security and privacy baseline"]],
    ["The ask", ["Raising: $[amount] pre-seed — to confirm", "Instrument: to confirm", "Runway target: [months] — to confirm"]],
    ["Use of funds", ["Engineering & integrations — [%]", "Security & compliance — [%]", "Design partners & go-to-market — [%]"]],
  ];
  const cw = 3.82, gap = 0.22;
  for (let i = 0; i < 3; i++) {
    const [head, items] = cols[i];
    const x = MX + i * (cw + gap);
    s.addShape("roundRect", { x, y: 3.3, w: cw, h: 2.55, fill: { color: i === 1 ? COL.deep2 : COL.deep }, line: { color: i === 1 ? COL.cyan : COL.line, width: i === 1 ? 1.5 : 1 }, rectRadius: 0.12 });
    T(s, head, { x: x + 0.28, y: 3.5, w: cw - 0.5, h: 0.35, fontSize: 16, bold: true, color: COL.white });
    T(s, items.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < items.length - 1, color: /\[|confirm/.test(t) ? COL.amber : COL.gray } })),
      { x: x + 0.28, y: 3.98, w: cw - 0.5, h: 1.75, fontSize: 13, paraSpaceAfter: 5 });
  }
  s.addImage({ path: LOGO, x: MX, y: 6.08, w: 0.38, h: 0.38 , altText: "DigiPae logo" });
  T(s, [{ text: "digipae.com", options: { color: COL.white, bold: true } }, { text: "     [founder email — to confirm]", options: { color: COL.amber } }],
    { x: MX + 0.55, y: 6.14, w: 8, h: 0.3, fontSize: 14 });
  s.addNotes(NOTES.ask);
  return s;
};

S.sources = async (pres, sec) => {
  const s = titled(pres, sec, "LIGHT", "Appendix A · Sources", "Sources Behind the Problem and Market Slides");
  const src = [
    ["KFF (2024)", "How Did Medicaid Renewal Outcomes Change During the Unwinding?", "kff.org/medicaid/how-did-medicaid-renewal-outcomes-change-during-the-unwinding"],
    ["GAO (2000)", "Benefit and Loan Programs: Improved Data Sharing Could Enhance Program Integrity (GAO/HEHS-00-119)", "gao.gov/products/hehs-00-119"],
    ["GAO (2021)", "Federal Low-Income Programs: verification of beneficiary information (GAO-21-183)", "gao.gov/products/GAO-21-183"],
    ["OMB via CEI (2023)", "FY2023 federal paperwork burden of 10.5 billion hours, as reported from OMB's annual burden report", "cei.org/blog/from-cuts-to-costs-why-federal-paperwork-keeps-piling-up"],
    ["USDA FNS (2022)", "National and State-Level Estimates of WIC Eligibility and Program Reach", "fns.usda.gov/research/wic/eer/2022"],
    ["HRSA (2024)", "Uniform Data System — national health center data (1,359 reporting awardees)", "data.hrsa.gov/topics/healthcenters/uds/overview/national"],
    ["KFF (Jul 2024)", "Total Medicaid MCOs — state health facts (291 nationally)", "kff.org/medicaid/state-indicator/total-medicaid-mcos"],
    ["Community Action Partnership", "National network of about 1,000 community action agencies", "communityactionpartnership.com"],
    ["211.org", "About 211 — more than 200 agencies nationwide", "211.org/about-us"],
    ["LSC (2023)", "LSC By the Numbers — 131 funded legal aid organizations", "lsc.gov"],
  ];
  const hdr = (t) => ({ text: t, options: { bold: true, color: COL.white, fill: { color: COL.deep } } });
  const c = (t, o = {}) => ({ text: t, options: { color: COL.ink, ...o } });
  const data = [[hdr("Source"), hdr("Title / data point"), hdr("URL")]];
  for (const r of src) data.push([c(r[0], { bold: true }), c(r[1]), c(r[2], { color: "0F7F8F" })]);
  s.addTable(data, { x: MX, y: 2.2, w: W - 2 * MX, colW: [2.2, 5.6, 4.13], fontSize: 10, fontFace: "Inter", rowH: 0.36,
    border: { type: "solid", color: "DCE4EC", pt: 0.75 }, fill: { color: COL.white }, valign: "middle", margin: [0, 0.1, 0, 0.1] });
  s.addNotes(NOTES.sources);
  return s;
};

S.assumptions = async (pres, sec) => {
  const s = titled(pres, sec, "LIGHT", "Appendix B · Market assumptions", "How the Bottom-Up Market Estimate Is Built");
  const hdr = (t, al = "left") => ({ text: t, options: { bold: true, color: COL.white, fill: { color: COL.deep }, align: al } });
  const c = (t, al = "left", o = {}) => ({ text: t, options: { color: COL.ink, align: al, ...o } });
  const data = [
    [hdr("Layer"), hdr("Formula"), hdr("Inputs"), hdr("Result", "right")],
    [c("TAM", "left", { bold: true }), c("Σ segment orgs × segment ACV"), c("1,359 × $24K + 291 × $150K + 1,000 × $12K + 200 × $12K + 131 × $12K"), c("$92.2M", "right", { bold: true })],
    [c("SAM", "left", { bold: true }), c("Initial-scope orgs × ACV"), c("Health centers, community action, 211, legal aid (2,690 orgs); excludes Medicaid plans (longer sales cycles)"), c("$48.6M", "right", { bold: true })],
    [c("SOM", "left", { bold: true }), c("Obtainable customers × blended ACV"), c("50 customers within 36 months × $18K blended ACV (assumption, to validate)"), c("$0.9M ARR", "right", { bold: true })],
  ];
  s.addTable(data, { x: MX, y: 2.25, w: W - 2 * MX, colW: [1.1, 3.0, 6.53, 1.3], fontSize: 12, fontFace: "Inter", rowH: 0.62,
    border: { type: "solid", color: "DCE4EC", pt: 0.75 }, fill: { color: COL.white }, valign: "middle", margin: [0, 0.12, 0, 0.12] });
  const notes = [
    "ACVs ($12K community nonprofits, $24K health centers, $150K Medicaid plans) are planning assumptions, not observed prices. Replace them with discovery data.",
    "Counts are national (US) and dated as cited; benefits-technology platforms are not yet counted.",
    "Adjacent regulated and government-service workflows are excluded until integration paths and demand are verified.",
  ];
  T(s, notes.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < notes.length - 1 } })),
    { x: MX, y: 5.0, w: W - 2 * MX, h: 1.5, fontSize: 13, color: COL.inkSoft, paraSpaceAfter: 5 });
  s.addNotes(NOTES.assumptions);
  return s;
};

// ---------- speaker notes ----------
const NOTES = {
  cover: `DigiPae is building the connectivity layer for government services: infrastructure that helps authorized organizations and applications work with government documents, verification, and eligibility workflows — with the person's consent.
Analogy we use: Plaid made it simpler for applications to connect to financial accounts. We are pursuing a similar infrastructure opportunity for government information. We are not affiliated with Plaid, and we do not connect to government systems today.
Stage: pre-seed. Operating company: CEIVIS LLC (corporate structure may change).`,
  problem: `Government services are connected by paperwork, not infrastructure. One applicant touches several portals, each with its own account and eligibility rules. The same facts — identity, address, income, household — are entered again for each program, and documents are found, uploaded, and checked by hand. Caseworkers and navigators repeat the same steps on the other side.
The amber markers are the repeated manual steps. That repetition is the problem we are going after.`,
  impact: `Individuals: In month 12 of the Medicaid unwinding, about two-thirds of people disenrolled lost coverage for procedural or paperwork reasons rather than a finding of ineligibility (KFF, 2024; procedural share fell from 74% in month 1 to 66% in month 12).
Organizations: GAO found that federally funded benefit and loan programs require similar types of information about individuals to determine eligibility (GAO/HEHS-00-119). GAO-21-183 (2021) found agencies increasingly use electronic data for verification and recommended HHS and HUD assess sharing more information about data sources.
Agencies and the public: OMB's annual burden report put federal paperwork at about 10.5 billion hours in FY2023 (as reported by CEI, 2023). This is government-wide, not benefits-specific — we use it to show scale, not to size our market.
Reach: WIC served an estimated 53.5% of eligible people in 2022 (USDA FNS).`,
  solution: `DigiPae sits between authorized sources — government portals and records where access is permitted, document issuers, and identity-verification providers — and the organizations and applications that help people apply for services.
One consent-based connection, reused across workflows: consent and authorization, document retrieval, verification workflows, and normalized data through APIs.
Important: we only connect where access is legally permitted and an integration path exists. Consent is necessary but not sufficient — it does not by itself create a right to access government data.`,
  experience: `Today: repeated forms, manual document collection, verification delays, then the application.
With DigiPae: the person authorizes sharing, permitted data or documents are retrieved, verification and workflow are structured, and the application is prepared faster.
"Faster" is the intended benefit. We will measure time saved and completion rates with design partners before making any quantitative claim.`,
  architecture: `One integration for customers, built from seven components. Status labels reflect what the founding team reports today and must be confirmed before this deck is shared:
- Prototype: consent and authorization flows; document retrieval and management (designed app screens and prototype).
- In development: identity-verification integration; eligibility workflow support; audit logging, access control, and security baseline.
- Planned: data normalization; developer APIs and webhooks.
We do not have live government integrations or agency partnerships today, and this slide does not claim specific APIs.`,
  gtm: `Start narrow: benefits-technology providers and organizations that manage eligibility or documentation workflows. The first job to be done is reducing repeated document collection and manual case preparation.
Expand to segments that share the same workflow: community health centers, Medicaid health plans, community action agencies.
Extend into adjacent regulated and government-service workflows only where verified integration paths and customer demand exist.
Proposed motion: founder-led design partnerships, then paid pilots, then developer self-serve onboarding.`,
  model: `Three proposed revenue lines: usage-based API pricing per authorized retrieval or verification; platform subscriptions by tier with included usage; and enterprise integration contracts for custom workflows, security reviews, and support.
The table is an illustrative structure. Price points are deliberately left as "to confirm" — we have no published pricing, customers, or revenue yet.`,
  market: `Bottom-up market sizing for the initial US wedge.
Counts: 1,359 HRSA health center awardees (UDS 2024); 291 Medicaid MCOs (KFF, July 2024); about 1,000 community action agencies (Community Action Partnership); 200+ 211 agencies (211.org); 131 LSC-funded legal aid programs (LSC, 2023). Benefits-technology platforms are not yet counted.
ACVs are illustrative assumptions: $12K for community nonprofits, $24K for health centers, $150K for Medicaid plans.
TAM ≈ $92M across identified segments. SAM ≈ $49M: the nonprofit, community, and health-center segments (2,690 orgs), excluding Medicaid plans because of longer sales cycles. SOM ≈ $0.9M ARR: 50 customers within 36 months at an $18K blended ACV.
The headline is deliberate: benefits is the wedge; adjacent regulated and government-service workflows are the larger opportunity, which we will size once integration paths are verified.`,
  competition: `We group the landscape by category and describe each company only by its public materials:
- Digital identity: Login.gov (GSA's sign-in service for government) and ID.me.
- Identity verification: Socure, Persona.
- Income and employment verification: Equifax The Work Number (used by agencies, including through CMS's data hub) and Truv (consumer-permissioned verification for SNAP, TANF, Medicaid, and housing).
- Benefits technology: Propel (connects to state EBT portals with user permission) and Code for America.
- Government digital services: Nava PBC.
- Data connectivity: Plaid.
Our proposed focus is consent-based connectivity for government documents and eligibility workflows, sold as developer infrastructure to organizations. Many of these companies could be partners or data sources rather than competitors. Note: Benefits Data Trust, a prominent benefits-access nonprofit, closed in August 2024.`,
  progress: `Done: DigiPae brand, product design, and app prototype screens; earlier digital-payments exploration, now secondary; positioning and launch content.
In progress: identity-verification integration; government benefits product development; staging environment and prototype; customer discovery and outreach.
Next 6–12 months: design-partner agreements, first permitted data-source integration, security and privacy baseline, and a paid pilot with defined success metrics.
Traction placeholders must be filled with real numbers before sharing. We do not claim paying customers, pilots, live government connections, partnerships, or production readiness.`,
  team: `Founder: Lochan Reddy (role and background to confirm). Cofounder: to confirm.
Why us: the founders' firsthand view of the problem (add the specific story) and the product, brand, and prototype work already shipped.
Planned hires and advisers: a founding engineer for integrations and security; a privacy and compliance adviser; a government benefits policy adviser.
Do not add credentials or prior employers that are not confirmed.`,
  ask: `Close: government services should be easier to connect to, easier to navigate, and easier to build upon.
Near-term milestones: sign design partners in benefits workflows, ship the first permitted integration, run a measured pilot, and establish a security and privacy baseline.
The ask, instrument, runway, and use-of-funds split are placeholders to confirm before fundraising.
Contact: digipae.com.`,
  sources: `Every statistic on the problem and market slides traces to one of these sources. KFF's unwinding tracker was archived on September 12, 2024. The OMB paperwork figure is cited via CEI's reporting of OMB's annual burden report; confirm against the OMB report before external use.`,
  assumptions: `TAM, SAM, and SOM are built bottom-up from dated organization counts and illustrative ACVs. Replace the ACV assumptions with customer-discovery data as soon as it exists, and add a count for benefits-technology platforms.`,
};

// ---------- build ----------
async function build(kind) {
  const full = kind === "full";
  const pres = makeDeck(full ? "DigiPae — Investor Pitch Deck" : "DigiPae — YC-Style 7-Slide Deck");
  if (full) {
    pres.addSection({ title: "Story" });
    await S.cover(pres, "Story"); await S.problem(pres, "Story"); await S.impact(pres, "Story");
    pres.addSection({ title: "Product" });
    await S.solution(pres, "Product"); await S.experience(pres, "Product"); await S.architecture(pres, "Product");
    pres.addSection({ title: "Business" });
    await S.gtm(pres, "Business"); await S.model(pres, "Business"); await S.market(pres, "Business"); await S.competition(pres, "Business");
    pres.addSection({ title: "Company" });
    await S.progress(pres, "Company"); await S.team(pres, "Company"); await S.ask(pres, "Company");
    pres.addSection({ title: "Appendix" });
    await S.sources(pres, "Appendix"); await S.assumptions(pres, "Appendix");
  } else {
    pres.addSection({ title: "YC" });
    await S.cover(pres, "YC");
    await S.impact(pres, "YC", "01 · Problem");
    await S.solution(pres, "YC", "02 · Solution");
    await S.progress(pres, "YC", "03 · Traction & progress");
    await S.market(pres, "YC", "04 · Market");
    await S.team(pres, "YC", "05 · Team");
    await S.ask(pres, "YC", "06 · Ask");
  }
  const file = path.join(OUT, full ? "DigiPae_Investor_Deck.pptx" : "DigiPae_YC_7-Slide.pptx");
  await pres.writeFile({ fileName: file });
  if (SKILL) {
    const { applyTheme } = require(path.join(SKILL, "scripts", "apply_theme.js"));
    await applyTheme(file, THEME);
  }
  console.log("wrote", file);
}
(async () => { for (const n of ICONS) await icon(n, COL.cyan); await build("full"); await build("yc"); })();
