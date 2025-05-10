from pprint import pprint

from DrissionPage import ChromiumOptions,ChromiumPage
import random
import time

#配置已保存到文件(以后都不会配置了）
# 创建 ChromiumOptions 实例
options = ChromiumOptions()
# 直接设置 _browser_path 属性
path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ChromiumOptions().set_browser_path(path).save()

#ChromiumPage 基于Selenium开发

#第一步：

#打开浏览器并且实例化
dp=ChromiumPage()
#监听数据包！！！重点  数据包特征（监听数据包中含有search-pc）
dp.listen.start('search-pc')
#打开你要爬虫的网址
dp.get('https://we.51job.com/pc/search?jobArea=000000&keyword=python%E5%B7%A5%E7%A8%8B%E5%B8%88&searchType=2&keywordType=')

#创建文件对象
import csv
f=open('数据集.csv', mode='w', encoding='utf-8', newline='')

#字典写入方法
csv_writer=csv.DictWriter(f,fieldnames=[
            '职位',
            '公司名称',
            '公司规模',
            '要求学历',
            '省份',
            '所属市',
            '所属区',
            '月薪',
            '最高月薪',
            '最低月薪',
            '工作经验'
])

#写入表头
csv_writer.writeheader()

# 抓取1到50页的数据：
for i in range(1, 51):
    print(f'正在采集第{i}页数据')
    #下滑页面处理
    dp.scroll.to_bottom()
    # 第二步：
    # 等待数据包加载
    r = dp.listen.wait()

    # 获取相应数据
    json_data = r.response.body

    # print(json_data)

    items = json_data['resultbody']['job']['items']
    # print(items)
    for item in items:
        try:
            dict = {
                '职位': item['jobName'],
                '公司名称': item['fullCompanyName'],
                '公司规模': item['companySizeString'],
                '要求学历': item['degreeString'],
                '省份': item['jobAreaLevelDetail']['provinceString'],
                '所属市': item['jobAreaLevelDetail']['cityString'],
                '所属区': item['jobAreaLevelDetail']['districtString'],
                '月薪': item['provideSalaryString'],
                '最高月薪': item['jobSalaryMax'],
                '最低月薪': item['jobSalaryMin'],
                '工作经验': item['workYearString']
            }
            # 写入数据
            csv_writer.writerow(dict)
            print(dict)
        except:
            pass

    # 翻页逻辑
    dp.ele('css:.btn-next').click()

    # 随机延时，模拟人工操作
    time.sleep(random.uniform(1, 2))

