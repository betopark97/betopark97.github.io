# RBAC

## Snowflake RBAC Best Practices

### Core System Roles

> **WARNING:**
>
> \- **Should do:** Account-level settings, billing/credit management, cross-region config, `CREATE SNOWFLAKE INTELLIGENCE`, enabling features.  
> - **Should NOT do:** Create day-to-day objects (databases, tables, warehouses), run automated scripts.  
> **Best practice:** Assign to 2+ users, require MFA, never set as anyone’s default role.

> **IMPORTANT:**
>
> \- **Creates/manages:** Privilege grants on all objects (has `MANAGE GRANTS`), role-to-role grants, role-to-user grants.  
> - **Inherits:** `USERADMIN`. **Use for:** `GRANT ... TO ROLE`, future grants, managed access schema grants.

> **NOTE:**
>
> \- **Creates:** Users (`CREATE USER`) and roles (`CREATE ROLE`).  
> - **Use for:** Provisioning new users, creating custom access/functional roles.

> **TIP:**
>
> \- **Creates:** Warehouses, databases, schemas, and all database objects.  
> - **Clarification:** While `SYSADMIN` can create these, **any role** with `CREATE` privileges can too.  
> - **Best practice:** All custom roles (like those used by dbt) must roll up to `SYSADMIN` so it inherits ownership and can manage all objects in the account.

## Custom Domain/Team Roles

Snowflake recommends a **two-tier pattern** to keep permissions scalable.

| Layer | Example | Purpose |
|----|----|----|
| **Access roles** | `db_sales_r`, `db_sales_rw` | Grant specific privileges on specific objects. |
| **Functional roles** | `analyst`, `data_engineer` | Bundle access roles by business function; granted to users. |

## Handling dbt & Automation Roles

In practice, you don’t run dbt as `SYSADMIN`. Instead, you create a dedicated role and “wire” it into the hierarchy.

### Example Setup

``` numberSource
-- 1. USERADMIN creates the role
CREATE ROLE DBT_ROLE;

-- 2. SECURITYADMIN grants object creation privileges
GRANT USAGE ON DATABASE my_db TO ROLE DBT_ROLE;

GRANT USAGE ON WAREHOUSE my_wh TO ROLE DBT_ROLE;

GRANT CREATE SCHEMA ON DATABASE my_db TO ROLE DBT_ROLE;

GRANT ALL ON SCHEMA my_db.my_schema TO ROLE DBT_ROLE;

-- 3. THE KEY STEP: Wire it into the hierarchy
GRANT ROLE DBT_ROLE TO ROLE SYSADMIN;
```

> **WARNING:**

## Role Hierarchy & Wiring

### The Relationship Chain

``` mermaid
graph LR
    AR[Access Roles] --> FR[Functional Roles]
    DBT[DBT_ROLE] --> SA[SYSADMIN]
    FR --> SA
    SA --> AA[ACCOUNTADMIN]
```

### Responsibility Matrix

- **USERADMIN:** Creates the custom roles.

- **SECURITYADMIN:** Grants privileges to access roles and wires functional roles to `SYSADMIN`.

- **Users/Service Accounts:** Assigned functional roles or tool-specific roles (like `DBT_ROLE`).

> **TIP:**

------------------------------------------------------------------------

Last modified: 2026-06-23

Back to top
