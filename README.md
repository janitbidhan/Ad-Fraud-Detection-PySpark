# CS 657 Mining Massive Datasets
	 

#### **Final Project: AdTracking Fraud Detection**


### Team : 
		- Janit Bidhan [link](jbidhan@gmu.edu)      
		- Sreenivasa Rayaprolu [link](srayapr@gmu.edu)

 #### Contents of README.md 
 - Folder Structure
 - Instructions to Run the files


### **Folder Structure**

``` 
    Final Project/ 
	
	    code/
	        Jupyter Notebooks/
	            Ad_Fraud_with_CatBoost.ipynb
				Ad_Fraud_with_LightGBM.ipynb
				Ad_Fraud_with_RF-LR-SCV.ipynb
				csv_to_parquet.ipynb

	        Python Code/
	            Ad_Fraud_with_CatBoost.py
				Ad_Fraud_with_LightGBM.py
				Ad_Fraud_with_RF-LR-SCV.py
				csv_to_parquet.py

		ScreenShots/
			1-running-on-persues-errors.png
			2-running-on-emr.png
		

		Presentation.pdf
		README.md
		REPORT.pdf
		video_presentation_link.txt 
```

## Code Files Description: 

	- csv_to_parquet.ipynb and csv_to_parquet.py: 
		This file converts .csv file to .parquet file and saves it in desired location.

	- Ad_Fraud_with_RF-LR-SCV.ipynb and Ad_Fraud_with_RF-LR-SCV.py:
		This is the code file which implements Logistic Regression, Random Forrest, LinearSVC classification models with different sampling techniques.

	- Ad_Fraud_with_CatBoost.ipynb and Ad_Fraud_with_CatBoost.py : 
		This is the code file which implements CatBoost Classification model with different sampling techniques.
	
	- Ad_Fraud_with_LightGBM.ipynb and Ad_Fraud_with_LightGBM.py  :
		This is the code file which implements LightGBM Classification model with different sampling techniques.  




## Instructions to Run Code and Infer Results

	Submitted python files can be run on any cluster. 
	We tested our python files on Persues Cluster, Amazon ElasticMapReduce Cluster, Databricks Cluster.

	To run files on Persues Cluster.
		1. SSH into Persues cluster with GMU ID 



	









	1. Download the TalkingData AdTracking Fraud Detection Challenge Dataset from Kaggle. [link](https://www.kaggle.com/competitions/talkingdata-adtracking-fraud-detection/data).

	2. Use  csv_to_parquet.ipynb or csv_to_parquet.py file to convert train.csv to parquet file.

	3. Use Ad_Fraud_with_RF-LR-SCV.ipynb or  Ad_Fraud_with_RF-LR-SCV.py to infer results from Logistic Regression, Random Forrest, Linear SVC over the sampling methods explained. 
		- Ad_Fraud_with_RF-LR-SCV.ipynb can be directly uploaded run on Google Colab. Make sure to add all the datafiles required to infer results.

	4. Use Ad_Fraud_with_CatBoost.ipynb or Ad_Fraud_with_CatBoost.py to infer results from CatBoost Classification Model over the sampling methods explained. 
		- Ad_Fraud_with_CatBoost.ipynb can be directly uploaded and run on Google Colab. Make Sure to add all the datafiles requires to infer the results. 

	5. Use Ad_Fraud_with_LightGBM.ipynb or Ad_Fraud_with_LightGBM.py to infer results from LightGBM Classification Model over the sampling methods explained.
		- Option 1: You might need to setup and use a cluster with 32GB memory.
		- Option 2: Use AWS ElasticMapReduce Cluster
			- Configure a culster with Spark-3.0.2 installed on Hadoop-2.7
			- Use mx2.large machine to create the cluster. By default it create 1 master node(32GB memory) and 2 slave nodes(32GB memory on each). 
			- However you can avoid this and have only 1 single master node for our task.
			- Generate SSH Keys for using the cluster and save it in secure folder.
			- Update the security Inbound rules of the cluster to include you IP address.
			- Create a S3 storage Bucket and upload the dataset.
			- You Can use Jupyter Notebook configured with EMR cluster or terminal to infer results.
			- Use SSH keys and Public IP Address of the cluster with puTTY or terminal depending on the operating system to SSH into created cluster.
			- upload the Ad_Fraud_with_LightGBM.py to cluster, update the folder paths and run ```spark-submit Ad_Fraud_with_LightGBM.py``` to infer results.
		
	


