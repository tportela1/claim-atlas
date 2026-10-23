# Personal claim record

Claim Atlas owns `~/.claim-atlas/claims.json` on every local host. It is separate from provider/assistant settings and is never packaged. Optional preferences live at `~/.claim-atlas/preferences.json`; store them only when requested. Hosting without persistence requires an explicit export, not a claim of permanent memory.

The version=1 record contains claims keyed by stable case identity. Each claim has title, current status and an events array. An event records kind (watched/filed/enrolled/paid/dismissed), on (ISO date), and for payments amount (decimal string) plus currency=USD. The utility currently supports USD only; do not relabel other currencies. Preserve extra fields and older events. No raw notices, IDs/PINs, addresses or medical/payment-account data belong in this ledger.

Read on scans; write only after explicit requests such as “I filed,” “watch this,” “dismiss this” or “I received $24.” Automatic enrollment is its own event, not a user filing. Unknown payment/date facts need clarification. Use the user's date/timezone, not a guessed host date. Past payments and expected estimates must remain separate.

Example (execute only when the user actually authorized recording):

```text
python scripts/records.py --case example-case --title "Example case" --event paid --on 2026-10-23 --amount 24.00
```

The helper validates the prior store, deduplicates identical events, keeps a .bak copy and atomically publishes the new JSON. Invalid existing data must not be reset. Report rendering never calls it automatically. Honor dismissed state during later merges.

Legacy records/reports are read only if the user requests import. Explain the mapping, retain the source, and preserve facts without inventing filing dates or amounts. Existing offline HTML remains usable; it need not be rewritten or erased when installing Claim Atlas.
