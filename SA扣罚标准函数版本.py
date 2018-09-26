import pandas as pd
import numpy as np
import datetime

def m2_over_rate():
    data = pd.read_excel("扣罚数据输入/M2M3逾期明细.xlsx", dtype={'贷款编号': 'O', 'SA工号': 'O'})
    m2 = data[data["首次M2"] == 1]
    m2_over_count = pd.pivot_table(m2, index=['SA工号'], values=['贷款编号'], aggfunc=[len])
    m2_zc = pd.read_excel("扣罚数据输入/m2首次注册数.xlsx", dtype={'SA工号': 'O'})
    m2_over_rate = pd.merge(m2_zc, m2_over_count, on="SA工号", how="left")
    for i in range(len(m2_over_rate)):
        m2_over_rate.loc[i, '首次M2逾期率'] = (m2_over_rate.iloc[i, 3] / m2_over_rate.iloc[i, 2]) * 100
    # 得到首次M2逾期率
    m2_over_rate = m2_over_rate[['SA工号', '首次M2逾期率']]
    return m2_over_rate

def m2_plus(m2_over_rate):
    data2 = pd.read_excel("扣罚数据输入/M2+逾期明细.xlsx", dtype={'贷款编号': 'O', 'SA工号': 'O'})
    def yikou():
        # 汇总首次M2和M2+的已经扣罚和退还的
        data11 = pd.read_excel("扣罚汇总/M2+扣罚汇总.xlsx", dtype={'贷款编号': 'O', 'SA工号': 'O'})
        data22 = pd.read_excel("扣罚汇总/首次M2扣罚汇总.xlsx", dtype={'贷款编号': 'O', 'SA工号': 'O'})
        yikou = pd.concat([data11, data22])
        return yikou
    yikou = yikou()
    # M2已经扣的剔除
    yikou = yikou[['贷款编号', '扣押月份', '退还月份']]
    data_m2_plus = pd.merge(data2, yikou, on="贷款编号", how="left")

    for i in range(len(data_m2_plus)):
        if np.isnan(data_m2_plus.loc[i, "扣押月份"]) == False and np.isnan(data_m2_plus.loc[i, "退还月份"]) == True:
            data_m2_plus.drop([i], inplace=True)
        else:
            pass

    data_m2_plus = data_m2_plus.reset_index(drop=True)  # 对索引重置
    data_m2_plus = data_m2_plus[['SA工号', 'SA姓名']]
    # 提取首次M2的数据
    data_first_m2 = pd.read_excel("扣罚数据输入/M2M3逾期明细.xlsx", dtype={'贷款编号': 'O', 'SA工号': 'O'})
    data_first_m2 = data_first_m2[data_first_m2["首次M2"] == 1]
    data_first_m2 = data_first_m2[['SA工号', 'SA姓名']]
    data_all = pd.concat([data_first_m2, data_m2_plus]).drop_duplicates(['SA工号'])  # 去重
    data_all = data_all.reset_index(drop=True)
    #导入M3逾期率
    overdue_rate_m3 = pd.read_excel("扣罚数据输入/M3+逾期率.xlsx",dtype={'SA工号':'O'})
    overdue_rate_m3 = overdue_rate_m3[['SA工号','M3+逾期率(%)']]
    people_list = pd.read_excel("扣罚数据输入/销售人员清单.xlsx",dtype={'SA工号':'O','入岗日期转换':np.datetime64})
    people_list = people_list[['SA工号','姓名','在岗状态','入岗日期转换','结算日期','在职天数']]
    data_all = pd.merge(data_all,people_list, on="SA工号",how="left",)
    data_all = pd.merge(data_all,m2_over_rate,on="SA工号",how="left")
    data_all = pd.merge(data_all,overdue_rate_m3,on="SA工号",how="left")
    #将NA的换成0
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
    return data_all


def is_mianchu(data_all):
        for i in range(len(data_all)):
            if data_all.loc[i, "在职天数"] >= 90:
                if data_all.loc[i, "首次M2逾期率"] < 5.0:
                    if data_all.loc[i, "M3+逾期率(%)"] < 7.0:
                        data_all.loc[i, "是否免除扣罚"] = "免"
                    else:
                        data_all.loc[i, "是否免除扣罚"] = "不"
                else:
                    data_all.loc[i, "是否免除扣罚"] = "不"
            else:
                if data_all.loc[i, "首次M2逾期率"] < 4.0:
                    data_all.loc[i, '是否免除扣罚'] = "免"
                else:
                    data_all.loc[i, "是否免除扣罚"] = "不"
        return data_all

def save(data_all):
    print("正在保存SA扣罚标准数据")
    data_all = data_all[["SA工号", "SA姓名", "在岗状态", "入岗日期转换", "结算日期", "在职天数", "M3+逾期率(%)", "首次M2逾期率", "是否免除扣罚"]]
    data_all.to_excel('数据输出/SA扣罚标准.xlsx')


#SA首次M2单笔扣罚

def m2_first():
    print('开始计算SA的首次M2单笔扣罚')
    zmd = pd.read_excel('扣罚数据输入/主门店汇总.xlsx', dtype={'贷款编号': 'O'})
    m2 = pd.read_excel("扣罚数据输入/M2M3逾期明细.xlsx", dtype={'贷款编号': 'O', 'SA工号': 'O'})
    m2 = m2[m2["首次M2"] == 1]
    m2 = m2[['贷款编号', '贷款金额', '产品名称', '商户', '门店', 'SA工号', 'SA姓名']]
    m2 = pd.merge(m2, zmd, on="贷款编号", how="left")#加上主门店的扣款

    for i in range(len(m2)):
        if m2.loc[i, '产品名称'] == '一般产品' or m2.loc[i, '产品名称'] == '优惠产品' or m2.loc[i, '产品名称'] == '优惠产品A' or m2.loc[
            i, '产品名称'] == '优惠产品B':
            if m2.loc[i, '贷款金额'] >= 1500:
                m2.loc[i, '扣罚'] = 180
            else:
                m2.loc[i, '扣罚'] = 90
        elif m2.loc[i, '产品名称'] == '003产品':
            m2.loc[i, '扣罚'] = 60
        elif m2.loc[i, '产品名称'] == "U客购":
            m2.loc[i, '扣罚'] = 300
        else:
            if m2.loc[i, '贷款金额'] >= 2300:
                m2.loc[i, '扣罚'] = 120
            elif 1800 <= m2.loc[i, '贷款金额'] < 2300:
                m2.loc[i, '扣罚'] = 80
            else:
                m2.loc[i, '扣罚'] = 40

    for i in range(len(m2)):
        if np.isnan(m2.loc[i, '每日提成金额']):
            m2.loc[i, '最终扣罚'] = m2.loc[i, '扣罚']
        else:
            m2.loc[i, '最终扣罚'] = m2.loc[i, '每日提成金额']

    #判断是否免除扣罚
    m2_mianchu = pd.read_excel("数据输出/SA扣罚标准.xlsx",dtype={'SA工号':'O'})
    m2_mianchu = m2_mianchu[['SA工号','是否免除扣罚']]
    m2 = pd.merge(m2,m2_mianchu,on="SA工号",how="left")

    for i in range(len(m2)):
        if m2.loc[i, '是否免除扣罚'] == '免':
            m2.loc[i, 'SA最终扣罚'] = 0
        elif m2.loc[i, '是否免除扣罚'] == '不':
            m2.loc[i, 'SA最终扣罚'] = m2.loc[i, '最终扣罚']
        else:
            print("免除扣罚出现问题，请核实！")

    m2['逾期等级'] = '首次M2'
    m2 = m2[['贷款编号', '贷款金额', '产品名称', '商户', '门店', 'SA工号', 'SA姓名', '逾期等级','最终扣罚', '是否免除扣罚', 'SA最终扣罚']]
    return m2

#M2+逾期明细

def m2_plus_koufa():
    print('开始计算SA的M2+单笔扣罚')
    def yikou():
        # 汇总首次M2和M2+的已经扣罚和退还的
        data1 = pd.read_excel("扣罚汇总/M2+扣罚汇总.xlsx", dtype={'贷款编号': 'O', 'SA姓名': 'O'})
        data2 = pd.read_excel("扣罚汇总/首次M2扣罚汇总.xlsx", dtype={'贷款编号': 'O', 'SA姓名': 'O'})
        yikou = pd.concat([data1, data2])
        return yikou
    yikou = yikou()
    yikou = yikou[['贷款编号', '扣押月份', '退还月份']]

    m2_plus = pd.read_excel('扣罚数据输入/M2+逾期明细.xlsx', dtype={'贷款编号': 'O', 'SA工号': 'O'})
    m2_plus = m2_plus[['贷款编号', '贷款金额', '商户', '门店', '产品名称', 'SA工号', 'SA姓名']]
    m2_plus = pd.merge(m2_plus, yikou, on="贷款编号", how="left")

    for i in range(len(m2_plus)):
        if np.isnan(m2_plus.loc[i, "扣押月份"]) == False and np.isnan(m2_plus.loc[i, "退还月份"]) == True:
            m2_plus.drop([i], inplace=True)
        else:
            pass

    m2_plus = m2_plus.reset_index(drop=True)

    m2_plus = m2_plus[['贷款编号', '贷款金额', '产品名称', '商户', '门店', 'SA工号', 'SA姓名']]
    zmd = pd.read_excel('扣罚数据输入/主门店汇总.xlsx', dtype={'贷款编号': 'O'})

    m2_plus = pd.merge(m2_plus, zmd, on="贷款编号", how="left")

    for i in range(len(m2_plus)):
        if m2_plus.loc[i, '产品名称'] == '一般产品' or m2_plus.loc[i, '产品名称'] == '优惠产品' or m2_plus.loc[i, '产品名称'] == '广州服务类产品' or m2_plus.loc[i, '产品名称'] == '优惠产品A' or m2_plus.loc[i, '产品名称'] == '优惠产品B':
            if m2_plus.loc[i, '贷款金额'] >= 1500:
                m2_plus.loc[i, '扣罚'] = 100
            else:
                m2_plus.loc[i, '扣罚'] = 50
        elif m2_plus.loc[i, '产品名称'] == '003产品':
            m2_plus.loc[i, '扣罚'] = 30
        elif m2_plus.loc[i, '产品名称'] == "U客购":
            m2_plus.loc[i, "扣罚"] = 180
        else:
            if m2_plus.loc[i, '贷款金额'] >= 2300:
                m2_plus.loc[i, '扣罚'] = 66
            elif 1800 <= m2_plus.loc[i, '贷款金额'] < 2300:
                m2_plus.loc[i, '扣罚'] = 44
            else:
                m2_plus.loc[i, '扣罚'] = 22

    m2_plus["最终扣罚"] = 0
    for i in range(len(m2_plus)):
        if np.isnan(m2_plus.loc[i, '每日提成金额']):
            m2_plus.loc[i, '最终扣罚'] = m2_plus.loc[i, '扣罚']
        else:
            m2_plus.loc[i, '最终扣罚'] = m2_plus.loc[i, '每日提成金额']

    m2_plus_mianchu = pd.read_excel("数据输出/SA扣罚标准.xlsx",dtype={'SA工号':'O'})
    m2_plus_mianchu = m2_plus_mianchu[['SA工号','是否免除扣罚']]
    m2_plus = pd.merge(m2_plus,m2_plus_mianchu,on="SA工号",how="left")

    for i in range(len(m2_plus)):
        if m2_plus.loc[i, '是否免除扣罚'] == "免":
            m2_plus.loc[i, 'SA最终扣罚'] = 0
        elif m2_plus.loc[i, '是否免除扣罚'] == "不":
            m2_plus.loc[i, 'SA最终扣罚'] = m2_plus.loc[i, '最终扣罚']
        else:
            print("免除扣罚出现问题，请核实！")

    m2_plus['逾期等级'] = 'M2+'
    m2_plus = m2_plus[['贷款编号', '贷款金额', '产品名称', '商户', '门店', 'SA工号', 'SA姓名', '逾期等级', '最终扣罚', '是否免除扣罚', 'SA最终扣罚']]
    return m2_plus

def hebing(m2,m2_plus):
    data = pd.concat([m2,m2_plus])
    data.to_excel("数据输出/SA单笔扣罚.xlsx")
    print("计算完成，good luck!")

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    m2_over_rate = m2_over_rate() #计算首次M2逾期率
    data_all = m2_plus(m2_over_rate) #
    data_all_1=is_mianchu(data_all) #计算扣罚免除
    save(data_all_1) #保存扣罚免除数据
    m2 = m2_first() #SA首次M2单笔扣罚
    m2_plus =m2_plus_koufa() #SA的M2+单笔扣罚
    hebing(m2,m2_plus) #合并并保存
    endtime = datetime.datetime.now()
    print("用时：%d秒" % (endtime - starttime).seconds)
