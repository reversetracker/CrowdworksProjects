import base64

import pulumi
import pulumi_azuread as azuread
import pulumi_tls as tls
from pulumi import ResourceOptions
from pulumi_azure_native import containerservice, network, authorization
from pulumi_kubernetes import Provider

from resource import resource_group


def camel_case(s):
    parts = s.split("-")
    camel_case_parts = [parts[0]] + [p.capitalize() for p in parts[1:]]
    return "".join(camel_case_parts)


config = pulumi.Config("nlp-aks")
prefix = config.require("prefix")

subscription_id = authorization.get_client_config().subscription_id

ad_app = azuread.Application(
    f"{prefix}-aks",
    display_name="aks",
)

ad_sp = azuread.ServicePrincipal(
    camel_case(f"{prefix}-aks-sp"),
    application_id=ad_app.application_id,
)

ad_sp_password = azuread.ServicePrincipalPassword(
    camel_case(f"{prefix}-aks-sp-password"),
    service_principal_id=ad_sp.id,
    end_date="2099-01-01T00:00:00Z",
)

ssh_key = tls.PrivateKey(
    f"{prefix}-ssh-key",
    algorithm="RSA",
    rsa_bits=4096,
)

vnet = network.VirtualNetwork(
    f"{prefix}-vnet",
    location=resource_group.location,
    resource_group_name=resource_group.name,
    address_space={
        "address_prefixes": ["10.0.0.0/8"],
    },
)

subnet_1 = network.Subnet(
    f"{prefix}-subnet-1",
    resource_group_name=resource_group.name,
    address_prefix="10.1.0.0/16",
    virtual_network_name=vnet.name,
)

subnet_2 = network.Subnet(
    f"{prefix}-subnet-2",
    resource_group_name=resource_group.name,
    address_prefix="10.2.0.0/16",
    virtual_network_name=vnet.name,
)

subnet_assignment_1 = authorization.RoleAssignment(
    f"{prefix}-subnet-permissions-1",
    principal_id=ad_sp.id,
    principal_type=authorization.PrincipalType.SERVICE_PRINCIPAL,
    role_definition_id=f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/4d97b98b-1d4f-4787-a291-c67834d212e7",
    scope=subnet_1.id,
)

subnet_assignment_2 = authorization.RoleAssignment(
    f"{prefix}-subnet-permissions-2",
    principal_id=ad_sp.id,
    principal_type=authorization.PrincipalType.SERVICE_PRINCIPAL,
    role_definition_id=f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/4d97b98b-1d4f-4787-a291-c67834d212e7",
    scope=subnet_2.id,
)

aks = containerservice.ManagedCluster(
    f"{prefix}-aks",
    location=resource_group.location,
    resource_group_name=resource_group.name,
    kubernetes_version="1.29.0",
    dns_prefix="dns",
    agent_pool_profiles=[
        {
            "name": "systempool",
            "mode": "System",
            "count": 1,
            "vm_size": "Standard_B4als_v2",
            "os_type": containerservice.OSType.LINUX,
            "max_pods": 110,
            "vnet_subnet_id": subnet_1.id,
            "enable_auto_scaling": True,
            "os_disk_size_gb": 100,
            "min_count": 1,
            "max_count": 10,
            "type": "VirtualMachineScaleSets",
        }
    ],
    linux_profile={
        "admin_username": "superuser",
        "ssh": {
            "public_keys": [
                {
                    "key_data": ssh_key.public_key_openssh,
                }
            ],
        },
    },
    service_principal_profile={
        "client_id": ad_app.application_id,
        "secret": ad_sp_password.value,
    },
    enable_rbac=True,
    network_profile={
        "network_plugin": "azure",
        "service_cidr": "10.10.0.0/16",
        "dns_service_ip": "10.10.0.10",
        "docker_bridge_cidr": "172.17.0.1/16",
    },
    opts=ResourceOptions(
        depends_on=[
            subnet_assignment_1,
            subnet_assignment_2,
        ]
    ),
    auto_scaler_profile=containerservice.ManagedClusterPropertiesAutoScalerProfileArgs(
        scale_down_delay_after_add="5m",
        scan_interval="20s",
    ),
)

standard_pool_1 = containerservice.AgentPool(
    "generalpool1",
    agent_pool_name="generalpool1",
    resource_name_=aks.name,
    resource_group_name=resource_group.name,
    mode="User",
    count=0,
    vm_size="Standard_B4als_v2",
    os_type=containerservice.OSType.LINUX,
    max_pods=110,
    vnet_subnet_id=subnet_1.id,
    enable_auto_scaling=True,
    os_disk_size_gb=100,
    min_count=0,
    max_count=10,
    type="VirtualMachineScaleSets",
)

gpu_pool = containerservice.AgentPool(
    "gpupool1",
    agent_pool_name="gpupool1",
    resource_name_=aks.name,
    resource_group_name=resource_group.name,
    mode="User",
    count=0,
    vm_size="Standard_NC16as_T4_v3",  # "Standard_NC24ads_A100_v4",
    os_type=containerservice.OSType.LINUX,
    max_pods=110,
    vnet_subnet_id=subnet_1.id,
    enable_auto_scaling=True,
    os_disk_size_gb=100,
    min_count=0,
    max_count=10,
    node_taints=["gpu=true:NoSchedule"],
    type="VirtualMachineScaleSets",
    tags={
        "SkipGPUDriverInstall": "true",
    },
)

kube_creds = pulumi.Output.all(resource_group.name, aks.name).apply(
    lambda args: containerservice.list_managed_cluster_user_credentials(
        resource_group_name=args[0],
        resource_name=args[1],
    )
)

kube_config = kube_creds.kubeconfigs[0].value.apply(
    lambda enc: base64.b64decode(enc).decode()
)

custom_provider = Provider("inflation-provider", kubeconfig=kube_config)
