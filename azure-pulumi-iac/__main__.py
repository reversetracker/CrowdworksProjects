import pulumi

import resource
from aks import kube_config
from aks import subscription_id
from registry import acr

pulumi.export("kubeconfig", kube_config)
pulumi.export("acr_login_server", acr.login_server)
pulumi.export("subscription_id", subscription_id)
pulumi.export("resource_group_id", resource.resource_group.id)
pulumi.export("resource_group_name", resource.resource_group.name)
