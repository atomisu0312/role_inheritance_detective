resource "snowflake_database_role" "read_role" {
  database = var.database_name
  name     = "${var.role_prefix}_R_ROLE"
  comment  = "read role"
}

resource "snowflake_database_role" "write_role" {
  database = var.database_name
  name     = "${var.role_prefix}_RW_ROLE"
  comment  = "read/write role"
}