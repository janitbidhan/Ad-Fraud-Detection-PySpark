# **CS 657 Mining Massive Datasets** 

## **Final Project: AdTracking Fraud Detection**


### Team : 
**Janit Bidhan** - [jbidhan@gmu.edu](jbidhan@gmu.edu)
**Sreenivasa Rayaprolu** - [srayapr@gmu.edu](srayapr@gmu.edu)

### Contents of README.md 
 - Folder Structure
 - Instructions to Run the files



## **Folder Structure**

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
			1.VPC-Creation.png
			2.EMR-Cluster-creation.png
			3.EMR-Cluster-configuration.png
			4.Persues-Command.png
			5.Persues-cluster-output.png
			6.Databricks-Loading-JarFiles.png
			7.Databricks-Cluster-configuration
			8.Databricks-WorkSpace.png
			9.Databricks-python-notebook.png
		Presentation.pdf
		README.md
		REPORT.pdf
		video_presentation_link.txt 
```

### Downloading Dataset:
	
- Create a account in [www.kaggle.com](www.kaggle.com)
- Go to [https://www.kaggle.com/competitions/talkingdata-adtracking-fraud-detection/data](https://www.kaggle.com/competitions/talkingdata-adtracking-fraud-detection/data) for downloading the data.


### Code Files Description: 

- ```csv_to_parquet.ipynb``` and ```csv_to_parquet.py```: 
		This file converts .csv file to .parquet file and saves it in desired location.

- ```Ad_Fraud_with_RF-LR-LSVC.ipynb``` and ```Ad_Fraud_with_RF-LR-LSVC.py```:
		This is the code file which implements Logistic Regression, Random Forrest, LinearSVC classification models with different sampling techniques.

- ```Ad_Fraud_with_CatBoost.ipynb``` and ```Ad_Fraud_with_CatBoost.py``` : 
		This is the code file which implements CatBoost Classification model with different sampling techniques.
	
- ```Ad_Fraud_with_LightGBM.ipynb``` and ```Ad_Fraud_with_LightGBM.py```  :
		This is the code file which implements LightGBM Classification model with different sampling techniques.  


### Order of Running the code:
- 1st : Run csv_to_parquet.py with ```spark-submit csv_to_parquet.py``` command
- 2nd : Run Ad_Fraud_with_RF-LR-LSVC.py with ```spark-submit Ad_Fraud_with_RF-LR-LSVC.py``` command.
- 3rd : Run Ad_Fraud_with_CatBoost.py with ```spark-submit Ad_Fraud_with_CatBoost.py``` command.
- 4th : Run Ad_Fraud_with_LightGBM.py with ```spark-submit Ad_Fraud_with_LightGBM.py``` command.



## Cluster creations to Run the code
* Submitted python files can be run on any cluster. 
* We tested our python files on Persues Cluster, Amazon ElasticMapReduce Cluster, Databricks Cluster.


### Instructions to Create Cluster on AWS ElasticMapReduce and run code :
	
- Create an AWS account.
- Create a new AWS VPC for this project. 
- Configure a culster with Spark-3.0.2 installed on Hadoop-2.7
- Use mx2.large machine to create the cluster. By default it create 1 master node(8GB memory) and 2 worker nodes(8GB memory on each).  
- Refer to Screenshots in for detailed EMR Cluster configuration
- It is recommmended to have above architecture of cluster to be able to run the python files.
- Generate SSH Keys for using the cluster and save it in secure folder.
- Update the security Inbound rules of the cluster to include you IP address.
- Create a new S3 storage Bucket and upload the dataset.
- Use SSH keys and Public IP Address of the cluster with puTTY or terminal depending on the operating system to SSH into created cluster.
- Use any file tranfer application application, to move python files in to EMR Cluster. 
- You can use AWS Cloud9 environment to SSH into cluster and run the code
- Use ```spark-submit file_name.py``` to run pyspark code. 


### Instructions to Create Cluster on Databricks and run it:
	
- Create a Databricks account.
- In Compute section create a cluster with above mentioned configuration.
- Refer to Screenshots for detailed cluster configuration.
- In Workspace section you can can upload the Jupyter Notebooks or python files.
- Go the required file and attach the created spark cluster to the workspace environment.
- For running code use ```spark-submit file_name.py``` in the terminal.



### Instructions to Run Code and Infer Results on Persues

- SSH into Persues cluster with GMU ID and patriot password.
-  Load files dataset and python files using a file transfering application. (csv_to_parquet.py, Ad_Fraud_with_RF-LR-LSVC, Ad_Fraud_with_CatBoost.py and Ad_Fraud_with_LightGBM.py ) 
- Update the file paths accordingly on all the python files.
- use Spark-submit file_name.py to run and infer the results. 


### Results in Jupyter Notebooks
- Submitted Jupyter notebooks have results saved in them. 
- Jupyter Notebooks can be used to for quick inference of results.
