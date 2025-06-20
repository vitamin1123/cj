import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# 创建保存图片的目录
if not os.path.exists('images'):
    os.makedirs('images')

# 定义下载函数
def download_image(image_id):
    try:
        image_id = image_id
        # 使用Picsum API获取随机图片，指定宽度为800像素
        # url = f'https://picsum.photos/seed/img{image_id}/800'
        url = f'https://i18.net/api.php?fl=meizi'
        response = requests.get(url, stream=True, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            # 保存图片
            file_path = os.path.join('images', f'{image_id}.jpg')
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return f"图片 {image_id} 下载成功"
        else:
            return f"图片 {image_id} 下载失败，状态码: {response.status_code}"
    
    except Exception as e:
        return f"图片 {image_id} 下载出错: {str(e)}"

# 主函数
def main():
    # 图片总数
    total_images = 45000
    # 每次下载的批量大小
    batch_size = 100
    
    print(f"开始下载 {total_images} 张图片...")
    
    # 分批次下载
    for batch in range(0, total_images, batch_size):
        start = batch
        end = min(batch + batch_size, total_images)
        current_batch = list(range(start + 1, end + 1))
        
        print(f"正在下载第 {start + 1}-{end} 张图片...")
        
        # 使用线程池并行下载
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(tqdm(executor.map(download_image, current_batch), 
                               total=len(current_batch), desc="下载进度"))
        
        # 打印批次结果
        success_count = sum(1 for r in results if "下载成功" in r)
        print(f"第 {start + 1}-{end} 张图片下载完成，成功: {success_count}/{len(current_batch)}")
        
        # 批次之间暂停，避免请求过于频繁
        time.sleep(2)
    
    print(f"全部下载完成！共下载 {total_images} 张图片，保存在 'images' 目录中。")

if __name__ == "__main__":
    main()    