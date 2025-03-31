resource "google_sql_database_instance" "magix_db_instance" {
  name             = var.magix_db_instance
  region           = var.magix_region # Choose your desired region
  database_version = "POSTGRES_17" # Choose your desired PostgreSQL version
  settings {
    tier    = "db-perf-optimized-N-2"
    edition = "ENTERPRISE_PLUS"
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "allowed-networks" # Replace with a descriptive name
        value = var.magix_db_authorized_nw # Replace with your IP address.  For example, "192.168.1.100/32"
      }
    }
  }
  deletion_protection  = false # Set to true for production.  This prevents accidental deletion.
}

resource "google_sql_database" "magix_db" {
  name     = var.magix_db # Choose your database name
  instance = google_sql_database_instance.magix_db_instance.name
}

resource "google_sql_user" "magix_db_user" {
  name     = var.magix_db_user # Choose your username
  instance = google_sql_database_instance.magix_db_instance.name
  password = var.magix_db_password # Choose a STRONG password.  Do NOT use "mypassword" in production.
}

output "cloudsql_instance_public_ip" {
  value = google_sql_database_instance.magix_db_instance.public_ip_address
}

output "cloudsql_default_database_name" {
  value = google_sql_database.magix_db.name
}

output "cloudsql_default_username" {
  value = google_sql_user.magix_db_user.name
}