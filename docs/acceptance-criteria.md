# Acceptance Criteria and Integration Risks

## Purpose

Define observable outcomes for the order-to-fulfilment integration and connect integration risks to planned tests.

These criteria describe required behaviour. They do not indicate that the behaviour is already implemented or tested.

## Reference

[Business scenario and system boundaries](business-scenario.md)

## Acceptance Criteria

### AC-001 — Successful delivery and correct mapping

Given a valid order and an available Fulfilment API,
when the order is submitted and processing completes,
then:

- Exactly one matching fulfilment record exists.
- orderId maps to externalOrderId.
- productId maps to sku.
- quantity maps to units.
- Delivery status indicates success only after downstream acceptance is confirmed.

### AC-002 — Invalid input

Given an order with a missing required field, an empty identifier,
or a quantity that is not a positive integer,
when it is submitted,
then:

- The Order API rejects it with a clear validation error.
- No downstream delivery is attempted.
- No fulfilment record is created.

Test cases must include zero, negative, fractional, string, null,
and boolean quantities.

### AC-003 — Repeated submission

Given an order already accepted with an idempotency key,
when the same key and payload are submitted again,
then:

- The response identifies the existing order.
- No additional logical order is created.
- No additional fulfilment record is created.

Verify both sequential and concurrent duplicate submissions.

### AC-004 — Conflicting submission

Given an idempotency key already associated with an accepted order,
when the key is submitted with a different payload,
then:

- The submission is rejected as a conflict.
- The original order remains unchanged.
- No additional fulfilment record is created.

### AC-005 — Recovery within the retry limit

Given a valid order and a transient downstream failure,
when the downstream service recovers before the attempt limit is reached,
then:

- Delivery is retried according to the configured policy.
- The destination contains exactly one matching fulfilment record.
- Final delivery status indicates success.
- Delivery attempts are recorded.

### AC-006 — Permanent downstream rejection

Given a downstream response classified as a permanent validation failure,
when the integration receives that response,
then:

- It does not automatically retry the rejected delivery.
- Delivery status indicates failure.
- A failure reason is available for diagnosis.
- No fulfilment record is created.

### AC-007 — Retry exhaustion

Given a downstream service that remains unavailable,
when the configured attempt limit is reached,
then:

- Automatic delivery attempts stop.
- Delivery status indicates failure.
- The attempt count and failure reason remain available.
- The order is retained for inspection and eligible recovery.

### AC-008 — Lost response after downstream commit

Given the Fulfilment API saves an order but its response is lost,
when the integration retries the delivery,
then:

- The Fulfilment API recognises the existing order.
- Exactly one fulfilment record exists.
- The integration can confirm delivery and record success.

If confirmation remains unavailable until attempts are exhausted,
the integration must report failure to confirm delivery rather than
claim that the destination contains no order.

### AC-009 — Replay after recovery

Given a delivery that failed because retries were exhausted,
and the downstream service has recovered,
when the lab operator triggers replay,
then:

- The original order identity and payload are retained.
- A new delivery cycle is recorded without erasing previous attempts.
- Delivery succeeds.
- Exactly one matching fulfilment record exists.

Test replay when no destination record exists and when the destination
already saved the order but confirmation was lost.

### AC-010 — Replay eligibility

Given an order already delivered successfully,
when replay is requested,
then:

- The request does not trigger another downstream delivery.
- The successful order remains unchanged.

Overlapping replay requests must not create competing delivery cycles.

### AC-011 — Delivery status accuracy

Given an accepted order,
when the client retrieves its delivery status,
then:

- The response identifies the correct order.
- The reported outcome agrees with recorded delivery evidence.
- A pending or failed delivery is never reported as successful.
- An unknown order returns a clear not-found response.

### AC-012 — Traceability

Given an accepted order,
when processing, retries, or replay occur,
then:

- A correlation ID connects the accepted order to downstream requests.
- Delivery attempts and outcomes can be located using that ID.
- Replay cycles can be distinguished from previous delivery attempts.

## Integration Risks and Planned Tests

Priority reflects business impact within this lab.

| Risk ID | Risk | Business impact | Priority | Criteria | Planned verification |
|---|---|---|---|---|---|
| R-001 | Incorrect field mapping | Wrong product or quantity fulfilled | High | AC-001 | Unit mapping tests and destination assertions |
| R-002 | Invalid input accepted | Unprocessable or incorrect orders | High | AC-002 | Parameterised validation and API tests |
| R-003 | Duplicate processing | Duplicate fulfilment | High | AC-003, AC-004, AC-008 | Sequential and concurrent duplicates; lost-response simulation |
| R-004 | Temporary failures cause undelivered orders | Fulfilment delayed or missed | High | AC-005, AC-007 | Controlled errors and retry exhaustion tests |
| R-005 | Permanent errors retried | Repeated failing traffic and delayed diagnosis | Medium | AC-006 | Permanent rejection with attempt-count assertions |
| R-006 | Incorrect delivery status | Caller receives misleading information | High | AC-001, AC-008, AC-011 | Status checks against known destination outcomes |
| R-007 | Unsafe replay | Duplicate fulfilment or competing delivery cycles | High | AC-009, AC-010 | Replay and overlapping replay tests |
| R-008 | Missing traceability | Failures difficult to diagnose | Medium | AC-012 | Correlation ID and attempt-history assertions |

## Test Evidence Rules

- An accepted API response alone is not proof of fulfilment.
- Successful delivery tests must inspect destination records.
- Duplicate tests must assert record counts as well as response bodies.
- Retry tests must assert attempt counts and final outcomes.
- Failure simulations must have controlled, repeatable behaviour.
- Tests must use isolated synthetic data.
- Automated tests will reference the acceptance criterion they verify.
- Test reports demonstrate executed checks; this document defines intended checks.

## Decisions Required Before Implementation

The API contracts and architecture decisions must specify:

- Endpoint paths, HTTP status codes, and error formats.
- Identifier length limits and whitespace handling.
- Strict field typing and treatment of unknown fields.
- Idempotency key requirements, scope, and retention.
- Behaviour when the same orderId arrives with a different key.
- Downstream uniqueness and duplicate-payload comparison rules.
- Delivery states and allowed transitions.
- Retryable errors, timeout settings, maximum attempts, and backoff.
- Whether attempt limits include the initial request.
- Replay eligibility, attempt budgets, and concurrency control.
- Correlation ID validation, generation, and propagation.
- Execution model and persistence.

Process-crash recovery and restart durability are not demonstrated by
HTTP retry tests. Their intended guarantees and test scope must be
explicitly decided in the architecture documentation.
