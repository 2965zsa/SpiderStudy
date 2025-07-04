import os
import time
from lxml import etree
import requests
from PIL import Image
from io import BytesIO

def download_images(images_dir='piclitl', max_images=400, pages=range(1, 5)):
    """
    下载图片的函数

    Args:
        images_dir (str, 可选): 图片保存路径。默认为 'piclitl'。
        max_images (int, 可选): 最大下载图片数量。默认为 400。
        pages (range, 可选): 要爬取的页面范围。默认为 range(1, 5)。

    Returns:
        None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
    }
    session = requests.Session()

    os.makedirs(images_dir, exist_ok=True)
    downloaded_images = 0

    for page in pages:
        url = f'https://www.vcg.com/creative-photo/nadaoderen/?page={page}'
        try:
            response = session.get(url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            response.encoding = 'utf-8'
            page_text = response.text
        except requests.RequestException as e:
            print(f'请求页面 {url} 出错：{e}')
            continue

        tree = etree.HTML(page_text)
        figure_list = tree.xpath('//div[@class="gallery_inner"]/figure')

        if not figure_list:
            print(f'页面 {url} 中未找到图片元素')
            continue

        for figure in figure_list:
            if downloaded_images >= max_images:
                break

            try:
                img_src = figure.xpath('./a/img/@data-src')[0]
                img_src = 'https:' + img_src
            except (IndexError, KeyError):
                print('未成功匹配到字段')
                continue

            img_name = f'A08({downloaded_images}).jpg'
            img_path = os.path.join(images_dir, img_name)

            try:
                img_data = session.get(img_src, headers=headers, timeout=10).content
            except requests.exceptions.RequestException as e:
                print(f'下载图片 {img_src} 出错：{e}')
                continue

            try:
                with BytesIO(img_data) as img_buffer:
                    img = Image.open(img_buffer)
                    img_rgb = img.convert('RGB')
                    img_rgb.save(img_path, 'JPEG')
                print(f'图片 {img_name} 下载成功')
                downloaded_images += 1
            except Exception as e:
                print(f'保存图片 {img_name} 出错：{e}')

    print(f'总共成功下载了 {downloaded_images} 张图片')

if __name__ == '__main__':
    start_time = time.time()
    download_images()
    end_time = time.time()
    print(f'图片下载完成，耗时 {end_time - start_time:.2f} 秒')