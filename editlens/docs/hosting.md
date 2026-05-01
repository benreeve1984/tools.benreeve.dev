# Hosting

EditLens is prepared as a static GitHub Pages page with Cloudflare in front of it. The public demo is currently disabled; these notes are for restoring it later.

## Current shape

- Origin: GitHub Pages for `benreeve1984/tools.benreeve.dev`
- Custom domain: `tools.benreeve.dev`
- DNS: Cloudflare proxied `CNAME` to `benreeve1984.github.io`
- Model artifacts: Hugging Face model repo `benreeve/editlens-roberta-large-onnx-int8`
- Runnable draft page source: `editlens/index.draft.html.txt`

GitHub Pages cannot set custom HTTP response headers. For EditLens, Cloudflare must add the response headers that enable cross-origin isolation for faster ONNX Runtime Web execution.

## Required Cloudflare response headers

Apply these headers to `https://tools.benreeve.dev/editlens` and `https://tools.benreeve.dev/editlens/*`:

```text
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Resource-Policy: cross-origin
```

Cloudflare Transform Rule expression:

```text
(http.host eq "tools.benreeve.dev" and (http.request.uri.path eq "/editlens" or starts_with(http.request.uri.path, "/editlens/")))
```

## Apply by API

Use the helper script from the repo root:

```sh
CLOUDFLARE_API_TOKEN="$(cat /Users/reeve/Developer/.cloudflare_api_token)" \
  scripts/apply-editlens-cloudflare-headers.sh
```

The token must be scoped to the `benreeve.dev` zone and must be able to edit response header transform rules. The DNS-only token in `/Users/reeve/Developer/.cloudflare_api_token` can read the zone and DNS record, but currently cannot call the Rulesets API.

## Apply in the dashboard

1. Open Cloudflare dashboard for `benreeve.dev`.
2. Go to Rules, then Transform Rules.
3. Create a Response Header Transform Rule.
4. Use the expression above.
5. Add the three headers above with operation `Set static`.
6. Save and deploy the rule.

## Verify production

After pushing to `main` and adding the Cloudflare rule:

```sh
curl -I https://tools.benreeve.dev/editlens/ | grep -i 'cross-origin'
```

Expected output includes the three headers listed above. In a browser console on the EditLens page, `window.crossOriginIsolated` should be `true`.
