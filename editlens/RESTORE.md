# Restore EditLens

The runnable browser demo is intentionally not published right now because the model output is not reliable enough for a public tool.

To re-enable it later:

1. Rename `editlens/index.draft.html.txt` to `editlens/index.html`.
2. Add the EditLens list item back to the root `index.html`.
3. If faster browser inference matters, apply the Cloudflare response-header rule described in `docs/hosting.md`.
4. Re-run a real browser smoke test before pushing.

Suggested homepage entry:

```html
<ul>
  <li>
    <a href="/editlens/">EditLens in the Browser</a>
    <span class="meta">&middot; local browser reproduction of Pangram's EditLens model &middot; <a href="https://github.com/benreeve1984/tools.benreeve.dev/commits/main/editlens">history</a></span>
  </li>
</ul>
```
