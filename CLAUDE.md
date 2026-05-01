# CLAUDE.md — instructions for AI assistants

This is the source for https://tools.benreeve.dev — local-first browser tools and static experiments by Ben Reeve. Sister repo for the main site is at https://github.com/benreeve1984/benreeve.dev.

## Conventions

- Prefer one self-contained root HTML file for simple tools.
- Heavier browser-native tools may live in `/tool-slug/` with local JS/CSS/assets, workers, WASM, or model-download code when the tool genuinely needs them.
- Tools must remain static: no backend, no analytics, no trackers, and no server-side processing of user data.
- Use the same serif style as the main site. Copy the inline `<style>` block from `index.html` here for consistency, or from `/Users/reeve/Developer/benreeve.dev/index.html` if working locally.
- Every new tool must (a) include the favicon link + theme-color + open-graph meta block from `index.html`, and (b) get an entry added to `index.html` linking to the tool + its source-history URL on GitHub.
- `CNAME` configures GH Pages — do not delete or edit it.

## Don'ts

- Avoid frameworks, build steps, bundlers, JSX, and TypeScript unless the tool genuinely needs them. Prefer plain HTML/CSS/JS.
- No web fonts (Google Fonts, Adobe Fonts, etc.). Stick to the system serif stack already defined.
- No analytics or trackers. Third-party runtime libraries are allowed only when the tool genuinely needs them, and the tool must disclose what is downloaded.
- No shared CSS/JS between tools — each tool must work in isolation.
- No changes to the visual style without Ben's explicit approval.
