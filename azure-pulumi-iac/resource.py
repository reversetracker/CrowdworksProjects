import pulumi
from pulumi_azure_native import resources

config = pulumi.Config("nlp-aks")
prefix = config.require("prefix")
location = config.get("location")

resource_group = resources.ResourceGroup(f"{prefix}-rg", location=location)
