APP_NAME    		 := elasticsearch
VERSION     		 := 8.5.1.rc1
REGION	    		 := koreasouth
NAMESPACE   		 := elasticsearch
REGISTRY    		 := akscontainerregistry73385a42.azurecr.io
REPOSITORY           := $(REGISTRY)/$(APP_NAME)
KUBE_CONTEXT         :=
AZURE_RESOURCE_GROUP := nlp-labs-rgac40d810

docker-build:
	@echo "=> Building $(APP_NAME):$(VERSION)"
	docker buildx build \
	--platform=linux/amd64 \
	-t $(APP_NAME):$(VERSION) \
	-f Dockerfile .

docker-tag:
	@echo "=> Tagging $(APP_NAME):$(VERSION) as $(REPOSITORY):$(VERSION)"
	docker tag $(APP_NAME):$(VERSION) $(REPOSITORY):$(VERSION)

azure-login:
	@echo "=> Logging into Azure Container Registry"
	az acr login --name $(shell echo $(REGISTRY) | cut -d. -f1)

azure-push:
	@echo '=> Publishing $(APP_NAME):$(VERSION) to $(REPOSITORY):$(VERSION)'
	docker push $(REPOSITORY):$(VERSION)

k8s-deploy:
	helm upgrade \
	--debug \
	--create-namespace \
	--kube-context $(KUBE_CONTEXT) \
	--namespace $(APP_NAME)-$(ENV) \
	--install $(APP_NAME)-$(ENV) \
	-f values.$(ENV).yaml .

helm-install-prod:
	@echo "=> Deploying $(APP_NAME)-prod to K8s"
	@make k8s-deploy ENV=prod

helm-install-dev:
	@echo "=> Deploying $(APP_NAME)-dev to K8s"
	@make k8s-deploy ENV=dev

helm-uninstall-prod:
	@echo "=> Uninstalling $(APP_NAME)-prod from K8s"
	helm uninstall $(APP_NAME)-prod -n $(APP_NAME)-prod

helm-uninstall-dev:
	@echo "=> Uninstalling $(APP_NAME)-dev from K8s"
	helm uninstall $(APP_NAME)-dev -n $(APP_NAME)-dev

release-prod: \
	docker-build docker-tag azure-login azure-push helm-install-prod

release-dev: \
	docker-build docker-tag azure-login azure-push helm-install-dev

# Watch Cluster Members
watch_all_cluster_members_come_up_prod:
	kubectl get pods --namespace=$(NAMESPACE)-prod -l app=elasticsearch-master -w

# Retrieve Elastic User Password
retrieve_elastic_user_password_prod:
	kubectl get secrets --namespace=$(NAMESPACE)-prod elasticsearch-master-credentials -ojsonpath='{.data.password}' | base64 -d
