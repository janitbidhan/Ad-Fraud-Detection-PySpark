# -*- coding: utf-8 -*-
"""csv to parquet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1I--6d3Yqj2tbXgtZZsemcR2zGUzmgxZ5
"""

#!pip install pyspark

from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("MapReduceFinalProject-FileConversion-CSVtoParquet").getOrCreate()

def convertCSVtoParquet(path='./Data/train.csv',savepath=''):
  dataDownload = spark.read\
        .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat')\
        .option("inferSchema",True)\
        .option('header', 'true')\
        .load(path).drop("attributed_time","click_time").distinct().na.drop().coalesce(100)

  dataDownload.coalesce(1).write.mode("overwrite").parquet(savepath)

convertCSVtoParquet(path='/content/drive/MyDrive/talkingdata-adtracking-fraud-detection/train.csv', savepath='/content/output')

