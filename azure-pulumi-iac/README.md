# Troubleshooting
1. AKS image pull permission is not currently set up by Pulumi.
2. The command below must be executed after the initial `pulumi up`.

```shell
az aks update -n nlp-labs-dev-aks70e28d5b -g nlp-labs-dev-rg77d4ce44 --attach-acr nlplabsakscontainerregistry48698c37
az aks check-acr --resource-group nlp-labs-dev-rg77d4ce44 --name nlp-labs-dev-aks70e28d5b --acr nlplabsakscontainerregistry48698c37.azurecr.io
```
