# OCI Object Storage (Terraform)

Infraestrutura como código para o bucket descrito em
[`docs/specs/oci-object-storage-n8n.md`](../../../docs/specs/oci-object-storage-n8n.md):

- Região `sa-saopaulo-1`
- Bucket `communitylab-assets`, privado (`NoPublicAccess`), camada Standard
- Versionamento habilitado (protege contra a sobrescrita do objeto de caminho fixo citada na especificação)

- IAM: grupo `communitylab-assets-rw` e política restrita a este bucket (`read buckets` + `manage objects`)

Usuários e chaves compatíveis com S3 **não** são gerenciados aqui: adicione os membros ao grupo pelo Console
(ou por outro código). Para aplicar, quem executa o Terraform precisa de permissão para gerenciar grupos e
políticas no tenancy.

## Uso

```bash
cd infra/terraform/oci-object-storage
cp terraform.tfvars.example terraform.tfvars   # defina os OCIDs do tenancy e do compartimento
terraform init
terraform plan
terraform apply
```

A autenticação usa `~/.oci/config` (perfil definido em `oci_config_profile`).

As saídas `s3_endpoint` e `namespace` alimentam a credencial S3 do n8n (seção 4 da especificação).

## Adotando o bucket existente

O bucket já existe. Para gerenciá-lo em vez de criar um novo, importe-o antes do `apply`:

```bash
terraform import oci_objectstorage_bucket.assets n/<namespace>/b/communitylab-assets
terraform plan   # revise: não deve mostrar mudanças, ou apenas tags/versionamento
```

O namespace é `grue2tm7tuaq`, conforme a especificação. Garanta que `compartment_ocid` seja o compartimento
que realmente contém o bucket; caso contrário, o plano tentará movê-lo.
