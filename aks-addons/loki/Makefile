APP_NAME     := loki
NAMESPACE    := loki
KUBE_CONTEXT := nlp-labs-aksc34c4444

## download dependency files
update:
	helm dependency update

## deployment or override deployment
install:
	helm upgrade \
 	--create-namespace \
	--kube-context ${KUBE_CONTEXT} \
 	--namespace ${NAMESPACE} \
 	--install ${APP_NAME} \
	--debug \
 	-f values.yaml .

## remove deployment
uninstall:
	helm uninstall ${APP_NAME} --namespace ${NAMESPACE}

## diff deployment
diff:
	helm diff \
	--allow-unreleased \
	--kube-context ${KUBE_CONTEXT} \
	--namespace ${NAMESPACE} \
	upgrade ${APP_NAME} \
	-f values.yaml .
