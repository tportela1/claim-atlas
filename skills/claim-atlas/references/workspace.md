# Private workspace and report contract

Store dated companion JSON and HTML under `~/.claim-atlas/reports/`. The user may choose another private location. Never place personal output inside a repository or installed skill. Retain earlier reports. Before updating today's report, merge case keys, decisions, evidence provenance and coverage scopes; do not replace a broad scan with a narrow one.

Run `python scripts/render_report.py INPUT.json OUTPUT.html` relative to the skill folder. It escapes data and renders a self-contained offline document. No web/mail access or tracker writes occur. Without execution, use the same data and visual contract, escaping untrusted text and preserving restrictive CSP; do not pretend a helper ran.

## Version 1 report data

Root fields: version=1, title, ISO date, mode, accounts (selected labels), coverage (array), cases (array). Optional summary, decisions, history persist user context. Public fictitious fixtures set demo=true to display a separate example label; real personal reports omit this flag. Coverage entries have source, status (complete/partial/blocked/historical/not_run), detail. Include dates, folders/pages, unprocessed candidates and source limitations. Plan generation and metadata retrieval do not imply interpreted coverage.

Each case has a unique key, title, lane, status, summary, next_step. Optional eligibility is confirmed/strong/possible/unknown/not_eligible. Optional deadline and verified_on are ISO dates; official_url is HTTPS; verification is readable source context; payout is the user's estimate or actual payment with uncertainty stated. Evidence is a string array; sources are {label,url}; criteria are {criterion,state,detail} with supported/unknown/contradicted; details are {label,value} private tracking facts only where needed.

Lane destinations belong to Claim Atlas: next-steps, discoveries, verification, tracking with nested payments, watchlist, closed, safety. Filing actions require confirmed eligibility, nonempty supported criteria and dated official verification. Follow-ups instead use case_ref referencing a tracked/payment owner. A case has one owner; outstanding tasks reference it. Security cards contain no live source links. Closed cards omit credentials. Never sum settlement funds or unknown payments into a promised total.

The design uses compact top navigation, a charcoal briefing header, clear primary action and light evidence cards. Navigation wraps on mobile; empty categories stay out of the way. Cards separate evidence, eligibility gaps and next steps. Counts derive from content; payments count within tracking. Keep meaningful empty states, accessible focus and mobile wrapping. No scripts, forms, remote fonts/images, analytics or arbitrary HTML. HTTPS references use noopener/noreferrer. Source links are not automatic eligibility endorsements.

For repeatable public inventory planning, public_inventory.py accepts a version=1 object with as_of, sources and cases. Sources have url, coverage, pages and optional limitation. Cases have key/title/status/sources/search_terms and optional official_url, verified_on, class_start/class_end/deadline. Only public facts belong here. CLI commands validate, plan and compare do not access mail or establish coverage. Keep generated plans private and adapt syntax/boundaries to connected tools.
