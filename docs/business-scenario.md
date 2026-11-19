# Business Scenario and System Boundaries

## Purpose

Define a small retail integration that can demonstrate functional correctness, data mapping, duplicate handling, retries, and recovery through automated tests.

## Business Scenario

A retail ordering system submits an order to the Order API.

The integration validates the request, transforms the order into the fulfilment format, and delivers it to the Fulfilment API.

The caller can check delivery status. A lab operator can inspect failed deliveries and replay them after the underlying problem is resolved.

Successful processing means the destination contains the correct fulfilment record. Acceptance by the Order API alone does not prove successful delivery.

## Actors and Responsibilities

| Actor or component | Responsibility |
|---|---|
| API client | Simulates the retail ordering system |
| Order API | Accepts and validates orders; exposes delivery status |
| Integration logic | Maps data and manages downstream delivery |
| Fulfilment API | Accepts mapped orders and prevents duplicate creation |
| Delivery state store | Records delivery status, attempts, and failures |
| Lab operator | Inspects failures and triggers replay |

The API client and lab operator interact with the lab from outside its system boundary. Both APIs, integration logic, and delivery state storage are inside the boundary.

A real storefront, payment provider, inventory system, and warehouse are outside the lab.

## Successful Order Journey

1. The client submits an order with an idempotency key.
2. The Order API validates required fields and values.
3. The integration records the accepted order and delivery state.
4. The integration maps the order to the fulfilment format.
5. The integration sends the request to the Fulfilment API.
6. The Fulfilment API records the order.
7. The integration records successful delivery.
8. The client checks delivery status.
9. Tests verify the destination record and its mapped values.

Processing may complete after the initial submission response. The API contract and architecture decisions will define the execution model.

## Example Mapping

| Incoming order field | Fulfilment field | Rule |
|---|---|---|
| orderId | externalOrderId | Required, non-empty string |
| productId | sku | Required, non-empty string |
| quantity | units | Required positive integer |

The initial lab supports one product per order.

## Initial Scope

- Receive orders through HTTP.
- Validate required fields, data types, and values.
- Map order data to the fulfilment format.
- Deliver orders to the Fulfilment API.
- Expose delivery status.
- Prevent duplicate fulfilment records.
- Retry transient failures within a defined limit.
- Record failed deliveries and support replay.
- Trace processing using a correlation ID.
- Run locally using synthetic data.

## Outside the Initial Scope

- Customer-facing UI.
- Payment processing.
- Inventory reservation.
- Shipping and physical warehouse operations.
- Multiple products in one order.
- Kafka or other message brokers.
- Cloud deployment.
- Production-scale performance and availability.

## Failure Scenarios

| Scenario | Required business outcome |
|---|---|
| Invalid order | Reject the request without creating a fulfilment record |
| Same idempotency key and payload submitted again | Do not create another fulfilment record |
| Same idempotency key used with a different payload | Reject the conflicting submission |
| Temporary downstream failure | Retry within a defined limit |
| Permanent downstream validation failure | Record failure without automatic retries |
| Retries exhausted | Keep the failed delivery visible |
| Downstream saved an order but its response was lost | Retrying must not create another fulfilment record |
| Failed delivery replayed after recovery | Deliver successfully without duplication |

## Business Success Criteria

- A valid order creates exactly one matching fulfilment record.
- Invalid input does not create a fulfilment record.
- Duplicate submissions do not create additional fulfilment records.
- Delivery failures are visible and traceable.
- A recoverable failed delivery can succeed through replay.
- Automated tests verify destination outcomes as well as API responses.

## Decisions to Define Next

- Endpoint paths, response codes, and error formats.
- Delivery statuses and allowed transitions.
- Execution model and persistence.
- Idempotency key scope and order identity rules.
- Retryable errors, attempt limits, and timing.
- Replay eligibility and behaviour.
- Correlation ID propagation.
