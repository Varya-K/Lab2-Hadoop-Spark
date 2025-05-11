
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <num_datanodes> <base|optimized>"
    echo "Example: $0 1 base"
    echo "Example: $0 3 optimized"
    exit 1
fi

num_datanodes="$1"
app_type="$2"

INPUT_PATH="hdfs://namenode:9000/data/flights/flights.csv"
OUTPUT_BASE_DIR="/results"
LOG_FILE=""
APP_SCRIPT=""
EXECUTOR_CORES=""
EXECUTOR_MEMORY=""

case "${num_datanodes}" in
    1)
        case "${app_type}" in
            base)
                EXECUTOR_CORES=2
                EXECUTOR_MEMORY="2g"
                APP_SCRIPT="/app/base_analysis.py"
                LOG_FILE="${OUTPUT_BASE_DIR}/1node_base.log"
                ;;
            optimized)
                EXECUTOR_CORES=2
                EXECUTOR_MEMORY="2g"
                APP_SCRIPT="/app/optimized.py"
                LOG_FILE="${OUTPUT_BASE_DIR}/1node_optimized.log"
                ;;
            *)
                echo "Invalid app_type: ${app_type}. Use 'base' or 'optimized'."
                exit 1
                ;;
        esac
        ;;
    3)
        case "${app_type}" in
            base)
                EXECUTOR_CORES=6
                EXECUTOR_MEMORY="4g"
                APP_SCRIPT="/app/base_analysis.py"
                LOG_FILE="${OUTPUT_BASE_DIR}/3node_base.log"
                ;;
            optimized)
                EXECUTOR_CORES=6
                EXECUTOR_MEMORY="4g"
                APP_SCRIPT="/app/optimized.py"
                LOG_FILE="${OUTPUT_BASE_DIR}/3node_optimized.log"
                ;;
            *)
                echo "Invalid app_type: ${app_type}. Use 'base' or 'optimized'."
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Invalid num_datanodes: ${num_datanodes}. Use 1 or 3."
        exit 1
        ;;
esac

OUTPUT_PATH="${OUTPUT_BASE_DIR}/${num_datanodes}node_${app_type}"

mkdir -p ./results/"${num_datanodes}node_${app_type}"
mkdir -p ./results

/opt/spark/bin/spark-submit \
    --master spark://spark:7077 \
    --total-executor-cores "${EXECUTOR_CORES}" \
    --executor-memory "${EXECUTOR_MEMORY}" \
    "${APP_SCRIPT}" \
    --input "${INPUT_PATH}" \
    --output "${OUTPUT_PATH}" \
    --log "${LOG_FILE}" \
    --executor-cores "${EXECUTOR_CORES}" \
    --executor-memory "${EXECUTOR_MEMORY}"