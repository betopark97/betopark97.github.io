---
title: Create Snippets
---

## Create User

```sql
USE ROLE useradmin;
CREATE USER {{ user }}
PASSWORD = '{{ password }}'
DEFAULT_ROLE = '{{ DEFAULT_ROLE }}'
EMAIL = '{{ email }}'; -- Optional

USE ROLE securityadmin;
GRANT ROLE {{ DEFAULT_ROLE }} TO USER {{ user }};
```

## Create Role

```sql
USE ROLE useradmin;
CREATE ROLE {{ DEFAULT_ROLE }};
GRANT USAGE ON WAREHOUSE {{ DEFAULT_WH }} TO ROLE {{ DEFAULT_ROLE }};
```

## Create Agent

1. Always have two roles for Agents (Snowflake Intelligence)
	- superior manager of all agents (owner of all agent)
	- inferior manager of a specific agent (reader of an agent)

- create the agent with sysadmin in the UI

2. [[create_role]] for the specific agent.

3. For both superior and inferior roles there are 2 types of grants needed:

-  give grants on snowflake intelligence - agent, schema, database
```sql
USE ROLE securityadmin;
GRANT USAGE ON AGENT SNOWFLAKE_INTELLIGENCE.AGENTS.{{ domain_agent }} TO ROLE {{ domain_agent_user_role }};
GRANT USAGE ON SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS TO ROLE {{ domain_agent_user_role }};
GRANTE USAGE ON DATABASE SNOWFLAKE_INTELLIGENCE TO ROLE {{ domain_agent_user_role }};
```

- give grants on underlying tables that the semantic view/model is using
- [TODO: add link to having a dbt_project.yml and how to manage the SELECT and REFERENCES in dbt for all tables that are needed for the agent]
- remember that views need all underlying tables

***

[Last modified: 2026-07-01]{.note-modified}
