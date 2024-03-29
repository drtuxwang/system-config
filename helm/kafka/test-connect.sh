#!/usr/bin/env bash

if [ $# != 2 ]
then
    echo "Usage $0 <kafka_pod> <kafka_endpoint>"
    exit 1
fi

echo
echo "Sending message (JMX_PORT=$2)..."
echo "kubectl exec -i $1 -- bash"
kubectl exec -i $1 -- bash << EOF
JMX_PORT= kafka-console-producer.sh --broker-list $2 --topic test
`date`: testing
tom
dick
harry
EOF

echo
echo "Receiving message (JMX_PORT=$2)..."
echo "kubectl exec -i $1 -- bash"
kubectl exec -i $1 -- bash << EOF
JMX_PORT= kafka-console-consumer.sh --bootstrap-server $2 --topic test --from-beginning
EOF

