#coding=UTF-8
from pyspark import SparkContext, SparkConf, SQLContext, Row, HiveContext
from pyspark.sql.types import *
from datetime import date, datetime, timedelta
import sys, re, os

st = datetime.now()
conf = SparkConf().setAppName('PROC_F_CI_LOAN_MORT_INFO').setMaster(sys.argv[2])
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

F_LN_XDXT_GUARANTY_INFO = sqlContext.read.parquet(hdfs+'/F_LN_XDXT_GUARANTY_INFO/*')
F_LN_XDXT_GUARANTY_INFO.registerTempTable("F_LN_XDXT_GUARANTY_INFO")
OCRM_F_CI_SYS_RESOURCE = sqlContext.read.parquet(hdfs+'/OCRM_F_CI_SYS_RESOURCE/*')
OCRM_F_CI_SYS_RESOURCE.registerTempTable("OCRM_F_CI_SYS_RESOURCE")

#任务[21] 001-01::
V_STEP = V_STEP + 1

sql = """
 SELECT monotonically_increasing_id() AS ID
           ,A.GUARANTYID AS GUARANTYID
           ,A.GUARANTYTYPE AS GUARANTYTYPE
           ,A.GUARANTYSTATUS AS GUARANTYSTATUS
           ,NVL(B.ODS_CUST_ID, A.OWNERID) AS OWNERID
           ,A.OWNERNAME AS OWNERNAME
           ,A.OWNERTYPE AS OWNERTYPE
           ,CAST(A.RATE AS DECIMAL(24,6)) AS RATE
           ,A.CUSTGUARANTYTYPE AS CUSTGUARANTYTYPE
           ,A.SUBJECTNO AS SUBJECTNO
           ,A.RELATIVEACCOUNT AS RELATIVEACCOUNT
           ,A.GUARANTYRIGHTID AS GUARANTYRIGHTID
           ,A.OTHERGUARANTYRIGHT AS OTHERGUARANTYRIGHT
           ,A.GUARANTYNAME AS GUARANTYNAME
           ,A.GUARANTYSUBTYPE AS GUARANTYSUBTYPE
           ,A.GUARANTYOWNWAY AS GUARANTYOWNWAY
           ,A.GUARANTYUSING AS GUARANTYUSING
           ,A.GUARANTYLOCATION AS GUARANTYLOCATION
           ,CAST(A.GUARANTYAMOUNT AS DECIMAL(24,6)) AS GUARANTYAMOUNT
           ,CAST(A.GUARANTYAMOUNT1 AS DECIMAL(24,6)) AS GUARANTYAMOUNT1
           ,CAST(A.GUARANTYAMOUNT2 AS DECIMAL(24,6)) AS GUARANTYAMOUNT2
           ,A.GUARANTYRESOUCE AS GUARANTYRESOUCE
           ,A.GUARANTYDATE AS GUARANTYDATE
           ,A.BEGINDATE AS BEGINDATE
           ,A.OWNERTIME AS OWNERTIME
           ,A.GUARANTYDESCRIPT AS GUARANTYDESCRIPT
           ,A.ABOUTOTHERID1 AS ABOUTOTHERID1
           ,A.ABOUTOTHERID2 AS ABOUTOTHERID2
           ,A.ABOUTOTHERID3 AS ABOUTOTHERID3
           ,A.ABOUTOTHERID4 AS ABOUTOTHERID4
           ,A.PURPOSE AS PURPOSE
           ,CAST(A.ABOUTSUM1 AS DECIMAL(24,6)) AS ABOUTSUM1
           ,CAST(A.ABOUTSUM2 AS DECIMAL(24,6)) AS ABOUTSUM2
           ,CAST(A.ABOUTRATE AS DECIMAL(24,6)) AS ABOUTRATE
           ,A.GUARANTYANA AS GUARANTYANA
           ,CAST(A.GUARANTYPRICE AS DECIMAL(24,6)) AS GUARANTYPRICE
           ,A.EVALMETHOD AS EVALMETHOD
           ,A.EVALORGID AS EVALORGID
           ,A.EVALORGNAME AS EVALORGNAME
           ,A.EVALDATE AS EVALDATE
           ,CAST(A.EVALNETVALUE AS DECIMAL(24,6)) AS EVALNETVALUE
           ,CAST(A.CONFIRMVALUE AS DECIMAL(24,6)) AS CONFIRMVALUE
           ,CAST(A.GUARANTYRATE AS DECIMAL(24,6)) AS GUARANTYRATE
           ,A.THIRDPARTY1 AS THIRDPARTY1
           ,A.THIRDPARTY2 AS THIRDPARTY2
           ,A.THIRDPARTY3 AS THIRDPARTY3
           ,A.GUARANTYDESCRIBE1 AS GUARANTYDESCRIBE1
           ,A.GUARANTYDESCRIBE2 AS GUARANTYDESCRIBE2
           ,A.GUARANTYDESCRIBE3 AS GUARANTYDESCRIBE3
           ,A.FLAG1 AS FLAG1
           ,A.FLAG2 AS FLAG2
           ,A.FLAG3 AS FLAG3
           ,A.FLAG4 AS FLAG4
           ,A.GUARANTYREGNO AS GUARANTYREGNO
           ,A.GUARANTYREGORG AS GUARANTYREGORG
           ,A.GUARANTYREGDATE AS GUARANTYREGDATE
           ,A.GUARANTYWODATE AS GUARANTYWODATE
           ,A.INSURECERTNO AS INSURECERTNO
           ,A.OTHERASSUMPSIT AS OTHERASSUMPSIT
           ,A.INPUTORGID AS INPUTORGID
           ,A.INPUTUSERID AS INPUTUSERID
           ,A.INPUTDATE AS INPUTDATE
           ,A.UPDATEUSERID AS UPDATEUSERID
           ,'' AS UPDATEDATE
           ,A.REMARK AS REMARK
           ,A.SAPVOUCHTYPE AS SAPVOUCHTYPE
           ,A.CERTTYPE AS CERTTYPE
           ,A.CERTID AS CERTID
           ,A.LOANCARDNO AS LOANCARDNO
           ,A.GUARANTYCURRENCY AS GUARANTYCURRENCY
           ,A.EVALCURRENCY AS EVALCURRENCY
           ,CAST(A.GUARANTYDESCRIBE4 AS DECIMAL(24,6)) AS GUARANTYDESCRIBE4
           ,CAST(A.DYNAMICVALUE AS DECIMAL(24,6)) AS DYNAMICVALUE
           ,A.YAPINNAME AS YAPINNAME
           ,A.YAPINCOUNT AS YAPINCOUNT
           ,A.COMPLETEYEAR AS COMPLETEYEAR
           ,A.STORETYPE AS STORETYPE
           ,A.RENTORNOT AS RENTORNOT
           ,A.RENTDATE AS RENTDATE
           ,A.RECORDTERM AS RECORDTERM
           ,A.RECORDTYPE AS RECORDTYPE
           ,A.ASSURENO AS ASSURENO
           ,A.ASSURETERM AS ASSURETERM
           ,CAST(A.ASSURESUM AS DECIMAL(24,6)) AS ASSURESUM
           ,A.ASSUREDEFINE AS ASSUREDEFINE
           ,A.GUARANTYTOCORE AS GUARANTYTOCORE
           ,A.IMPAWNFLAG AS IMPAWNFLAG
           ,A.ACCRUALBEGINDATE AS ACCRUALBEGINDATE
           ,A.ACCRUALENDDATE AS ACCRUALENDDATE
           ,A.DEPREBEGINDATE AS DEPREBEGINDATE
           ,A.DEPREENDDATE AS DEPREENDDATE
           ,A.IMPAWNDEPACCOUNTM AS IMPAWNDEPACCOUNTM
           ,A.IMPAWNDEPACCOUNTO AS IMPAWNDEPACCOUNTO
           ,A.DEBTORRIGHT AS DEBTORRIGHT
           ,A.DEPOSITACCOUNT AS DEPOSITACCOUNT
           ,A.IMPAWNBILLNO AS IMPAWNBILLNO
           ,A.STOPPAYNO AS STOPPAYNO
           ,A.RULEVALUE AS RULEVALUE
           ,A.CASHVALUE AS CASHVALUE
           ,A.SAFETYVALUE AS SAFETYVALUE
           ,CAST(A.GARNORVALUE AS DECIMAL(24,6)) AS GARNORVALUE
           ,A.CERTINTEGRITY AS CERTINTEGRITY
           ,A.CARRYINGCAPACITY AS CARRYINGCAPACITY
           ,A.MIGRATEFLAG AS MIGRATEFLAG
           ,A.MFGUARANTYID AS MFGUARANTYID
           ,A.GUARANTYCONTRACTNO AS GUARANTYCONTRACTNO
           ,A.INSURANCECATEGORY AS INSURANCECATEGORY
           ,A.INSURANCEENTNAME AS INSURANCEENTNAME
           ,A.INSURANCEENDDATE AS INSURANCEENDDATE
           ,A.GUARANTYENDDATE AS GUARANTYENDDATE
           ,A.ISASSURE AS ISASSURE
           ,A.SIGNORG AS SIGNORG
           ,A.SIGNNO AS SIGNNO
           ,A.ABATEFLAG AS ABATEFLAG
           ,A.HOSEVALMETHOD AS HOSEVALMETHOD
           ,A.HOSEVALORGNAME AS HOSEVALORGNAME
           ,A.HOSEVALORGID AS HOSEVALORGID
           ,A.HOSEVALDATE AS HOSEVALDATE
           ,A.HOSEVALCURRENCY AS HOSEVALCURRENCY
           ,CAST(A.HOSEVALNETVALUE AS DECIMAL(24,6)) AS HOSEVALNETVALUE
           ,A.HOSCONFIRMCURRENCY AS HOSCONFIRMCURRENCY
           ,CAST(A.HOSCONFIRMVALUE AS DECIMAL(24,6)) AS HOSCONFIRMVALUE
           ,A.GURCONFIRMCURRENCY AS GURCONFIRMCURRENCY
           ,CAST(A.GURCONFIRMVALUE AS DECIMAL(24,6)) AS GURCONFIRMVALUE
           ,A.CONTRACTCURRENCY AS CONTRACTCURRENCY
           ,CAST(A.CONTRACTSUM AS DECIMAL(24,6)) AS CONTRACTSUM
           ,CAST(A.GUARANTYRATIO AS DECIMAL(24,6)) AS GUARANTYRATIO
           ,A.HOSCONTRACTCURRENCY AS HOSCONTRACTCURRENCY
           ,CAST(A.HOSCONTRACTSUM AS DECIMAL(24,6)) AS HOSCONTRACTSUM
           ,CAST(A.HOSGUARANTYRATIO AS DECIMAL(24,6)) AS HOSGUARANTYRATIO
           ,CAST(A.HOSGUARANTYRATIO1 AS DECIMAL(24,6)) AS HOSGUARANTYRATIO1
           ,A.CURCONTRACTCURRENCY AS CURCONTRACTCURRENCY
           ,CAST(A.CURCONTRACTSUM AS DECIMAL(24,6)) AS CURCONTRACTSUM
           ,CAST(A.CURGUARANTYRATIO AS DECIMAL(24,6)) AS CURGUARANTYRATIO
           ,CAST(A.CURGUARANTYRATIO1 AS DECIMAL(24,6)) AS CURGUARANTYRATIO1
           ,A.CUREVALCURRENCY AS CUREVALCURRENCY
           ,CAST(A.CUREVALNETVALUE AS DECIMAL(24,6)) AS CUREVALNETVALUE
           ,A.ODS_ST_DATE AS ODS_ST_DATE
    FROM F_LN_XDXT_GUARANTY_INFO A                              --押品基本信息
   LEFT JOIN OCRM_F_CI_SYS_RESOURCE B                          --系统来源中间表
     ON A.OWNERID               = B.SOURCE_CUST_ID 
    AND B.ODS_SYS_ID            = 'LNA' """

sql = re.sub(r"\bV_DT\b", "'"+V_DT10+"'", sql)
ACRM_F_CI_LOAN_MORT_INFO = sqlContext.sql(sql)
ACRM_F_CI_LOAN_MORT_INFO.registerTempTable("ACRM_F_CI_LOAN_MORT_INFO")
dfn="ACRM_F_CI_LOAN_MORT_INFO/"+V_DT+".parquet"
ACRM_F_CI_LOAN_MORT_INFO.cache()
nrows = ACRM_F_CI_LOAN_MORT_INFO.count()
ACRM_F_CI_LOAN_MORT_INFO.write.save(path=hdfs + '/' + dfn, mode='overwrite')
ACRM_F_CI_LOAN_MORT_INFO.unpersist()
ret = os.system("hdfs dfs -rm -r /"+dbname+"/ACRM_F_CI_LOAN_MORT_INFO/"+V_DT_LD+".parquet")
et = datetime.now()
print("Step %d start[%s] end[%s] use %d seconds, insert ACRM_F_CI_LOAN_MORT_INFO lines %d") % (V_STEP, st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"), (et-st).seconds, nrows)
