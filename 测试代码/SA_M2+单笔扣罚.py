import pandas as pd
import numpy as np
from tqdm import tqdm

def yikou():
    # 汇总首次M2和M2+的已经扣罚和退还的
    data1 = pd.read_excel("扣罚汇总/M2+扣罚汇总.xlsx",dtype={'贷款编号':'O','SA姓名':'O'})
    data2 = pd.read_excel("扣罚汇总/首次M2扣罚汇总.xlsx",dtype={'贷款编号':'O','SA姓名':'O'})
    yikou = pd.concat([data1, data2])
    return yikou
yikou = yikou()

m2_plus = pd.read_excel('M2+/m2_plus.xlsx',dtype={'贷款编号':'O','SA工号':'O'})
m2_plus = m2_plus[['贷款编号','贷款金额','商户','门店','产品名称','SA工号','SA姓名']]
#m2_plus['贷款编号'] = m2_plus['贷款编号'].astype('O')
#m2_plus['SA工号'] = m2_plus['SA工号'].astype('O')

m2 = pd.read_excel('首次M2/首次M2明细表.xlsx',dtype={'贷款编号':'O','SA工号':'O'})
m2 = m2[['贷款编号','贷款金额','产品名称','SA工号','SA姓名']]
#m2['贷款编号'] = m2['贷款编号'].astype('O')
#m2['SA工号'] = m2['SA工号'].astype('O')
m2_over=pd.pivot_table(m2,index=['SA工号'],values=['贷款编号'],aggfunc=[len])
m2_over_rate = pd.read_excel("首次m2/首次M2注册数.xlsx",dtype={'SA工号':'O'})
m2_over = pd.merge(m2_over_rate,m2_over,on="SA工号",how="left",suffixes=('','_y'))
m2_over['首次M2逾期率'] = 0.0

#首次M2逾期率计算
for i in tqdm(range(len(m2_over))):
    m2_over.loc[i,'首次M2逾期率'] = (m2_over.iloc[i,3] /m2_over.iloc[i,2])*100

#m2_over['SA工号'] = m2_over['SA工号'].astype('O')
m2_over = m2_over[['SA工号','首次M2逾期率']]

yikou = yikou[['贷款编号','扣押月份','退还月份']]
#yikou['贷款编号'] = yikou['贷款编号'].astype('O')
m2_plus = pd.merge(m2_plus,yikou,on="贷款编号",how="left")

m2_plus_ = m2_plus.copy()
for i in tqdm(range(len(m2_plus_))):
    if np.isnan(m2_plus_.loc[i,"扣押月份"]) == True or np.isnan(m2_plus_.loc[i,"退还月份"])==True:
        m2_plus_.drop([i],inplace=True)


for i in tqdm(range(len(m2_plus))):
    if np.isnan(m2_plus.loc[i, "扣押月份"]) == False:
        m2_plus.drop([i], inplace=True)
    else:
        pass

m2_plus = m2_plus.reset_index(drop=True)  # 对索引重置
m2_plus = pd.concat([m2_plus,m2_plus_],ignore_index=True)
m2_plus = m2_plus[['贷款编号','贷款金额','产品名称','商户','门店','SA工号','SA姓名']]
zmd = pd.read_excel('首次M2/主门店汇总.xlsx',dtype={'贷款编号':'O'})
#zmd['贷款编号'] = zmd['贷款编号'].astype('O')
m2_plus = pd.merge(m2_plus, zmd, on="贷款编号", how="left")

m2_plus["扣罚"] = 0
for i in tqdm(range(len(m2_plus))):
    if m2_plus.loc[i, '产品名称'] == '一般产品' or m2_plus.loc[i, '产品名称'] == '优惠产品' or m2_plus.loc[i, '产品名称'] == '广州服务类产品' or m2_plus.loc[i, '产品名称'] == '优惠产品A' or m2_plus.loc[i, '产品名称'] == '优惠产品B':
        if m2_plus.loc[i, '贷款金额'] >= 1500:
            m2_plus.loc[i, '扣罚'] = 100
        else:
            m2_plus.loc[i, '扣罚'] = 50
    elif m2_plus.loc[i, '产品名称'] == '003产品':
        m2_plus.loc[i, '扣罚'] = 30
    elif m2_plus.loc[i,'产品名称'] =="U客购":
        m2_plus.loc[i,"扣罚"] = 180
    else:
        if m2_plus.loc[i, '贷款金额'] >= 2300:
            m2_plus.loc[i, '扣罚'] = 66
        elif 1800 <= m2_plus.loc[i, '贷款金额'] < 2300:
            m2_plus.loc[i, '扣罚'] = 44
        else:
            m2_plus.loc[i, '扣罚'] = 22

m2_plus["最终扣罚"] = 0
for i in tqdm(range(len(m2_plus))):
    if np.isnan(m2_plus.loc[i, '每日提成金额']):
        m2_plus.loc[i, '最终扣罚'] = m2_plus.loc[i, '扣罚']
    else:
        m2_plus.loc[i, '最终扣罚'] = m2_plus.loc[i, '每日提成金额']

m2_plus['逾期等级'] = 'M2+'

m2_SA = m2_plus.drop_duplicates(["SA工号"])
m2_SA = m2_SA[['SA工号']]
overdue_rate_m3 = pd.read_excel("首次M2/Overdue_rate_M3.xlsx",dtype={'SA工号':'O'})

m2_SA = pd.merge(m2_SA,m2_over,on="SA工号",how="left",suffixes=('','_y'))
m2_SA = pd.merge(m2_SA,overdue_rate_m3,on="SA工号",how="left",suffixes=('','_y'))

people_list = pd.read_excel("首次M2/people_listing.xlsx",dtype={'SA工号':'O','入岗日期转换':np.datetime64})
people_list = people_list[['SA工号','姓名','在岗状态','入岗日期转换','结算日期','在职天数']]
m2_SA = pd.merge(m2_SA,people_list, on="SA工号",how="left",suffixes=('','_y'))

for i in tqdm(range(len(m2_SA))):
    if np.isnan(m2_SA.loc[i,"首次M2逾期率"]):
        m2_SA.loc[i,"首次M2逾期率"] = 0
    else:
        pass

for i in tqdm(range(len(m2_SA))):
    if np.isnan(m2_SA.loc[i,"M3+逾期率(%)"]):
        m2_SA.loc[i,"M3+逾期率(%)"] = 0
    else:
        pass


m2_SA["是否免除扣罚"] = 0
for i in tqdm(range(len(m2_SA))):
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
m2_SA = m2_SA[["SA工号","SA姓名","在岗状态","入岗日期转换","结算日期","在职天数","M3+逾期率(%)","首次M2逾期率","是否免除扣罚"]]
m2_SA.to_excel('数据输出/SA_M2+扣罚标准.xlsx')


m2_sa = m2_SA.copy()
m2_sa = m2_sa[['SA工号','是否免除扣罚']]

m2_plus = pd.merge(m2_plus,m2_sa,on="SA工号",how="left")

m2_plus['SA最终扣罚'] = 0
for i in tqdm(range(len(m2_plus))):
    if m2_plus.loc[i,'是否免除扣罚'] == 1:
        m2_plus.loc[i,'SA最终扣罚'] = 0
    elif m2_plus.loc[i,'是否免除扣罚'] == 0:
        m2_plus.loc[i,'SA最终扣罚'] = m2_plus.loc[i,'最终扣罚']
    else:
        print("免除扣罚出现问题，请核实！")


m2_plus.to_excel("数据输出/SA的M2+单笔扣罚.xlsx")







