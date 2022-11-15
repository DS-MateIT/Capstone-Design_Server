from selenium import webdriver
import random
import time
from webdriver_manager.chrome import ChromeDriverManager

# 최신 크롬 드라이버 사용하도록 세팅: 현재 OS에 설치된 크롬 브라우저 버전에 맞게 cache에 드라이버 설치
from selenium.webdriver.chrome.service import Service
service = Service(ChromeDriverManager().install())


def naver_keyword(keywords):
    #keywords += " "    # 스페이스로 한 칸 뛰고 검색
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('http://www.naver.com/')
    time.sleep(5)
    
    input_element = driver.find_element_by_class_name('green_window')  # 검색창
    input_element.find_element_by_name('query').send_keys(keywords)  # 키워드 입력
    #input_element.click()
    
    time.sleep(10)
    uls = driver.find_elements_by_class_name('kwd_lst')
    
    auto_keywords = []   # 자동완성
    breaker = False
    for ul in uls:
        lis = ul.find_elements_by_tag_name('li')
        if len(lis):
            for li in lis:
                keyword = li.find_element_by_class_name('kwd').find_element_by_class_name('fix').text.strip()
                #if keyword == keywords: continue    # 검색어는 결과에 추가하지 않음
                if keyword == '': continue   # 빈 검색어는 추가하지 않음
                auto_keywords.append(keyword)
                
                if len(auto_keywords) >= 3:
                    breaker = True
                    break
            if breaker == True:
                break

    
    if auto_keywords:
        print("자동완성어 추출 성공!!\n")
    elif not auto_keywords:
        print("자동완성어 없어!\n")
    
    print(auto_keywords)

    driver.close()
    
    return auto_keywords
