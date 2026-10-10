# Brand tokens

`tokens.yml` is authoritative. Each accent defines text and its tinted background,
not a bare swatch. All pairs pass WCAG AA normal-text contrast (≥4.5:1).
The unit tests compute sRGB relative luminance in both themes.

| Accent | Light text | Light background | Ratio | Dark text | Dark background | Ratio |
| --- | --- | --- | --- | --- | --- | --- |
| foundation-blue | #075985 | #e0f2fe | 6.59:1 | #7dd3fc | #082f49 | 8.32:1 |
| iot-green | #166534 | #dcfce7 | 6.49:1 | #86efac | #052e16 | 10.62:1 |
| protocol-violet | #5b21b6 | #ede9fe | 7.57:1 | #c4b5fd | #2e1065 | 8.25:1 |
| interface-amber | #92400e | #fef3c7 | 6.37:1 | #fcd34d | #451a03 | 10.39:1 |
| teal | #115e59 | #ccfbf1 | 6.73:1 | #5eead4 | #042f2e | 9.78:1 |
| coral | #9f1239 | #ffe4e6 | 6.68:1 | #fda4af | #4c0519 | 8.27:1 |
| slate | #334155 | #f1f5f9 | 9.45:1 | #cbd5e1 | #0f172a | 12.02:1 |
| neutral-grey | #374151 | #f3f4f6 | 9.37:1 | #d1d5db | #111827 | 12.04:1 |

Area mappings live in `tokens.yml`. The three product overrides are foundation
blue, IoT green and protocol violet. Applications, including CodexUI, use interface
amber. The remaining areas use teal, coral, slate and neutral grey respectively.

Glyphs share a 24×24 view box and 1.5-unit stroke; their color is `currentColor`.
The organization mark is copied unchanged from SNode.C, not redrawn or recolored.
Its source commit and path are recorded in [EVIDENCE.md](../EVIDENCE.md).
