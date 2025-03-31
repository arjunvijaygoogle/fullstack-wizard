variable "magix_project_id" {
  type = string
  description = "GCP Project id for magix project"
}

variable "my_account" {
  type = string
  description = "my account to give the intial permission to devops account"
}

variable "devops_sa_account_name" {
  type = string
  description = "devops service account name"
}

variable "magix_region" {
  type = string
  description = "GCP Project region for magix project"
}

variable "magix_db_instance" {
  type = string
  description = "instance for magix_db"
}
variable "magix_db" {
  type = string
  description = "db name for magix_db"
}

variable "magix_db_user" {
  type = string
  description = "user for magix_db"
}

variable "magix_db_password" {
  type = string
  sensitive = true
  description = "password for magix_db"
}

variable "magix_db_authorized_nw" {
  type = string
  description = "db authorized networks list"
}

variable "magix_bucket_name" {
  type = string
  description = "magix bucket name"
}