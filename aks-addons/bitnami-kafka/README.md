
1. install client pod
```shell
kubectl run kafka-client \
    --restart='Never' \
    --image docker.io/bitnami/kafka:3.4.0-debian-11-r2 \
    --namespace kafka \
    --command \
    -- sleep infinity
kubectl exec --tty -i kafka-client --namespace kafka -- bash
```

2. produce message
```shell
kafka-console-producer.sh \
    --broker-list kafka.kafka.svc.cluster.local:9092 \
    --topic test
```

3. consume message
```shell
kafka-console-consumer.sh \
    --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
    --topic test \
    --from-beginning
```

4. delete topic
```shell
kafka-topics.sh \
    - zookeeper \
    --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
    --delete \
    --topic `THE_TOPIC_NAME`
```