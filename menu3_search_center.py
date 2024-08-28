import streamlit as st
import pandas as pd
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import folium
from streamlit_folium import st_folium

# st.set_page_config(page_title="AI시스템", page_icon="🕹️", layout="wide", initial_sidebar_state="expanded")

# horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 2px; border: none; background-color: #25383C;'><br>"    
# st.sidebar.text("dd")

def load_data(file_path):
    return pd.read_csv(file_path, encoding='cp949')

def display_map(company_info):
    m = folium.Map(location=[company_info['Latitude'], company_info['Longitude']], zoom_start=15)
    folium.Marker([company_info['Latitude'], company_info['Longitude']], popup=company_info['회사명']).add_to(m)
    st_folium(m)

def crawl_blog(keyword, max_results=2):
    base_url = "https://section.blog.naver.com/Search/Post.naver?pageNo={}&rangeType=ALL&orderBy=sim&keyword="
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    results = []

    search_url = base_url.format(1) + keyword
    driver.get(search_url)
    time.sleep(random.uniform(2, 4))  # 랜덤한 sleep 시간 추가

    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 3))  # 랜덤한 sleep 시간 추가

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    desc_inner_elements = soup.find_all(class_="desc_inner")

    for desc_inner_element in desc_inner_elements[:max_results]:
        href_value = desc_inner_element.get('href')
        if not href_value:
            continue

        m_url = "https://m." + href_value.replace("https://","")
        res = requests.get(m_url)
        time.sleep(random.uniform(2, 2))
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "lxml")

        date_element = soup.find("p", attrs={'class':'blog_date'})
        title_element = soup.find("span", class_=lambda x: x and ("se-fs- se-ff-" in x or "se-fs-fs26 se-ff-" in x))
        text_element = soup.find("div", attrs={'class':'se-main-container'})

        if date_element and title_element and text_element:
            date = date_element.text.rstrip()
            title = title_element.text
            text = text_element.text.replace("\n", "").replace("\t", "")

            results.append({
                'date': date,
                'href': href_value,
                'title': title,
                'text': text[:300]  # 본문을 최대 300자로 제한
            })

    driver.quit()
    return results


