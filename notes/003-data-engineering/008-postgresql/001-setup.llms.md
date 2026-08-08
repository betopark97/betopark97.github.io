# Setup

## Installation

## Locate Binaries

``` numberSource
ls /usr/lib/postgresql
```

Add the binary path permanently to your shell config file.

``` numberSource
echo 'export PATH="/usr/lib/postgresql/{version}/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Verify the tools are active.

``` numberSource
which initdb pg_ctl psql
```

## Initialize Database

Create a directory inside your home folder to hold and own the database files and initialize with your user as a superuser.

``` numberSource
initdb -D $HOME/pgdata -U $USER -A trust
```

## Configure the Port & Socket (Optional)

By default, PostgreSQL tries to bind to port 5432 and write sockets to system directories requiring sudo. You can update configuration to use the port of your liking and Unix socket folder /tmp.

``` numberSource
# Change port
sed -i 's/#port = 5432/port = {port}/' $HOME/pgdata/postgresql.conf

# Set socket directory to /tmp
sed -i "s|^#*unix_socket_directories = .*|unix_socket_directories = '/tmp'|" $HOME/pgdata/postgresql.conf

# Direct psql to the /tmp
echo 'export PGHOST=/tmp' >> ~/.bashrc
source ~/.bashrc
```

## Start the Server

Start the server process in the background (`-D`) using `pg_ctl` and direct logs to a dedicated file.

``` numberSource
pg_ctl -D $HOME/pgdata -l $HOME/pgdata/server.log start
```

Check it’s working.

``` numberSource
# Verify status of server
pg_ctl -D $HOME/pgdata status

# Check live logs
tail -f $HOME/pgdata/server.log
```

## Connect to the Server

``` numberSource
psql -p 5432 -d postgres
```

------------------------------------------------------------------------

Last modified: 2026-08-06

Back to top
