# HTTP to HTTPS

## What HTTPS Actually Is

HTTPS is not a different protocol. It is the same HTTP request and response, wrapped in a TLS tunnel before it leaves the machine. Two things happen inside that wrap:

- **Encryption** — nobody between the browser and the server can read or modify the bytes.
- **Identity** — the server proves it really is `example.com` by presenting a **certificate** signed by a **Certificate Authority (CA)** the browser already trusts.

The encryption is the easy part; any process can generate a key pair in a second. The identity part is the whole problem. A certificate is a CA’s signed statement that “whoever holds this private key controls this domain name”. You cannot manufacture that yourself — you have to prove domain control to a CA, and the CA hands back a certificate that expires (Let’s Encrypt: 90 days).

So “turn on HTTPS” really means three separate jobs:

1.  Get a domain name that resolves to your public IP.
2.  Prove to a CA that you control it, and receive a certificate.
3.  Terminate TLS on port 443 with that certificate, and keep renewing it forever.

## What You Need Before Anything Works

| Requirement | Why | How to check |
|----|----|----|
| A real domain name | Certificates are issued for names, never for bare IPs. `https://203.0.113.5` cannot be made valid. | `dig +short app.example.com` |
| DNS A/AAAA record pointing at your public IP | The CA connects back to that name to verify you. | `dig +short app.example.com` matches `curl -s ifconfig.me` |
| Ports 80 and 443 reachable from the internet | Port 80 is used for the ACME HTTP-01 challenge and for the HTTP→HTTPS redirect. 443 serves the real traffic. | `curl -I http://app.example.com` from outside your network |
| Router port-forward / cloud firewall rule | Home servers need 80 and 443 forwarded to the host; cloud VMs need the security group opened. | Same as above |

> **NOTE:**
>
> Many residential ISPs block inbound port 80 and 443, and CGNAT means you may not own your public IP at all. If `curl` from outside times out, no amount of Docker configuration will fix it — see [No Public Port 80](#no-public-port-80-dns-01) below.

## Why You Do Not Add TLS to the App Container

The instinct is to make the application itself speak HTTPS. Almost always wrong:

- Every app then needs its own certificate logic, its own renewal cron, and its own copy of the private key.
- Renewal usually needs a restart, so the app goes down every 60 days.
- Only one container can bind port 443. A second service means a second host or a second port.
- Application servers (gunicorn, uvicorn, the Streamlit dev server, `node`) are not hardened for direct internet exposure.

The standard pattern instead: **the app keeps speaking plain HTTP, and a reverse proxy in front of it terminates TLS.**

``` numberSource
internet --443/TLS--> [ reverse proxy ] --80/plain HTTP--> [ app container ]
                       (owns the cert)     (docker network, never published)
```

This is safe because the plain-HTTP leg never leaves the Docker bridge network. Traffic between containers on the same user-defined network does not touch the host’s NIC or the internet.

The key Docker consequence: **stop publishing the app’s port.** Use `expose` (or nothing at all — containers on the same network reach each other by service name regardless) instead of `ports`. If you leave `ports: - "8000:8000"` in place, anyone can bypass your proxy and hit the app over plain HTTP.

``` numberSource
services:
  app:
    image: myapp:latest
    expose:
      - "8000"        # visible to other containers only
    # ports:          # <- delete this; it publishes to the host
    #   - "8000:8000"
```

## The Lazy Default: Caddy

Caddy gets a certificate from Let’s Encrypt on first boot, redirects HTTP to HTTPS, and renews in the background, with no cron job and no extra container. For a new setup this is the shortest path that is also correct.

`Caddyfile`:

``` numberSource
app.example.com {
    reverse_proxy app:8000
}
```

`docker-compose.yml`:

``` numberSource
services:
  app:
    image: myapp:latest
    expose:
      - "8000"

  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data      # certificates live here — must persist
      - caddy_config:/config
    depends_on:
      - app

volumes:
  caddy_data:
  caddy_config:
```

`docker compose up -d`, then `https://app.example.com` works. That is the whole setup.

Two details that matter:

- **`caddy_data` must be a named volume.** Certificates and the ACME account key are stored there. Lose it and every `docker compose up` requests fresh certificates, which walks straight into Let’s Encrypt’s rate limit (5 duplicate certificates per week).
- **The upstream is `app:8000`, not `localhost:8000`.** Inside a container, `localhost` is that container itself. Docker’s embedded DNS resolves the Compose service name.

Multiple services are one block each:

``` numberSource
app.example.com {
    reverse_proxy app:8000
}

dashboard.example.com {
    reverse_proxy streamlit:8501
}
```

## Nginx + Certbot

Use this when nginx is already in the stack or the config has to stay nginx-shaped. It is more moving parts: nginx does not speak ACME, so certbot fetches certificates into a shared volume and nginx reads them from disk.

The chicken-and-egg problem: nginx will not start with a `ssl_certificate` path that does not exist yet, but certbot needs nginx serving port 80 to answer the HTTP-01 challenge. Solution — start with an HTTP-only config, issue the certificate, then add the TLS server block and reload.

`docker-compose.yml`:

``` numberSource
services:
  app:
    image: myapp:latest
    expose:
      - "8000"

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - certs:/etc/letsencrypt
      - acme:/var/www/certbot
    depends_on:
      - app

  certbot:
    image: certbot/certbot
    volumes:
      - certs:/etc/letsencrypt
      - acme:/var/www/certbot
    # renew twice a day; certbot no-ops until the cert is within 30 days of expiry
    entrypoint: >
      sh -c "trap exit TERM; while :; do certbot renew --webroot -w /var/www/certbot --quiet; sleep 12h; done"

volumes:
  certs:
  acme:
```

Step 1 — HTTP-only `nginx.conf`, enough to answer the challenge:

``` numberSource
server {
    listen 80;
    server_name app.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://app:8000;
    }
}
```

Step 2 — bring it up and issue the certificate once:

``` numberSource
docker compose up -d nginx
docker compose run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    -d app.example.com \
    --email you@example.com --agree-tos --no-eff-email
```

Step 3 — final `nginx.conf`: port 80 redirects (except the challenge path), port 443 serves.

``` numberSource
server {
    listen 80;
    server_name app.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;      # keep this — renewals use it
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    http2 on;
    server_name app.example.com;

    ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;

    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # needed for websockets (Streamlit, Jupyter, socket.io, HMR)
        proxy_http_version 1.1;
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Step 4 — `docker compose up -d` to start certbot’s renewal loop, and reload nginx after each renewal. Nginx caches certificates in memory at startup, so a renewed certificate on disk changes nothing until reload. Simplest fix is a nightly restart:

``` numberSource
0 4 * * * cd /srv/myapp && docker compose exec -T nginx nginx -s reload
```

## Traefik

Worth it when containers come and go and you do not want to edit proxy config for each one. Traefik reads the Docker socket and configures itself from labels on each service.

``` numberSource
services:
  traefik:
    image: traefik:v3
    restart: unless-stopped
    command:
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.web.http.redirections.entrypoint.to=websecure
      - --entrypoints.web.http.redirections.entrypoint.scheme=https
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.le.acme.email=you@example.com
      - --certificatesresolvers.le.acme.storage=/letsencrypt/acme.json
      - --certificatesresolvers.le.acme.httpchallenge=true
      - --certificatesresolvers.le.acme.httpchallenge.entrypoint=web
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - letsencrypt:/letsencrypt

  app:
    image: myapp:latest
    labels:
      - traefik.enable=true
      - traefik.http.routers.app.rule=Host(`app.example.com`)
      - traefik.http.routers.app.entrypoints=websecure
      - traefik.http.routers.app.tls.certresolver=le
      - traefik.http.services.app.loadbalancer.server.port=8000

volumes:
  letsencrypt:
```

> **NOTE:**
>
> Mounting `/var/run/docker.sock` gives that container root-equivalent control of the host. Mount it read-only, and do not do it on a box where the proxy is also running untrusted workloads.

## No Public Port 80: DNS-01

If port 80 is blocked, the machine is behind CGNAT, or the service is internal-only, the HTTP-01 challenge cannot work. Use the **DNS-01** challenge instead: the CA asks you to publish a specific TXT record, and the proxy creates it through your DNS provider’s API. This also works for `*.example.com` wildcards.

Caddy needs a provider-specific build, e.g. Cloudflare:

``` numberSource
{
    acme_dns cloudflare {env.CF_API_TOKEN}
}

app.internal.example.com {
    reverse_proxy app:8000
}
```

``` numberSource
services:
  caddy:
    image: caddy:2-alpine   # replace with a build including the cloudflare dns module
    environment:
      CF_API_TOKEN: ${CF_API_TOKEN}   # scoped to Zone:DNS:Edit on one zone only
```

The domain still has to exist and be under your DNS control, but it never needs to resolve to a public IP — a name pointing at `10.0.0.5` gets a fully trusted certificate this way.

## Local Development

For `localhost` and LAN work there is no CA that will issue you a certificate. Two options:

- **`mkcert`** — creates a local CA, installs it into the OS and browser trust stores, and issues certificates for any name. No warnings, no public DNS.

  ``` numberSource
  mkcert -install
  mkcert app.localhost localhost 127.0.0.1
  # mount app.localhost+2.pem and app.localhost+2-key.pem into the proxy
  ```

- **Caddy’s internal CA** — `tls internal` in a site block issues a self-signed certificate automatically. Zero setup, but browsers warn until you trust Caddy’s root manually.

  ``` numberSource
  app.localhost {
    tls internal
    reverse_proxy app:8000
  }
  ```

Never reuse a development certificate in production, and never disable certificate verification in clients to work around a warning — that removes the identity guarantee that is the entire point.

## Making the App Behave Behind a Proxy

Once TLS terminates at the proxy, the app receives plain HTTP and — unless told otherwise — thinks the request was insecure. Symptoms: redirect loops, `http://` links in generated pages, login cookies rejected, every client IP logged as the proxy’s.

The proxy must send the forwarding headers (Caddy and Traefik do it by default; nginx needs the `proxy_set_header` lines above), and the app must be configured to trust them:

| Framework | Setting |
|----|----|
| Django | `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`, plus the public hostname in `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` |
| FastAPI / uvicorn | `--proxy-headers --forwarded-allow-ips="*"` |
| Flask | `werkzeug.middleware.proxy_fix.ProxyFix(app.wsgi_app, x_proto=1, x_for=1)` |
| Streamlit | `--server.headless true`; proxy must forward websocket upgrade headers or the page loads and then hangs on “Connecting…” |
| Express | `app.set("trust proxy", 1)` |

> **NOTE:**
>
> Only trust forwarding headers when a proxy you control is actually in front. A directly-exposed app that trusts `X-Forwarded-For` lets any client spoof its own IP past rate limits and IP allowlists.

## Checklist and Gotchas

- **Delete `ports:` from every app service.** Anything still published bypasses TLS.
- **Persist the certificate volume** (`caddy_data`, `/etc/letsencrypt`, `acme.json`). Otherwise every rebuild re-issues and hits Let’s Encrypt’s rate limit — 5 duplicate certificates per exact name set per week.
- **Test against the staging CA first.** Let’s Encrypt staging issues untrusted certificates but has generous limits: Caddy `acme_ca https://acme-staging-v02.api.letsencrypt.org/directory`, certbot `--staging`. Switch to production only after the flow works end to end, and delete the staging certificates when you do.
- **Point DNS before the first start.** Requesting a certificate for a name that does not yet resolve to you burns a failed-validation attempt.
- **`acme.json` needs mode 600** if bind-mounted; Traefik refuses to start otherwise. A named volume avoids the issue.
- **Add HSTS only when HTTPS is stable.** `Strict-Transport-Security` tells browsers to refuse plain HTTP for that domain for the stated duration, and it is cached client-side — you cannot take it back by removing the header. Start with a short `max-age`, and leave `includeSubDomains`/`preload` alone until certain.
- **Renewal is the part that breaks.** It fails months later, silently, usually because port 80 got closed or the webroot mount changed. Check expiry from outside: `echo | openssl s_client -connect app.example.com:443 2>/dev/null | openssl x509 -noout -dates`.

------------------------------------------------------------------------

Last modified: 2026-08-28

Back to top
