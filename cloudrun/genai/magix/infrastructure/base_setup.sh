#!/bin/bash

# Input file name (you can change this if needed)
input_file="variables.tfvars"

# Read the file line by line
while IFS= read -r line; do
  # Check if the line contains an equals sign (indicating a variable assignment)
  if [[ "$line" =~ "=" ]]; then
    # Split the line into variable name and value
    IFS="=" read -r variable_name variable_value <<< "$line"

    # Remove any potential leading/trailing whitespace from variable name and value
    variable_name=$(echo "$variable_name" | tr -d '[:space:]')
    variable_value=$(echo "$variable_value" | tr -d '[:space:]')

    # Remove leading/trailing double quotes and whitespace
    variable_value=$(echo "$variable_value" | sed -e 's/^[[:space:]]*"//' -e 's/"[[:space:]]*$//')

    # Export the variable as an environment variable
    export "$variable_name"="$variable_value"

    # Optional: Print a confirmation message
    echo "Exported: $variable_name=$variable_value"
  fi
done < "$input_file"

echo "Successfully exported variables from $input_file"


sa_email="${devops_sa_account_name}@${magix_project_id}.iam.gserviceaccount.com"

# Check if the service account exists
if gcloud iam service-accounts list --project="${magix_project_id}" --filter="email=${sa_email}" --format="value(email)" | grep -q "${sa_email}"; then
  echo "Service account '${sa_email}' already exists."
else
  echo "Service account '${sa_email}' does not exist. Creating it..."
  
  # Create the service account
  gcloud iam service-accounts create "${devops_sa_account_name}" \
      --display-name="${devops_sa_account_name}" \
      --project="${magix_project_id}"

  # Verify creation
  if [ $? -eq 0 ]; then
    echo "Service account '${sa_email}' created successfully."
  else
    echo "Error creating service account '${sa_email}'. Please check the logs."
    exit 1
  fi
fi

gcloud iam service-accounts add-iam-policy-binding "$sa_email" \
 --member="user:${my_account}" \
 --role="roles/iam.serviceAccountTokenCreator" \

gcloud projects add-iam-policy-binding "${magix_project_id}" \
    --member="serviceAccount:${sa_email}" \
    --role="roles/cloudsql.admin" \
    --condition=None

gcloud projects add-iam-policy-binding "${magix_project_id}" \
    --member="serviceAccount:${sa_email}" \
    --role="roles/iam.serviceAccountTokenCreator" \
    --condition=None

gcloud projects add-iam-policy-binding "${magix_project_id}" \
    --member="serviceAccount:${sa_email}" \
    --role="roles/storage.admin" \
    --condition=None
    
export GOOGLE_IMPERSONATE_SERVICE_ACCOUNT=$sa_email

terraform init
terraform plan --var-file variables.tfvars
terraform apply --var-file variables.tfvars --auto-approve



