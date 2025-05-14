# README

В данной лабораторной работе:

1. В качестве набора данных был выбран dataset **2015 Flight Delays and Cancellations** (обрезанный до 100.000 строк). В нем 31 признак, несколько из которых являются категориальными, например DAY_OF_WEEK).
2. Были созданы Docker файлы с namenode, 1 datanode/3 datanodes и Spark.
3. Создано 2 Spark Application: в одном просто замеряется время и RAM, в другом оптимизированный вариант первого файла (с использование repartition и persist)

Чтобы запустить программу нужно:

1. Запустить кластер:
    
    ```bash
        docker-compose -f docker-compose-1-datanode.yml up -d
    ```
    
    или 
    
    ```bash
        docker-compose -f docker-compose-3-datanodes.yml up -d
    ```
    
2. Загрузить данные в HDFS:
    
    ```bash
        docker exec namenode bash /scripts/upload-data.sh 1
    ```
    
    или
    
    ```bash
        docker exec namenode bash /scripts/upload-data.sh 3
    ```
    
3. Запустить Spark Application
    
    ```bash
        docker exec spark bash /scripts/run-spark.sh 1 base
    ```
    
    или
    
    ```bash
        docker exec spark bash /scripts/run-spark.sh 1 optimized
    ```
    
    или
    
    ```bash
        docker exec spark bash /scripts/run-spark.sh 3 base
    ```
    
    или
    
    ```bash
        docker exec spark bash /scripts/run-spark.sh 3 optimized
    ```
    

После каждого эксперимента нужно остановить кластер:

```bash
docker-compose -f файл_compose.yml down -v
```

После проведения экспериментов должны появится лог файлы в папке results

На моем компьютере команды 1 и 2 выполняются успешно. Однако 3 шаг выдает ошибку, связанную с тем, что Spark испытывает сложности с выделением и использованием вычислительных ресурсов (ядер/потоков) для экзекьютора при обработке данных из HDFS: WARN TaskSchedulerImpl: Initial job has not accepted any resources; check your cluster UI to ensure that workers are registered and have sufficient resources. На следующем скрине видно, что для экзекьютора не было выделено ядер для выполнения:

![image](https://github.com/user-attachments/assets/c11fa877-5f54-4cda-9330-6b23450100b6)


Я использовала разные образы для Spark: bde2020 и apache/spark, но проблема не пропадала.

В связи с этим, я не смогла сравнить результаты 😢
