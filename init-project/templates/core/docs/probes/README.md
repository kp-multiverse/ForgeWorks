# Reality probes -- scaffolding, not records

A probe is one real observation of an external collaborator -- one real call,
dispatch, or run -- recorded at `docs/probes/<id>-<name>.md` while you build
against it. Optional convention: record one for a flaky or under-documented
collaborator. Stable, well-documented APIs may be coded against their docs
instead.

Fixtures and fakes are authored FROM these files -- never from docs, README
claims, a sibling endpoint, or memory.

**Delete the probe once its finding has landed** in the fixture, the test, or
a `docs/gotchas.md` entry -- normally in the same merge. The fixture is the
durable artifact; the probe is only how you got it. This directory should be
near empty between features. A probe kept "for reference" is a doc nobody
reads that quietly goes stale against the API it describes.

## Format

```
# <id> probe: <collaborator>
Date: <date>
How observed: <the exact command / call / script used>

## Request (as sent)
<verbatim>

## Response (as observed)
<verbatim, trimmed to the relevant shape>

## Verdict
What this confirms or kills. Red flags, if any, each with a mitigation or an
explicit user acceptance.
```
