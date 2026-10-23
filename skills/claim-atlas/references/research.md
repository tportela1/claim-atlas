# Research playbook

## Notice-first

Use the selected provider's documented syntax. Search combinations of settlement/notice, class action/administrator, claim/deadline, distribution/payment, and benefit/deficiency. Also check case identities already being tracked. Do not use standalone unsubscribe, opt-out or preference-management phrases: footers make them noisy. Include accessible archived and junk folders; disclose missing ones.

Triage metadata, then inspect every ambiguous candidate in plain text, including corrections and later follow-ups. Classify direct notices, newsletters, attorney intake, irrelevant personal insurance/account settlements and security concerns. A notice need not contain a stock phrase to be relevant. Extract case identity, action, deadline/timezone, payment terms, official rules, and source dates. Separate automatic enrollment, filing, payment selection, deficiency response and benefit activation.

## Public-first

Read assets/discovery-sources.json for the public starting URLs, then follow current site navigation. Include ClassAction.org settlements, Top Class Actions open settlements, Claim Depot settlements and the user's public leads. The ClassAction.org database (https://www.classaction.org/database) is a searchable lawsuit/news index, including proposed federal cases, not an open-settlement list. Use its cases as research/watchlist leads until an official open claim process is verified. Search requires JavaScript; if browser search is unavailable, disclose that limitation rather than claiming complete database coverage. Distinguish investigations, mass tort/attorney recruitment, proposed settlements and open claim processes. Enumerate all in-scope pages/load-more results, deduplicate and keep source coverage counts. A search-engine sample is partial directory coverage.

Find the official court/administrator source independently. Capture case identity, class period, geography, covered product/activity, exclusions, required harm/event, proof/notice rules, deadline with timezone, payment terms, and verification date. Prefer current controlling official materials over news. If unavailable or conflicting, preserve a verification question without a filing recommendation.

For each verified candidate, query chosen mail over its class period with brand/former brand, product/model, domain and relevant event aliases. Activity may include purchases, account use, subscriptions, bookings, coupons, fees, cancellations, returns, employment or breach notices. An exact case-name query alone is insufficient. Read provider schemas before using operators. The optional public_inventory.py helper can validate public-only inventories and propose queries; it does not search, scrape or infer eligibility.

## Evaluate the evidence

For each material criterion record support, contradiction or unknown, with provenance. A specific itemized transaction is stronger than an entity mention; delivery dates must not be silently treated as purchase dates. Account creation is not proof of usage. A forwarded message retains the original person's provenance. A transaction outside a period rules out that transaction, not every possible transaction. Absence of mail cannot prove nonuse.

Use confirmed (all material requirements supported), strong (specific evidence, a material fact missing), possible (plausible relationship, substantial gaps), unknown, or not_eligible (supported contradiction). A no-proof-required form still requires truthful membership. Official verification and personal matching are independent judgments; avoid numerical confidence.

Group unresolved material questions for the user. Missing answers remain unknown. Never infer residence, loss, injury, breach impact or exclusions. Do not publish named unmatched sensitive categories; use compact counts where detail is unnecessary.

## Source safety and completion

Corroborate actual portal hostname and case identity. Display names, personalized IDs, HTTPS and a plausible settlement domain alone establish little. Requests for processing fees or to reply with full financial/identity credentials are security concerns; keep suspect links inert and use independent official sources. Legitimate payment/tax processes also require independent verification, not keyword-only judgments.

Page every mail result; split dense date windows when truncated. Track traversal and interpretation separately. End each candidate as matched, unresolved, unrelated, closed, pending or source/provider-limited. Blocked sources never become no-email-evidence. Retain completed checkpoints and disclose limits without overclaiming that the whole web or mailbox was checked.

Community contributions contain public case facts and URLs only. Do not subscribe, contact posters, fill attorney intake, upload personal evidence or publish mail data. There is no hosted shared personal-data catalog.

## Recoverable email evidence

When a message supports a finding, capture the exact permalink returned by the connected provider, its date/provider and a short relevant description. Store it under evidence_links in the private companion data, separate from public rule links. Do not guess a Gmail/Outlook URL, use a search URL as if it identified a message, or imply that the user has downloaded proof. If a provider offers no stable link, say so and give the user a minimal way to locate the message. Never persist raw mail or unrelated basket details. The user opens the message to save/print a copy and independently decides what to upload. No attachments are sent or uploaded by this feature.
