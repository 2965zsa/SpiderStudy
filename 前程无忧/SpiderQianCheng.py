from pprint import pprint
from DrissionPage import ChromiumOptions, ChromiumPage
import random
import time
import csv
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

# 配置浏览器路径
try:
    path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    options = ChromiumOptions().set_browser_path(path).save()
    logging.info("浏览器路径配置成功")
except Exception as e:
    logging.error(f"浏览器路径配置失败: {str(e)}")
    exit(1)

# 创建浏览器实例
try:
    dp = ChromiumPage()
    logging.info("浏览器实例化成功")
except Exception as e:
    logging.error(f"浏览器实例化失败: {str(e)}")
    exit(1)

# 监听数据包
dp.listen.start('search-pc')
logging.info("数据包监听已启动")

# 打开目标网址
try:
    dp.get(
        'https://we.51job.com/pc/search?jobArea=000000&keyword=python%E5%B7%A5%E7%A8%8B%E5%B8%88&searchType=2&keywordType=')
    logging.info("成功打开目标网址")
except Exception as e:
    logging.error(f"打开网址失败: {str(e)}")
    dp.quit()
    exit(1)

# 创建CSV文件
try:
    filename = f'python_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    with open(filename, mode='w', encoding='utf-8-sig', newline='') as f:  # 使用utf-8-sig解决Excel中文乱码问题
        fieldnames = [
            '职位', '公司名称', '公司规模', '要求学历', '省份',
            '所属市', '所属区', '月薪', '最高月薪', '最低月薪', '工作经验'
        ]

        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        logging.info("CSV文件创建成功，开始爬取数据...")

        # 抓取1到50页的数据
        for page_num in range(1, 51):
            start_time = time.time()
            logging.info(f"正在采集第{page_num}页数据")

            # 下滑页面加载所有内容
            dp.scroll.to_bottom()
            logging.debug("页面已滑动到底部")

            # 等待数据包加载（增加重试机制）
            data_acquired = False
            for retry in range(3):  # 最多重试3次
                try:
                    r = dp.listen.wait(timeout=10)
                    json_data = r.response.body
                    items = json_data['resultbody']['job']['items']
                    data_acquired = True
                    break
                except Exception as e:
                    logging.warning(f"第{retry + 1}次获取数据失败: {str(e)}")
                    time.sleep(2)  # 等待后重试

            if not data_acquired:
                logging.error(f"第{page_num}页数据获取失败，跳过此页")
                continue

            # 处理当前页数据
            records_count = 0
            for item in items:
                try:
                    # 处理可能缺失的字段
                    district = item['jobAreaLevelDetail'].get('districtString', '')

                    record = {
                        '职位': item['jobName'],
                        '公司名称': item['fullCompanyName'],
                        '公司规模': item['companySizeString'],
                        '要求学历': item['degreeString'],
                        '省份': item['jobAreaLevelDetail']['provinceString'],
                        '所属市': item['jobAreaLevelDetail']['cityString'],
                        '所属区': district,
                        '月薪': item['provideSalaryString'],
                        '最高月薪': item.get('jobSalaryMax', ''),
                        '最低月薪': item.get('jobSalaryMin', ''),
                        '工作经验': item['workYearString']
                    }

                    csv_writer.writerow(record)
                    records_count += 1
                except Exception as e:
                    logging.error(f"处理记录时出错: {str(e)}")
                    pprint(item)  # 打印出错的数据项

            logging.info(f"第{page_num}页完成，共获取{records_count}条记录")

            # 翻页处理（最后一页时退出）
            if page_num < 50:
                try:
                    next_btn = dp.ele('css:.btn-next', timeout=5)
                    if next_btn:
                        next_btn.click()
                        # 等待新页面加载
                        dp.wait.load_start()
                        time.sleep(random.uniform(1.5, 2.5))  # 随机延时
                    else:
                        logging.warning("未找到下一页按钮，爬取结束")
                        break
                except Exception as e:
                    logging.error(f"翻页失败: {str(e)}")
                    break

            # 计算并记录页面处理时间
            page_time = time.time() - start_time
            logging.info(f"第{page_num}页处理耗时: {page_time:.2f}秒")

    logging.info(f"数据爬取完成，结果已保存到: {filename}")

except Exception as e:
    logging.error(f"爬取过程中发生错误: {str(e)}")
finally:
    # 确保浏览器关闭
    try:
        dp.quit()
        logging.info("浏览器已关闭")
    except:
        pass