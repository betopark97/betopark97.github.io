# Google Analytics

Event-based web analytics with GA4: installing it, and keeping your own visits out.

Google Analytics 4 (GA4) is an event-based web analytics product. A **property** holds the data, a **data stream** represents one site or app within it, and a **measurement ID** (`G-XXXXXXXXXX`) identifies that stream to the code on the page. Every interaction — including a pageview — is an event.

These pages cover getting it onto a site, keeping your own traffic out of the numbers, and auditing what a tag container is actually doing.

## Reading Path

| Page | What it answers |
|----|----|
| [Installation](../../../notes/004-data-analysis/004-google-analytics/001-installation.llms.md) | gtag.js versus Tag Manager, and why loading both can double your numbers |
| [Excluding Your Own Traffic](../../../notes/004-data-analysis/004-google-analytics/002-excluding-your-own-traffic.llms.md) | how to stop counting yourself, and why IP filtering usually fails |
| [Auditing a Container](../../../notes/004-data-analysis/004-google-analytics/003-auditing-a-container.llms.md) | reading any GTM container’s real configuration without console access |

Back to top
