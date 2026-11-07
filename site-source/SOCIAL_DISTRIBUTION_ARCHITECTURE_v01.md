# WebSocial distribution architecture — proposal, not deployed

Intake: upload to a private Drive folder or authenticated admin form. Do not accept uploads directly through public GitHub Pages.

Pipeline: ingest -> metadata/rights review -> identify content type -> draft bilingual captions and crops -> preview -> user approval -> platform-specific scheduling/publishing -> log URLs, errors, metrics.

Recommended initial implementation: GitHub Pages (public website) + private Google Drive inbox + Google Apps Script or GitHub Actions for orchestration + approved publishing integrations. Instagram professional account and Meta permissions may be required. X API, YouTube API and other platform policies/quotas vary. No tokens in public repository. Do not automatically post identifiable participants or children without rights approval.

Phases: (1) draft-only queue (2) human approval (3) selective auto-publish where APIs permit (4) monitoring and retry logs.
