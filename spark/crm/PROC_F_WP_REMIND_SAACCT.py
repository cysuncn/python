#coding=UTF-8
from pyspark import SparkContext, SparkConf, SQLContext, Row, HiveContext
from pyspark.sql.types import *
from datetime import date, datetime, timedelta
import sys, re, os

st = datetime.now()
conf = SparkConf().setAppName('PROC_F_WP_REMIND_SAACCT').setMaster(sys.argv[2])
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

OCRM_F_PD_PROD_INFO = sqlContext.read.parquet(hdfs+'/OCRM_F_PD_PROD_INFO/*')
OCRM_F_PD_PROD_INFO.registerTempTable("OCRM_F_PD_PROD_INFO")
ACRM_F_CI_ASSET_BUSI_PROTO = sqlContext.read.parquet(hdfs+'/ACRM_F_CI_ASSET_BUSI_PROTO/*')
ACRM_F_CI_ASSET_BUSI_PROTO.registerTempTable("ACRM_F_CI_ASSET_BUSI_PROTO")
ACRM_F_DP_SAVE_INFO = sqlContext.read.parquet(hdfs+'/ACRM_F_DP_SAVE_INFO/*')
ACRM_F_DP_SAVE_INFO.registerTempTable("ACRM_F_DP_SAVE_INFO")
OCRM_F_WP_REMIND_RULE = sqlContext.read.parquet(hdfs+'/OCRM_F_WP_REMIND_RULE/*')
OCRM_F_WP_REMIND_RULE.registerTempTable("OCRM_F_WP_REMIND_RULE")

#任务[21] 001-01::
V_STEP = V_STEP + 1

sql = """
 SELECT monotonically_increasing_id()     AS ID 
       ,E.RULE_ID               AS RULE_ID 
       ,A.CUST_ID               AS CUST_ID 
       ,A.CORE_CUST_NAME        AS CUST_NAME 
       ,A.ACCT_NO               AS CR_ACCT_NO 
	   ,'' as DP_ACCT_NO
       ,C.PRODUCT_ID            AS PROD_ID 
       ,C.PROD_NAME             AS PROD_NAME 
       ,B.BAL_RMB               AS ACCT_BAL 
       ,B.MS_AC_BAL - B.UP_BAL                AS CHANGE_AMT 
       ,DATE(B.LTDT)                       AS CHANGE_DATE 
       ,A.MANAGE_BRAN           AS MANAGE_BRAN 
       ,A.AGENCY_BRAN           AS CREATE_BRAN 
       ,'A000110'               AS REMIND_TYPE 
       ,V_DT                    AS MSG_CRT_DATE 
       ,A.FR_ID                 AS FR_ID 
   FROM OCRM_F_WP_REMIND_RULE E                                --提醒规则表
  INNER JOIN ACRM_F_CI_ASSET_BUSI_PROTO A                      --统一客户信息表
     ON E.CUST_TYPE             = A.CUST_TYP 
    AND A.FR_ID                 = E.ORG_ID 
    AND A.LN_APCL_FLG           = 'Y' 
  INNER JOIN ACRM_F_DP_SAVE_INFO B                             --负债协议
     ON A.CUST_ID               = B.CUST_ID 
    AND B.FR_ID                 = E.ORG_ID 
    AND B.MS_AC_BAL <> B.UP_BAL 
  INNER JOIN OCRM_F_PD_PROD_INFO C                             --产品表
     ON A.PRODUCT_ID            = C.PRODUCT_ID 
    AND C.FR_ID                 = E.ORG_ID 
  WHERE E.REMIND_TYPE           = 'A000110' 
    AND DATE(B.LTDT)                     = V_DT """

sql = re.sub(r"\bV_DT\b", "'"+V_DT10+"'", sql)
OCRM_F_WP_REMIND_SAACCT = sqlContext.sql(sql)
OCRM_F_WP_REMIND_SAACCT.registerTempTable("OCRM_F_WP_REMIND_SAACCT")
dfn="OCRM_F_WP_REMIND_SAACCT/"+V_DT+".parquet"
OCRM_F_WP_REMIND_SAACCT.cache()
nrows = OCRM_F_WP_REMIND_SAACCT.count()
OCRM_F_WP_REMIND_SAACCT.write.save(path=hdfs + '/' + dfn, mode='overwrite')
OCRM_F_WP_REMIND_SAACCT.unpersist()
#ret = os.system("hdfs dfs -rm -r /"+dbname+"/OCRM_F_WP_REMIND_SAACCT/"+V_DT_LD+".parquet")
et = datetime.now()
print("Step %d start[%s] end[%s] use %d seconds, insert OCRM_F_WP_REMIND_SAACCT lines %d") % (V_STEP, st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"), (et-st).seconds, nrows)