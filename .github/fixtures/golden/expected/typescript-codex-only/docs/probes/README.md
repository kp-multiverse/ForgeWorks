# Reality probes

One file per observed external collaborator, at `docs/probes/<id>-<name>.md`.
Optional convention: record a probe for a flaky or under-documented
collaborator -- one real call, real dispatch, or real run -- during feature
development. Stable, well-documented APIs may be coded against their docs
instead.

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

Fixtures and fakes are authored FROM these files -- never from docs, README
claims, a sibling endpoint, or memory.
