# Gate C

1. **Coverage** – every S-id (incl. `ext`) and every dependency `S###.d#` (code and data) from B has a row in `_work/C_trace.md` (counts B vs C).
2. **State vocabulary** – only `SAME_AS_SOURCE|SAME_AS_BEFORE|DIVERGED|SIGNATURE_DIFF|MISSING|RENAMED|RENAMED_CANDIDATE`.
3. **Evidence** – every non-MISSING row has `TGT:path:line`; every MISSING row lists the searches done (name R2, file R11, symbol R12, literal R8).
4. **Comparison done** – every `SAME_AS_*` was produced by an R7 comparison against the **port version** / REQ-B (note when "modulo aliases").
5. **Target renames** – every `RENAMED` has R11/R12 evidence of ≥ Medium and an alias-map target entry; weaker ones are `RENAMED_CANDIDATE`.
6. **Callers** – every `SIGNATURE_DIFF`/`DIVERGED` row lists target callers (or `none`).
7. **Data gaps** – every data dependency has a target status per place (each language table, each enum-sized table, defaults, version/checksum).
8. **Fixpoint reached** – the last closure iteration added 0 items; iterations recorded.
9. **Flows** – every formula has a source chain and a target chain (or the break point / `entry not found` blocker).
10. **No assumed equivalence** – every `Low` and `RENAMED_CANDIDATE` is in `### Blockers` with a yes/no question.
11. **Read-only** (marker check incl. `TARGET_ROOT`) and **status row** updated.
