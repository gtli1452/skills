/**
 * Generative art starter patterns for local HTML sketches.
 * Use p5.js if it is already available, or translate the same structure to
 * Canvas API / SVG when offline execution matters more than library choice.
 */

let params = {
  seed: 12345,
  density: 0.55,
  drift: 0.72,
  flowScale: 0.014,
  lineWeight: 1.2,
  background: '#050816',
  palette: ['#38bdf8', '#a78bfa', '#f97316', '#f8fafc']
};

function initializeSeed(seed) {
  params.seed = Number(seed) || 1;
  if (typeof randomSeed === 'function') randomSeed(params.seed);
  if (typeof noiseSeed === 'function') noiseSeed(params.seed);
}

function setup() {
  createCanvas(1200, 1200);
  pixelDensity(2);
  initializeSeed(params.seed);
  buildScene();
  noLoop();
}

function draw() {
  background(params.background);
  renderScene();
}

function regenerate(nextParams = {}) {
  params = { ...params, ...nextParams };
  initializeSeed(params.seed);
  buildScene();
  if (typeof redraw === 'function') redraw();
}

function updateParameter(name, value) {
  const numeric = Number(value);
  params[name] = Number.isFinite(numeric) ? numeric : value;
  regenerate();
}

function buildScene() {
  // Precompute particles, fields, cells, or geometry here.
  // Keep generation deterministic by only using seeded randomness.
}

function renderScene() {
  // Render the scene here. Separate generation from drawing when possible.
}

function exportImage(prefix = 'generative-art') {
  if (typeof saveCanvas === 'function') {
    saveCanvas(`${prefix}-${params.seed}`, 'png');
  }
}

function fadeBackground(hex, alpha = 18) {
  const c = color(hex);
  c.setAlpha(alpha);
  noStroke();
  fill(c);
  rect(0, 0, width, height);
}

function hashStringToSeed(input) {
  let hash = 0;
  for (let i = 0; i < input.length; i += 1) {
    hash = (hash << 5) - hash + input.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash) || 1;
}

function mulberry32(seed) {
  let t = seed >>> 0;
  return function next() {
    t += 0x6D2B79F5;
    let value = Math.imul(t ^ (t >>> 15), 1 | t);
    value ^= value + Math.imul(value ^ (value >>> 7), 61 | value);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}
