resource "snowflake_schema" "schema_01" {
  database                    = snowflake_database.db1.name
  name                        = "SCHEMA_01"
  comment                     = "SCHEMA_01スキーマ（${var.env}）"
  data_retention_time_in_days = var.data_retention_time_in_days
  is_transient                = false
  with_managed_access         = false
}

resource "snowflake_schema" "schema_11" {
  database                    = snowflake_database.db1.name
  name                        = "SCHEMA_11"
  comment                     = "SCHEMA_11スキーマ（${var.env}）"
  data_retention_time_in_days = var.data_retention_time_in_days
  is_transient                = false
  with_managed_access         = false
}

resource "snowflake_schema" "schema_12" {
  database                    = snowflake_database.db1.name
  name                        = "SCHEMA_12"
  comment                     = "SCHEMA_12スキーマ（${var.env}）"
  data_retention_time_in_days = var.data_retention_time_in_days
  is_transient                = false
  with_managed_access         = false
}

resource "snowflake_schema" "schema_21" {
  database                    = snowflake_database.db2.name
  name                        = "SCHEMA_21"
  comment                     = "SCHEMA_21スキーマ（${var.env}）"
  data_retention_time_in_days = var.data_retention_time_in_days
  is_transient                = false
  with_managed_access         = false
}
