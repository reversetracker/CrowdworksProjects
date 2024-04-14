from pulumi_azure_native import containerregistry

from resource import resource_group

acr = containerregistry.Registry(
    f"nlpLabsAksContainerRegistry",
    resource_group_name=resource_group.name,
    sku=containerregistry.SkuArgs(
        name=containerregistry.SkuName.BASIC,
    ),
    admin_user_enabled=True,
)
