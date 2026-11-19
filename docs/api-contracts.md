# API Contracts and Mapping Rules

## Status

Design specification for the initial lab. These interfaces are not yet implemented.

## Services

- Order API: accepts orders, exposes delivery status, and supports replay.
- Fulfilment API: receives mapped orders and exposes destination records.

Both services accept and return JSON.

## Order Payload

```json
{
  "orderId": "ORD-1001",
  "productId": "CHAIR-001",
  "quantity": 2
}
```

| Field | Type | Rules |
|---|---|---|
| orderId | string | 1–64 characters; letters, digits, hyphens, and underscores only |
| productId | string | 1–64 characters; letters, digits, hyphens, and underscores only |
| quantity | integer | 1–10000 inclusive; strings, booleans, fractions, and null rejected |

All fields are required. Unknown fields are rejected.

Identifiers are case-sensitive. Values are not trimmed or otherwise normalised.

## Headers

### Content-Type

POST requests require `application/json`.

### Idempotency-Key

Required for `POST /orders`.

- 1–128 characters.
- Letters, digits, hyphens, and underscores only.
- Case-sensitive.
- Associated with one validated order payload.
- Retained for the lifetime of the stored order in this lab.
- Invalid requests do not reserve the key.

Payload equality compares validated field values, independent of JSON property order.

### X-Correlation-ID

Optional on incoming requests.

- Same format rules as Idempotency-Key.
- If absent, the service generates a UUID.
- An invalid supplied value produces a validation error.
- Responses include this header.
- Accepted orders retain their original correlation ID.
- Delivery attempts and replay use that original ID.
- A repeated incoming request may have its own request correlation ID; it does not replace the stored order correlation ID.

## Order API

### POST /orders

Accept an order for processing.

| Condition | HTTP status | Outcome |
|---|---|---|
| New valid order and unused key | 202 | Order persisted and accepted for delivery |
| Existing key with identical payload | 200 | Existing order returned without scheduling another delivery |
| Existing key with different payload | 409 | Idempotency conflict |
| Existing orderId submitted under another key | 409 | Order identity conflict |
| Invalid payload or required header | 422 | Validation error |
| Malformed JSON | 400 | Invalid JSON error |
| Unsupported content type | 415 | Unsupported media type |
| Storage unavailable before acceptance | 503 | Acceptance not confirmed; caller may retry with the same key |

Acceptance does not mean fulfilment has completed.

New order response:

```json
{
  "orderId": "ORD-1001",
  "status": "PENDING",
  "correlationId": "corr-1001",
  "deliveryCycle": 1,
  "attemptCount": 0,
  "failure": null
}
```

The response includes a Location header pointing to `/orders/ORD-1001`.

Concurrent duplicate requests must resolve to one stored order and one active delivery cycle.

### GET /orders/{orderId}

| Condition | HTTP status |
|---|---|
| Order exists | 200 |
| Well-formed orderId does not exist | 404 |
| Invalid orderId format | 422 |

Returns the order status representation shown above.

`attemptCount` is the number of downstream POST attempts started in the current delivery cycle.

### POST /orders/{orderId}/replay

No request body is required.

| Condition | HTTP status | Outcome |
|---|---|---|
| Failed order eligible for replay | 202 | New delivery cycle scheduled |
| Order pending, processing, or already delivered | 409 | Replay rejected |
| Permanent downstream rejection | 409 | Replay rejected |
| Order does not exist | 404 | Not found |
| Invalid orderId format | 422 | Validation error |

Replay preserves the original payload, order identity, and correlation ID.

The delivery cycle increments and its attempt count resets to zero. Previous delivery history is retained.

Concurrent replay requests must schedule at most one active cycle.

## Delivery Statuses

| Status | Meaning |
|---|---|
| PENDING | Accepted and waiting for delivery |
| PROCESSING | Delivery cycle active, including retry waiting periods |
| DELIVERED | Destination acceptance confirmed |
| FAILED | Delivery cycle stopped without confirmed success |

Allowed transitions:

- PENDING → PROCESSING
- PROCESSING → DELIVERED
- PROCESSING → FAILED
- FAILED → PENDING, only through eligible replay

DELIVERED is terminal.

A failed status does not prove the destination contains no order. The destination may have saved the order before its response was lost.

## Fulfilment Payload and Mapping

```json
{
  "externalOrderId": "ORD-1001",
  "sku": "CHAIR-001",
  "units": 2
}
```

| Source | Destination | Transformation |
|---|---|---|
| orderId | externalOrderId | Copy unchanged |
| productId | sku | Copy unchanged |
| quantity | units | Copy unchanged |

Destination fields use the same validation rules as their source fields. All are required; unknown fields are rejected.

## Fulfilment API

### POST /fulfilment-orders

`externalOrderId` is the destination uniqueness key and remains unchanged across retries and replay.

| Condition | HTTP status | Outcome |
|---|---|---|
| New valid order | 201 | Record created |
| Existing externalOrderId with identical payload | 200 | Existing record returned |
| Existing externalOrderId with different payload | 409 | Conflict; existing record unchanged |
| Invalid payload | 422 | Validation error |
| Malformed JSON | 400 | Invalid JSON error |
| Unsupported content type | 415 | Unsupported media type |

Successful responses contain the stored fulfilment payload.

A unique constraint and atomic handling must prevent concurrent duplicate creation.

### GET /fulfilment-orders/{externalOrderId}

| Condition | HTTP status |
|---|---|
| Record exists | 200 |
| Well-formed identifier does not exist | 404 |
| Invalid identifier format | 422 |

A successful response contains the stored fulfilment payload.

## Delivery Confirmation

An order is marked DELIVERED only after a downstream 200 or 201 response whose body matches the expected fulfilment payload.

A malformed or mismatched success response is a permanent protocol failure and requires investigation.

## Retry and Replay Policy

- Maximum three attempts per delivery cycle, including the initial attempt.
- Retry connection failures, timeouts, and HTTP 502, 503, and 504.
- Wait one second before attempt two and two seconds before attempt three.
- Configure the HTTP client with a two-second timeout for each connection, read, write, and pool phase.
- Do not automatically retry other HTTP errors or protocol failures.
- Exhausted retryable failures are eligible for manual replay.
- Permanent failures are not eligible for replay in the initial lab.

Unexpected response loss is handled by sending the same destination identity and payload again. Destination deduplication prevents an additional record.

Tests may replace waiting with a controlled clock. E2E tests exercise the configured retry behaviour.

## Errors

API errors use this common shape:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "correlationId": "corr-1001"
}
```

Error messages must not expose stack traces or credentials.

Order status responses use `failure: null` unless status is FAILED.

A failed delivery exposes:

```json
{
  "code": "RETRY_EXHAUSTED",
  "message": "Delivery could not be confirmed within three attempts.",
  "replayEligible": true
}
```

Failure codes:

- RETRY_EXHAUSTED
- DOWNSTREAM_REJECTED
- DOWNSTREAM_PROTOCOL_ERROR

## Related Documents

- [Business scenario](business-scenario.md)
- [Acceptance criteria and risks](acceptance-criteria.md)

## Architecture Follow-up

The architecture document will define persistence, scheduling, concurrency control, and process-restart behaviour.

This contract does not claim crash recovery or production availability guarantees.
