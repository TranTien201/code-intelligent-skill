---
name: port-request
description: Port a request-specific change (C/C++ or similar source) from a local source codebase to a local target codebase through six approval-gated checkpoints (A diff the request, B trace it back into the latest source incl. renamed/moved code, feature extensions and data dependencies, C map to target with closure, D plan, E merge, F validate). Produces an auditable Before/After target snapshot, a single PORT_REPORT.md, and traceable work files. Use when the user wants to port/copy/apply a request (a Before/After change folder) from one codebase/model to another.
user-invocable: true
---

# Port Request (orchestrator)

This file is the controller. It defines inputs, outputs, the state machine and global rules.
The detailed procedure of each checkpoint lives in `checkpoints/`, its exit checklist in `gates/`.
`SK` below means this skill's directory (`.claude/skills/port-request`).

**Read only what the active checkpoint needs:** this file + `SK/references/glossary.md` (always),
then `SK/checkpoints/<X>-*.md` and `SK/gates/<X>.md` for the active checkpoint `<X>`.
Other references are loaded when a checkpoint file tells you to.

## 1. Inputs

| Name | Required | Meaning |
|---|---|---|
| `SOURCE_ROOT` | yes | Local source codebase (current state). Read-only. |
| `TARGET_ROOT` | yes | Local target codebase (current state). Read-only. |
| `SOURCE_REQUEST` | yes | Absolute path of the source change folder; must contain `Before/` and `After/`. Read-only. |
| `TARGET_REQUEST_ID` | yes | User-provided label. Never derive or guess it from another input. |
| `OUTPUT_PARENT` | yes | Local parent folder for output. |
| `APPROVAL_MODE` | no | `interactive` (default) or `auto`. See §5. |
| `BUILD_CMD` | no | Command to build/validate the target. If absent it is discovered in Checkpoint F. |

Validation before anything else:
- All 5 required inputs present; every path exists; `SOURCE_REQUEST/Before/` and `SOURCE_REQUEST/After/` both exist and are directories, and at least one of them is non-empty.
- If anything is missing or invalid: **stop and ask** for the complete value (interactive), or write nothing and print the problem (auto). Never substitute a default for a required input.

## 2. Outputs

`OUTPUT_ROOT = OUTPUT_PARENT/formula-source-<TARGET_REQUEST_ID>/`

```
OUTPUT_ROOT/
├── PORT_REPORT.md   # the ONLY report. Never create alternate/timestamped/backup copies.
├── Before/          # Checkpoint E: unmodified target snapshot
├── After/           # Checkpoint E: target snapshot + approved port only
├── diffs/           # A: source request diffs (diffs/source/...); E/F: diffs/output.diff
└── _work/           # structured intermediate files (schemas in references/work-artifacts.md)
```

`diffs/` and `_work/` are legitimate outputs: they hold the evidence the report cites.
Nothing is ever written outside `OUTPUT_ROOT`.

The report structure is defined **only** in `SK/references/report-template.md`. Copy it exactly;
never rename headings, columns or status words.

## 3. Task init (run once, before Checkpoint A)

1. Validate inputs (§1). Inputs are plain folders delivered by the customer: two latest trees
   (`SOURCE_ROOT`, `TARGET_ROOT`) and one request folder with `Before/` and `After/` (full tree or only changed files).
   Check tools and record the result in Run Metadata notes of the Gate A result:
   ```bash
   for t in diff grep awk sed find rsync shasum file iconv git; do command -v $t >/dev/null && echo "OK $t" || echo "MISSING $t"; done
   ```
   `git` is used **only as a file tool** (`git diff --no-index`, `git merge-file`; no repository needed). If it is
   missing, use the `diff`-only fallbacks in the recipes. **Never use `diff3 -m`** (the macOS/BSD version produced
   wrong merges in testing).
2. Create `OUTPUT_ROOT`, `OUTPUT_ROOT/diffs`, `OUTPUT_ROOT/_work` if missing.
3. If `PORT_REPORT.md` does not exist: create it from `SK/references/report-template.md`; every
   checkpoint body = `Not started.`. Fill `Run Metadata`; `REPORT_PATH` = absolute report path;
   `Created at (UTC)` = output of `date -u +%Y-%m-%dT%H:%M:%SZ`. These two values are never changed later.
4. If it exists: do not recreate it; continue with §4 (resume).
5. Record input integrity baseline (once, if `_work/input_baseline.txt` is missing):
   ```bash
   touch "$OUTPUT_ROOT/_work/.start_marker"
   (cd "$SOURCE_REQUEST" && find Before After -type f -exec shasum {} +) > "$OUTPUT_ROOT/_work/input_baseline.txt"
   ```
   Checkpoint F re-checks this (see `gates/F.md`).

## 4. State machine and resume

Statuses: only `Not started`, `In progress`, `Complete`, `Blocked` (exact spelling; never `Completed`).

Order: A → B → C → D → E → F. To decide what to do, read the `Workflow Status` table:
- Active checkpoint = first row whose status is not `Complete`.
- A needs no approval. B–F need an approval (§5) **given after the previous checkpoint became `Complete`**.
- If the active checkpoint needs approval and none was received: show the previous checkpoint's
  summary and ask for approval. Do nothing else.

Running a checkpoint `X`:
1. Write the exact approval text into `X`'s `Approval to start` cell; set status `In progress`.
2. Clear only `X`'s report section (and `X`'s `_work` files), then follow `SK/checkpoints/X-*.md`.
3. Run `SK/gates/X.md`. Fix and re-run the gate at most 2 times.
4. All gate items PASS → status `Complete`, `Next approval gate` = `Awaiting Checkpoint <next> approval`
   (`None` after F). Any item still FAIL → status `Blocked`, `Next approval gate` = `Blocked: <failed item>`.
5. Present the checkpoint summary (template at the end of each checkpoint file) and **stop**.

Re-running an earlier checkpoint invalidates everything after it: set every later row to
`Not started` / `Not received`, their bodies to `Not started.`, and delete their `_work` files.
Never touch earlier checkpoints' sections.

Report editing: edit only the active section and its Workflow Status row (use targeted Edit, not a
full rewrite). Keep entries concise and factual.

## 5. Approval

- `interactive`: a valid approval is a user message, sent after the stop, that explicitly approves
  continuing (e.g. "approve B", "OK, go to C", "đồng ý"). Record it verbatim. Questions, comments or
  partial agreement are not approval: answer them and keep waiting.
- `auto`: record `AUTO (APPROVAL_MODE=auto)` as the approval and continue to the next checkpoint
  without stopping. Decisions that would normally need the user (CONFLICT, low-confidence mapping,
  unclear build command) are resolved with the default rule in `SK/references/decision-table.md`,
  marked `AUTO-DECIDED` in the report, and listed in `Final Handoff` for human review.
- A `Blocked` checkpoint always stops, in both modes.

## 6. Global rules (apply to every checkpoint)

1. **Read-only inputs.** Never create, edit, delete, chmod or build inside `SOURCE_ROOT`, `TARGET_ROOT`
   or `SOURCE_REQUEST`. Builds run only inside `OUTPUT_ROOT/After` or `OUTPUT_ROOT/Before`.
2. **Scope.** Inside `SOURCE_REQUEST` read only `Before/` and `After/`. No remote services, no network.
   Inputs are **plain folders without version history** (no `.git`): never rely on commit history; every
   rename/move/evolution is inferred from content only (recipes R11–R14).
3. **Evidence or nothing.** Every claim about code cites `path:line` (repository-relative, prefixed
   with the root name: `SRC:`, `TGT:`, `REQ-B:`, `REQ-A:`, `OUT-B:`, `OUT-A:`). No evidence →
   write `unknown` / `Not identified` and add a blocker. Never assume two things are equivalent.
4. **IDs everywhere.** Hunks `H###`, symbols `S###`, mappings `M###`, planned changes `P###`,
   executed changes `E###` (see `references/work-artifacts.md`). Every downstream item names its upstream ID.
5. **Seed from the request, port from latest.** The request diff (A) is only the seed. Every request item is
   traced back into `SOURCE_ROOT` (B: anchoring, even across renamed/moved files and functions), the feature's
   later extensions and all code + data dependencies are collected, and the **port version** from latest source
   is what gets merged (glossary). Ported text is copied as-is; adaptation (alias renames, partial takes,
   conflict options) only where the approved plan (D) says so, each one listed.
6. **Search with commands, read narrowly.** Use the recipes in `references/c-cpp-search-recipes.md`;
   read only the line ranges you need (`sed -n 'a,bp'`), not whole repositories.
7. **Encoding.** Detect with `file -I`. Never change a file's encoding or line endings in `After/`.
   For viewing non-UTF-8 files use `iconv -f <enc> -t UTF-8` into `_work/`, never in place.
8. Do not start the next checkpoint's work early (e.g. no snapshots before E, no build before F).
