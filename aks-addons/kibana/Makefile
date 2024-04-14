NAMESPACE     := elasticsearch
STACK         := kibana

diff-prod:
	@echo "=> Running Helm Diff"
	helm diff upgrade $(STACK) --namespace $(NAMESPACE)-prod -f values.prod.yaml

uninstall-prod:
	@echo "=> Running Helm Uninstall"
	helm uninstall $(STACK) --namespace $(NAMESPACE)-prod

update-prod: uninstall-prod install-prod

# Kubernetes Operations
watch-members-prod:
	@echo "=> Watching Cluster Members"
	kubectl get pods --namespace=$(NAMESPACE)-prod -l app=elasticsearch-master -w

retrieve-password-prod:
	@echo "=> Retrieving Elastic User Password"
	kubectl get secrets --namespace=$(NAMESPACE)-prod elasticsearch-master-credentials -ojsonpath='{.data.password}' | base64 -d

## DO NOT USE 'INSTALL' BUT DO USE 'UPDATE' ##
## DO NOT USE 'INSTALL' BUT DO USE 'UPDATE' ##
## DO NOT USE 'INSTALL' BUT DO USE 'UPDATE' ##
## DO NOT USE 'INSTALL' BUT DO USE 'UPDATE' ##
## DO NOT USE 'INSTALL' BUT DO USE 'UPDATE' ##
## DO NOT USE 'INSTALL' BUT DO USE 'UPDATE' ##
## DO NOT USE 'INSTALL' BUT DO USE 'UPDATE' ##

install-prod:
	@echo "=> Installing kibana-prod using Helm"
	helm upgrade \
	--debug \
	--create-namespace \
	--install $(STACK) \
	--namespace $(NAMESPACE)-prod \
	-f values.prod.yaml .

## DO NOT USE THIS BUT DO USE 'UPDATE' ##
## DO NOT USE THIS BUT DO USE 'UPDATE' ##
## DO NOT USE THIS BUT DO USE 'UPDATE' ##
## DO NOT USE THIS BUT DO USE 'UPDATE' ##
## DO NOT USE THIS BUT DO USE 'UPDATE' ##
## DO NOT USE THIS BUT DO USE 'UPDATE' ##
## DO NOT USE THIS BUT DO USE 'UPDATE' ##
