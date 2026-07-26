# Product Vision: Pillarwatch

The north star for this project. Captures the *what* and *why*. Stable across iterations.

For the enforceable feature list, see `features.json`.

---

## Positioning (Geoffrey Moore)

For **An on-call engineer at a small team who wants an honest status page without paying for or trusting a SaaS status vendor.**
who **no honest status page without paying for or trusting a SaaS vendor**,
Pillarwatch is a **self-hosted status page**
that **an honest, self-hosted status page with no third party in the loop**.
Unlike **a paid third-party status-page SaaS, or no status page at all**,
we **single-binary self-hosted install instead of a hosted SaaS subscription**.

## 5W answers

- **Who:** An on-call engineer at a small team who wants an honest status page without paying for or trusting a SaaS status vendor.
- **What:** A self-hosted status page that shows the up/down history of a small team's own services, no third-party dependency.
- **Why:** Small teams either run no status page (users find out about outages from support tickets) or hand uptime data to a third-party SaaS that is one more thing to trust and pay for.
- **When:** 2026-08-09
- **Where:** A single Linux VM, reverse-proxied behind the team's existing domain.
- **How:** see the core flow in `docs/features.json`

## Scope

**In scope** -- what v1 will do:

- Service registration with a health-check URL and poll interval.
- Poller with an up/down/degraded state machine and transition history.
- Public status page with current status and a 90-day history bar per service.

**Out of scope (non-goals)** -- what it deliberately will NOT do:

- No multi-region or synthetic-transaction checks.
- No paging/alerting integrations in the first cut -- the page itself is the notification.

## Business goals

Outcome + metric + target. Cap at three.

- time from real outage to page reflecting it -- under one poll interval
- self-hosted install time -- under 10 minutes on a single binary

## Success looks like

> A service outage shows up on the public page within one poll interval of the health check failing, with no manual step.

---

*Last updated: 2026-07-26*
