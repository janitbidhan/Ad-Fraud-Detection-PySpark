# -*- coding: utf-8 -*-
"""Final File with LightGBM.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1U8_HpdZJ9X5qb2g4798yQSQVO-9MyC-d

***Running on Google Colab might not give Results.***
***Needs atleast 30 GB memory. Run this on AWS EMR cluster***

1.   **Installing OpenJDK-8**
2.   **Installing Spark-3.0.3 on Hadoop-2.7**
3.   **Installing LightGBM Machine Learning Model**
4.   **Setting up *JAVA_HOME* and *SPARK_HOME***
5.   **Defining Spark Session**
6.   **Adding LightJBM Model's Jar Files to Spark Context.**
"""

# !apt-get install openjdk-8-jdk-headless -qq > /dev/null
# !wget -q https://archive.apache.org/dist/spark/spark-3.0.3/spark-3.0.3-bin-hadoop2.7.tgz
# !tar xf spark-3.0.3-bin-hadoop2.7.tgz

# import os
# os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
# os.environ["SPARK_HOME"] = "/content/spark-3.0.3-bin-hadoop2.7"
# !pip install -q findspark==1.4.2

# import findspark
# findspark.init()

import pyspark
from pyspark.sql import SparkSession
spark = pyspark.sql.SparkSession.builder.appName("FinalProject") \
            .config("spark.jars.packages", "com.microsoft.ml.spark:mmlspark_2.12:1.0.0-rc3-49-659b7743-SNAPSHOT") \
            .config("spark.jars.repositories", "https://mmlspark.azureedge.net/maven") \
            .getOrCreate()
spark

"""# Libraries

1.   **Installing Visualization Libraries.**
2.   **Importing Spark, Catboost libraries**


"""

#Libraries for Visualization purposesly
# !pip install seaborn
# !pip install prettytable

#Imports
from pyspark.sql.functions import row_number, count, isnan, countDistinct
from pyspark.sql.window import *
import random
import numpy as np
from functools import reduce
from pyspark.sql.window import *
from pyspark.sql.window import Window
from pyspark.ml.linalg import VectorUDT
from pyspark.sql.types import ArrayType, DoubleType,FloatType
from pyspark.sql import Row, functions as F
from pyspark.ml.feature import StringIndexer, VectorAssembler,BucketedRandomProjectionLSH, VectorSlicer, VectorAssembler, StringIndexer, MinMaxScaler
from pyspark.sql.functions import col, when, lit, udf, row_number, array, create_map, struct, explode
from pyspark.ml import Pipeline
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.mllib.evaluation import BinaryClassificationMetrics
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.ml.classification import *
from pyspark.ml.evaluation import *
from prettytable import PrettyTable

#For visualization purposes only
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#Used for our main Task
# ADDED FOR lightgbm
from mmlspark.lightgbm import LightGBMClassifier

"""# Data Stats Functions


1. **checkNullsInData**: Returns percentage of rows with Null against the Total Rows
2. **checkNullPerTable**: Returns number of Null records full table.
3. **getAttributeCount** : Returns the count for each label.
4. **getCompleteSummary**: Returns the complete summary of the table.


"""

# Percentage of rows with Null against the Total Rows
def checkNullsInData(data):
    # Show how many Null we have in the Dataframe
    totalRows = data.count()
    drop = data.na.drop().count()
    print("Total: ", totalRows)
    print("Left After Dropping:", drop)
    return (totalRows - drop) / totalRows * 100


#Number of Nulls full Table
def checkNullPerTable(data):
    # Show how many Null we have in the Dataframe
    print("% Of Drops: ",checkNullsInData(data))
    # this shows there are a lot of duplicacy in the data.# this shows there are a lot of duplicacy in the data.
    # Lets see the percentage: 
    print("% of drop per column")
    return data.select([(count(when(isnan(c) | col(c).isNull(), c))*100/count(lit(1))).alias(c) for c in data.columns])

# GET COUNT FOR EACH LABEL
def getAttributeCount(data, label="is_attributed"):
    print("Stats for is attributed:")
    data.groupBy(label).count().show()

# GET COMPLETE SUMMARY OF THE DATA
def getCompleteSummary(data, label="is_attributed"):
    print("Summary")
    print("_________")
    data.summary().show()
    print("_________")
    checkNullPerTable(data)
    print("_________")
    print("Unique Values for each column in the table")
    data.agg(*(countDistinct(col(c)).alias(c) for c in data.columns)).show()
    print("_________")
    print("Number of values in is_attributed for each label.")
    print("_________")
    getAttributeCount(data, label)
    print("_________")

"""
## Utility Functions
1. **getFeaturesData**: For returning Vectorized features and label. It also drops exta coulmns if required.
2. **findImbalance** : It is used for finding imbalance ratio between the two labels and returns the data Not Fraud, data Fraud, ratio
3. **vectorizeData** : Returns Vector Assembled feature by merging all feature columns.
4. **stratifiedTrainTestSplit**: It is used for splitting the sampled dataset randomly in 80:20 ratio where 80 is for Training and 20 is for Testing """

#For returning Vectorized features and label. It also drops exta coulmns if required.
def getFeaturesData(
    data, inputColumnsList=["ip", "app", "device", "os", "channel"], drop=False
):
    va = VectorAssembler(inputCols=inputColumnsList, outputCol="features")
    transformedData = va.transform(data)
    if drop:
        return (
            va.transform(data)
            .drop(*inputColumnsList)
            .withColumnRenamed("is_attributed", "label")
        )
    return va.transform(data)

#It is used for finding imbalance ratio between the two labels and returns the data Not Fraud, data Fraud, ratio
def findImbalance(data):
    dataNotFraud = data.filter(col("is_attributed") == 0)
    dataFraud = data.filter(col("is_attributed") == 1)
    countFraud = dataFraud.count()
    countNotFraud = dataNotFraud.count()
    ratio = int(countNotFraud / countFraud)
    print(
        "Count Fraud: {}\nCount Not Fraud: {}\nRatio: {}".format(
            countFraud, countNotFraud, ratio
        )
    )
    return dataNotFraud, dataFraud, ratio


#Returns Vector Assembled feature by merging all feature columns.
def vectorizeData(data, NumericColumns, targetColumn):
    if data.select(targetColumn).distinct().count() != 2:
        raise ValueError("Target col must have exactly 2 classes")
    if targetColumn in NumericColumns:
        NumericColumns.remove(targetColumn)
    assembler = VectorAssembler(inputCols=NumericColumns, outputCol="features")
    vectorizedData = assembler.transform(data)
    keepColumns = [a for a in vectorizedData.columns if a not in NumericColumns]
    return (
        vectorizedData.select(*keepColumns)
        .withColumn("label", vectorizedData[targetColumn])
        .drop(targetColumn)
    )



#It is used for splitting the sampled dataset randomly in 80:20 ratio where 80 is for Training and 20 is for Testing
def stratifiedTrainTestSplit(data, ifprint=False):
    print("\n-----TRAIN TEST SPLIT STARTED----")
    dataNotFraud, dataFraud, ratio= findImbalance(data)
    dataNotFraudTrain,dataNotFraudTest=dataNotFraud.randomSplit([0.8, 0.2])
    dataFraudTrain,dataFraudTest=dataFraud.randomSplit([0.8, 0.2])
    train = dataNotFraudTrain.union(dataFraudTrain)
    test = dataFraudTest.union(dataNotFraudTest)
    if print:
        print("\n----SAMPLES IN TRAIN----")
        dataNotFraud, dataFraud, ratio= findImbalance(train)
        print("\n----SAMPLES IN TEST-----")
        dataNotFraud, dataFraud, ratio= findImbalance(test)
    return train , test

"""
## Sampling Functions
1. **randomOverSample**: It takes the ratio and does random over sampling of the lower count label to match as the higher count label as per the ratio and returns the vectorized data.
2. **randomUnderSamplingWithoutTransformation**:  It takes the ratio and does random over sampling of the lower count label to match as the higher count label as per the ratio and returns the data.
3. **randomUnderSamplingStratified**: It is used for doing undersampling in a stratified way keeping percentage of labels as per rates r1 and r2, It returns the combined data.
4. **randomUnderSampling**:  It takes the ratio and does random under sampling of the decrease the higher count label to match as per the ratio.
5. **randomUnderSamplingWithoutTransformation**: It takes the ratio and does random over sampling of the lower count label to match as per the ratio to the higher count label and returns the data.
6. **randomUnderSamplingStratified** : It is used for undersampled in a stratified way keeping percentage of labels as per rates r1 and r2, It returns the combined data.
7. **randomUnderSampling** : It takes the ratio and does random under sampling of the decrease the higher count label to match as per the ratio.
8. **completeOverSampling** : It duplicates the minority class records to match the passed ratio."""

# It takes the ratio and does random over sampling of the lower count label to match as the higher count label as per the ratio.
def randomOverSample(dataNotFraud, dataFraud, ratio):
    dataFraud = dataFraud.sample(True, float(ratio), 24)
    totalData = dataFraud.unionAll(dataNotFraud)
    return getFeaturesData(totalData, drop=True)

#It takes the ratio and does random over sampling of the lower count label to match as per the ratio to the higher count label and returns the data.
def randomUnderSamplingWithoutTransformation(dataNotFraud, dataFraud, ratio):
    dataNotFraud = dataNotFraud.sample(False, 1 / ratio, 24)
    return dataNotFraud.unionAll(dataFraud)

# It is used for undersampled in a stratified way keeping percentage of labels as per rates r1 and r2, It returns the combined data.
def randomUnderSamplingStratified(data, r1=0.1, r2=0.4):
    dataNotFraudSampled = data.filter(col("is_attributed") == 0).sample(False, r1)
    dataFraudSampled = data.filter(col("is_attributed") == 1).sample(False, r2)
    out = dataNotFraudSampled.union(dataFraudSampled)
    return out

# It takes the ratio and does random under sampling of the decrease the higher count label to match as per the ratio.
def randomUnderSampling(dataNotFraud, dataFraud, ratio):
    dataNotFraud = dataNotFraud.sample(False, 1 / ratio, 24)
    totalData = dataNotFraud.unionAll(dataFraud)
    return getFeaturesData(totalData, drop=True)


def completeOverSampling(dataNotFraud, dataFraud, ratio):
    a = range(ratio)
    # duplicate the minority rows
    oversampledData = dataFraud.withColumn(
        "test", explode(array([lit(x) for x in a]))
    ).drop("test")
    # combine both oversampled minority rows and previous majority rows combined_df = major_df.unionAll(oversampled_df)
    totalData = dataNotFraud.unionAll(oversampledData)
    return getFeaturesData(totalData, drop=True)

"""## SMOTE: Synthetic Minority Over-sampling Technique Implementation

1. **checkValidityOfColumnsCheck**: Checking validity of functions, if all columns are correctly type identified.
2. **getNumericCategoricalColumns**: Returns the lists of numerical and string columns.
3. **smote**: Used above mentioned utlity functions in implementing custom function for SMOTE 
"""

# Utlity functions of SMOTE


#Checking validity of functions, if all columns are correctly type identified.
def checkValidityOfColumnsCheck(allColumns, data):
    if len(set(allColumns)) == len(data.columns):
        print("All columns are been covered.")
    elif len(set(allColumns)) < len(data.columns):
        not_handle_list = list(set(data.columns) - set(allColumns))
        print(
            "Not all columns are covered,The columns missed out: {0}".format(
                not_handle_list
            )
        )
    else:
        mistake_list = list(set(allColumns) - set(data.columns))
        print("The columns been hardcoded wrongly: {0}".format(mistake_list))


#Returns the lists of numerical and string columns.
def getNumericCategoricalColumns(data, excludedList=[]):
    timestampColumns = [
        item[0] for item in data.dtypes if item[1].lower().startswith(("time", "date"))
    ]
    stringColumns = [
        item[0]
        for item in data.dtypes
        if item[1].lower().startswith("string")
        and item[0] not in excludedList + timestampColumns
    ]
    numericColumns = [
        item[0]
        for item in data.dtypes
        if item[1].lower().startswith(("big", "dec", "doub", "int", "float"))
        and item[0] not in excludedList + timestampColumns
    ]
    allColumns = timestampColumns + stringColumns + numericColumns + excludedList
    checkValidityOfColumnsCheck(allColumns, data)
    return numericColumns, stringColumns



# Synthetic Minority Over-sampling Technique Implementation 
def smote(dataInit, seed, bucketLength, k, multiplier):
    NumericColumns, CatColumns = getNumericCategoricalColumns(dataInit)
    data = vectorizeData(dataInit, NumericColumns, targetColumn="is_attributed")
    dataInputFraud = data[data["label"] == 1]

    # LSH, bucketed random projection
    bucketedRandomProjection = BucketedRandomProjectionLSH(
        inputCol="features", outputCol="hashes", seed=seed, bucketLength=bucketLength
    )
    # smote only applies on existing minority instances
    model = bucketedRandomProjection.fit(dataInputFraud)
    model.transform(dataInputFraud)

    # here distance is calculated from bucketedRandomProjection's param inputCol
    selfJoinWithDistance = model.approxSimilarityJoin(
        dataInputFraud, dataInputFraud, float("inf"), distCol="EuclideanDistance"
    )
    # remove self-comparison (distance 0)
    selfJoinWithDistance = selfJoinWithDistance.filter(
        selfJoinWithDistance.EuclideanDistance > 0
    )
    overOriginalRows = Window.partitionBy("datasetA").orderBy("EuclideanDistance")
    selfSimilarity = selfJoinWithDistance.withColumn(
        "r_num", F.row_number().over(overOriginalRows)
    )
    selfSimilaritySelected = selfSimilarity.filter(selfSimilarity.r_num <= k)
    overOriginalRowsNoOrder = Window.partitionBy("datasetA")

    # list to store batches of synthetic data
    res = []
    # two udf for vector add and subtract, subtraction include a random factor [0,1]
    subtractVectorUDF = F.udf(
        lambda arr: random.uniform(0, 1) * (arr[0] - arr[1]), VectorUDT()
    )
    addVectorUDF = F.udf(lambda arr: arr[0] + arr[1], VectorUDT())

    # retain original columns
    originalColumns = dataInputFraud.columns
    print("Generating New Samples")
    for i in range(multiplier):
        # logic to randomly select neighbour: pick the largest random number generated row as the neighbour
        randomSelectedData = (
            selfSimilaritySelected.withColumn("rand", F.rand())
            .withColumn("max_rand", F.max("rand").over(overOriginalRowsNoOrder))
            .where(F.col("rand") == F.col("max_rand"))
            .drop(*["max_rand", "rand", "r_num"])
        )
        # create synthetic feature numerical part
        vecDiff = randomSelectedData.select(
            "*",
            subtractVectorUDF(F.array("datasetA.features", "datasetB.features")).alias(
                "vecdiff"
            ),
        )
        vecModified = vecDiff.select(
            "*", addVectorUDF(F.array("datasetA.features", "vecdiff")).alias("features")
        )
        for c in originalColumns:
            # randomly select neighbour or original data
            colSubsititue = random.choice(["datasetA", "datasetB"])
            val = "{0}.{1}".format(colSubsititue, c)
            if c != "features":
                # do not unpack original numerical features
                vecModified = vecModified.withColumn(c, F.col(val))
        vecModified = vecModified.drop(
            *["datasetA", "datasetB", "vecdiff", "EuclideanDistance"]
        )
        res.append(vecModified)
    print("Samples Generation Complete.")

    unionedData = reduce(DataFrame.unionAll, res)
    # union synthetic instances with original full (both minority and majority) data
    return unionedData.union(data.select(unionedData.columns))

"""## Machine Learning Model Implementation

**LightGBM** : Implementation of LightGBM Classification Model. Returns predictions.

"""

def lightGBMC(train,test, isCV=False):
    print(">>> LightGBMClassifier Invoked")
    model = LightGBMClassifier(
        objective="binary", featuresCol="features", labelCol="label", isUnbalance=True
    )
    fitted_model = model.fit(train)
    predictions = fitted_model.transform(test)
    return {"predictions":predictions}

"""## Sample Data Creation

**diffSampledData** : Returns the required sampled data upon specification.
"""

def diffSampledData(data, isUnderSample=False,isOverSample=False ,isSMOTE=False, ifprint=False):
    sampledData={}
    print("\n---Comparing data using various Sampling Techniques---")

    # print("\n--NO Sampling--")
    # sampledData['NO_SAMPLING_APPLIED']=getFeaturesData(data, drop=True)

    # Find each class data
    dataNotFraud, dataFraud, ratio= findImbalance(data)
    if isUnderSample:
        print("\n--Undersampling--")
        # Random UnderSample
        underSampledData=randomUnderSampling(dataNotFraud,dataFraud,ratio)
        # getAttributeCount(underSampledData,"label")
        sampledData['underSampledData']=underSampledData
        
    if isOverSample:
        print("\n--Random OverSampling--")
        #Random OverSample
        randomOverSampleddata=randomOverSample(dataNotFraud,dataFraud,int(ratio*0.75))
        # getAttributeCount(randomOverSampleddata,"label")
        sampledData['randomOverSampleddata']=randomOverSampleddata

    # print("\n--Complete OverSampling--")
    # #Complete Oversample
    # completeOversampledData=completeOverSampling(dataNotFraud,dataFraud,ratio)
    # getAttributeCount(completeOversampledData,"label")
    # sampledData['completeOversampledData']=completeOversampledData
    
    if isSMOTE:
        print("\n--SMOTE OverSampling--")
        #SMOTE
        oversampledDataSMOTE= smote(data, seed=24,bucketLength=200,k=3,multiplier=int(ratio*0.75))
        sampledData['oversampledDataSMOTE']=oversampledDataSMOTE
    
    if ifprint:
        if isSMOTE:
            print("\n--SMOTE OverSampling--")
            getAttributeCount(oversampledDataSMOTE,"label")
        if isOverSample:
            print("\n--Random OverSampling--")
            getAttributeCount(randomOverSampleddata,"label")
        # print("\n--Complete OverSampling--")
        # getAttributeCount(completeOversampledData,"label")
        if isUnderSample:
            print("\n--Undersampling--")
            getAttributeCount(underSampledData,"label")
    return sampledData

"""## Results 

1. **getResults**: Main method to run the specified Machine Learning models. Return Evaluation metrics. In case of Cross Validation, returns Best Model.

2. **filldetails** : Adds all the metrics from different oversampling techniques into table.

3. **printConfusionMatrix** ( ***For Visualization purposes only***): Prints confusion Matrix.

4. **otherMetrics** : Caluclates Precison, Recall, Accuracy and F1 Score.

5. **getEvalutions**: Evaluates predictions with labels and returns the metrics
"""

# Adds all the metrics from different oversampling techniques into table.
def filldetails(analysisTable, predictions, sampling, model):
    cf_matrix, ROC, accuracy, F1, precision, recall = getEvalutions(predictions)
    print(sampling, model, ROC, accuracy, F1, precision, recall, cf_matrix)
    analysisTable+=str(sampling) +" , "+ str(model)+" , "+ str(ROC)+" , "+ str(accuracy)+" , "+str(F1)+" , "+ str(precision)+" , "+ str(recall)+" , "+str(cf_matrix)
    

#Main method to run the specified Machine Learning models. Return Evaluation metrics. In case of Cross Validation, returns Best Model.
def getResults(sampledData, test, isLR=False, isRF=False, isLSVC=False, isCatBoost=False, isLightGBM=False,isCV=False):
    # Specify the Column Names while initializing the Table
    analysisTable = "\n\n\nOutputs\n"
    #analysisTable = PrettyTable(["Sampling", "Model", "ROC", "accuracy", "F1", "precision", "recall", "Matrix"])
    results = {}
    testData = getFeaturesData(test, drop=True)
    testData.cache()
    for sampling in sampledData:
        print(">>>>>>>>>>>>>>>>Started :", sampling)
        train = sampledData[sampling]
        res={}
        if isLightGBM:
            #LightGBM
            modelDataLightGBM = lightGBMC(train, testData, isCV=isCV)
            filldetails(analysisTable, modelDataLightGBM["predictions"], sampling, "LightGBM")
            res["LightGBM"]=modelDataLightGBM
        if len(res.keys())>1:
            results[sampling] = res
        print("<<<<<<<<<<<<<<Finished :", sampling)
    return results, analysisTable

# print the confusion matrix 
#USING SEABORN LIBRARY FOR VISUALIZATION PURPOSES
def printConfusionMatrix(cf_matrix):
    group_names = ["True Neg","False Pos","False Neg","True Pos"]
    group_counts = ["{0:0.0f}".format(value) for value in
                    cf_matrix.flatten()]
    group_percentages = ["{0:.2%}".format(value) for value in
                         cf_matrix.flatten()/np.sum(cf_matrix)]
    labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
              zip(group_names,group_counts,group_percentages)]
    labels = np.asarray(labels).reshape(2,2)
    sns.heatmap(cf_matrix, annot=labels, fmt="", cmap='Blues')


#Caluclate F1-score, Recall, Accuaracy, Precision
def otherMetrics(cf):
    tp = cf[0][0]
    fp = cf[1][0]
    fn = cf[0][1]
    tn = cf[1][1]
    precision = np.round((tp)/(tp+fp),3)
    recall =  np.round((tp)/(tp+fn),3)
    accuracy= np.round((tp+tn)/(tp+fp+fn+tn),3)
    F1=np.round((2*precision*recall)/(precision+recall),3)
    return accuracy, F1, precision, recall


#Evaluate the predictions with actual labels.
def getEvalutions(predictions):
    evaluator=BinaryClassificationEvaluator(labelCol='label')
    ROC = evaluator.evaluate(predictions, {evaluator.metricName: "areaUnderROC"})
    preds_and_labels = predictions.withColumn('label', F.col('label').cast(FloatType())).orderBy('prediction').select(['prediction','label'])
    metrics = MulticlassMetrics(preds_and_labels.rdd.map(tuple))
    cf_matrix=metrics.confusionMatrix().toArray()
    # printConfusionMatrix(cf_matrix)
    accuracy, F1, precision, recall= otherMetrics(cf_matrix)
    return cf_matrix, np.round(ROC,3), accuracy, F1, precision, recall

"""## Demo 
**Training and Testing on train_sample.csv data provided along with actual Dataset.**
"""

def demoData(path="/content/drive/MyDrive/talkingdata-adtracking-fraud-detection/train_sample.csv"):
    dataDownload = spark.read\
      .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat')\
      .option("inferSchema",True)\
      .option('header', 'true')\
      .load(path).drop("attributed_time","click_time").distinct().na.drop()
    dataNotFraud, dataFraud, ratio= findImbalance(dataDownload)
    print("\n--Undersampling to create demo set--")
    # Random UnderSample the big data to form processable ratio for demo.
    underSampledData=randomUnderSamplingWithoutTransformation(dataNotFraud,dataFraud,int(ratio/8))
    getCompleteSummary(underSampledData)
    trainSample,testSample=stratifiedTrainTestSplit(underSampledData, ifprint=False)
    sampledData=diffSampledData(trainSample,isUnderSample=True,isOverSample=False ,isSMOTE=False, ifprint=False)
    results, analysisTable= getResults(sampledData,testSample,isLightGBM=True)
    print("\n________________RESULTS______________\n",analysisTable)
    return results, analysisTable

resultsDemo, analysisTableDemo= demoData(path='/content/drive/MyDrive/Final Project CS 657/talkingdata-adtracking-fraud-detection/train_sample.csv')

"""## 6 Million Records
**Training and Testing on sampled 6 Million records from train.csv**
"""

def RUN6MTEST(path="../Data/Sampled_data.parquet"):
    dataDownload=spark.read.parquet(path)
    getCompleteSummary(dataDownload)
    trainSample,testSample=stratifiedTrainTestSplit(dataDownload, ifprint=False)
    sampledData=diffSampledData(trainSample, isUnderSample=False,isOverSample=True, isSMOTE=False, ifprint=False)
    results, analysisTable= getResults(sampledData,testSample,isLightGBM=True)
    print("\n________________RESULTS______________\n",analysisTable)
    return results, analysisTable

results6M, analysisTable6M= RUN6MTEST()

"""## 26 Million Records
**Training and Testing on sampled 26 Million records from train.csv**

"""

def RUN26MTEST(path="../Data/Sampled25M.parquet"):
    dataDownload=spark.read.parquet(path)
    getCompleteSummary(dataDownload)
    trainSample,testSample=stratifiedTrainTestSplit(dataDownload, ifprint=False)
    sampledData=diffSampledData(trainSample, isUnderSample=False,isOverSample=True, ifprint=False)
    results, analysisTable= getResults(sampledData,testSample,isLightGBM=True)
    print("\n________________RESULTS______________\n",analysisTable)
    return results, analysisTable

results26M, analysisTable26M= RUN26MTEST()
