variable "region" {
  description = "OCI region (spec section 2)."
  type        = string
  default     = "sa-saopaulo-1"
}

variable "oci_config_profile" {
  description = "Profile name in ~/.oci/config."
  type        = string
  default     = "DEFAULT"
}

variable "tenancy_ocid" {
  description = "Tenancy OCID, used to resolve the Object Storage namespace."
  type        = string
}

variable "compartment_ocid" {
  description = "Compartment OCID that will own the bucket."
  type        = string
}

variable "bucket_name" {
  description = "Bucket name."
  type        = string
  default     = "communitylab-assets"
}

variable "storage_tier" {
  description = "Standard or Archive. The spec uses Standard."
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Standard", "Archive"], var.storage_tier)
    error_message = "storage_tier must be Standard or Archive."
  }
}

variable "versioning" {
  description = "Object versioning. Enabled mitigates the fixed-object-key overwrite noted in spec section 3.3."
  type        = string
  default     = "Enabled"

  validation {
    condition     = contains(["Enabled", "Disabled", "Suspended"], var.versioning)
    error_message = "versioning must be Enabled, Disabled or Suspended."
  }
}

variable "freeform_tags" {
  description = "Tags applied to the bucket."
  type        = map(string)
  default = {
    project = "communitylab"
    team    = "equipe-14-g10"
  }
}