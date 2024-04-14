STACK=internal-nginx
NAMESPACE=default
CONTEXT=arn:aws:eks:ap-northeast-2:576471727047:cluster/eks-cluster-prod

update:  ## download dependency files
	helm dependency update

deploy:  ## deployment
	helm upgrade \
 	--create-namespace \
	--kube-context ${KUBE_CONTEXT} \
 	--namespace ${NAMESPACE} \
 	--install ${APP_NAME} \
 	--debug \
 	-f values.yaml .

diff:  ## diff
	helm diff \
	--kube-context ${KUBE_CONTEXT} \
	--namespace ${NAMESPACE} \
	upgrade ${APP_NAME} \
	-f values.yaml .

uninstall:
	helm uninstall ${APP_NAME} --namespace ${NAMESPACE}
