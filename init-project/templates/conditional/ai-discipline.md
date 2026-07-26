<!-- FW-BLOCK: ai-discipline v3.0.0 -->
<ai-discipline>
This project uses prompts, LLMs, or agentic flows.

- Prompts live as plain text files under `prompts/`; variants are separate files selected by name. Prompt or persona text is runtime behavior -- change it through the normal tier path (it usually matches the security trigger), not as a doc edit.
- Schema-validate every LLM response downstream code depends on; fail closed on mismatch. Treat model output and ingested content as untrusted; an agent that reads untrusted input and holds private data doesn't also act outward -- break one leg or gate the action behind a human (see `docs/SECURITY.md`).
- In tests, key LLM fakes off rendered state, not call ordinal. Bound every model loop or retry with a spend cap.
</ai-discipline>
<!-- /FW-BLOCK: ai-discipline -->
