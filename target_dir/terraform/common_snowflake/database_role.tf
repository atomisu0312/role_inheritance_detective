locals {
  # fivetranはterraform管理でないのでここでベタ書き
  additional_ex0_schema_names = {
    "dev" : [
      "DEV_EX01",
      "DEV_EX02",
    ],
    "stg" : [
      "STG_EX01",
      "STG_EX02",
    ],
    "prod" : [
      "PROD_EX01",
      "PROD_EX02",
    ],
  }
}
module "db1_role" {
  providers = {
    snowflake               = snowflake
    snowflake.securityadmin = snowflake.securityadmin
  }
  source        = "../snowflake_database_role"
  role_prefix   = upper("${var.env}_DB1")
  database_name = snowflake_database.db1.name
  schema_names = [
    snowflake_schema.schema_11.name,
    snowflake_schema.schema_12.name,
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
    snowflake_schema.schema_21.name,
  ]
}