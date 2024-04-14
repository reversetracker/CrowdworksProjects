APP_NAME     := external-nginx
NAMESPACE    := default
KUBE_CONTEXT := nlp-labs-dev-aks70e28d5b

update:  ## download dependency files
	helm dependency update

install:  ## deployment
	helm upgrade \
 	--create-namespace \
	--kube-context ${KUBE_CONTEXT} \
 	--namespace ${NAMESPACE} \
 	--install ${APP_NAME} \
 	--debug \
 	-f values.yaml .

uninstall:
	helm uninstall ${APP_NAME} --namespace ${NAMESPACE}

diff:  ## diff
	helm diff \
	--allow-unreleased \
	--kube-context ${KUBE_CONTEXT} \
	--namespace ${NAMESPACE} \
	upgrade ${APP_NAME} \
	-f values.yaml .
