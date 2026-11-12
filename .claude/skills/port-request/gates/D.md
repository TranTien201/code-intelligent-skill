# Gate D

1. **Mapping coverage** – every row of `_work/C_trace.md` maps to ≥1 M-id (show counts).
2. **Classes** – port class only from `decision-table.md`; the matching row number is recorded per M-id.
3. **Decisions** – no `CONFLICT`, `NEEDS_CONFIRMATION`, `TAKE_LATEST_PARTIAL`, `SOURCE_GONE`, `ADAPT_MERGE` conflict, `ENABLE_GUARD`, `LAYOUT_RISK` or `UNCLASSIFIED` remains without a user answer (interactive) or an `AUTO-DECIDED` mark (auto).
4. **Plan coverage** – every M-id whose class requires a change has ≥1 P-id; every P-id names one M-id; SKIP/REPORT_ONLY M-ids have none.
5. **Anchors** – every P-id (except `add-file`) has an anchor copied from target text with `TGT:path:line`, and the anchor occurs exactly once in that file (`grep -c -F`).
6. **Data** – every data dependency `MISSING` in target has P-ids for every place listed in C (all languages / tables / defaults / version).
7. **Aliases** – every identifier in planned text that the target knows under another name is substituted (check planned text against the alias map); each substitution listed.
8. **Extensions** – every `ext` item is either planned or explicitly excluded with the user's answer.
9. **Content** – every P-id has a content source and full new text in `_work/D_plan.md`; adaptations ≠ `none` are listed in Risks.
10. **Build inclusion** – every new source file has an `add-to-build` P-id (or evidence the build picks it up automatically, e.g. wildcard).
11. **Order** – declarations/types/macros planned before their users.
12. **Label convention** – found with 3 evidence lines, or `None found` with the search pattern.
13. **Validation plan** – command(s), working directory, baseline run, fallback, open questions.
14. **No snapshots** – `OUTPUT_ROOT/Before` and `After` were not created or modified in D.
15. **Status row** updated.
