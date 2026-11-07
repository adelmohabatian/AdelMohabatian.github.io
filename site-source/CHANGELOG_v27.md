# WebSocial v2.7 — Gmail form integration

- Integrated the user-tested Google Apps Script web app into `/contact/` via an iframe.
- Removed the previous mailto form and its script to avoid competing submit buttons.
- Retained original black-and-white portrait, responsive size, social links, and the existing sitewide language selector.
- Switching EN/FA reloads the Google form with `?lang=en` or `?lang=fa`.
- Added a fallback direct link in case embedded forms are blocked by the browser.
- No journal article PDFs included. All other pages and assets preserved from v2.6.
- Google Apps Script deployment remains owned and maintained by the site owner; changes to the Google Form HTML require an Apps Script redeployment.
- Test a real submission after GitHub deployment; a green GitHub Actions status alone does not confirm email delivery.
