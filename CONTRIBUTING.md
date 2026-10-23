# Improve Claim Atlas

Start with the user journey in docs/product.md and the boundaries in docs/architecture.md. Use AGENTS.md for shared development guidance.

For a public lead, submit the case identity, public discovery URL, official source if available, jurisdiction, class dates and date checked. Mark guesses clearly. Do not post your email, order numbers, medical details, claim IDs, PINs or private report. A popular post is still a lead until verified.

For code or workflow changes, explain the user problem and resulting behavior. Add behavior tests for material state or safety changes, using fictitious data. Do not add a provider claim without documenting the tools/capabilities needed. Renderer changes need desktop/mobile review; research instructions must preserve account choice and truthful uncertainty.

Before submitting, run `python scripts/build-demo.py`, `python tools/manage.py build` and `python tools/manage.py check`. Keep all release editions current. Preserve applicable license notices. No production mail access is needed for offline checks.
