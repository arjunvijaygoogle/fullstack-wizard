locals {
  devops_service_account_email = "${var.devops_sa_account_name}@${var.magix_project_id}.iam.gserviceaccount.com"
}

# provider "google" {
#   alias = "impersonation"
#   scopes = [
#     "https://www.googleapis.com/auth/cloud-platform",
#     "https://www.googleapis.com/auth/userinfo.email",
#   ]

# }


# #receive short-lived access token
# data "google_service_account_access_token" "default" {
#   provider               = google.impersonation
#   target_service_account = local.devops_service_account_email
#   scopes                 = ["cloud-platform", "userinfo-email"]
#   lifetime               = "3600s"

# }


# # default provider to use the the token
# provider "google" {
#   project         = var.magix_project_id
#   region          = var.magix_region
#   access_token    = data.google_service_account_access_token.default.access_token
#   request_timeout = "60s"
# }

provider "google" {
  project     = var.magix_project_id
  region      = "us-central1"
}