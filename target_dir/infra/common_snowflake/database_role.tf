module "db1_role" {
  providers = {
    snowflake               = snowflake
    snowflake.securityadmin = snowflake.securityadmin
  }
  source        = "../snowflake_database_role"
  role_prefix   = upper("${var.env}_DB1")
  database_name = snowflake_database.db1.name
  schema_names = [
    snowflake_schema.db1.name,
  ]
}

module "db2_role" {
  providers = {
    snowflake               = snowflake
    snowflake.securityadmin = snowflake.securityadmin
  }
  source        = "../snowflake_database_role"
  role_prefix   = upper("${var.env}_DB2")
  database_name = snowflake_database.db2.name
  schema_names = [
    snowflake_schema.db2.name,
  ]
}