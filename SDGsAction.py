
# %%
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import os
import time
import random

def clean_text(text):
    """清理文本中的多余空格，将连续多个空格替换为一个空格。"""
    return ' '.join(text.split())

def get_soup_from_url(url, retries=3, delay=1):
    """发送HTTP请求并返回解析后的BeautifulSoup对象，带有重试机制。"""
    for attempt in range(retries):
        try:
            # 随机延迟 1 到 2 秒之间
            time.sleep(delay + random.uniform(0, 0.5))
            
            response = requests.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if attempt < retries - 1:
                print(f"重试第 {attempt + 1} 次...")
                time.sleep(delay)
            else:
                print("达到最大重试次数，终止请求")
                return None

def get_absolute_url(row, base_url):
    """处理每个views-row的div标签，提取并访问a标签的href。"""
    span_tag = row.find('span', class_='field-content')
    if not span_tag:
        print("未找到class='field-content'的span标签")
        return None

    a_tag = span_tag.find('a')
    if not a_tag or 'href' not in a_tag.attrs:
        print("未找到a标签或href属性")
        return None

    relative_href = a_tag['href']
    absolute_href = urljoin(base_url, relative_href)
    
    return absolute_href

def process_action_url(ActionURL):
    """处理每个ActionURL并存储结果到DataFrame中。"""
    detail_soup = get_soup_from_url(ActionURL)
    # if not detail_soup:
    #     return df_existing

    # 提取Title
    title_tag = detail_soup.find('h1', class_='separator-bottom mt-5')
    Title = title_tag.get_text(strip=True) if title_tag else '-'
    
    # 提取Initiator和ActionID
    place_div = detail_soup.find('div', class_='place')
    if place_div:
        h6_tags = place_div.find_all('h6')
        Initiator = h6_tags[0].get_text(strip=True) if len(h6_tags) > 0 else '-'
        ActionID = h6_tags[1].get_text(strip=True) if len(h6_tags) > 1 else '-'
    else:
        Initiator = '-'
        ActionID = '-'
    
    # # 检查ActionID是否已存在
    # if ActionID in df_existing['ActionID'].values:
    #     return df_existing

    # 查找包含内容为 "Type of initiative" 的h5标签
    h5_tag = detail_soup.find('h5', string="Type of initiative")
    if h5_tag:
        parent_div = h5_tag.find_parent('div')
        if parent_div:
            content_div = parent_div.find('div', class_='content')
            Type = content_div.get_text(strip=True) if content_div else '-'
        else:
            Type = '-'
    else:
        Type = '-'
    
    # 查找包含内容为 "Timeline" 的h5标签
    timeline_h5_tag = detail_soup.find('h5', string="Timeline")
    if timeline_h5_tag:
        next_div = timeline_h5_tag.find_next_sibling('div', class_='content')
        if next_div:
            start_date_div = next_div.find('div', class_='views-field views-field-field-start-date')
            if start_date_div:
                field_content_div = start_date_div.find('div', class_='field-content')
                StartTime = field_content_div.get_text(strip=True) if field_content_div else '-'
            else:
                StartTime = '-'
            
            end_date_div = next_div.find('div', class_='views-field views-field-field-date-of-completion')
            if end_date_div:
                field_content_div = end_date_div.find('div', class_='field-content')
                EndTime = field_content_div.get_text(strip=True) if field_content_div else '-'
            else:
                EndTime = '-'
        else:
            StartTime = EndTime = '-'
    else:
        StartTime = EndTime = '-'
    
    # 查找class为views-field views-field-field-location的div标签
    location_div = detail_soup.find('div', class_='views-field views-field-field-location')
    if location_div:
        field_content_div = location_div.find('div', class_='field-content')
        GeographicalCoverage = field_content_div.get_text(strip=True) if field_content_div else '-'
    else:
        GeographicalCoverage = '-'
    
    # 查找所有class为good-practices-goal-wrapper的span标签中的a标签，并获取内容
    spans = detail_soup.find_all('span', class_='good-practices-goal-wrapper')
    a_contents = [span.find('a').get_text(strip=True) for span in spans if span.find('a')]
    SDGs = ','.join(a_contents) if a_contents else '-'
    
    
    # 查找包含内容为 "Region" 的h5标签
    region_h5_tag = detail_soup.find('h5', string="Region")
    if region_h5_tag:
        next_div = region_h5_tag.find_next_sibling('div', class_='content')
        if next_div:
            # 查找所有class为list-group-item的li标签
            li_tags = next_div.find_all('li', class_='list-group-item')
            region_items = [li.get_text(strip=True) for li in li_tags]
            Region = ','.join(region_items) if region_items else '-'
        else:
            Region = '-'
    else:
        Region = '-'
        
        
        
    country_h5_tag = detail_soup.find('h5', string="Countries")
    if country_h5_tag:
        next_div = country_h5_tag.find_next_sibling('div', class_='content-block')
        if next_div:
            # 查找所有class为list-group-item的li标签
            li_tags = next_div.find_all('span', class_='field-content')
            country_items = [li.get_text(strip=True) for li in li_tags]
            Countries = ','.join(country_items) if country_items else '-'
        else:
            Countries = '-'
    else:
        Countries = '-'
        
        
    

    Title = clean_text(Title)
    Initiator = clean_text(Initiator)
    ActionID = clean_text(ActionID)
    Type = clean_text(Type)
    StartTime = clean_text(StartTime)
    EndTime = clean_text(EndTime)
    GeographicalCoverage = clean_text(GeographicalCoverage)
    SDGs = clean_text(SDGs)
    Region = clean_text(Region)
    Countries = clean_text(Countries)
    
    
    # 创建新记录
    new_record = {
        'Title': Title,
        'Initiator': Initiator,
        'ActionID': ActionID,
        'Type': Type,
        'StartTime': StartTime,
        'EndTime': EndTime,
        'Countries': Countries,
        'Region': Region,
        'GeographicalCoverage': GeographicalCoverage,
        'SDGs': SDGs
    }
    
    # 添加到DataFrame
    df_new = pd.DataFrame([new_record])
    
    return df_new
    

#%%
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
def main():
    page_number = 1  # 页数计数器
    
    # start = 5
    # end = 150
    
    start = 429
    end = 450

    
    for page_number in range(start,end+1):
        base_url = f"https://sdgs.un.org/partnerships/browse?page={page_number-1}"
    
        soup = get_soup_from_url(base_url)
        if not soup:
            return

        # 初始化DataFrame
        df_file = 'results.xlsx'
        if os.path.exists(df_file):
            df_existing = pd.read_excel(df_file)
        else:
            df_existing = pd.DataFrame(columns=['Page','Title', 'Initiator', 'ActionID', 'Type', 'StartTime', 'EndTime', 'Countries','Region','GeographicalCoverage', 'SDGs'])
        


        print(f"正在处理第 {page_number} 页")
        
        # 处理当前页面
        view_content = soup.find('div', class_='view-content row')
        if not view_content:
            print("未找到class='view-content row'的div元素")

        views_rows = view_content.find_all('div', class_='views-row')
        
        for row in views_rows:
            ActionURL = get_absolute_url(row, base_url)
            if ActionURL:  # 仅处理有效的URL
                try:
                    df_new = process_action_url(ActionURL)
                    df_new['Page'] = page_number
                    df_existing = pd.concat([df_existing, df_new], ignore_index=True)
                except Exception as e:
                    print(f"Error processing URL: {ActionURL}")
                    print(f"Error details: {e}")

        
        # 保存到本地文件
        df_existing.to_excel(df_file, index=False)

if __name__ == "__main__":
    main()

# %%



# %%

leftPages = [234,245,428]

for page_number in leftPages:
    base_url = f"https://sdgs.un.org/partnerships/browse?page={page_number-1}"

    soup = get_soup_from_url(base_url)

    # 初始化DataFrame
    df_file = 'results.xlsx'
    if os.path.exists(df_file):
        df_existing = pd.read_excel(df_file)
    else:
        df_existing = pd.DataFrame(columns=['Page','Title', 'Initiator', 'ActionID', 'Type', 'StartTime', 'EndTime', 'Countries','Region','GeographicalCoverage', 'SDGs'])
    


    print(f"正在处理第 {page_number} 页")
    
    # 处理当前页面
    view_content = soup.find('div', class_='view-content row')
    if not view_content:
        print("未找到class='view-content row'的div元素")

    views_rows = view_content.find_all('div', class_='views-row')
    
    for row in views_rows:
        ActionURL = get_absolute_url(row, base_url)
        if ActionURL:  # 仅处理有效的URL
            try:
                df_new = process_action_url(ActionURL)
                df_new['Page'] = page_number
                df_existing = pd.concat([df_existing, df_new], ignore_index=True)
            except Exception as e:
                print(f"Error processing URL: {ActionURL}")
                print(f"Error details: {e}")

    
    # 保存到本地文件
    df_existing.to_excel(df_file, index=False)




# %%
