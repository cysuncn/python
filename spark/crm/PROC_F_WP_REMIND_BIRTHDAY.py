#coding=UTF-8
from pyspark import SparkContext, SparkConf, SQLContext, Row, HiveContext
from pyspark.sql.types import *
from datetime import date, datetime, timedelta
import sys, re, os

st = datetime.now()
conf = SparkConf().setAppName('PROC_F_WP_REMIND_BIRTHDAY').setMaster(sys.argv[2])
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

OCRM_F_CI_CUST_DESC = sqlContext.read.parquet(hdfs+'/OCRM_F_CI_CUST_DESC/*')
OCRM_F_CI_CUST_DESC.registerTempTable("OCRM_F_CI_CUST_DESC")
OCRM_F_CI_PER_CUST_INFO = sqlContext.read.parquet(hdfs+'/OCRM_F_CI_PER_CUST_INFO/*')
OCRM_F_CI_PER_CUST_INFO.registerTempTable("OCRM_F_CI_PER_CUST_INFO")
OCRM_F_WP_REMIND_RULE = sqlContext.read.parquet(hdfs+'/OCRM_F_WP_REMIND_RULE/*')
OCRM_F_WP_REMIND_RULE.registerTempTable("OCRM_F_WP_REMIND_RULE")

#任务[21] 001-01::
V_STEP = V_STEP + 1

sql = """
 SELECT monotonically_increasing_id()     AS ID 
       ,E.RULE_ID               AS RULE_ID 
       ,A.CUST_ID               AS CUST_ID 
       ,A.CUST_NAME             AS CUST_NAME 
       ,A.CUST_BIR              AS BIRTHDAY 
       ,B.OBJ_RATING            AS OBJ_RATING 
       ,''                    AS REMIND_TYPE 
       ,V_DT                    AS MSG_CRT_DATE 
       ,E.ORG_ID                AS FR_ID 
   FROM OCRM_F_WP_REMIND_RULE E                                --提醒规则表
  INNER JOIN OCRM_F_CI_PER_CUST_INFO A                         --对私客户信息表
     ON A.FR_ID                 = E.ORG_ID 
    AND LENGTH(TRIM(A.CUST_BIR))                       = 10 
  INNER JOIN OCRM_F_CI_CUST_DESC B                             --统一客户信息表
     ON A.CUST_ID               = B.CUST_ID 
    AND B.FR_ID                 = E.ORG_ID 
  WHERE E.REMIND_TYPE           = 'A000103' 
    AND concat(SUBSTR(V_DT, 1, 4),'-',SUBSTR(A.CUST_BIR, 6, 2),'-',SUBSTR(A.CUST_BIR, 9, 2)) = date_add(V_DT,coalesce(E.BEFOREHEAD_DAY,0)) """

sql = re.sub(r"\bV_DT\b", "'"+V_DT10+"'", sql)
OCRM_F_WP_REMIND_BIRTHDAY = sqlContext.sql(sql)
OCRM_F_WP_REMIND_BIRTHDAY.registerTempTable("OCRM_F_WP_REMIND_BIRTHDAY")
dfn="OCRM_F_WP_REMIND_BIRTHDAY/"+V_DT+".parquet"
OCRM_F_WP_REMIND_BIRTHDAY.cache()
nrows = OCRM_F_WP_REMIND_BIRTHDAY.count()

#删除当天数据，支持重跑
ret = os.system("hdfs dfs -rm -r /"+dbname+"/OCRM_F_WP_REMIND_BIRTHDAY/"+V_DT+".parquet ")
OCRM_F_WP_REMIND_BIRTHDAY.write.save(path=hdfs + '/' + dfn, mode='append')
OCRM_F_WP_REMIND_BIRTHDAY.unpersist()
#ret = os.system("hdfs dfs -rm -r /"+dbname+"/OCRM_F_WP_REMIND_BIRTHDAY/"+V_DT_LD+".parquet")
et = datetime.now()
print("Step %d start[%s] end[%s] use %d seconds, insert OCRM_F_WP_REMIND_BIRTHDAY lines %d") % (V_STEP, st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"), (et-st).seconds, nrows)