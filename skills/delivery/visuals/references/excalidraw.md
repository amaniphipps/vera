# Excalidraw diagrams

Build hand-drawn style diagrams by writing Excalidraw element JSON and saving as a `.excalidraw` file. These open at excalidraw.com for viewing and editing. No account or API key needed.

## When to use

Architecture diagrams, flowcharts, sequence diagrams, concept maps. Files open at excalidraw.com or export to PNG/SVG for attachment.

## File envelope

Wrap the elements array and save:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "agent",
  "elements": [ ... ],
  "appState": { "viewBackgroundColor": "#ffffff" }
}
```

## Element types

Every element needs `type`, `id` (unique), `x`, `y`, `width`, `height`.

Defaults that apply automatically: `strokeColor` `#1e1e1e`, `backgroundColor` transparent, `fillStyle` solid, `strokeWidth` 2, `roughness` 1 (the hand-drawn look), `opacity` 100. Canvas background is white.

- Rectangle: `{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 100 }`. Add `roundness: { "type": 3 }` for rounded corners.
- Ellipse: `{ "type": "ellipse", ... }`.
- Diamond: `{ "type": "diamond", ... }`.
- Arrow: `{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 200, "height": 0, "points": [[0,0],[200,0]], "endArrowhead": "arrow" }`.
  - `points` are `[dx, dy]` offsets from `x, y`.
  - `endArrowhead`: `null | "arrow" | "bar" | "dot" | "triangle"`.
  - `strokeStyle`: `"solid" | "dashed" | "dotted"`.
- Text: `{ "type": "text", "id": "t1", "x": 150, "y": 138, "text": "Hello", "fontSize": 20, "fontFamily": 1, "strokeColor": "#1e1e1e", "originalText": "Hello", "autoResize": true }`.
  - `x` is the left edge. To center at `cx`, use `x = cx - (len * fontSize * 0.5) / 2`.
  - Do not rely on `textAlign` or `width` to position standalone text.

## Labels: container binding

There is no `label` property on shapes. Writing `"label": { "text": "..." }` is silently ignored and produces blank shapes. Bind a text element to the shape instead.

The shape lists the text in `boundElements`; the text points back with `containerId`:

```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 80,
  "roundness": { "type": 3 }, "backgroundColor": "#a5d8ff", "fillStyle": "solid",
  "boundElements": [{ "id": "t_r1", "type": "text" }] },
{ "type": "text", "id": "t_r1", "x": 105, "y": 110, "width": 190, "height": 25,
  "text": "Hello", "fontSize": 20, "fontFamily": 1, "strokeColor": "#1e1e1e",
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "r1", "originalText": "Hello", "autoResize": true }
```

The pattern works on rectangle, ellipse, diamond, and arrows. Set `fontFamily: 1` (the hand-drawn font) on every text element. Keep `originalText` equal to `text` and set `autoResize: true`.

## Arrow bindings

Connect arrows to shapes with `startBinding` and `endBinding`:

```json
{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 150, "height": 0,
  "points": [[0,0],[150,0]], "endArrowhead": "arrow",
  "startBinding": { "elementId": "r1", "fixedPoint": [1, 0.5] },
  "endBinding": { "elementId": "r2", "fixedPoint": [0, 0.5] } }
```

`fixedPoint` anchors: top `[0.5,0]`, bottom `[0.5,1]`, left `[0,0.5]`, right `[1,0.5]`.

Arrow points must start at `[0,0]`: `[[0,0], [dx,dy], ...]`. A single-point arrow (`[[dx,dy]]` with no `[0,0]`) renders nothing on export. Arrowhead direction follows point order, start to end.

## Z-order

Array order is draw order. First is back, last is front. Emit progressively: background zone, shape, its bound text, its arrows, next shape. Do not batch all rectangles then all texts then all arrows. Place bound text right after its container shape.

## Sizing

- Minimum font size 16 for body and labels, 20 for titles, 14 only for secondary annotations and sparingly. Never below 14.
- Minimum shape size about 120x60 for labeled boxes.
- Leave 20 to 30 px gaps between elements. Prefer fewer, larger elements over many tiny ones.

## Color (light background)

Pastel fills for shape backgrounds:

| Use | Fill | Hex |
|---|---|---|
| Primary / input | light blue | `#a5d8ff` |
| Success / output | light green | `#b2f2bb` |
| Warning / external | light orange | `#ffd8a8` |
| Processing / special | light purple | `#d0bfff` |
| Error / critical | light red | `#ffc9c9` |
| Notes / decisions | light yellow | `#fff3bf` |
| Storage / data | light teal | `#c3fae8` |

Primary stroke colors: blue `#4a9eed`, amber `#f59e0b`, green `#22c55e`, red `#ef4444`, purple `#8b5cf6`.

Text contrast is critical. Minimum text color on white is `#757575`; do not use light gray on white. Colored text on light fills uses a dark variant. White text only on dark backgrounds.

Background zones for layered diagrams: blue `#dbe4ff`, purple `#e5dbff`, green `#d3f9d8`, with opacity 30 to 35.

No emoji in text. Excalidraw's font does not render emoji.

## Dark mode

The first element is a large dark rectangle covering the canvas:

```json
{ "type": "rectangle", "id": "darkbg", "x": -4000, "y": -3000,
  "width": 10000, "height": 7500, "backgroundColor": "#1e1e2e",
  "fillStyle": "solid", "strokeColor": "transparent", "strokeWidth": 0 }
```

Then use dark fills (blue `#1e3a5f`, green `#1a4d2e`, purple `#2d1b69`, orange `#5c3d1a`, red `#5c1a1a`, teal `#1a4d4d`) and light text (`#e5e5e5` primary, `#a0a0a0` muted). Never use text darker than `#555` on dark.

## Mermaid to Excalidraw

If you start from a Mermaid diagram, translate it by hand. Nodes become rectangles, ellipses, or diamonds. Edges become arrows with bindings. Apply the same binding and z-order rules above. If a converter is available in your toolchain, use it as a first pass, then check the output against the same rules.

## Export to PNG/SVG

For a shareable file, upload the `.excalidraw` (if your toolchain has that helper) or open at excalidraw.com and export.

For a local PNG/SVG render without a browser, the official renderer is `@excalidraw/excalidraw` with `exportToSvg`, rendered to PNG with resvg. Gotchas from real runs:

- `convertToExcalidrawElements` normalizes hand-written JSON, but bound text inside boxes renders off-center in the offline export. Recenter labels from the bundled font metrics before export, and run a recenter pass after conversion too.
- Convert the bundled woff2 fonts to ttf before rendering. If a font is missing, resvg falls back to plain sans glyphs and still exits 0. Vision-check the hand-drawn look; do not trust exit code 0.
- jsdom needs a URL (`http://localhost/`) or localStorage throws. Stub the 2D context return, which jsdom gives as null but the renderer feature-tests on.
- Count rendered arrows by matching each source `x,y` against the SVG transforms, then vision-check direction. Do not grep for `marker-end`; Excalidraw draws arrowheads as paths.
- The browser at excalidraw.com is the best visual QA tool for the shareable file. Use the local pipeline when a PNG/SVG attachment is the deliverable.