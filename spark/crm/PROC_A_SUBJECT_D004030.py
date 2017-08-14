#coding=UTF-8
from pyspark import SparkContext, SparkConf, SQLContext, Row, HiveContext
from pyspark.sql.types import *
from datetime import date, datetime, timedelta
import sys, re, os

st = datetime.now()
conf = SparkConf().setAppName('PROC_A_SUBJECT_D004030').setMaster(sys.argv[2])
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

ACRM_A_TARGET_D004008 = sqlContext.read.parquet(hdfs+'/ACRM_A_TARGET_D004008/*')
ACRM_A_TARGET_D004008.registerTempTable("ACRM_A_TARGET_D004008")
ACRM_A_TARGET_D004009 = sqlContext.read.parquet(hdfs+'/ACRM_A_TARGET_D004009/*')
ACRM_A_TARGET_D004009.registerTempTable("ACRM_A_TARGET_D004009")

#任务[21] 001-01::
V_STEP = V_STEP + 1

sql = """
 SELECT A.CUST_ID               AS CUST_ID 
       ,''                    AS ORG_ID 
       ,'D004030'               AS INDEX_CODE 
       ,CASE WHEN A.INDEX_VALUE / B.INDEX_VALUE > 1.5 THEN 0 WHEN A.INDEX_VALUE / B.INDEX_VALUE < 2 / 3 THEN 2 ELSE 1 END                     AS INDEX_VALUE 
       ,SUBSTR(V_DT, 1, 7)                       AS YEAR_MONTH 
       ,V_DT                    AS ETL_DATE 
       ,'1'                     AS CUST_TYPE 
       ,A.FR_ID                 AS FR_ID 
   FROM ACRM_A_TARGET_D004008 A                                --当月持有产品数
  INNER JOIN ACRM_A_TARGET_D004009 B                           --持有产品数年初数
     ON A.CUST_ID               = B.CUST_ID 
    AND A.FR_ID                 = B.FR_ID 
  WHERE A.CUST_TYPE             = '1' """

sql = re.sub(r"\bV_DT\b", "'"+V_DT10+"'", sql)
ACRM_A_TARGET_D004030 = sqlContext.sql(sql)
ACRM_A_TARGET_D004030.registerTempTable("ACRM_A_TARGET_D004030")
dfn="ACRM_A_TARGET_D004030/"+V_DT+".parquet"
ACRM_A_TARGET_D004030.cache()
nrows = ACRM_A_TARGET_D004030.count()
ACRM_A_TARGET_D004030.write.save(path=hdfs + '/' + dfn, mode='overwrite')
ACRM_A_TARGET_D004030.unpersist()
ACRM_A_TARGET_D004008.unpersist()
ACRM_A_TARGET_D004009.unpersist()
ret = os.system("hdfs dfs -rm -r /"+dbname+"/ACRM_A_TARGET_D004030/"+V_DT_LD+".parquet")
et = datetime.now()
print("Step %d start[%s] end[%s] use %d seconds, insert ACRM_A_TARGET_D004030 lines %d") % (V_STEP, st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"), (et-st).seconds, nrows)