---
title: Sources
---
This section is so that I don't spend too much time trying to re-read the official documentation as sometimes it's cluttered with a lot of different ways to connect to source providers. It will hold sources that I have to connect to frequently either for my personal projects or work (but it will still be biased for work).

## Google Sheets

### Setup credentials (Service account credentials)

1. Sign in to console.cloud.google.com.
2. Make a project (match the name of the project repo if unsure).
3. Create a `Service Account`.
	- Just enter the name of the project again and skip everything.
4. Generate credentials:
	- Navigate to `IAM & Admin` and select `Service Accounts`.
	- Click the `Service Accounts` that you just created.
	- Search for `Keys`, then create a `JSON key`.
	- Save the credentials somewhere safe (e.g. Bitwarden).
5. Enable "Google Sheets API"

### dlt credentials

From the JSON key, there are three components that need to be added to the `.dt/secrets.toml` (`project_id`, `client_email` and `private_key`).

```toml
[sources.google_sheets.credentials]
project_id = ""
client_email = ""
private_key = "" # add the private key as is with the \n escapes!!!
```

> [!note]
> If you didn't init dlt with Google Sheets as a source, you need to `uv add google-auth`.

***

[Last modified: 2026-07-27]{.note-modified}
