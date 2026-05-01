#!/usr/bin/env bash
set -euo pipefail

: "${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN to a token with Zone Transform Rules edit permission.}"

ZONE_ID="${CLOUDFLARE_ZONE_ID:-95c79f8d93126779470e44d157ae0b95}"
HOSTNAME="${CLOUDFLARE_HOSTNAME:-tools.benreeve.dev}"
PHASE="http_response_headers_transform"
RULE_REF="editlens_cross_origin_isolation_headers"
API_BASE="https://api.cloudflare.com/client/v4/zones/${ZONE_ID}"

cf_api() {
  local method="$1"
  local path="$2"
  local data="${3:-}"
  local response

  if [[ -n "$data" ]]; then
    response="$(curl -sS \
      --request "$method" \
      --header "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
      --header "Content-Type: application/json" \
      --data "$data" \
      "${API_BASE}${path}")"
  else
    response="$(curl -sS \
      --request "$method" \
      --header "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
      "${API_BASE}${path}")"
  fi

  if ! jq -e '.success == true' >/dev/null <<<"$response"; then
    jq -r '.errors[]? | "Cloudflare API error \(.code): \(.message)"' <<<"$response" >&2
    return 1
  fi

  printf '%s\n' "$response"
}

rule_json="$(jq -n \
  --arg host "$HOSTNAME" \
  --arg ref "$RULE_REF" \
  '{
    ref: $ref,
    description: "Cross-origin isolation headers for EditLens browser inference",
    expression: "(http.host eq \"\($host)\" and (http.request.uri.path eq \"/editlens\" or starts_with(http.request.uri.path, \"/editlens/\")))",
    action: "rewrite",
    action_parameters: {
      headers: {
        "Cross-Origin-Opener-Policy": {
          operation: "set",
          value: "same-origin"
        },
        "Cross-Origin-Embedder-Policy": {
          operation: "set",
          value: "require-corp"
        },
        "Cross-Origin-Resource-Policy": {
          operation: "set",
          value: "cross-origin"
        }
      }
    }
  }')"

rulesets="$(cf_api GET /rulesets)"
ruleset_id="$(jq -r --arg phase "$PHASE" '.result[]? | select(.kind == "zone" and .phase == $phase) | .id' <<<"$rulesets" | head -n 1)"

if [[ -z "$ruleset_id" ]]; then
  payload="$(jq -n \
    --arg phase "$PHASE" \
    --argjson rule "$rule_json" \
    '{
      name: "Zone response header transforms",
      description: "Zone-level response header transform rules.",
      kind: "zone",
      phase: $phase,
      rules: [$rule]
    }')"
  created="$(cf_api POST /rulesets "$payload")"
  jq -r '.result | "Created ruleset \(.id) with EditLens header rule."' <<<"$created"
  exit 0
fi

ruleset="$(cf_api GET "/rulesets/${ruleset_id}")"
payload="$(jq \
  --arg ref "$RULE_REF" \
  --argjson rule "$rule_json" \
  '.result
    | {
        name,
        description,
        kind,
        phase,
        rules: (((.rules // []) | map(select(.ref != $ref))) + [$rule])
      }' <<<"$ruleset")"

updated="$(cf_api PUT "/rulesets/${ruleset_id}" "$payload")"
jq -r '.result | "Updated ruleset \(.id) with EditLens header rule."' <<<"$updated"
