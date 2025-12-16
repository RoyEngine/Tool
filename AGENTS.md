# AGENTS — Starsector Localization Tool (V0)

This file is the working contract for automated agents (Codex) and contributors.
Follow it strictly. If requirements conflict, this file wins.

## 1) V0 Objective (CLI Closed Loop, Minimal but Real)
Deliver a deterministic, auditable CLI closed loop for Java/Kotlin source localization:

- Increment A — Extract (Minimal Usable)
- Increment B — Apply (Minimal Usable)
- Increment C — Extend (Learning Alignment, Minimal High-Confidence)

Manual translation only in V0 (no machine translation).

## 2) Canonical Repo Layout (Scheme B, MUST)
- Tool code (canonical): `legacy/Localization_Tool/src`
- Fixtures (do not move):
  - English: `legacy/Localization_File/source/English/<ModFolder>/src`
  - Chinese: `legacy/Localization_File/source/Chinese/<ModFolder>/src`
- Output (generated):
  - Extract: `legacy/Localization_File/output/Extract_English/**` and `Extract_Chinese/**`
  - Apply:   `legacy/Localization_File/output/Apply_*/**` (should be gitignored)
  - Extend:  `legacy/Localization_File/output/Extend_*/**` (should be gitignored)

Note:
- `<ModFolder>` is the mod root folder (it may include `mod_info.json`, `README.md`, etc.), and MUST contain `src/`.

## 3) V0 Non-Goals (MUST NOT)
- Do NOT implement jar decompile/unpack inside Extract main flow.
- Do NOT translate `data/localization` CSV/JSON in V0.
- Do NOT perform global search/replace by raw text only.
- Do NOT “auto-fix” syntax by guessing (must skip + report).

Jar-related utilities may exist, but must be isolated behind a separate command or utility module,
and not imported by Extract core pipeline.

## 4) Rules YAML Compatibility (MUST)
Rules YAML must remain backward compatible with the current schema:

Top-level:
- `version`
- `created_at`
- `mappings: []`

Each mapping MUST keep at least:
- `id`
- `original`
- `translated`
- `context`
- `status`
- `placeholders`

You MAY add fields such as:
- `rel_path`, `loc`, `key`, `node_type`, `lang`, `hash`, etc.
But MUST NOT rename/remove existing ones.

### Status Values (V0)
Use a small stable set:
- `untranslated`  (default)
- `translated`    (human-confirmed)
- `skipped`       (explicitly ignore)
- `fuzzy`         (auto-filled suggestion; NOT confirmed)
- `placeholder_mismatch`
- `locate_failed`

## 5) Determinism Requirements (MUST)
- Mod folder enumeration MUST be sorted by folder name.
- File enumeration inside `src/` MUST be sorted by relative path.
- Apply replacements MUST be done per-file in reverse order of byte ranges (descending start_byte)
  to avoid offset shifts.

## 6) Kotlin Placeholder Safety (MUST)
Kotlin interpolation is high risk:
- `$var`
- `${expr}`
- raw strings `""" ... """` may also include interpolation

Extract MUST capture placeholders into `placeholders`.
Apply MUST validate placeholder consistency:
- If mismatch: skip replacement and record `placeholder_mismatch` in report.

## 7) CLI Interface (V0)
Run from repo root.

### 7.1 Extract (all mods under a language root)
- `python legacy/Localization_Tool/src/main.py extract --lang English --source-root legacy/Localization_File/source/English --out-root legacy/Localization_File/output`
- `python legacy/Localization_Tool/src/main.py extract --lang Chinese --source-root legacy/Localization_File/source/Chinese --out-root legacy/Localization_File/output`

Optional:
- `--mod "<ModFolderName>"` to run one mod only.
- `--rules-out "<path>"` to force a stable output path for CI.

### 7.2 Apply (one mod at a time)
- `python legacy/Localization_Tool/src/main.py apply --src legacy/Localization_File/source/English/<ModFolder> --rules <PATH_TO_YAML> --out <OUT_DIR>`

### 7.3 Extend (learning alignment, minimal high confidence)
Goal: auto-fill English rules using existing Chinese source/rules when alignment is high confidence.
- `python legacy/Localization_Tool/src/main.py extend --en-src legacy/Localization_File/source/English/<ModFolder> --zh-src legacy/Localization_File/source/Chinese/<ModFolder> --en-rules <EN_YAML> --zh-rules <ZH_YAML> --out <OUT_EN_YAML>`

Extend MUST NOT overwrite human-confirmed translations unless `--force` is explicitly provided.

## 8) Reporting (MUST)
Apply and Extend MUST produce a machine-readable report (`report.json`) including:
- total mappings processed
- replaced/filled count
- skipped count (by reason)
- failures (by reason) including file + mapping id/key

At minimum include reasons:
- `placeholder_mismatch`
- `locate_failed`
- `status_not_translated` (or equivalent)
- `parse_failed`

## 9) Minimal Delivery Increments (MUST, in this order)

### Increment A — Extract Minimal Usable (DoD)
- Can parse `.java/.kt/.kts` under `src/` using Tree-sitter.
- Produces one rules YAML per `<ModFolder>` per language.
- If rules already exist, merges deterministically:
  - Preserve existing `translated/status` for existing ids/keys.
  - Add new entries as `untranslated`.
  - Optionally mark removed entries as `stale` (do not delete silently).

### Increment B — Apply Minimal Usable (DoD)
- Reads an English `<ModFolder>/src`.
- Applies only mappings with `status=translated`.
- Performs safe replacements (reverse order per file).
- Outputs translated tree + `report.json`.

### Increment C — Extend Learning Alignment (DoD)
- High-confidence alignment only (exact match by stable key; no aggressive fuzzy in V0).
- Writes a new English rules YAML where auto-filled entries are `status=fuzzy` by default.
- Produces `report.json` explaining what was matched and what was not.

## 10) Notes for Codex Cloud
- Prefer small PRs aligned with the three increments.
- Each PR must include a short test plan section in the PR description.
- Do not refactor unrelated modules while closing V0 loop.
