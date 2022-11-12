# keywordtool.io
import selenium
from selenium import webdriver
from time import sleep
import time
import random

URL = "https://keywordtool.io/youtube/"
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.keys import Keys
#from pymouse import PyMouse
import time

def youtube_keyword(keywords):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(URL)
    
    # verify human 클릭
    time.sleep(3)

    #select_youtube = driver.find_element_by_class_name('nav-item-search-youtube nav-item').find_element_tag_name('a').
    #input_element = driver.find_element_by_xpath('//input[@id="search-form-youtube-keyword-md"]')  # 검색창
    input_element = wait(driver, 50).until(EC.element_to_be_clickable((By.XPATH, '//input[@id="search-form-youtube-keyword-md"]')))
    input_element.send_keys(keywords)  # 키워드 입력
    input_element.click()
    
    time.sleep(3)

    #search_button = driver.find_element_by_class_name('search-form-youtube-submit')
    search_button = wait(driver, 50).until(EC.element_to_be_clickable((By.CLASS_NAME, 'search-form-youtube-submit')))
    search_button.click()
    time.sleep(10)
    
    #import pyautogui
    #print(pyautogui.position())
    
    # verify human 클릭
    #m = PyMouse()
    #time.sleep(4) 
    #m.press(130,520) 
    #m.release(130,520)
    #m.press(130,520) 
    #time.sleep(4) # press for 4 seconds
    #m.release(130,520)

    #time.sleep(5)
    driver.execute_script("window.scrollTo(0, 300)")   # 페이지 스크롤
    auto_keywords = []   # 자동완성

    #table = driver.find_element_by_class_name('col-keyword p-0')   # 테이블
    table = driver.find_element_by_xpath('//table[@class="search-results-table table table-hover"]')
    #tables = driver.find_elements_by_xpath('//td[@class="col-keyword p-0"]')
    tbody = table.find_element_by_xpath('//tbody')
    rows = tbody.find_elements_by_xpath('//tr')
    
    breaker = False   # 이중 for문을 빠져나가기 위한 bool변수
    for cell in rows:
        
        body=cell.find_elements_by_xpath('//td[@class="col-keyword p-0"]/div')
        for item in body:
            #item.find_element_by_xpath('//span[@class="keyword-panel-keyword cursor-pointer"]')#

            time.sleep(3)
            keyword = item.find_element_by_class_name('font-weight-bold').text
            #keyword = wait(item, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'font-weight-bold'))).text
            
            if keyword == keywords: continue    # 검색어인 '설현'은 결과에 추가하지 않음
            auto_keywords.append(keyword)
            
            if len(auto_keywords) >= 3:
                breaker = True
                break
        if breaker == True:
            break

    for word in auto_keywords:   # 빈 요소는 제거
        if not word:
            auto_keywords.remove(word)
    
    if auto_keywords:
        print("자동완성어 추출 성공!!\n")
    elif not auto_keywords:
        print("자동완성어 없어!")
    print(auto_keywords)
    driver.close()
    
    return auto_keywords


# keywords = youtube_keyword('지구오락실')
'''
keywords = youtube_keyword('마라탕 먹방')

# keywords_list = ['설현', '김연아', '마라탕', '먹방 유튜버', '힙한 플레이리스트', '앵무새', '귀여운 앵무새',
                 #'스펀지 웃긴 편', '한소희', '간단한 요리']

keywords_list = ['설현', '김연아', '마라탕', '먹방 유튜버']
    
    
    
import pandas as pd
result = pd.DataFrame(columns=['search_word', 'result_words'])

search_list=[]
result_list=[]
for i in range(len(keywords_list)):
    search_list.append(keywords_list[i])
    result_list.append(youtube_keyword(keywords_list[i]))
    
result['search_word'] = search_list
result['result_words'] = result_list
'''


# keywords = youtube_keyword('설현')  ['설현 직캠', '설현 직캠 레전드', '설현 레전드']
# keywords = youtube_keyword('김연아 결혼')  ['김연아 결혼식', '김연아 결혼 발표', '김연아 결혼 사주']
# keywords = youtube_keyword('마라탕 먹방')  ['마라탕 먹방 asmr', '마라탕 먹방 레전드', '마라탕 먹방 상윤쓰']