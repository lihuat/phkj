import numpy as np
import pandas as pd

m2 = pd.read_excel('首次M2/首次M2明细表.xlsx')
zmd = pd.read_excel('首次M2/主门店汇总.xlsx')
m2 = m2[['贷款编号','贷款金额','产品名称','SA工号','SA姓名']]
m2['贷款编号'] = m2['贷款编号'].astype('O')
m2['SA工号'] = m2['SA工号'].astype('O')
zmd['贷款编号'] = zmd['贷款编号'].astype('O')

m2_over = pd.pivot_table(m2,index=['SA工号'],values=['贷款编号'],aggfunc=[len])
m2_over_rate = pd.read_excel("首次m2/m2首次注册数.xlsx")#
m2_over = pd.merge(m2_over_rate,m2_over,on="SA工号",how="left",suffixes=('','_y'))
m2_over['首次M2逾期率'] = 0.0

#首次M2逾期率计算
for i in range(len(m2_over)):
    m2_over.loc[i,'首次M2逾期率'] = (m2_over.iloc[i,3] /m2_over.iloc[i,2])*100

m2_over['SA工号'] = m2_over['SA工号'].astype('O')
m2_over = m2_over[['SA工号','首次M2逾期率']]



m2 = pd.merge(m2, zmd, on="贷款编号", how="left")
m2["扣罚"] = 0
for i in range(len(m2)):
    if m2.loc[i, '产品名称'] == '一般产品' or m2.loc[i, '产品名称'] == '优惠产品':
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

#判断是否免除扣罚
m2_SA = m2.drop_duplicates(["SA工号"])
m2_SA = m2_SA[['SA工号']]
overdue_rate_m3 = pd.read_excel("首次M2/Overdue_rate_M3.xlsx")#导入M3逾期率
overdue_rate_m3['SA工号'] = overdue_rate_m3['SA工号'].astype('O')
m2_SA = pd.merge(m2_SA,m2_over,on="SA工号",how="left",suffixes=('','_y'))
m2_SA = pd.merge(m2_SA,overdue_rate_m3,on="SA工号",how="left",suffixes=('','_y'))

people_list = pd.read_excel("首次M2/people_listing.xlsx")#导入人员清单
people_list['SA工号'] = people_list['SA工号'].astype('O')
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

#m2.to_excel("SA首次M2单笔扣罚.xlsx")
m2 = m2[['贷款编号','贷款金额','SA工号','SA姓名','是否免除扣罚','SA最终扣罚']]
m2.to_csv("数据输出/SA首次M2单笔扣罚.csv")

