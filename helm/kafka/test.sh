#!/bin/bash

if [ $# != 2 ]
then
    echo "Usage $0 <kafka_pod> <kafka_endpoint>"
fi

echo
echo "Sending message..."
kubectl exec -i $1 -- bash << EOF
JMX_PORT= kafka-console-producer.sh --broker-list $2 --topic test
`date`: testing
tom
dick
harry
EOF

echo
echo "Receiving message..."
kubectl exec -i $1 -- bash << EOF
JMX_PORT= kafka-console-consumer.sh --bootstrap-server $2 --topic test --from-beginning
EOF

