# Docker & SQL Engines — Daily Operations Handbook

**Environment:** CachyOS/Linux with Fish shell, Docker Engine + Compose, SQL Server 2022 Developer, PostgreSQL 18, Oracle MySQL 8.4 LTS.  
**Updated:** 17 November 2026  
**Audience:** Local data engineering and SQL development.  
**Rule:** All shell snippets are **Fish-compatible**. SQL snippets are executed inside their corresponding database clients, not directly at the Fish prompt.

> **Security:** This handbook deliberately does not contain your passwords. Your existing credentials are stored in `~/.config/sql-engines/sqlserver/.env` (mode `600`). Never paste passwords into command arguments, Git repositories, screenshots, or shared logs. A password previously exposed in a conversation should be rotated if there is any possibility it was shared beyond your private environment.

## 0. Your actual setup

| Engine | Docker container | Image/tag | Host connection | Administrative login | Normal development login |
|---|---|---|---|---|---|
| Microsoft SQL Server | `sqlserver` | `mcr.microsoft.com/mssql/server:2022-latest` | `127.0.0.1:1433` | `sa` | `sa` for now; create restricted users when needed |
| PostgreSQL | `postgresql` | `postgres:18` (observed 18.7) | `127.0.0.1:5432` | `postgres` | `postgres` for now; create app-specific roles when needed |
| Oracle MySQL Community Server | `mysql` | `mysql:8.4` (observed 8.4.13) | `127.0.0.1:3306` | `root` (inside container) | `developer` (also accessible over TCP) |

All three services are declared in **one** Compose file:

- Compose: `~/.config/sql-engines/sqlserver/compose.yaml`
- Password variables: `~/.config/sql-engines/sqlserver/.env`
- Compose project name: `sqlserver` (this is the **project** name, not a requirement to start SQL Server)
- SQL Server data: `~/.local/share/sql-engines/sqlserver/data/`
- PostgreSQL data: `~/.local/share/sql-engines/postgresql/data/18/docker/`
- MySQL data: `~/.local/share/sql-engines/mysql/data/`
- Backups: `~/.local/share/sql-engines/backups/{sqlserver,postgresql,mysql}/`
- Portfolio SQL scripts: `~/Projects/SQL_Engines/Test/` — **scripts only**, not Docker configuration.

All database services have `restart: "no"` in Compose. SQL Server has a 4 GiB container memory limit and 2 CPU quota; PostgreSQL and MySQL each have a 2 GiB memory limit and 2 CPU quota. These are **maximum limits, not reserved RAM**. The databases do not need to run together.

### The four layers you must distinguish

1. **Image:** downloaded template, e.g. `postgres:18`. Images on disk consume **storage**, not running database CPU/RAM.
2. **Container:** instance of an image, e.g. `postgresql`. A **stopped** container retains metadata but runs no database process.
3. **Database engine/server:** SQL Server, PostgreSQL, or MySQL process **inside a running container**. One server can host **many databases**.
4. **Database, user, and client:** databases hold tables/data; logins/roles control access; `psql`, `mysql`, `sqlcmd`, DBeaver and VS Code are clients. You **do not** need a new Docker container or a new database user for each database.

---

# 1. Docker: services, startup and shutdown

## 1.1 What are Docker, docker.service, docker.socket and containerd.service?

- **Docker Engine / `dockerd` / `docker.service`:** the daemon that creates, starts, stops, networks and manages containers. `docker` in your terminal is the **client** that sends requests to the daemon.
- **`docker.socket`:** a systemd socket-activation unit for the Docker API. If it is active, connecting to the socket can **start `docker.service` on demand**, even if you previously stopped the service. It is **not** a separate database engine. You normally do not need to start it manually.
- **`containerd.service`:** lower-level container runtime used by Docker to manage container tasks. Starting Docker normally starts required dependencies automatically. Do **not** manually start all three units to use Docker.
- **Docker Compose:** reads the YAML and creates/starts **only the services you request** when you specify service names. Compose is not itself a persistent background daemon.

## 1.2 Start Docker without starting any database container

```fish
sudo systemctl start docker.service
sudo docker info --format 'Docker Engine: {{.ServerVersion}}'
sudo docker ps -a
```

**Important:** Starting the daemon does **not** guarantee that *all* containers stay stopped. Any existing container with a restart policy such as `always` or `unless-stopped` can be started by Docker automatically. Your **three SQL containers** are configured with `restart: "no"`; other future containers (Airflow, Kafka, etc.) must be checked individually.

## 1.3 Prevent automatic container startup

**When defining new Compose services:**

```yaml
services:
  example:
    image: some-image:tag
    restart: "no"
```

**For containers that already exist:** inspect policies first:

```fish
sudo docker ps -aq | xargs -r sudo docker inspect --format '{{.Name}} restart={{.HostConfig.RestartPolicy.Name}}'
```

**Set a specific existing container to manual-only:**

```fish
sudo docker update --restart=no sqlserver postgresql mysql
```

For a future Airflow/Kafka container, replace the names with its actual container names. For containers created through Compose, **also** set `restart: "no"` in their Compose YAML; otherwise a future recreation can reapply the old policy.

**Review before changing policies:** `always`, `unless-stopped`, and `on-failure` may be intentional for some services. Do not indiscriminately change production containers.

**Check your SQL policies:**

```fish
for c in sqlserver postgresql mysql
    sudo docker inspect $c --format '{{.Name}} restart={{.HostConfig.RestartPolicy.Name}} status={{.State.Status}}'
end
```

To make sure *no* container is currently running before shutting down Docker:

```fish
sudo docker ps --format 'table {{.Names}}\t{{.Status}}'
```

## 1.4 Stop Docker completely when finished

**First stop any running containers gracefully**, particularly databases and Kafka/Airflow services. Do not stop Docker while active work is writing to a database.

```fish
sudo docker stop -t 120 sqlserver  # only if SQL Server is running
sudo docker stop -t 60 postgresql  # only if PostgreSQL is running
sudo docker stop -t 60 mysql       # only if MySQL is running
```

A stopped container may return an informational message if stopped again. For a general environment, inspect `sudo docker ps` and stop other running containers too. To stop **all currently running** containers deliberately:

```fish
set running (sudo docker ps -q)
if test (count $running) -gt 0
    sudo docker stop -t 120 $running
end
```

Then stop socket activation **and** the daemon:

```fish
sudo systemctl stop docker.socket docker.service
sudo systemctl stop containerd.service
```

`containerd` may be required by **other** workloads, such as Kubernetes; stop it only if you know nothing else uses it. Stopping `docker.socket` prevents Docker API requests from silently reactivating the daemon. You may see a warning about active dependencies; inspect with `systemctl status` if a unit remains active.

**Verify:**

```fish
systemctl is-active docker.service docker.socket containerd.service
systemctl is-enabled docker.service docker.socket containerd.service
```

`inactive` means not running **now**; `disabled` means not automatically enabled at boot. These are different states. A disabled service can still be started manually or by a dependency.

**If needed, disable boot activation (one-time operation):**

```fish
sudo systemctl disable docker.service docker.socket containerd.service
```

Do not `mask` the services as a routine measure; masking can make manual startup confusing.

**CPU/RAM expectations:** a stopped database container has **no running database process**, so no database process CPU/RAM usage. The Docker daemon and containerd may still consume some resources until stopped. Docker images and bind-mounted database files continue using **disk space**.

## 1.5 Everyday quick reference

```fish
# Start daemon only:
sudo systemctl start docker.service

# Show running containers:
sudo docker ps

# Show running + stopped containers:
sudo docker ps -a

# Start exactly one engine:
sudo docker start sqlserver
sudo docker start postgresql
sudo docker start mysql

# Stop exactly one engine:
sudo docker stop -t 120 sqlserver
sudo docker stop -t 60 postgresql
sudo docker stop -t 60 mysql

# Observe memory/CPU of running containers:
sudo docker stats --no-stream

# Logs:
sudo docker logs --tail 50 sqlserver
sudo docker logs --tail 50 postgresql
sudo docker logs --tail 50 mysql
```

**Never use** `docker compose up -d` **without a service name** when you intend to start only one database. That command can start all services in the Compose project. Instead:

```fish
sudo docker compose --project-directory ~/.config/sql-engines/sqlserver \
    -f ~/.config/sql-engines/sqlserver/compose.yaml \
    up -d --no-deps postgresql
```

For **existing containers**, `sudo docker start <name>` is simpler and does not recreate anything. Use Compose when deploying/reconfiguring services.

---

# 2. SQL Server 2022 Developer

## 2.1 Start, connect, stop

```fish
sudo systemctl start docker.service
sudo docker start sqlserver
sudo docker logs --tail 25 sqlserver
```

SQL Server on an HDD can take tens of seconds to recover. Wait for a message similar to **`Recovery is complete`** before querying.

**Open SQL Server's interactive command-line client:**

```fish
sudo docker exec -it sqlserver \
    /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C
```

Enter the `sa` password when prompted. `-C` trusts the server certificate; acceptable for this **local development** instance, not a blanket recommendation for production. At the `1>` prompt, SQL statements are executed when you enter `GO` on its own line:

```sql
SELECT @@VERSION AS version;
GO
SELECT name, state_desc FROM sys.databases;
GO
```

Quit with `QUIT` on its own line. You can also connect from DBeaver using `127.0.0.1`, port `1433`, login `sa`, password from your `.env`.

**Stop:**

```fish
sudo docker stop -t 120 sqlserver
```

SQL Server then runs no SQL Server process and consumes no database-process CPU/RAM. Its database files remain in the bind mount. Exit code `137` on a previous stop was **not** reported by Docker as `OOMKilled`; it may reflect a forced kill after a slow shutdown. The longer timeout helps but does not guarantee graceful shutdown.

## 2.2 One SQL Server instance can host many databases

`sqlserver` is **one container running one SQL Server instance**. Within it, you can have `master`, `model`, `msdb`, `tempdb`, plus dozens of user databases. Starting `sqlserver` makes **all attached online databases** in that instance available after startup/recovery. You do **not** need a separate container or login for every database.

- `sa`: built-in **system administrator** SQL Server login; use for setup, restoring backups, server configuration, and managing logins.
- **Login:** identity authenticated at the server level.
- **Database user:** identity mapped to a login **inside a particular database**, with database-specific permissions.
- For professional day-to-day use, create a dedicated login and database user with limited rights; for local administration, `sa` is sufficient.

**Example: create a database and a restricted database user** (run within `sqlcmd`; choose a **new unique password**, replace placeholder before executing):

```sql
USE master;
GO
CREATE DATABASE SandboxDB;
GO
CREATE LOGIN sandbox_login WITH PASSWORD = 'REPLACE_WITH_NEW_STRONG_PASSWORD';
GO
USE SandboxDB;
GO
CREATE USER sandbox_user FOR LOGIN sandbox_login;
GO
ALTER ROLE db_datareader ADD MEMBER sandbox_user;
ALTER ROLE db_datawriter ADD MEMBER sandbox_user;
GO
```

This user can read/write existing tables but **cannot necessarily create/alter schemas**. For schema development, grant the necessary DDL permissions or a suitable role intentionally; do not default to `sysadmin`. If `SandboxDB` or `sandbox_login` already exists, creation statements will error; check first.

## 2.3 Restore a `.bak` file from `~/Downloads` — complete workflow

**Key distinction:** `.bak` is a SQL Server **backup archive**, not a `.mdf`/`.ldf` file to open manually. SQL Server's `RESTORE` command reads the backup and **creates the physical data (`.mdf`, optional `.ndf`) and log (`.ldf`) files** automatically. The **logical file names** inside the backup may differ from its filename and must be inspected first.

**Prerequisites:** the backup must be compatible with SQL Server 2022 (backups from **newer** major versions cannot generally be restored to older SQL Server). A backup from an untrusted source may contain harmful database objects/code: inspect and avoid running unknown stored procedures. Ensure adequate free HDD space. Do not restore over an existing database without deliberate backup and review.

### A. Start SQL Server and stage the backup

Assume the downloaded file is `~/Downloads/ExampleDatabase.bak`. **Replace the filename with your actual file**:

```fish
sudo systemctl start docker.service
sudo docker start sqlserver

# Stage a COPY (preserve the original in Downloads):
cp ~/Downloads/ExampleDatabase.bak \
    ~/.local/share/sql-engines/backups/sqlserver/ExampleDatabase.bak

# SQL Server runs as UID 10001 in your current image; make this file readable:
sudo chown 10001:0 \
    ~/.local/share/sql-engines/backups/sqlserver/ExampleDatabase.bak
sudo chmod 640 \
    ~/.local/share/sql-engines/backups/sqlserver/ExampleDatabase.bak

# Verify the file is visible from the container:
sudo docker exec sqlserver \
    ls -lh /var/opt/mssql-backups/ExampleDatabase.bak
```

The bind mount maps the **host** `~/.local/share/sql-engines/backups/sqlserver/` to the **container** `/var/opt/mssql-backups/`. No `docker cp` is required. Your host backup directory is private; avoid changing parent directory permissions unnecessarily. The `10001:0` ownership is specific to your **existing SQL Server setup**, not a universal SQL Server rule.

### B. Inspect the backup (do not restore blindly)

Open interactive `sqlcmd`:

```fish
sudo docker exec -it sqlserver \
    /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C
```

At the `sqlcmd` prompt, enter:

```sql
RESTORE HEADERONLY
FROM DISK = N'/var/opt/mssql-backups/ExampleDatabase.bak';
GO

RESTORE FILELISTONLY
FROM DISK = N'/var/opt/mssql-backups/ExampleDatabase.bak';
GO

RESTORE VERIFYONLY
FROM DISK = N'/var/opt/mssql-backups/ExampleDatabase.bak';
GO
```

- `HEADERONLY`: backup metadata, database name, backup type, version, position/backup set.
- `FILELISTONLY`: **logical file names**, file types (`D` = data, `L` = log), original paths, and potentially **multiple data files**.
- `VERIFYONLY`: checks readability/completeness to a degree, but is **not a substitute for a test restore**.

For backups containing multiple backup sets, you may need `WITH FILE = <position>` in inspection and restore statements. For differential/log backup chains, the sequence is more complex; the example below assumes a **single full database backup**.

### C. Restore to a NEW database and safe Linux paths

**Example only:** suppose `FILELISTONLY` returned logical names `Example_Data` and `Example_Log`. Substitute the **actual** names from your output. If there are extra `.ndf`, filestream, or other files, add **one `MOVE` per logical file** with an appropriate unique target path; do not assume there are exactly two.

```sql
USE master;
GO
RESTORE DATABASE [ExampleDatabase]
FROM DISK = N'/var/opt/mssql-backups/ExampleDatabase.bak'
WITH
    MOVE N'Example_Data' TO N'/var/opt/mssql/data/ExampleDatabase.mdf',
    MOVE N'Example_Log'  TO N'/var/opt/mssql/data/ExampleDatabase_log.ldf',
    RECOVERY,
    STATS = 10;
GO

SELECT name, state_desc
FROM sys.databases
WHERE name = N'ExampleDatabase';
GO
```

**Important:** use a **new database name** and unique output filenames. Do **not** add `WITH REPLACE` unless you intentionally want to overwrite an existing database and have verified backups. `RECOVERY` brings the restored database online; a multi-stage differential/log restore requires `NORECOVERY` until the final stage.

### D. Inspect the restored data and log files

```sql
USE [ExampleDatabase];
GO
SELECT
    name AS logical_name,
    type_desc,
    physical_name,
    size * 8.0 / 1024 AS size_mb
FROM sys.database_files;
GO
```

Typical physical paths:

- `/var/opt/mssql/data/ExampleDatabase.mdf` — main data file
- `/var/opt/mssql/data/ExampleDatabase_log.ldf` — transaction log

These are **SQL Server-managed binary files**. Do not edit, rename, move, or delete them in the file manager while SQL Server is running. Use SQL commands and supported database maintenance procedures.

**Verify backup/restore history** (optional):

```sql
USE msdb;
GO
SELECT TOP (20) destination_database_name, restore_date
FROM dbo.restorehistory
ORDER BY restore_date DESC;
GO
```

**If restore fails:** do not retry with `REPLACE` automatically. Check the exact error, SQL Server version, backup type, logical names, existing database names, target path uniqueness, file permissions, and disk space.

### E. Restore from a different host folder

Your container **cannot automatically see** arbitrary paths such as `~/Downloads`, `/media/drive`, or `~/Projects`. Copy the `.bak` into the **existing mapped backup folder** as above, or explicitly add another read-only bind mount to Compose and recreate the container carefully. The copy approach is simpler and safer for occasional restores.

### F. Optional full backup of an existing SQL Server database

```sql
BACKUP DATABASE [ExampleDatabase]
TO DISK = N'/var/opt/mssql-backups/ExampleDatabase_full.bak'
WITH INIT, CHECKSUM, STATS = 10;
GO
```

Backups on the **same HDD** do not protect against physical HDD failure. Keep a second copy on external or remote storage for important data.

---

# 3. PostgreSQL 18

## 3.1 Start, connect and stop

```fish
sudo systemctl start docker.service
sudo docker start postgresql
sudo docker exec -u postgres postgresql pg_isready -U postgres
```

**Open `psql` inside the container:**

```fish
sudo docker exec -it -u postgres postgresql \
    psql -U postgres -d postgres
```

Inside `psql`:

```sql
SELECT version();
SELECT current_user, current_database();
\l
\du
\q
```

Commands beginning with `\` (`\l`, `\du`, `\q`) are **psql meta-commands**, not ordinary SQL. SQL statements end with `;`.

**Stop:**

```fish
sudo docker stop -t 60 postgresql
```

## 3.2 Roles versus databases

- The `postgres` **role** is the default superuser/admin; the `postgres` **database** is a separate object that happens to have the same name.
- A PostgreSQL **cluster/server** can host multiple databases, each with schemas and tables.
- **Roles** can log in (`LOGIN`), own databases, and receive privileges. One login role can access several databases when granted access.
- You **do not** need a new user for every database. Prefer separate roles for applications, projects, or privilege boundaries. Avoid `postgres` for routine application connections.

**Create a new project role and database:** open the `psql` session connected to the `postgres` database, then run (replace password placeholder):

```sql
CREATE ROLE weather_dev LOGIN PASSWORD 'REPLACE_WITH_NEW_STRONG_PASSWORD';
CREATE DATABASE weather_db OWNER weather_dev;
```

Connect as that user from DBeaver: host `127.0.0.1`, port `5432`, database `weather_db`, user `weather_dev`, chosen password. Because the role **owns** the database, it can generally manage objects it owns; do not grant `SUPERUSER` to normal accounts.

**List databases/roles:**

```sql
\l
\du
```

**Switch databases in psql:** `\c weather_db` (or specify `-d weather_db` when opening `psql`).

**Delete a role only after transferring/removing objects it owns.** Never drop `postgres`.

## 3.3 PostgreSQL 18 persistent volume: important

Your tested mapping is:

```text
Host:      ~/.local/share/sql-engines/postgresql/data/
Container: /var/lib/postgresql/
Actual PGDATA inside container: /var/lib/postgresql/18/docker/
```

This is **correct for the official `postgres:18` image** and was verified through container recreation. Do **not** change the mount to the older `/var/lib/postgresql/data` location; that guidance applies to older image majors. PostgreSQL 18 automatically creates the version-specific subdirectory.

**PostgreSQL backups (optional):** `pg_dump` makes a logical backup; `pg_restore` restores it to an existing database. Keep backups separate from the live data directory and off-HDD for critical data.

---

# 4. MySQL 8.4 LTS

## 4.1 `root` versus `developer`

**`root`** is MySQL's built-in administrative account, **not** the Linux root account. In your setup it is `root@localhost` and is intended for administration **inside the MySQL container**. Use it for creating users, adjusting privileges, managing server settings, and emergency administration.

**`developer`** is a MySQL account you created, currently authenticated as `developer@%`. `%` is MySQL's host wildcard; it permits connections through Docker networking, subject to the password and network rules. Your published MySQL host port is **only** `127.0.0.1:3306`, so it is not published on your laptop's public network interfaces. Other containers on reachable Docker networks may still attempt to connect.

**Important permission detail:** you previously granted `ALL PRIVILEGES ON *.*` to `developer`. That is **very broad**: it is convenient for a personal lab but **not least-privilege professional practice**. It does not necessarily include `GRANT OPTION`, and is not exactly equivalent to `root`, but it permits substantial server-wide changes. For production or sensitive data, create a **project-specific user** restricted to one database.

## 4.2 Start, log in and stop

```fish
sudo systemctl start docker.service
sudo docker start mysql

# Admin login (inside container; prompts for password):
sudo docker exec -it mysql mysql -u root -p

# Normal development login (inside container; prompts for password):
sudo docker exec -it mysql mysql -u developer -p
```

At the `mysql>` prompt:

```sql
SELECT VERSION(), CURRENT_USER(), DATABASE();
SHOW DATABASES;
EXIT;
```

**Stop:**

```fish
sudo docker stop -t 60 mysql
```

## 4.3 Create and use a MySQL database

Log in as `developer` (or `root` for administration), then:

```sql
CREATE DATABASE IF NOT EXISTS weather_lab
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE weather_lab;
SELECT DATABASE();
SHOW TABLES;
```

A **database** is a namespace for tables/views; a **user** is an account with privileges. You can create many databases under one running `mysql` container. You do **not** need to create a new container or user for each database.

## 4.4 Add a new MySQL user — recommended project-scoped pattern

Log in as `root` first:

```fish
sudo docker exec -it mysql mysql -u root -p
```

Then run SQL (replace the example password with a new, unique strong password):

```sql
CREATE DATABASE IF NOT EXISTS weather_lab;

CREATE USER 'weather_app'@'%'
IDENTIFIED BY 'REPLACE_WITH_NEW_STRONG_PASSWORD';

GRANT ALL PRIVILEGES ON weather_lab.* TO 'weather_app'@'%';

SHOW GRANTS FOR 'weather_app'@'%';
```

This account can manage objects **within `weather_lab`**, not every database. For a read-only reporting user:

```sql
CREATE USER 'weather_reader'@'%'
IDENTIFIED BY 'REPLACE_WITH_ANOTHER_STRONG_PASSWORD';

GRANT SELECT ON weather_lab.* TO 'weather_reader'@'%';
SHOW GRANTS FOR 'weather_reader'@'%';
```

`FLUSH PRIVILEGES` is **not required** after normal `CREATE USER` and `GRANT` statements. `CREATE USER` errors if the account exists; use `IF NOT EXISTS` only when that behavior is intended.

**Change a user's password:**

```sql
ALTER USER 'weather_app'@'%'
IDENTIFIED BY 'A_NEW_UNIQUE_STRONG_PASSWORD';
```

**Remove a user intentionally:**

```sql
DROP USER 'weather_app'@'%';
```

Be careful: deleting a MySQL user does not automatically remove all its tables or databases.

## 4.5 MySQL account names contain a host component

`'root'@'localhost'` and `'developer'@'%'` are **different accounts**. The part after `@` describes which client host may authenticate as that user; it is **not** the host address you enter into DBeaver. In DBeaver, enter host `127.0.0.1` and username `developer`. For local root administration, use `sudo docker exec -it mysql mysql -u root -p`.

**Inspect current account privileges** from a MySQL admin session:

```sql
SELECT user, host FROM mysql.user ORDER BY user, host;
SHOW GRANTS FOR 'developer'@'%';
```

---

# 5. DBeaver / VS Code connection reference (next phase)

DBeaver Flatpak is **not configured yet**. The table below describes the intended connections, not a claim that host-side connections have been tested.

| Client setting | SQL Server | PostgreSQL | MySQL |
|---|---|---|---|
| Host | `127.0.0.1` | `127.0.0.1` | `127.0.0.1` |
| Port | `1433` | `5432` | `3306` |
| Username | `sa` initially | `postgres` initially | `developer` |
| Password | SQL Server password | PostgreSQL password | Developer account password |
| Database | `master` or desired database | `postgres` or desired database | optional initially; select desired schema |
| Container must be running? | Yes | Yes | Yes |

**Flatpak caveat:** sandboxed applications may have network access but must be checked. We will verify the actual Flatpak permissions, JDBC driver installation, and host TCP connections when setting up DBeaver. Avoid giving Flatpak unrestricted filesystem access unless genuinely required; network access and carefully scoped folders are usually preferable. SQL Server's local development TLS certificate may require an explicit client trust setting.

---

# 6. Common pitfalls and troubleshooting

| Symptom | Likely explanation | What to do |
|---|---|---|
| `Cannot connect to Docker daemon` | Docker service stopped or socket unavailable | `sudo systemctl start docker.service` |
| Database client `Connection refused` | Container stopped, engine starting, or wrong port | `sudo docker ps`, then `sudo docker logs --tail 40 <container>` |
| SQL Server starts slowly | Database recovery and HDD I/O | Wait for `Recovery is complete` |
| SQL Server exit `137` | SIGKILL; possibly forced shutdown | Inspect `sudo docker inspect sqlserver --format '{{.State.OOMKilled}}'`; use longer graceful stop timeout |
| PostgreSQL database missing after `pg_restore` | Destination database not created | Create destination database before `pg_restore`, unless using supported creation workflow |
| PostgreSQL password works inside but not from DBeaver | Different local socket versus host TCP auth or client config | Check host `127.0.0.1`, port `5432`, user, password, `pg_hba.conf` if needed |
| MySQL `root` login fails from DBeaver | Root is `root@localhost` | Use `developer` or a dedicated TCP-enabled project user |
| `.bak` cannot be read | Wrong mount path or permissions | Stage it under the existing SQL Server backup bind mount; verify from container |
| Restore says logical file not found | Guessed logical name | Run `RESTORE FILELISTONLY`, then use actual names in `MOVE` |
| Restored `.mdf` or `.ldf` path conflicts | Existing files/database or duplicate target paths | Choose unique paths; do not blindly use `WITH REPLACE` |
| Docker starts other containers unexpectedly | Their restart policies are not `no` | Inspect with `docker inspect`; update both running container and Compose definitions |
| `docker compose up -d` starts all SQL engines | No service specified | Use `docker start <container>` or `compose up -d --no-deps <service>` |

**Avoid these commands for routine operations:** `docker compose down -v`, `docker volume prune`, `docker system prune --volumes`, and `rm -rf` on database data directories. Your current data uses bind mounts, but destructive cleanup commands can still remove other important Docker resources or persistent volumes.

---

# 7. Recommended daily routines

### A. I only want Docker available, with no database engines running

```fish
sudo systemctl start docker.service
sudo docker ps
```

If any container is running, stop it deliberately. Verify all desired containers have `restart: "no"`. Merely starting Docker is **not** a universal guarantee of zero running containers when future workloads have different policies.

### B. I want to work only with PostgreSQL

```fish
sudo systemctl start docker.service
sudo docker start postgresql
sudo docker exec -it -u postgres postgresql psql -U postgres -d postgres
# After leaving psql:
sudo docker stop -t 60 postgresql
```

### C. I want to work only with MySQL

```fish
sudo systemctl start docker.service
sudo docker start mysql
sudo docker exec -it mysql mysql -u developer -p
# After leaving mysql:
sudo docker stop -t 60 mysql
```

### D. I want to work only with SQL Server

```fish
sudo systemctl start docker.service
sudo docker start sqlserver
# Wait for SQL Server recovery, then:
sudo docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C
# After leaving sqlcmd:
sudo docker stop -t 120 sqlserver
```

### E. I am done with ALL Docker work today

```fish
# Check for any other running containers first:
sudo docker ps

# Stop your SQL containers if running:
for c in sqlserver postgresql mysql
    if test (sudo docker inspect -f '{{.State.Running}}' $c) = true
        if test $c = sqlserver
            sudo docker stop -t 120 $c
        else
            sudo docker stop -t 60 $c
        end
    end
end

# Stop any other running workloads deliberately before proceeding.
sudo systemctl stop docker.socket docker.service
sudo systemctl stop containerd.service
systemctl is-active docker.service docker.socket containerd.service
```

---

# 8. Official documentation

- Docker daemon start: https://docs.docker.com/engine/daemon/start/
- Docker container restart policies: https://docs.docker.com/engine/containers/start-containers-automatically/
- Docker Compose reference: https://docs.docker.com/compose/compose-file/
- SQL Server restore from `.bak` in Linux container: https://learn.microsoft.com/en-us/sql/linux/tutorial-restore-backup-in-sql-server-container?view=sql-server-ver16
- Official PostgreSQL image, version-specific PGDATA: https://hub.docker.com/_/postgres
- PostgreSQL SQL roles: https://www.postgresql.org/docs/current/user-manag.html
- MySQL account management: https://dev.mysql.com/doc/refman/8.4/en/account-management-statements.html

**Bottom line:** Start `docker.service` once; manually start only the container(s) you need; stop containers after use; then stop Docker's socket, service and (if unused elsewhere) containerd. Keep the three engines' data on their existing persistent bind mounts. Create databases inside each engine, and create additional users only when different permissions or project isolation are useful.
