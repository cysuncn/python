#coding=UTF-8
from pyspark import SparkContext, SparkConf, SQLContext, Row, HiveContext
from pyspark.sql.types import *
from datetime import date, datetime, timedelta
import sys, re, os

st = datetime.now()
conf = SparkConf().setAppName('PROC_O_CSP_ELESIGNINFOHIST').setMaster(sys.argv[2])
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

#删除当天的
ret = os.system("hdfs dfs -rm -r /"+dbname+"/F_CSP_ELESIGNINFOHIST/"+V_DT+".parquet")
#----------来源表---------------
O_CSP_ELESIGNINFOHIST = sqlContext.read.parquet(hdfs+'/O_CSP_ELESIGNINFOHIST/*')
O_CSP_ELESIGNINFOHIST.registerTempTable("O_CSP_ELESIGNINFOHIST")

#任务[11] 001-01::
V_STEP = V_STEP + 1

sql = """
 SELECT MAINTJNLNO              AS MAINTJNLNO 
       ,MAINTCODE               AS MAINTCODE 
       ,MAINTMCHANNELID         AS MAINTMCHANNELID 
       ,MAINTDATE               AS MAINTDATE 
       ,MAINTTIMESTAMP          AS MAINTTIMESTAMP 
       ,CIFNO                   AS CIFNO 
       ,USERNO                  AS USERNO 
       ,AREA                    AS AREA 
       ,SYSID                   AS SYSID 
       ,STATE                   AS STATE 
       ,USERNAME                AS USERNAME 
       ,USERADDR                AS USERADDR 
       ,SIGNACTYPE              AS SIGNACTYPE 
       ,SIGNACNO                AS SIGNACNO 
       ,SIGNACNAME              AS SIGNACNAME 
       ,PHONE                   AS PHONE 
       ,SIGNDATE                AS SIGNDATE 
       ,INVALIDDATE             AS INVALIDDATE 
       ,SIGNORG                 AS SIGNORG 
       ,BATCHJNLNO              AS BATCHJNLNO 
       ,SIGNCHANNEL             AS SIGNCHANNEL 
       ,ADDTELLERNO             AS ADDTELLERNO 
       ,CREATETIME              AS CREATETIME 
       ,UPDTELLERNO             AS UPDTELLERNO 
       ,UPDATETIME              AS UPDATETIME 
       ,FR_ID                   AS FR_ID 
       ,V_DT                    AS ODS_ST_DATE 
       ,'CSP'                   AS ODS_SYS_ID 
   FROM O_CSP_ELESIGNINFOHIST A                                --代缴费电费签约信息历史表
"""

sql = re.sub(r"\bV_DT\b", "'"+V_DT10+"'", sql)
F_CSP_ELESIGNINFOHIST = sqlContext.sql(sql)
F_CSP_ELESIGNINFOHIST.registerTempTable("F_CSP_ELESIGNINFOHIST")
dfn="F_CSP_ELESIGNINFOHIST/"+V_DT+".parquet"
F_CSP_ELESIGNINFOHIST.cache()
nrows = F_CSP_ELESIGNINFOHIST.count()
F_CSP_ELESIGNINFOHIST.write.save(path=hdfs + '/' + dfn, mode='append')
F_CSP_ELESIGNINFOHIST.unpersist()
et = datetime.now()
print("Step %d start[%s] end[%s] use %d seconds, insert F_CSP_ELESIGNINFOHIST lines %d") % (V_STEP, st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"), (et-st).seconds, nrows)