<!-- FW-BLOCK: memory v3.0.0 -->
<memory>
This project wires **mem0** for persistent memory across sessions, scoped to user (facts about the human), session (the current interaction), and agent (facts the agent itself confirmed) -- schema and stored fields live in `docs/memory.md`.
Read relevant memories at session start; write one only when the fact is durable and its scope is unambiguous (if you cannot say which scope, do not store it), and update `docs/memory.md` in the same change. Verify the API against Context7 for the pinned `mem0ai` version before writing memory code.
</memory>
<!-- /FW-BLOCK: memory -->
