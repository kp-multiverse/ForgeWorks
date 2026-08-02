# Reality probes -- the provenance of a fixture

A probe is one real observation of an external collaborator -- one real call,
dispatch, or run -- recorded at `docs/probes/<id>-<name>.md`. Optional
convention: record one for a flaky or under-documented collaborator. Stable,
well-documented APIs may be coded against their docs instead.

Fixtures and fakes are authored FROM these files -- never from docs, README
claims, a sibling endpoint, or memory. The test or fixture cites its probe by
path, and that citation is the point: it is how a reader knows the fixture
reflects reality rather than someone's idea of the API.

**A probe lives exactly as long as something cites it.** Delete it when the
fixture it backs is deleted, or when nothing references it any more -- then it
is a stale description of an API nobody checks. Do NOT delete a probe merely
because its feature merged: `grep -r "docs/probes/<name>" .` first, and if a
test or source comment names it, the probe stays. Re-observe rather than
delete when the collaborator changes.

A probe that no fixture cites is scaffolding -- delete that one on sight.

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
