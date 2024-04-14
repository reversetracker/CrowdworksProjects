APP_NAME             := miraeasset
FRONTEND_APPNAME     := $(APP_NAME)-frontend
BACKEND_APPNAME      := $(APP_NAME)-backend
VERSION              := $(shell poetry version --short)
REGION               := koreacentral
REGISTRY             := nlplabsakscontainerregistry48698c37.azurecr.io
GIT_BRANCH           := $(shell git rev-parse --abbrev-ref HEAD)
KUBE_CONTEXT         := nlp-labs-dev-aks70e28d5b
GITHUB_TOKEN         := $(shell cat .github_token)

show-version:
	@echo "=> New version: `poetry version --short`"

poetry-version: ## Increase the poetry version based on the SNAPSHOT_VERSION value (major, minor, or patch).
ifeq ($(SNAPSHOT_VERSION),minor)
	@echo "=> Incrementing minor version using poetry"
	@poetry version minor
else ifeq ($(SNAPSHOT_VERSION),major)
	@echo "=> Incrementing major version using poetry"
	@poetry version major
else
	@echo "=> Incrementing patch version using poetry"
	@poetry version patch
endif
	@make show-version

git-commit:
	@git add .
	@git commit -m "Update version to `poetry version --short`"

git-tag:
	@git tag -a `poetry version --short` -m "Release `poetry version --short`"

git-push:
	@echo "GIT Pushing => $(GIT_BRANCH)"
	@git push origin $(GIT_BRANCH) --tags

docker-build:
	@echo "=> Building $(FRONTEND_APPNAME):$(VERSION)"
	docker buildx build \
	--platform=linux/amd64 \
	-t $(FRONTEND_APPNAME):$(VERSION) \
	-f dockers/streamlit.Dockerfile .
	@echo "=> Building $(BACKEND_APPNAME):$(VERSION)"
	docker buildx build \
	--platform=linux/amd64 \
	-t $(BACKEND_APPNAME):$(VERSION) \
	-f dockers/fastapi.Dockerfile .

docker-tag:
	@echo "=> Tagging $(FRONTEND_APPNAME):$(VERSION) as $(REGISTRY)/$(FRONTEND_APPNAME):$(VERSION)"
	docker tag $(FRONTEND_APPNAME):$(VERSION) $(REGISTRY)/$(FRONTEND_APPNAME):$(VERSION)

	@echo "=> Tagging $(BACKEND_APPNAME):$(VERSION) as $(REGISTRY)/$(BACKEND_APPNAME):$(VERSION)"
	docker tag $(BACKEND_APPNAME):$(VERSION) $(REGISTRY)/$(BACKEND_APPNAME):$(VERSION)

azure-login:
	@echo "=> Logging into Azure Container Registry"
	az acr login --name $(shell echo $(REGISTRY) | cut -d. -f1)

azure-push:
	@echo '=> Publishing $(FRONTEND_APPNAME):$(VERSION) to $(REGISTRY)/$(FRONTEND_APPNAME):$(VERSION)'
	docker push $(REGISTRY)/$(FRONTEND_APPNAME):$(VERSION)
	@echo '=> Publishing $(BACKEND_APPNAME):$(VERSION) to $(REGISTRY)/$(BACKEND_APPNAME):$(VERSION)'
	docker push $(REGISTRY)/$(BACKEND_APPNAME):$(VERSION)

k8s-deploy:
	@echo "=> Deploying $(FRONTEND_APPNAME)-$(ENV) to K8s"
	helm upgrade \
	--create-namespace \
	--kube-context $(KUBE_CONTEXT) \
	--namespace $(APP_NAME)-$(ENV) \
	--install -f helms/$(FRONTEND_APPNAME)/values.$(ENV).yaml $(FRONTEND_APPNAME)-$(ENV) ./helms/$(FRONTEND_APPNAME)/ \
	--set image.tag=$(VERSION) \
	--set image.repository=$(REGISTRY)/$(FRONTEND_APPNAME)

	@echo "=> Deploying $(BACKEND_APPNAME)-$(ENV) to K8s"
	helm upgrade \
	--create-namespace \
	--kube-context $(KUBE_CONTEXT) \
	--namespace $(APP_NAME)-$(ENV) \
	--install -f helms/$(BACKEND_APPNAME)/values.$(ENV).yaml $(BACKEND_APPNAME)-$(ENV) ./helms/$(BACKEND_APPNAME)/ \
	--set image.tag=$(VERSION) \
	--set image.repository=$(REGISTRY)/$(BACKEND_APPNAME)


helm-install-prod:
	@echo "=> Updating config from .env files"
	@if kubectl get configmap $(APP_NAME)-prod-config -n $(APP_NAME)-prod > /dev/null 2>&1; then \
		echo "Deleting existing ConfigMap..."; \
		kubectl delete configmap $(APP_NAME)-prod-config -n $(APP_NAME)-prod; \
	else \
		echo "ConfigMap does not exist, skipping deletion."; \
	fi
	@if kubectl get namespace $(APP_NAME)-prod > /dev/null 2>&1; then \
		echo "Namespace already exists..."; \
	else \
		echo "Creating namespace $(APP_NAME)-prod..."; \
		kubectl create namespace $(APP_NAME)-prod; \
	fi
	@kubectl create configmap $(APP_NAME)-prod-config --from-env-file=.env.k8s.prod -n $(APP_NAME)-prod
	@echo "=> Deploying $(APP_NAME)-prod to K8s"
	@make k8s-deploy ENV=prod

helm-install-dev:
	@echo "=> Updating config from .env files"
	@if kubectl get configmap $(APP_NAME)-dev-config -n $(APP_NAME)-dev > /dev/null 2>&1; then \
		echo "Deleting existing ConfigMap..."; \
		kubectl delete configmap $(APP_NAME)-dev-config -n $(APP_NAME)-dev; \
	else \
		echo "ConfigMap does not exist, skipping deletion."; \
	fi
	@if kubectl get namespace $(APP_NAME)-dev > /dev/null 2>&1; then \
		echo "Namespace already exists..."; \
	else \
		echo "Creating namespace $(APP_NAME)-dev..."; \
		kubectl create namespace $(APP_NAME)-dev; \
	fi
	@kubectl create configmap $(APP_NAME)-dev-config --from-env-file=.env.k8s.dev -n $(APP_NAME)-dev
	@echo "=> Deploying $(APP_NAME)-dev to K8s"
	@make k8s-deploy ENV=dev

helm-uninstall-prod:
	@echo "=> Uninstalling $(APP_NAME)-prod from K8s"
	helm uninstall $(FRONTEND_APPNAME)-prod -n $(APP_NAME)-prod
	helm uninstall $(BACKEND_APPNAME)-prod -n $(APP_NAME)-prod

helm-uninstall-dev:
	@echo "=> Uninstalling $(APP_NAME)-dev from K8s"
	helm uninstall $(FRONTEND_APPNAME)-dev -n $(APP_NAME)-dev
	helm uninstall $(BACKEND_APPNAME)-dev -n $(APP_NAME)-dev

snapshot: \
	poetry-version git-commit git-tag git-push

release-prod: \
	docker-build docker-tag azure-login azure-push helm-install-prod

release-dev: \
	docker-build docker-tag azure-login azure-push helm-install-dev

gunicorn-v1:
	@echo "Starting server..."
	gunicorn rag_backend.apps.v1:app -c gunicorn.conf.py

locust:
	@echo "Starting locust..."
	locust -f locust_conf.py --host=http://0.0.0.0:80
