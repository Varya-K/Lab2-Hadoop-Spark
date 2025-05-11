
REQUIRED_DATANODES=1 

if [ "$#" -eq 1 ]; then
    REQUIRED_DATANODES="$1"
fi


until hdfs dfsadmin -safemode get | grep -q "is OFF"; do
  sleep 2
done

until hdfs dfsadmin -report | grep "Live datanodes" | awk '{print $NF}' | grep -q "${REQUIRED_DATANODES}"; do
  sleep 2
done


hdfs dfs -mkdir -p /data/flights
hdfs dfs -put -f /data/flights.csv /data/flights/
hdfs dfs -ls /data/flights