# Writing standard -- Simplified Technical English

All agent output follows this standard: chat messages, docs, commit
messages, code comments, error messages, and job cards. It is adapted
from ASD-STE100, the aerospace controlled language.

## Rules

- Keep each sentence under 20 words.
- Put one instruction in each sentence.
- Use the active voice. Name the actor.
- Use simple tenses (present, past). Do not narrate actions with "-ing" clauses.
- Do not hedge in instructions: "should", "would", "may", "might" are
  banned there. Say what to do, or give the condition.
- Put the condition before the command ("If the gate is red, stop.").
- Use one meaning per word. Do not switch between synonyms for one thing.
- Do not drop words that carry meaning ("Close the valve", not "Close valve").
- Prefer the plain word over jargon. Gloss any term of art at first use.

## Two modes

- **Strict** -- procedures, error messages, ledger lines, job cards,
  commit subjects: every rule applies.
- **STE-flavored** -- explanatory prose (README sections, gotcha entries,
  a plan's Approach section): keep the discipline; relax the vocabulary
  lock when precision needs a technical term.

## Why

One meaning per word, in short active sentences, costs fewer tokens and
fewer misreadings -- for humans and for agents. Published evals of an
STE skill measured about 73% fewer writing violations, with lower token
counts, across six models.
