locals {
  data_lake_bucket = "houses-data-bucket"
}

variable "profile" {
  type = string
  description = ""
  default = "tf1.2.2"
}

variable "project" {
  type = string
  description = ""
  default = "1232742434897"
}

variable "region" {
  type = string
  description = "Region for AWS resources."
  default = "sa-east-1"
}

variable "acl" {
  type = string
  description = ""
  default = "private"
}

variable "db_password" {
  type = string
  description = ""
  default = "1231231Aa"
}

