# Authentication

There are various ways to authenticate yourself to Snowflake, but when building data pipelines and automation, my recommendation would be to use the key-pair authentication.

## 1. Private Key Generation

create an unencrypted version of the private key

``` numberSource
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
```

this will create something that looks like:

``` numberSource
-----BEGIN ENCRYPTED PRIVATE KEY-----
MIIE6T...
-----END ENCRYPTED PRIVATE KEY-----
```

## 2. Public Key Generation

create a public key from the private key

``` numberSource
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

this will create something that looks like:

``` numberSource
-----BEGIN PUBLIC KEY-----
MIIBIj...
-----END PUBLIC KEY-----
```

## 3. Snowflake User Key-Pair Assignment

give your key for the `SECURITYADMIN` to register to your user, you can register two RSA public keys

``` numberSource
-- Switch to Security Admin to manage user authentication credentials
USE ROLE securityadmin;

-- RSA_PUBLIC_KEY for python data ingestion
ALTER USER {{ user }}
SET RSA_PUBLIC_KEY = '
-----BEGIN PUBLIC KEY-----
MIIBI...
-----END PUBLIC KEY-----
';

-- RSA_PUBLIC_KEY for dbt connection + dbeaver
ALTER USER {{ user }}
SET RSA_PUBLIC_KEY_2 = '
-----BEGIN PUBLIC KEY-----
MIIBI...
-----END PUBLIC KEY-----
';
```

------------------------------------------------------------------------

Last modified: 2026-06-17

Back to top
