#coding=UTF-8
from pyspark import SparkContext, SparkConf, SQLContext, Row, HiveContext
from pyspark.sql.types import *
from datetime import date, datetime, timedelta
import sys, re, os

st = datetime.now()
conf = SparkConf().setAppName('PROC_A_SUBJECT_D002017').setMaster(sys.argv[2])
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

OCRM_F_CI_CUSTLNAINFO = sqlContext.read.parquet(hdfs+'/OCRM_F_CI_CUSTLNAINFO/*')
OCRM_F_CI_CUSTLNAINFO.registerTempTable("OCRM_F_CI_CUSTLNAINFO")

#任务[21] 001-01::
V_STEP = V_STEP + 1

sql = """
 SELECT A.FR_ID                 AS FR_ID 
       ,A.CUST_ID               AS CUST_ID 
       ,MAX(A.EXP_DATE)                       AS EXP_DATE 
   FROM OCRM_F_CI_CUSTLNAINFO A                                --客户信用信息
  WHERE EXP_DATE > V_DT 
  GROUP BY FR_ID 
       ,CUST_ID """

sql = re.sub(r"\bV_DT\b", "'"+V_DT10+"'", sql)
TMP_CUSTLNA_INFO_01 = sqlContext.sql(sql)
TMP_CUSTLNA_INFO_01.registerTempTable("TMP_CUSTLNA_INFO_01")
dfn="TMP_CUSTLNA_INFO_01/"+V_DT+".parquet"
TMP_CUSTLNA_INFO_01.cache()
nrows = TMP_CUSTLNA_INFO_01.count()
TMP_CUSTLNA_INFO_01.write.save(path=hdfs + '/' + dfn, mode='overwrite')
TMP_CUSTLNA_INFO_01.unpersist()
ret = os.system("hdfs dfs -rm -r /"+dbname+"/TMP_CUSTLNA_INFO_01/"+V_DT_LD+".parquet")
et = datetime.now()
print("Step %d start[%s] end[%s] use %d seconds, insert TMP_CUSTLNA_INFO_01 lines %d") % (V_STEP, st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"), (et-st).seconds, nrows)

#任务[21] 001-02::
V_STEP = V_STEP + 1

sql = """
 SELECT A.CUST_ID               AS CUST_ID 
       ,''                    AS ORG_ID 
       ,'D002017'               AS INDEX_CODE 
       ,A.CREDIT_LINE           AS INDEX_VALUE 
       ,SUBSTR(V_DT, 1, 7)                       AS YEAR_MONTH 
       ,V_DT                    AS ETL_DATE 
       ,A.CUST_TYPE             AS CUST_TYPE 
       ,A.FR_ID                 AS FR_ID 
   FROM OCRM_F_CI_CUSTLNAINFO A                                --客户信用信息
  INNER JOIN TMP_CUSTLNA_INFO_01 B                             --客户信用信息临时表01
     ON A.FR_ID                 = B.FR_ID 
    AND A.CUST_ID               = B.CUST_ID 
    AND A.EXP_DATE              = B.EXP_DATE """

sql = re.sub(r"\bV_DT\b", "'"+V_DT10+"'", sql)
ACRM_A_TARGET_D002017 = sqlContext.sql(sql)
ACRM_A_TARGET_D002017.registerTempTable("ACRM_A_TARGET_D002017")
dfn="ACRM_A_TARGET_D002017/"+V_DT+".parquet"
ACRM_A_TARGET_D002017.cache()
nrows = ACRM_A_TARGET_D002017.count()
ACRM_A_TARGET_D002017.write.save(path=hdfs + '/' + dfn, mode='overwrite')
ACRM_A_TARGET_D002017.unpersist()
OCRM_F_CI_CUSTLNAINFO.unpersist()
TMP_CUSTLNA_INFO_01.unpersist()
ret = os.system("hdfs dfs -rm -r /"+dbname+"/ACRM_A_TARGET_D002017/"+V_DT_LD+".parquet")
et = datetime.now()
print("Step %d start[%s] end[%s] use %d seconds, insert ACRM_A_TARGET_D002017 lines %d") % (V_STEP, st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"), (et-st).seconds, nrows)