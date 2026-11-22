output "namespace" {
  description = "Object Storage namespace."
  value       = data.oci_objectstorage_namespace.this.namespace
}

output "bucket_name" {
  description = "Bucket name."
  value       = oci_objectstorage_bucket.assets.name
}

output "s3_endpoint" {
  description = "Endpoint for the n8n S3 credential (enable Force Path Style)."
  value       = "https://${data.oci_objectstorage_namespace.this.namespace}.compat.objectstorage.${var.region}.oraclecloud.com"
}