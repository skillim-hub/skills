#!/usr/bin/env bash
set -euo pipefail
ENVIRONMENT="${1:-${PARKING_FINE_ENV:-sandbox}}"
CREATE_RESPONSE="$(parking-fine-checker create \
  --env "$ENVIRONMENT" \
  --issuer-type "${PARKING_FINE_ISSUER_TYPE:-municipality}" \
  --issuer-name "${PARKING_FINE_ISSUER_NAME:-Example Municipality}" \
  --vehicle-number "${PARKING_FINE_VEHICLE_NUMBER:-12-345-67}" \
  --notice-number "${PARKING_FINE_NOTICE_NUMBER:-1001}" \
  --amount-ils "${PARKING_FINE_AMOUNT_ILS:-250.00}" \
  --notice-date "${PARKING_FINE_NOTICE_DATE:-10/03/2026}" \
  --due-date "${PARKING_FINE_DUE_DATE:-08/06/2026}")"
CASE_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["case_id"])' <<< "$CREATE_RESPONSE")"
parking-fine-checker lookup \
  --env "$ENVIRONMENT" \
  --case-id "$CASE_ID" \
  --issuer-type "${PARKING_FINE_ISSUER_TYPE:-municipality}" \
  --issuer-name "${PARKING_FINE_ISSUER_NAME:-Example Municipality}" \
  --vehicle-number "${PARKING_FINE_VEHICLE_NUMBER:-12-345-67}" \
  --notice-number "${PARKING_FINE_NOTICE_NUMBER:-1001}"
