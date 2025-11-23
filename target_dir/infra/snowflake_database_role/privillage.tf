#-----------------------------------------------------------
# read role
#-----------------------------------------------------------

#-----------------------------------------------------------
# database privileges
#-----------------------------------------------------------

resource "snowflake_grant_privileges_to_database_role" "db" {
  provider           = snowflake.securityadmin
  privileges         = ["USAGE"]
  database_role_name = "${snowflake_database_role.read_role.database}.${snowflake_database_role.read_role.name}"
  on_database        = snowflake_database_role.read_role.database
}

#-----------------------------------------------------------
# schema privileges
#-----------------------------------------------------------
resource "snowflake_grant_privileges_to_database_role" "schema_read" {
  provider           = snowflake.securityadmin
  for_each           = { for schema in var.schema_names : schema => schema }
  privileges         = ["USAGE"]
  database_role_name = "${snowflake_database_role.read_role.database}.${snowflake_database_role.read_role.name}"
  on_schema {
    schema_name = "${snowflake_database_role.read_role.database}.${each.value}"
  }
}

#-----------------------------------------------------------
# schema object future privileges
#-----------------------------------------------------------
resource "snowflake_grant_privileges_to_database_role" "table_read" {
  provider           = snowflake.securityadmin
  for_each           = { for schema in var.schema_names : schema => schema }
  privileges         = ["SELECT"]
  database_role_name = "${snowflake_database_role.read_role.database}.${snowflake_database_role.read_role.name}"
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "${snowflake_database_role.read_role.database}.${each.value}"
    }
  }
}

resource "snowflake_grant_privileges_to_database_role" "view_read" {
  provider           = snowflake.securityadmin
  for_each           = { for schema in var.schema_names : schema => schema }
  privileges         = ["SELECT"]
  database_role_name = "${snowflake_database_role.read_role.database}.${snowflake_database_role.read_role.name}"
  on_schema_object {
    future {
      object_type_plural = "VIEWS"
      in_schema          = "${snowflake_database_role.read_role.database}.${each.value}"
    }
  }
}

resource "snowflake_grant_privileges_to_database_role" "stage" {
  provider           = snowflake.securityadmin
  for_each           = { for schema in var.schema_names : schema => schema }
  privileges         = ["USAGE"]
  database_role_name = "${snowflake_database_role.read_role.database}.${snowflake_database_role.read_role.name}"
  on_schema_object {
    future {
      object_type_plural = "STAGES"
      in_schema          = "${snowflake_database_role.read_role.database}.${each.value}"
    }
  }
}

resource "snowflake_grant_privileges_to_database_role" "file_format" {
  provider           = snowflake.securityadmin
  for_each           = { for schema in var.schema_names : schema => schema }
  privileges         = ["USAGE"]
  database_role_name = "${snowflake_database_role.read_role.database}.${snowflake_database_role.read_role.name}"
  on_schema_object {
    future {
      object_type_plural = "FILE FORMATS"
      in_schema          = "${snowflake_database_role.read_role.database}.${each.value}"
    }
  }
}

#-----------------------------------------------------------
# write role
#-----------------------------------------------------------
#-----------------------------------------------------------
# read privileges
#-----------------------------------------------------------

# read roleを継承
resource "snowflake_grant_database_role" "read" {
  provider                  = snowflake.securityadmin
  database_role_name        = "${snowflake_database_role.write_role.database}.${snowflake_database_role.write_role.name}"
  parent_database_role_name = "${snowflake_database_role.write_role.database}.${snowflake_database_role.read_role.name}"
}

#-----------------------------------------------------------
# schema privileges
#-----------------------------------------------------------
resource "snowflake_grant_privileges_to_database_role" "schema_write" {
  provider = snowflake.securityadmin
  for_each = { for schema in var.schema_names : schema => schema }
  privileges = [
    "CREATE TABLE",
    "CREATE VIEW",
  ]
  database_role_name = "${snowflake_database_role.write_role.database}.${snowflake_database_role.write_role.name}"
  on_schema {
    schema_name = "${snowflake_database_role.write_role.database}.${each.value}"
  }
}

#-----------------------------------------------------------
# schema object future privileges
#-----------------------------------------------------------
resource "snowflake_grant_privileges_to_database_role" "table_write" {
  provider = snowflake.securityadmin
  for_each = { for schema in var.schema_names : schema => schema }
  privileges = [
    "INSERT",
    "UPDATE",
    "TRUNCATE",
    "DELETE",
  ]
  database_role_name = "${snowflake_database_role.write_role.database}.${snowflake_database_role.write_role.name}"
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "${snowflake_database_role.write_role.database}.${each.value}"
    }
  }
}
