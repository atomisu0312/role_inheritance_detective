variable "role_prefix" {
  type = string
}

variable "database_name" {
  type = string
}

variable "schema_names" {
  type = list(string)
}

variable "comment" {
  default = ""
  type    = string
}