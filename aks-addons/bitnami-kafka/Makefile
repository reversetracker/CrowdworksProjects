STACK=kafka
NAMESPACE=kafka
CONTEXT=arn:aws:eks:ap-northeast-2:576471727047:cluster/eks-cluster-prod

update:  ## download dependency files
	helm dependency update

install:  ## deployment
	helm upgrade \
 	--create-namespace \
	--kube-context ${CONTEXT} \
 	--namespace ${NAMESPACE} \
 	--install ${STACK} \
	--debug \
 	-f values.yaml .

uninstall:
	helm uninstall ${STACK} --namespace ${NAMESPACE}

diff:  ## diff
	helm diff \
	--kube-context ${CONTEXT} \
	--namespace ${NAMESPACE} \
	upgrade ${STACK} \
	-f values.yaml .
