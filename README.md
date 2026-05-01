# tools.benreeve.dev

Source for [tools.benreeve.dev](https://tools.benreeve.dev) — local-first browser tools and static experiments by Ben Reeve.

## Stack

- Plain HTML/CSS/JS by default. Heavier tools may use a directory with local assets, workers, WASM, or downloaded model files when the tool needs them.
- Static hosting only. No server-side processing of user data.
- No analytics or trackers. Third-party runtime libraries are allowed only when disclosed and necessary for the tool.
- Hosted from the `main` branch root on GitHub Pages.
- DNS via Cloudflare, served from the proxied custom domain `tools.benreeve.dev`.
- Browser-native tools that need custom headers use Cloudflare Response Header Transform Rules in front of GitHub Pages.
- Sister repo [`benreeve.dev`](https://github.com/benreeve1984/benreeve.dev) hosts the main site

## Layout

```
.
├── CNAME         # tells GitHub Pages which custom domain to serve
├── README.md
├── editlens/     # example directory-based browser-native tool
├── index.html    # landing page listing all tools
└── scripts/      # deployment helpers for static hosting
```

## Adding a tool

1. For a small tool, create `tool-slug.html` in the repo root and keep it self-contained.
2. For a heavier browser-native tool, create `tool-slug/` with an `index.html` and any local static assets it needs.
3. Add an entry to `index.html` using the template at the bottom of that file.
4. Commit and push. The tool is live at `https://tools.benreeve.dev/tool-slug.html` or `https://tools.benreeve.dev/tool-slug/`.
5. Optionally, add a corresponding entry to the colophon on [benreeve.dev](https://benreeve.dev/colophon.html).

## Local preview

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deployment

Pushing to `main` deploys automatically through GitHub Pages. Cloudflare remains in front of the GitHub Pages origin so specific tools can get response headers that GitHub Pages cannot set.

EditLens requires cross-origin isolation headers for faster browser inference. Apply or update its Cloudflare Response Header Transform Rule with:

```sh
CLOUDFLARE_API_TOKEN="$(cat /Users/reeve/Developer/.cloudflare_api_token)" \
  scripts/apply-editlens-cloudflare-headers.sh
```

That token must have Transform Rules edit permission on the `benreeve.dev` zone. See `editlens/docs/hosting.md` for the exact rule and verification command.
