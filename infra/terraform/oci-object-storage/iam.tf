variable "iam_group_name" {
  description = "Grupo IAM com acesso ao bucket."
  type        = string
  default     = "communitylab-assets-rw"
}

resource "oci_identity_group" "rw" {
  compartment_id = var.tenancy_ocid # grupos vivem no tenancy
  name           = var.iam_group_name
  description    = "Leitura/escrita de objetos em ${var.bucket_name}."
  freeform_tags  = var.freeform_tags
}

resource "oci_identity_policy" "rw" {
  compartment_id = var.compartment_ocid
  name           = "${var.bucket_name}-rw"
  description    = "Permite que ${var.iam_group_name} use objetos em ${var.bucket_name}."
  freeform_tags  = var.freeform_tags

  statements = [
    "Allow group ${oci_identity_group.rw.name} to read buckets in compartment id ${var.compartment_ocid} where target.bucket.name = '${var.bucket_name}'",
    "Allow group ${oci_identity_group.rw.name} to manage objects in compartment id ${var.compartment_ocid} where target.bucket.name = '${var.bucket_name}'",
  ]
}

output "iam_group_id" {
  description = "OCID do grupo. Adicione membros pelo Console ou por outro código."
  value       = oci_identity_group.rw.id
}
