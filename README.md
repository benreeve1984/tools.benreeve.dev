# tools.benreeve.dev

Source for [tools.benreeve.dev](https://tools.benreeve.dev) — standalone single-page tools, each living as its own self-contained HTML file.

## Stack

- Plain HTML (and inline CSS/JS as needed per tool), no framework, no build step
- Hosted on [GitHub Pages](https://pages.github.com/) from the `main` branch root
- DNS via Cloudflare, served from custom domain `tools.benreeve.dev`
- Sister repo [`benreeve.dev`](https://github.com/benreeve1984/benreeve.dev) hosts the main site

## Layout

```
.
├── CNAME         # tells GitHub Pages which custom domain to serve
├── README.md
└── index.html    # landing page listing all tools
```

## Adding a tool

1. Create `tool-slug.html` in the repo root. Make it self-contained (inline CSS and JS — no build step, no shared assets).
2. Add an entry to `index.html` using the template at the bottom of that file.
3. Commit and push. The tool is live at `https://tools.benreeve.dev/tool-slug.html` within a minute.
4. Optionally, add a corresponding entry to the colophon on [benreeve.dev](https://benreeve.dev/colophon.html).

## Local preview

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deployment

Pushing to `main` deploys automatically via GitHub Pages.
