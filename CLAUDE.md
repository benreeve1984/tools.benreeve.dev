# CLAUDE.md — instructions for AI assistants

This is the source for https://tools.benreeve.dev — standalone single-page tools by Ben Reeve. Sister repo for the main site is at https://github.com/benreeve1984/benreeve.dev.

## Conventions

- One self-contained HTML file per tool, dropped in the repo root. CSS and JS inline — no shared assets, no subdirectories.
- Use the same serif style as the main site. Copy the inline `<style>` block from `index.html` here for consistency, or from `/Users/reeve/Developer/benreeve.dev/index.html` if working locally.
- Every new tool must (a) include the favicon link + theme-color + open-graph meta block from `index.html`, and (b) get an entry added to `index.html` linking to the tool + its source-history URL on GitHub.
- `CNAME` configures GH Pages — do not delete or edit it.

## Don'ts

- No frameworks, no build step, no bundler, no JSX, no TypeScript. Plain HTML/CSS/JS only.
- No web fonts (Google Fonts, Adobe Fonts, etc.). Stick to the system serif stack already defined.
- No analytics, trackers, or third-party scripts.
- No shared CSS/JS between tools — each tool must work in isolation.
- No changes to the visual style without Ben's explicit approval.
