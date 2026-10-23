# Claim Atlas implementation contract

## Boundaries

The host agent performs web/mail research and asks eligibility questions. The portable skill defines the workflow. Local utilities validate/render/record explicitly supplied data; they do no research and never submit claims. Product requirements live in product.md; shared contributor guidance lives in AGENTS.md.

## Components

- skills/claim-atlas/SKILL.md: short discovery/recording router.
- references/research.md: notice and public-first paths, evidence judgment and coverage.
- references/workspace.md: private report data and display contract.
- references/records.md: explicit event recording and imports.
- scripts/render_report.py + assets/report.css: escaped, inert offline report rendering. Fictitious docs/demo-data.json is the public fixture.
- scripts/public_inventory.py: public-only validation, query planning and run comparison.
- scripts/records.py: atomic user-authorized event ledger updates with a prior-copy backup.
- tools/manage.py: cross-platform Python installer, release builder and verification entrypoint.
- tools/inspect_html.py: structural/resource safety inspection without a browser.

## Data ownership

All hosts use ~/.claim-atlas/claims.json, preferences.json and reports/. The ledger has version 1 and claims keyed by case identity, each with title/status/events. Filing, automatic enrollment and payments are distinct events. Scan output does not mutate the ledger. Preserve unknown fields, prior events, dismissals and earlier research scope. Legacy import is user-requested and retains source files.

Reports use their own case lanes: next-steps, discoveries, verification, tracking/payments, watchlist, closed and safety. One owner per case; outstanding actions reference a tracked owner. Evidence gaps are not negative eligibility findings. Official verification and personal class criteria are separate. See the workspace guide for exact renderer fields.

## Distribution

The installed payload is only the skill folder, excluding output and bytecode. Installer staging and rename rollback protect existing installs; opaque old output trees/symlinks are preserved without importing data. New reports always go outside the installed skill. Releases contain ZIP, byte-identical .skill and an embedded guide edition. No private output is a build input. Build all editions before checking them against the current skill source.

Verification covers installer preservation/failure rollback, deterministic public release content, safe rendering, event records, public-only query planning and fictitious demo freshness. Windows, macOS and Linux CI run the same Python command. Browser review remains necessary for changes in presentation. Keep screenshot provenance current when layout or demo data changes.
