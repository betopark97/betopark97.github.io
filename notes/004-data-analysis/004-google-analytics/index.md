---
title: Google Analytics
description: "Event-based web analytics with GA4: installing it, and keeping your own visits out."
icon: logos:google-analytics
---
Google Analytics 4 (GA4) is an event-based web analytics product. A **property** holds the data, a **data stream** represents one site or app within it, and a **measurement ID** (`G-XXXXXXXXXX`) identifies that stream to the code on the page. Every interaction — including a pageview — is an event.

These pages cover getting it onto a site, keeping your own traffic out of the numbers, and auditing what a tag container is actually doing.

## Reading Path

| Page | What it answers |
| --- | --- |
| [Installation](001-installation.md) | gtag.js versus Tag Manager, and why loading both can double your numbers |
| [Excluding Your Own Traffic](002-excluding-your-own-traffic.md) | how to stop counting yourself, and why IP filtering usually fails |
| [Auditing a Container](003-auditing-a-container.md) | reading any GTM container's real configuration without console access |
