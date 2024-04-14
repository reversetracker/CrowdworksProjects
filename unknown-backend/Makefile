ACCOUNT_ID  := 533448761297
APP_NAME    := unknown-backend
VERSION     := $(shell poetry version --short)
REGION      := ap-northeast-2
CONTEXT     := arn:aws:eks:$(REGION):$(ACCOUNT_ID):cluster/your-mother
ECR         := $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com
DOCKER_REPO := "$(ECR)/$(APP_NAME):$(VERSION)"
GIT_BRANCH  := $(shell git rev-parse --abbrev-ref HEAD)

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
	@echo "=> Building $(APP_NAME):$(VERSION)"
	docker buildx build \
	--build-arg GITHUB_TOKEN=$(GITHUB_TOKEN) \
	--platform=linux/amd64 \
	-t $(APP_NAME):$(VERSION) \
	-f Dockerfile .

docker-tag:
	@echo "=> Tagging $(APP_NAME):$(VERSION) as $(DOCKER_REPO)"
	docker tag $(APP_NAME):$(VERSION) $(DOCKER_REPO)

aws-login:
	@echo "=> Logging into AWS Account"
	aws ecr get-login-password --region $(REGION) | \
	docker login --username AWS --password-stdin $(ECR)

aws-push:
	@echo '=> Publishing $(APP_NAME):$(VERSION) to $(DOCKER_REPO)'
	docker push $(DOCKER_REPO)

k8s-deploy:
	cp .env.k8s.$(ENV) helms/$(APP_NAME)/configs/.env.k8s.$(ENV)
	helm upgrade \
	--create-namespace \
	--kube-context $(CONTEXT) \
	--namespace $(APP_NAME)-$(ENV) \
	--install -f helms/$(APP_NAME)/values.$(ENV).yaml $(APP_NAME)-$(ENV) ./helms/$(APP_NAME)/ \
	--set image.tag=$(VERSION) \
	--set image.repository=$(ECR)/$(APP_NAME)

helm-install-prod:
	@echo "=> Deploying $(APP_NAME)-prod to K8s"
	@make k8s-deploy ENV=prod

helm-install-dev:
	@echo "=> Deploying $(APP_NAME)-dev to K8s"
	@make k8s-deploy ENV=dev

helm-uninstall-prod:
	@echo "=> Uninstalling main-backend-prod from K8s"
	helm uninstall $(APP_NAME)-prod -n $(APP_NAME)-prod

helm-uninstall-dev:
	@echo "=> Uninstalling main-backend-dev from K8s"
	helm uninstall $(APP_NAME)-dev -n $(APP_NAME)-dev

snapshot: \
	poetry-version git-commit git-tag git-push

release-prod: \
	docker-build docker-tag aws-login aws-push helm-install-prod

release-dev: \
	docker-build docker-tag aws-login aws-push helm-install-dev