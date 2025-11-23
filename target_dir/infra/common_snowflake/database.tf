resource "snowflake_database" "db1" {
  name                        = upper("${var.env}_DB1")
  comment                     = "DB1（${var.env}）"
  data_retention_time_in_days = var.data_retention_time_in_days
}

resource "snowflake_database" "db2" {
  name                        = upper("${var.env}_DB2")
  comment                     = "DB2（${var.env}）"
  data_retention_time_in_days = var.data_retention_time_in_days
}

