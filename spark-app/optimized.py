import time
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg
from pyspark.storagelevel import StorageLevel
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

flights_schema = StructType([
    StructField("YEAR", IntegerType(), True),
    StructField("MONTH", IntegerType(), True),
    StructField("DAY", IntegerType(), True),
    StructField("DAY_OF_WEEK", IntegerType(), True),
    StructField("AIRLINE", StringType(), True),
    StructField("FLIGHT_NUMBER", IntegerType(), True),
    StructField("TAIL_NUMBER", StringType(), True),
    StructField("ORIGIN_AIRPORT", StringType(), True),
    StructField("DESTINATION_AIRPORT", StringType(), True),
    StructField("SCHEDULED_DEPARTURE", StringType(), True),
    StructField("DEPARTURE_TIME", StringType(), True),
    StructField("DEPARTURE_DELAY", DoubleType(), True),
    StructField("TAXI_OUT", DoubleType(), True),
    StructField("WHEELS_OFF", StringType(), True),
    StructField("SCHEDULED_TIME", DoubleType(), True),
    StructField("ELAPSED_TIME", DoubleType(), True),
    StructField("AIR_TIME", DoubleType(), True),
    StructField("DISTANCE", DoubleType(), True),
    StructField("WHEELS_ON", StringType(), True),
    StructField("TAXI_IN", DoubleType(), True),
    StructField("SCHEDULED_ARRIVAL", StringType(), True),
    StructField("ARRIVAL_TIME", StringType(), True),
    StructField("ARRIVAL_DELAY", DoubleType(), True),
    StructField("DIVERTED", IntegerType(), True),
    StructField("CANCELLED", IntegerType(), True),
    StructField("CANCELLATION_REASON", StringType(), True),
    StructField("AIR_SYSTEM_DELAY", DoubleType(), True),
    StructField("SECURITY_DELAY", DoubleType(), True),
    StructField("AIRLINE_DELAY", DoubleType(), True),
    StructField("LATE_AIRCRAFT_DELAY", DoubleType(), True),
    StructField("WEATHER_DELAY", DoubleType(), True)
])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--log', required=True)
    parser.add_argument('--executor-cores', required=True, type=int)
    parser.add_argument('--executor-memory', required=True)
    args = parser.parse_args()

    start_time = time.time()

    spark = SparkSession.builder \
        .appName("FlightsOptimizedAnalysis") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.executor.cores", str(args.executor_cores)) \
        .config("spark.executor.memory", args.executor_memory) \
        .config("dfs.client.socket-timeout", "600000") \
        .config("dfs.client.read.timeout", "600000") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN") # Устанавливаем WARN

    try:
        df = spark.read.csv(args.input, header=True, schema=flights_schema)

        df = df.repartition(8, "AIRLINE")
        df.persist(StorageLevel.MEMORY_AND_DISK)

        row_count = df.count()

        airline_stats = df.groupBy("AIRLINE").agg(
            count("*").alias("flight_count"),
            avg("DEPARTURE_DELAY").alias("avg_delay")
        ).persist(StorageLevel.MEMORY_AND_DISK)

        busy_routes = df.groupBy("ORIGIN_AIRPORT", "DESTINATION_AIRPORT") \
                       .agg(count("*").alias("flight_count")) \
                       .orderBy(col("flight_count").desc()) \
                       .limit(10)

        airline_stats.write.csv(f"{args.output}/airline_stats", mode="overwrite", compression="gzip", header=True)
        busy_routes.write.csv(f"{args.output}/busy_routes", mode="overwrite", compression="gzip", header=True)

        end_time = time.time()
        duration = end_time - start_time
        with open(args.log, "w") as f:
            f.write(f"Execution time: {duration:.2f} seconds\n")
            f.write(f"Data size: {row_count} rows\n")
            f.write("Optimizations used: repartition(), persist(), compression\n")


    except Exception as e:
        with open(args.log, "w") as f:
             f.write(f"Error: {e}\n")
             f.write(f"Execution time until error: {time.time() - start_time:.2f} seconds\n")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()