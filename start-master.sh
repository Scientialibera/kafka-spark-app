#!/bin/bash
# Start the Spark master process
export SPARK_MASTER_HOST=`hostname`
exec $SPARK_HOME/bin/spark-class org.apache.spark.deploy.master.Master \
  --host $SPARK_MASTER_HOST \
  --port 7077 \
  --webui-port 8080
