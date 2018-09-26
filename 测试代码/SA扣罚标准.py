"""
1、先算首次M2逾期率
2、算扣罚标准
3、首次M2扣罚
4、M2+扣罚

"""


import pandas as pd
import numpy as np


#计算首次M2逾期率
#-----------------------------------------------------------------------------------
#导入首次M2逾期明细
data = pd.read_excel("测试代码/M2M3逾期明细.xlsx",dtype={'贷款编号':'O','SA工号':'O'})
#提取首次M2的数据
m2 = data[data["首次M2"]==1]
#透视逾期单数
m2_over_count = pd.pivot_table(m2,index=['SA工号'],values=['贷款编号'],aggfunc=[len])
#导入首次M2的注册数据
m2_zc = pd.read_excel("首次m2/m2首次注册数.xlsx",dtype={'SA工号':'O'})
m2_over_rate = pd.merge(m2_zc,m2_over_count,on="SA工号",how="left")
#计算首次M2逾期率
for i in range(len(m2_over_rate)):
    m2_over_rate.loc[i,'首次M2逾期率'] = (m2_over_rate.iloc[i,3] /m2_over_rate.iloc[i,2])*100
#得到首次M2逾期率
m2_over_rate = m2_over_rate[['SA工号','首次M2逾期率']]
#---------------------------------------------------------------------------------------------
#M2+逾期明细
data2 = pd.read_excel("测试代码/M2+逾期明细.xlsx",dtype={'贷款编号':'O','SA工号':'O'})
def yikou():
    # 汇总首次M2和M2+的已经扣罚和退还的
    data11 = pd.read_excel("扣罚汇总/M2+扣罚汇总.xlsx",dtype={'贷款编号':'O','SA工号':'O'})
    data22 = pd.read_excel("扣罚汇总/首次M2扣罚汇总.xlsx",dtype={'贷款编号':'O','SA工号':'O'})
    yikou = pd.concat([data11, data22])
    return yikou
yikou = yikou()

#M2已经扣的剔除
yikou = yikou[['贷款编号','扣押月份','退还月份']]
data2 = pd.merge(data2,yikou,on="贷款编号",how="left")

for i in range(len(data2)):
    if np.isnan(data2.loc[i, "扣押月份"]) == False and np.isnan(data2.loc[i, "退还月份"]) == True:
        data2.drop([i], inplace=True)
    else:
        pass

data2 = data2.reset_index(drop=True)  # 对索引重置

data_first_m2 = m2.copy()
data_first_m2 = data_first_m2[['SA工号','SA姓名']]
data_m2_plus = data2.copy()
data_m2_plus = data_m2_plus[['SA工号','SA姓名']]
data_all = pd.concat([data_first_m2,data_m2_plus]).drop_duplicates(['SA工号'])#去重
data_all = data_all.reset_index(drop=True)

overdue_rate_m3 = pd.read_excel("首次M2/Overdue_rate_M3.xlsx",dtype={'SA工号':'O'})
overdue_rate_m3 = overdue_rate_m3[['SA工号','M3+逾期率(%)']]
people_list = pd.read_excel("首次M2/people_listing.xlsx",dtype={'SA工号':'O','入岗日期转换':np.datetime64})
people_list = people_list[['SA工号','姓名','在岗状态','入岗日期转换','结算日期','在职天数']]
data_all = pd.merge(data_all,people_list, on="SA工号",how="left",)
data_all = pd.merge(data_all,m2_over_rate,on="SA工号",how="left")
data_all = pd.merge(data_all,overdue_rate_m3,on="SA工号",how="left")


for i in range(len(data_all)):
    if np.isnan(data_all.loc[i,"首次M2逾期率"]):
        data_all.loc[i,"首次M2逾期率"] = 0
    else:
        pass

for i in range(len(data_all)):
    if np.isnan(data_all.loc[i,"M3+逾期率(%)"]):
        data_all.loc[i,"M3+逾期率(%)"] = 0
    else:
        pass


#计算扣罚标准
for i in range(len(data_all)):
    if data_all.loc[i,"在职天数"] >= 90 :
        if data_all.loc[i,"首次M2逾期率"] < 5.0:
            if data_all.loc[i,"M3+逾期率(%)"] < 7.0:
                data_all.loc[i,"是否免除扣罚"] = "免"
            else:
                data_all.loc[i,"是否免除扣罚"] = "不"
        else:
             data_all.loc[i,"是否免除扣罚"] = "不"
    else:
        if data_all.loc[i,"首次M2逾期率"] < 4.0:
            data_all.loc[i,'是否免除扣罚'] = "免"
        else:
            data_all.loc[i,"是否免除扣罚"] = "不"
data_all = data_all[["SA工号","SA姓名","在岗状态","入岗日期转换","结算日期","在职天数","M3+逾期率(%)","首次M2逾期率","是否免除扣罚"]]
data_all.to_excel('数据输出/SA扣罚标准1.xlsx')
