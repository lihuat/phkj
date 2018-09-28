import numpy as np
import pandas as pd

m2 = pd.read_excel('首次M2/首次M2明细表.xlsx',dtype={'SA工号':"O",'贷款编号':'O'})
zmd = pd.read_excel('首次M2/主门店汇总.xlsx',dtype={'贷款编号':'O'})
m2 = m2[['贷款编号','贷款金额','产品名称','商户','门店','SA工号','SA姓名']]
#首次M2逾期率计算------------------------------------------------------------------
#先复制一份首次M2明细，并透视
m2_1 = m2.copy()
m2_1 = m2_1[["SA工号",'贷款编号']]
#透视
m2_over = pd.pivot_table(m2_1,index=['SA工号'],values=['贷款编号'],aggfunc=[len])
m2_over_rate = pd.read_excel("首次m2/首次M2注册数.xlsx",dtype={'SA工号':'O'})
m2_over = pd.merge(m2_over_rate,m2_over,on="SA工号",how="left",suffixes=('','_y'))
m2_over['首次M2逾期率'] = 0.0

for i in range(len(m2_over)):
    m2_over.loc[i,'首次M2逾期率'] = (m2_over.iloc[i,3] /m2_over.iloc[i,2])*100

m2_over['SA工号'] = m2_over['SA工号'].astype('O')
m2_over = m2_over[['SA工号','首次M2逾期率']]

#--------------------------------------------------------------------------------------

m2 = pd.merge(m2, zmd, on="贷款编号", how="left")#加上主门店的扣款
m2["扣罚"] = 0
for i in range(len(m2)):
    if m2.loc[i, '产品名称'] == '一般产品' or m2.loc[i, '产品名称'] == '优惠产品' or m2.loc[i, '产品名称'] == '优惠产品A' or m2.loc[i, '产品名称'] == '优惠产品B':
        if m2.loc[i, '贷款金额'] >= 1500:
            m2.loc[i, '扣罚'] = 180
        else:
            m2.loc[i, '扣罚'] = 90
    elif m2.loc[i, '产品名称'] == '003产品':
        m2.loc[i, '扣罚'] = 60
    elif m2.loc[i,'产品名称'] =="U客购":
        m2.loc[i, '扣罚'] = 300
    else:
        if m2.loc[i, '贷款金额'] >= 2300:
            m2.loc[i, '扣罚'] = 120
        elif 1800 <= m2.loc[i, '贷款金额'] < 2300:
            m2.loc[i, '扣罚'] = 80
        else:
            m2.loc[i, '扣罚'] = 40

m2["最终扣罚"] = 0
for i in range(len(m2)):
    if np.isnan(m2.loc[i, '每日提成金额']):
        m2.loc[i, '最终扣罚'] = m2.loc[i, '扣罚']
    else:
        m2.loc[i, '最终扣罚'] = m2.loc[i, '每日提成金额']

m2['逾期等级'] = '首次M2'

#判断是否免除扣罚------------------------------------------------------------------------------
m2_2 = m2.copy()#复制一份新的m2
m2_SA = m2_2.drop_duplicates(["SA工号"])#按照工号去重
m2_SA = m2_SA[['SA工号']]

overdue_rate_m3 = pd.read_excel("首次M2/Overdue_rate_M3.xlsx",dtype={'SA工号':'O'})#导入M3逾期率
m2_SA = pd.merge(m2_SA,m2_over,on="SA工号",how="left",suffixes=('','_y'))
m2_SA = pd.merge(m2_SA,overdue_rate_m3,on="SA工号",how="left",suffixes=('','_y'))
people_list = pd.read_excel("首次M2/people_listing.xlsx",dtype={'SA工号':'O','入岗日期转换':np.datetime64})#导入人员清单
people_list = people_list[['SA工号','姓名','在岗状态','入岗日期转换','结算日期','在职天数']]
m2_SA = pd.merge(m2_SA,people_list, on="SA工号",how="left",suffixes=('','_y'))

for i in range(len(m2_SA)):
    if np.isnan(m2_SA.loc[i,"首次M2逾期率"]):
        m2_SA.loc[i,"首次M2逾期率"] = 0
    else:
        pass

for i in range(len(m2_SA)):
    if np.isnan(m2_SA.loc[i,"M3+逾期率(%)"]):
        m2_SA.loc[i,"M3+逾期率(%)"] = 0
    else:
        pass


m2_SA["是否免除扣罚"] = 0
for i in range(len(m2_SA)):
    if m2_SA.loc[i,"在职天数"] >= 90 :
        if m2_SA.loc[i,"首次M2逾期率"] < 5.0:
            if m2_SA.loc[i,"M3+逾期率(%)"] < 7.0:
                m2_SA.loc[i,"是否免除扣罚"] = 1
            else:
                m2_SA.loc[i,"是否免除扣罚"] = 0
        else:
             m2_SA.loc[i,"是否免除扣罚"] = 0
    else:
        if m2_SA.loc[i,"首次M2逾期率"] < 4.0:
            m2_SA.loc[i,'是否免除扣罚'] = 1
        else:
            m2_SA.loc[i,"是否免除扣罚"] = 0

#扣罚标准
m2_SA.to_excel('数据输出/SA_first_M2扣罚标准.xlsx')

#----------------------------------------------------------
m2_SA = m2_SA[["SA工号","是否免除扣罚"]]
m2 = pd.merge(m2,m2_SA,on="SA工号",how="left")

m2['SA最终扣罚'] = 0
for i in range(len(m2)):
    if m2.loc[i,'是否免除扣罚'] == 1.0:
        m2.loc[i,'SA最终扣罚'] = 0
    elif m2.loc[i,'是否免除扣罚'] == 0.0:
        m2.loc[i,'SA最终扣罚'] = m2.loc[i,'最终扣罚']
    else:
        print("免除扣罚出现问题，请核实！")

m2 = m2[['贷款编号','贷款金额','产品名称','商户','门店','SA工号','SA姓名','最终扣罚','是否免除扣罚','SA最终扣罚']]
m2.to_excel("数据输出/SA首次M2单笔扣罚.xlsx")

