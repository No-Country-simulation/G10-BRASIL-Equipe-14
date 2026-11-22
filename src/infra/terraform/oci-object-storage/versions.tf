terraform {
  required_version = ">= 1.5.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 6.0"
    }
  }
}

# Authenticates with ~/.oci/config using the chosen profile.
provider "oci" {
  region              = var.region
  config_file_profile = var.oci_config_profile
}