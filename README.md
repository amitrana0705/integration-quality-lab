# Integration Quality Lab

A practical quality engineering project built around a retail order-to-fulfilment integration.

This lab will demonstrate how to define integration requirements, build connected services, automate meaningful tests, and verify behaviour under failure conditions.

> **Project status:** Planning and documentation. Application code, automated tests, containers, and CI workflows are not yet implemented. Features below describe the intended scope.

## Objective

Build a small, reproducible integration system that provides inspectable evidence of:

- API design and validation.
- Source-to-destination data mapping.
- API schema conformance.
- Automated testing at different levels.
- Retry, duplicate handling, and failure recovery.
- Observability and delivery traceability.
- Continuous integration and published test results.

The project connects integration engineering, quality engineering, and DevOps practices through one working business scenario.

## Business Scenario

A retail order is submitted to an Order API. The integration validates the request, transforms the payload, and delivers it to a Fulfilment API.

The order's delivery status must remain visible so successful and failed processing can be verified.

### Planned Architecture

- **Order API:** Accepts orders and exposes their delivery status.
- **Integration logic:** Validates, transforms, and delivers orders.
- **Fulfilment API:** Receives fulfilment requests and records accepted orders.
- **Delivery state store:** Tracks processing status, attempts, and failures.
- **Controlled test dependency:** Simulates downstream errors and timeouts.

Mocks will provide controlled failure scenarios. Complete E2E tests will exercise the running Order API and Fulfilment API together.

## Example Data Mapping

Incoming order:

```json
{
  "orderId": "ORD-1001",
  "productId": "CHAIR-001",
  "quantity": 2
}
```

Outgoing fulfilment request:

```json
{
  "externalOrderId": "ORD-1001",
  "sku": "CHAIR-001",
  "units": 2
}
```

| Source field | Destination field | Planned rule |
|---|---|---|
| `orderId` | `externalOrderId` | Required, non-empty string |
| `productId` | `sku` | Required, non-empty string |
| `quantity` | `units` | Required positive integer |

Detailed mapping and validation rules will be documented before implementation.

## Expected Behaviour

The lab will define and verify these acceptance criteria:

1. Valid orders reach fulfilment with the correct mapped data.
2. Invalid orders are rejected with clear validation errors.
3. Repeating a submission with the same idempotency key and payload does not create another fulfilment order.
4. Reusing an idempotency key with a different payload is rejected.
5. Transient delivery failures trigger a bounded retry policy.
6. Permanent validation failures are not retried.
7. Deliveries that exhaust retries remain visible as failed.
8. Failed deliveries can be replayed after the underlying problem is resolved.
9. Replay does not create duplicate fulfilment orders.
10. A correlation ID connects the incoming request, delivery attempts, and final outcome.

Exact response codes, retry limits, and replay semantics will be specified in the API contract and design documentation.

## Test Strategy

| Test layer or focus | What it will verify | Planned evidence |
|---|---|---|
| Unit | Validation, mapping, and retry decisions in isolation | Focused automated assertions |
| API | Request handling, responses, and error behaviour | HTTP request and response assertions |
| Schema conformance | Requests and responses match the OpenAPI specification | Schema validation results |
| Integration | Components exchange and process data correctly | Captured downstream payloads and persisted state |
| Resilience | Retries, duplicate handling, timeouts, and replay | Attempt counts and verified final outcomes |
| E2E | The complete order journey across running services | Destination records and final delivery status |

Functional requirements will be verified across these layers.

An accepted API response alone will not count as proof of successful downstream delivery. Tests must inspect the relevant destination outcome.

Schema conformance will be the initial contract-related scope. Consumer–provider contract verification is a possible later extension and will be identified separately if implemented.

## Planned Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and test implementation |
| FastAPI | Order and fulfilment services |
| OpenAPI | API interface specifications |
| pytest | Automated test execution |
| HTTPX | HTTP requests in tests |
| Docker Compose | Reproducible local service environment |
| GitHub Actions | Automated checks and test execution |

Persistence and failure-simulation tools will be selected during implementation and documented with their tradeoffs.

## Build, Run, and Test

Executable setup instructions will be added and verified as the implementation progresses.

The intended developer workflow is:

1. Clone the repository.
2. Install the documented prerequisites.
3. Start the local services.
4. Submit a sample order.
5. Inspect its delivery status and destination record.
6. Run the automated test suite.
7. Simulate a downstream failure.
8. Verify retries and recovery.
9. Review the corresponding GitHub Actions results.

No application run or test commands are available at the current documentation-only stage.

## Documentation

- [Business scenario and system boundaries](docs/business-scenario.md)
- [Acceptance criteria and integration risks](docs/acceptance-criteria.md)
- [API contracts and mapping rules](docs/api-contracts.md)
- [Order API specification](contracts/order-api.yaml)
- [Fulfilment API specification](contracts/fulfilment-api.yaml)

## Implementation Roadmap

### Milestone 1 — Define the Integration

- [ ] Document the business scenario and system boundaries.
- [ ] Define acceptance criteria and integration risks.
- [ ] Define API contracts and mapping rules.
- [ ] Record the initial architecture decisions.

### Milestone 2 — Build One Working Journey

- [ ] Implement the Order API.
- [ ] Implement the Fulfilment API.
- [ ] Implement validation and mapping.
- [ ] Deliver a valid order successfully.
- [ ] Expose delivery status.
- [ ] Add unit and happy-path integration tests.

### Milestone 3 — Verify Failure Behaviour

- [ ] Add controlled downstream failure simulation.
- [ ] Implement and test bounded retries.
- [ ] Implement and test idempotency.
- [ ] Record exhausted deliveries.
- [ ] Implement and test replay.
- [ ] Add correlation IDs and structured logs.

### Milestone 4 — Make Results Reproducible

- [ ] Add Docker Compose.
- [ ] Automate checks and tests with GitHub Actions.
- [ ] Publish machine-readable test reports.
- [ ] Add E2E tests across running services.
- [ ] Verify setup instructions from a clean environment.

### Milestone 5 — Publish the Demonstration

- [ ] Document a successful order journey.
- [ ] Document a failure-and-recovery walkthrough.
- [ ] Explain key design decisions and limitations.
- [ ] Link to actual CI runs and test evidence.
- [ ] Record a short demonstration.

## Definition of Done

The initial lab will be complete when:

- A new contributor can start it using the documented instructions.
- A valid order reaches fulfilment with correct data.
- Invalid input, duplicates, transient failures, and exhausted retries have verified outcomes.
- A failed delivery can be replayed without creating duplicates.
- Automated tests run in GitHub Actions.
- Reports and demonstration steps support the documented claims.
- Known limitations and design tradeoffs are recorded.

## Portfolio Evidence

The repository will demonstrate both implementation and engineering reasoning:

- **Requirements:** What should happen and how success is measured.
- **Architecture:** How components interact and why.
- **Automation:** How correctness and failure behaviour are verified.
- **Operations:** How processing is traced and recovered.
- **CI:** How changes are checked consistently.

Evidence links will be added only after the corresponding implementation and checks exist.

## Scope and Boundaries

This is a personal engineering lab using synthetic retail data and independently written code.

It is not a production system and does not contain employer code, internal architecture, credentials, or customer information.

Initial scope focuses on functional correctness and resilience. Performance, security, cloud deployment, and messaging platforms may be explored later through separately defined requirements.

## Author

Amit Rana
