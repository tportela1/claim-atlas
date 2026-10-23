# Implementation rewrite

The current project uses a new Python maintenance entrypoint, new installation transaction and tests, new HTML inspection implementation, and a new Claim Atlas event ledger. The former shell installer, shell packaging/check suite, single-file builder and report-audit implementation were removed. Runtime-specific legacy tracker coupling was replaced by ~/.claim-atlas storage. Research guides were rewritten around the user's notice-first/public-first specification.

The renderer, public-only inventory helper, report visual system and fictitious fixtures were developed for Claim Atlas and retained through this rewrite, with product-review improvements. They are not the former project's HTML template or UI.

The implementation was written after exposure to an earlier project. It is not described as a clean-room process, and standard formats, MIT legal text and common installation concepts may resemble other projects. Applicable historical copyright notices remain preserved. A fresh Git history describes this release tree; it does not change the history of earlier work.
