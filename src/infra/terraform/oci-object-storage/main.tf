data "oci_objectstorage_namespace" "this" {
  compartment_id = var.tenancy_ocid
}

# Private bucket (spec: "Política de acesso: privado", "Camada: Standard").
resource "oci_objectstorage_bucket" "assets" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.this.namespace
  name           = var.bucket_name

  access_type   = "NoPublicAccess"
  storage_tier  = var.storage_tier
  versioning    = var.versioning
  freeform_tags = var.freeform_tags
}