#coding=UTF-8
from pyspark import SparkContext, SparkConf, SQLContext, Row, HiveContext
from pyspark.sql.types import *
from datetime import date, datetime, timedelta
import sys, re, os

st = datetime.now()
conf = SparkConf().setAppName('PROC_A_SUBJECT_D002014').setMaster(sys.argv[2])
sc = SparkContext(conf = conf)
sc.setLogLevel('WARN')
if len(sys.argv) > 5:
    if sys.argv[5] == "hive":
        sqlContext = HiveContext(sc)
else:
    sqlContext = SQLContext(sc)
hdfs = sys.argv[3]
dbname = sys.argv[4]

#处理需要使用的日期
etl_date = sys.argv[1]
#etl日期
V_DT = etl_date  
#上一日日期
V_DT_LD = (date(int(etl_date[0:4]), int(etl_date[4:6]), int(etl_date[6:8])) + timedelta(-1)).strftime("%Y%m%d")
#月初日期
V_DT_FMD = date(int(etl_date[0:4]), int(etl_date[4:6]), 1).strftime("%Y%m%d") 
#上月末日期
V_DT_LMD = (date(int(etl_date[0:4]), int(etl_date[4:6]), 1) + timedelta(-1)).strftime("%Y%m%d")
#10位日期
V_DT10 = (date(int(etl_date[0:4]), int(etl_date[4:6]), int(etl_date[6:8]))).strftime("%Y-%m-%d")
V_STEP = 0

ACRM_A_AGREEMENT_TARGET = sqlContext.read.parquet(hdfs+'/ACRM_A_AGREEMENT_TARGET/*')
ACRM_A_AGREEMENT_TARGET.registerTempTable("ACRM_A_AGREEMENT_TARGET")

#任务[21] 001-01::
V_STEP = V_STEP + 1

sql = """
 SELECT  CAST(B.CUST_ID AS VARCHAR(32))               AS CUST_ID 
         ,CAST('' AS VARCHAR(20)) AS ORG_ID    	--插入的空值，包顺龙2017/05/13
		 ,CAST('D002014' AS VARCHAR(20))               AS INDEX_CODE
		 ,CAST(DECIMAL(SUBSTR(V_DT, 1, 4) - SUBSTR(START_DATE_MIN, 1, 4))  AS DECIMAL(22,2))                     AS INDEX_VALUE 
         ,CAST(SUBSTR(V_DT, 1, 7)  AS VARCHAR(7))                     AS YEAR_MONTH 
		 ,CAST(V_DT   AS DATE)                  AS ETL_DATE 
        ,CAST(B.CUST_TYP AS VARCHAR(5))             AS CUST_TYPE 
        ,CAST(B.FR_ID  AS VARCHAR(5))               AS FR_ID    
   FROM ACRM_A_AGREEMENT_TARGET B                              --
"""

sql = re.sub(r"\bV_DT\b", "'"+V_DT10+"'", sql)
ACRM_A_TARGET_D002014 = sqlContext.sql(sql)
ACRM_A_TARGET_D002014.registerTempTable("ACRM_A_TARGET_D002014")
dfn="ACRM_A_TARGET_D002014/"+V_DT+".parquet"
ACRM_A_TARGET_D002014.cache()
nrows = ACRM_A_TARGET_D002014.count()
ACRM_A_TARGET_D002014.write.save(path=hdfs + '/' + dfn, mode='overwrite')
ACRM_A_TARGET_D002014.unpersist()
ACRM_A_AGREEMENT_TARGET.unpersist()
ret = os.system("hdfs dfs -rm -r /"+dbname+"/ACRM_A_TARGET_D002014/"+V_DT_LD+".parquet")
et = datetime.now()
print("Step %d start[%s] end[%s] use %d seconds, insert ACRM_A_TARGET_D002014 lines %d") % (V_STEP, st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"), (et-st).seconds, nrows)
