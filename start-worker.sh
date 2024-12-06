#!/bin/bash
# Start the Spark worker process and link to the master
# The master URL will be provided as an environment variable or defaulted below
: "${SPARK_MASTER:=spark://spark-master:7077}"
exec $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker \
  --webui-port 8081 $SPARK_MASTER
