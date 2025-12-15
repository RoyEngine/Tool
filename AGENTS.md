# Project: Starsector Mod Localizer (V0)

## Goal
Implement V0 CLI in Localization_Tool/:
- extract -> update -> apply -> report
Target: Java/Kotlin source strings under src/. Translation is manual.

## Non-negotiable constraints
- occurrence_key = rel_path + start_byte + end_byte + kind (primary key)
- No absolute paths in rules
- Deterministic ordering:
  - files by rel_path
  - occurrences by start_byte
- Apply replacements per-file in reverse start_byte order
- Kotlin template/interpolation: default NEED_REVIEW and skipped by apply

## Repo layout
- Localization_Tool/: new implementation ONLY
- legacy/: reference only; do not add new logic here

## Commands (must work)
- python -m Localization_Tool.starsector_localizer.cli extract --mod-root <mod> --rules <rules.yaml>
- python -m Localization_Tool.starsector_localizer.cli update  --mod-root <mod> --rules <rules.yaml>
- python -m Localization_Tool.starsector_localizer.cli apply   --mod-root <mod> --rules <rules.yaml> --out <out_dir>
- python -m Localization_Tool.starsector_localizer.cli report  --rules <rules.yaml> --out <report_dir>

## Acceptance
- Provide runnable commands + example under Localization_Tool/examples/
- Keep changes minimal and reviewable.
