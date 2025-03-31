resource "google_storage_bucket" "magix_storage" {
 name          = var.magix_bucket_name
 location      = "US"
 storage_class = "STANDARD"

 uniform_bucket_level_access = true
}