---
name: algorithmic-art
description: Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request generative art, flow fields, particle systems, or algorithmic visuals. Deliver a standalone local HTML viewer and original code rather than platform-specific runtime output.
license: Complete terms in LICENSE.txt
---

Algorithmic philosophies are computational aesthetic movements that are then expressed through code. Output a philosophy `.md` file plus a standalone local `viewer.html` file, and optionally a separate `.js` source file if the user explicitly wants split files.

This happens in two steps:
1. Algorithmic Philosophy Creation (`.md`)
2. Express it by creating p5.js generative art (`viewer.html`, optionally `sketch.js`)

First, undertake this task:

## ALGORITHMIC PHILOSOPHY CREATION

To begin, create an ALGORITHMIC PHILOSOPHY (not static images or templates) that will be interpreted through:
- Computational processes, emergent behavior, mathematical beauty
- Seeded randomness, noise fields, organic systems
- Particles, flows, fields, forces
- Parametric variation and controlled chaos

### THE CRITICAL UNDERSTANDING
- What is received: Some subtle input or instructions by the user to take into account, but use as a foundation; it should not constrain creative freedom.
- What is created: An algorithmic philosophy/generative aesthetic movement.
- What happens next: The implementation pass receives the philosophy and expresses it in code, creating p5.js sketches that are 90% algorithmic generation and 10% essential parameters.

Consider this approach:
- Write a manifesto for a generative art movement
- The next phase involves writing the algorithm that brings it to life

The philosophy must emphasize: Algorithmic expression. Emergent behavior. Computational beauty. Seeded variation.

### HOW TO GENERATE AN ALGORITHMIC PHILOSOPHY

**Name the movement** (1-2 words): "Organic Turbulence" / "Quantum Harmonics" / "Emergent Stillness"

**Articulate the philosophy** (4-6 paragraphs - concise but complete):

To capture the ALGORITHMIC essence, express how this philosophy manifests through:
- Computational processes and mathematical relationships?
- Noise functions and randomness patterns?
- Particle behaviors and field dynamics?
- Temporal evolution and system states?
- Parametric variation and emergent complexity?

**CRITICAL GUIDELINES:**
- **Avoid redundancy**: Each algorithmic aspect should be mentioned once. Avoid repeating concepts about noise theory, particle dynamics, or mathematical principles unless adding new depth.
- **Emphasize craftsmanship REPEATEDLY**: The philosophy MUST stress multiple times that the final algorithm should appear as though it took countless hours to develop, was refined with care, and comes from someone at the absolute top of their field. This framing is essential - repeat phrases like "meticulously crafted algorithm," "the product of deep computational expertise," "painstaking optimization," "master-level implementation."
- **Leave creative space**: Be specific about the algorithmic direction, but concise enough that the implementation pass still has room to make interpretive implementation choices at an extremely high level of craftsmanship.

The philosophy must guide the implementation to express ideas ALGORITHMICALLY, not through static images. Beauty lives in the process, not the final frame.

### PHILOSOPHY EXAMPLES

**"Organic Turbulence"**
Philosophy: Chaos constrained by natural law, order emerging from disorder.
Algorithmic expression: Flow fields driven by layered Perlin noise. Thousands of particles following vector forces, their trails accumulating into organic density maps. Multiple noise octaves create turbulent regions and calm zones. Color emerges from velocity and density - fast particles burn bright, slow ones fade to shadow. The algorithm runs until equilibrium - a meticulously tuned balance where every parameter was refined through countless iterations by a master of computational aesthetics.

**"Quantum Harmonics"**
Philosophy: Discrete entities exhibiting wave-like interference patterns.
Algorithmic expression: Particles initialized on a grid, each carrying a phase value that evolves through sine waves. When particles are near, their phases interfere - constructive interference creates bright nodes, destructive creates voids. Simple harmonic motion generates complex emergent mandalas. The result of painstaking frequency calibration where every ratio was carefully chosen to produce resonant beauty.

**"Recursive Whispers"**
Philosophy: Self-similarity across scales, infinite depth in finite space.
Algorithmic expression: Branching structures that subdivide recursively. Each branch slightly randomized but constrained by golden ratios. L-systems or recursive subdivision generate tree-like forms that feel both mathematical and organic. Subtle noise perturbations break perfect symmetry. Line weights diminish with each recursion level. Every branching angle the product of deep mathematical exploration.

**"Field Dynamics"**
Philosophy: Invisible forces made visible through their effects on matter.
Algorithmic expression: Vector fields constructed from mathematical functions or noise. Particles born at edges, flowing along field lines, dying when they reach equilibrium or boundaries. Multiple fields can attract, repel, or rotate particles. The visualization shows only the traces - ghost-like evidence of invisible forces. A computational dance meticulously choreographed through force balance.

**"Stochastic Crystallization"**
Philosophy: Random processes crystallizing into ordered structures.
Algorithmic expression: Randomized circle packing or Voronoi tessellation. Start with random points, let them evolve through relaxation algorithms. Cells push apart until equilibrium. Color based on cell size, neighbor count, or distance from center. The organic tiling that emerges feels both random and inevitable. Every seed produces unique crystalline beauty - the mark of a master-level generative algorithm.

*These are condensed examples. The actual algorithmic philosophy should be 4-6 substantial paragraphs.*

### ESSENTIAL PRINCIPLES
- **ALGORITHMIC PHILOSOPHY**: Creating a computational worldview to be expressed through code
- **PROCESS OVER PRODUCT**: Always emphasize that beauty emerges from the algorithm's execution - each run is unique
- **PARAMETRIC EXPRESSION**: Ideas communicate through mathematical relationships, forces, behaviors - not static composition
- **ARTISTIC FREEDOM**: The implementation pass interprets the philosophy algorithmically - provide creative implementation room
- **PURE GENERATIVE ART**: This is about making LIVING ALGORITHMS, not static images with randomness
- **EXPERT CRAFTSMANSHIP**: Repeatedly emphasize the final algorithm must feel meticulously crafted, refined through countless iterations, the product of deep expertise by someone at the absolute top of their field in computational aesthetics

**The algorithmic philosophy should be 4-6 paragraphs long.** Fill it with poetic computational philosophy that brings together the intended vision. Avoid repeating the same points. Output this algorithmic philosophy as a `.md` file.

---

## DEDUCING THE CONCEPTUAL SEED

**CRITICAL STEP**: Before implementing the algorithm, identify the subtle conceptual thread from the original request.

**THE ESSENTIAL PRINCIPLE**:
The concept is a **subtle, niche reference embedded within the algorithm itself** - not always literal, always sophisticated. Someone familiar with the subject should feel it intuitively, while others simply experience a masterful generative composition. The algorithmic philosophy provides the computational language. The deduced concept provides the soul - the quiet conceptual DNA woven invisibly into parameters, behaviors, and emergence patterns.

This is **VERY IMPORTANT**: The reference must be so refined that it enhances the work's depth without announcing itself. Think like a jazz musician quoting another song through algorithmic harmony - only those who know will catch it, but everyone appreciates the generative beauty.

---

## P5.JS IMPLEMENTATION

With the philosophy AND conceptual framework established, express it through code. Pause to gather thoughts before proceeding. Use the philosophy you created and the instructions below.

### ⚠️ STEP 0: READ THE TEMPLATES FIRST ⚠️

**CRITICAL: BEFORE writing any HTML:**

1. **Read** `templates/viewer.html`
2. **Read** `templates/generator_template.js`
3. **Use them as the starting point** for a standalone local viewer with sidebar controls, seeded exploration, and export actions
4. **Keep the parts that make exploration easy**: layout shell, seed controls, parameter wiring, and regenerate/reset/download actions
5. **Replace the demo copy, palette, parameter set, and algorithm** with something original for the request

**Avoid:**
- Creating platform-specific output that only works in a hosted runtime
- Depending on hidden APIs or undocumented viewer features
- Leaving behind pseudo-code or placeholders when a working viewer is expected

**Follow these practices:**
- Deliver files that work when saved locally and opened in a browser
- Prefer a single `viewer.html` with inline UI and JS unless the user wants split files
- Keep the algorithm original to the request; the template is scaffolding, not the finished piece

To create gallery-quality computational art that lives and breathes, use the algorithmic philosophy as the foundation.

### TECHNICAL REQUIREMENTS

**Seeded Randomness (Art Blocks Pattern)**:
```javascript
let seed = 12345;
randomSeed(seed);
noiseSeed(seed);
```

**Parameter Structure - FOLLOW THE PHILOSOPHY**:

To establish parameters that emerge naturally from the algorithmic philosophy, consider: "What qualities of this system can be adjusted?"

```javascript
let params = {
  seed: 12345,
  // Add parameters that control YOUR algorithm:
  // - Quantities (how many?)
  // - Scales (how big? how fast?)
  // - Probabilities (how likely?)
  // - Ratios (what proportions?)
  // - Angles (what direction?)
  // - Thresholds (when does behavior change?)
};
```

**To design effective parameters, focus on the properties the system needs to be tunable rather than thinking in terms of "pattern types."**

**Core Algorithm - EXPRESS THE PHILOSOPHY**:

**CRITICAL**: The algorithmic philosophy should dictate what to build.

To express the philosophy through code, avoid thinking "which pattern should I use?" and instead think "how do I express this philosophy through code?"

If the philosophy is about **organic emergence**, consider using:
- Elements that accumulate or grow over time
- Random processes constrained by natural rules
- Feedback loops and interactions

If the philosophy is about **mathematical beauty**, consider using:
- Geometric relationships and ratios
- Trigonometric functions and harmonics
- Precise calculations creating unexpected patterns

If the philosophy is about **controlled chaos**, consider using:
- Random variation within strict boundaries
- Bifurcation and phase transitions
- Order emerging from disorder

**The algorithm flows from the philosophy, not from a menu of options.**

To guide the implementation, let the conceptual essence inform creative and original choices. Build something that expresses the vision for this particular request.

**Canvas Setup**: Standard p5.js structure:
```javascript
function setup() {
  createCanvas(1200, 1200);
  // Initialize your system
}

function draw() {
  // Your generative algorithm
  // Can be static (noLoop) or animated
}
```

### CRAFTSMANSHIP REQUIREMENTS

**CRITICAL**: To achieve mastery, create algorithms that feel like they emerged through countless iterations by a master generative artist. Tune every parameter carefully. Ensure every pattern emerges with purpose. This is NOT random noise - this is CONTROLLED CHAOS refined through deep expertise.

- **Balance**: Complexity without visual noise, order without rigidity
- **Color Harmony**: Thoughtful palettes, not random RGB values
- **Composition**: Even in randomness, maintain visual hierarchy and flow
- **Performance**: Smooth execution, optimized for real-time if animated
- **Reproducibility**: The same seed should always produce the same result

### OUTPUT FORMAT

Output:
1. **Algorithmic Philosophy** - Markdown or text explaining the generative aesthetic
2. **Standalone Viewer** - A self-contained `viewer.html` with p5.js, the algorithm, parameter controls, and UI
3. **Optional Editable Source** - `sketch.js` only when a split-file setup helps the user

The viewer should run locally in a browser with no platform-specific runtime required. Start from the provided template, then replace the demo algorithm with something original.

---

## INTERACTIVE VIEWER CREATION

**REMINDER: `templates/viewer.html` and `templates/generator_template.js` should already have been read (see STEP 0). Use them as the foundation.**

To allow exploration of the generative art, create a self-contained local HTML viewer. Ensure the file works immediately when opened in a browser - no additional platform features required.

### CRITICAL: WHAT'S FIXED VS VARIABLE

The template files provide the general scaffolding needed for a clean local experience.

**KEEP OR ADAPT DELIBERATELY:**
- Layout structure (header, sidebar, main canvas area)
- Seed section in the sidebar
- Actions section with regenerate, reset, and download controls
- Clear parameter wiring between the UI and the p5.js sketch

**CUSTOMIZE FOR EACH PIECE:**
- The entire p5.js algorithm
- The parameters object
- The Parameters section in the sidebar
- The Colors section if the piece needs adjustable palettes
- The title, subtitle, and explanatory copy

**Every viewer should have unique parameters and an original algorithm.** The shell provides usability; the artwork provides identity.

### REQUIRED FEATURES

**1. Parameter Controls**
- Sliders for numeric parameters (particle count, noise scale, speed, etc.)
- Color pickers only when the piece benefits from editable palettes
- Real-time or quick-regeneration updates when parameters change
- A reset button to restore defaults

**2. Seed Navigation**
- Display the current seed number
- "Previous" and "Next" buttons to cycle through seeds
- "Random" for quick exploration
- A numeric input to jump to a specific seed
- When the user asks for many variations, expose presets or export numbered outputs

**3. Single-File Structure**
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
  <style>
    /* All viewer styling inline */
  </style>
</head>
<body>
  <div id="canvas-container"></div>
  <div id="controls"></div>
  <script>
    // All p5.js code and UI handlers inline here
  </script>
</body>
</html>
```

**4. Action Controls**
- Regenerate button
- Reset button
- Download PNG button

### USING THE VIEWER

The local HTML viewer should work immediately:
1. **As a file**: Save `viewer.html` and open it in any browser
2. **For editing**: Keep the logic inline, or split it into `viewer.html` + `sketch.js` if the user explicitly wants editable source separation
3. **For sharing**: Hand off the HTML file or the HTML/JS pair as normal local files

---

## VARIATIONS & EXPLORATION

The viewer should include seed navigation by default, allowing users to explore variations without regenerating everything from scratch. If the user wants specific variations highlighted:

- Add preset seed buttons ("Variation 1: Seed 42", etc.)
- Add a gallery mode that renders multiple seeds sequentially or exports numbered PNGs
- Keep the workflow grounded in the same local viewer

This is like creating a series of prints from the same plate - the algorithm is consistent, but each seed reveals different facets of its potential.

---

## THE CREATIVE PROCESS

**User request** → **Algorithmic philosophy** → **Implementation**

Each request is unique. The process involves:
1. **Interpret the user's intent** - What aesthetic is being sought?
2. **Create an algorithmic philosophy** (4-6 paragraphs) describing the computational approach
3. **Implement it in code** - Build the algorithm that expresses this philosophy
4. **Design appropriate parameters** - What should be tunable?
5. **Build matching UI controls** - Sliders, inputs, or pickers for those parameters

**The constants**:
- A clean local viewer shell
- Seed navigation
- A standalone HTML deliverable

**Everything else is variable**:
- The algorithm itself
- The parameters
- The UI controls
- The visual outcome

To achieve the best results, trust creativity and let the philosophy guide the implementation.

---

## RESOURCES

This skill includes helpful templates and documentation:

- **templates/viewer.html**: Starting point for local generative-art viewers
  - Keep the overall layout, seed controls, and actions unless the request clearly needs something different
  - Replace the demo title, parameters, palette, and algorithm
  - Use it to ship a working local viewer, not a mockup

- **templates/generator_template.js**: Reference for p5.js best practices and code structure principles
  - Shows how to organize parameters, use seeded randomness, and structure classes
  - Use these principles to build something original
  - Embed algorithms inline in `viewer.html` unless split files are specifically helpful

**Critical reminder**:
- The templates are the **starting point**, not the finished answer
- The **algorithm is where you create** something unique
- Don't copy the demo blindly - build what the philosophy demands
