from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
import pandas as pd
import config
##### youtube data api

API_KEY = config.youtube_api_key    # API Key
YOUTUBE_API_SERVICE_NAME="youtube"
YOUTUBE_API_VERSION="v3"
youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=API_KEY)

# 검색 결과 가져오기
search_response = youtube.search().list(
    q = "설현",   # 검색어 설현
    order = "relevance",    # 관련성 순으로 보여줌
    part = "snippet",
    maxResults = 30
).execute()

print(search_response)

# 영상 title, description, thumbnail등의 정보는 items항목에 있으므로 items가져옴
video_json = {}
json_index = 0


for item in search_response['items']:
    if item['id']['kind'] == 'youtube#video':
        video_json[json_index] = {"videoId": item['id']['videoId'], 
                                  "title": item['snippet']['title'], 
                                  "desc" : item['snippet']['description'], 
                                  "thumbnail": item['snippet']['thumbnails']['medium']['url']}
    
        json_index += 1 
    
# json을 데이터프레임으로 변환
videoId = []
title = []
desc = []
thumbnail = []

for i in range(len(video_json)):
    videoId.append(video_json[i]['videoId'])
    title.append(video_json[i]['title'])
    desc.append(video_json[i]['desc'])
    thumbnail.append(video_json[i]['thumbnail'])
    
df = pd.DataFrame({"videoId": videoId,
                   "title": title,
                   "desc": desc,
                   "thumbnail": thumbnail})



##### tf-idf
stop_words = [')','?','1','"(', '_', ')/','\n','.',',', '<','!','(','(', '??','..', '4', '|', '>', '?(', '"…', '#', '&', '・', "']",'.',' ','/',"'",'’','”','“','·', '[','!','\n','·','‘','"','\n ',']',':','…',')','(','-', 'nan','가','요','답변','...','을','수','에','질문','제','를','이','도',
                      '좋','1','는','로','으로','2','것','은','다',',','니다','대','들',
                      '들','데','..','의','때','겠','고','게','네요','한','일','할',
                      '10','?','하는','06','주','려고','인데','거','좀','는데','~','ㅎㅎ',
                      '하나','이상','20','뭐','까','있는','잘','습니다','다면','했','주려',
                      '지','있','못','후','중','줄','6','과','어떤','기본','!!',
                      '단어','라고','합','가요','....','보이','네','무지','했습니다',
              '이다','대해','에게','입니다','있다','사람','대한','3','합니다','및','장','에서','하고','검','한다','만',
             '적', '성', '삼', '등', '전', '인', '그', '했다', '와', '위', '해', '권', '된', '서', '말', '분',
             '것', '그', '이', '수', '최고', '우리', '생각', '자신', '이야기', '점', '현실', '더', '보고', '존재', '모습', 
                       '속', '말', '장면', '일', '대한', '뿐',  '가장', '때', '정말', '지금', '나', '상황', '정도' '면', '습', '게', '자', '끝', '볼', '건', '못', 
                       '마치', '기도', '보', '곳', '그', '이상', '원래', '일이', '전', '사람', '도', '막', '를', '다른', '부터', '자기', '시대','평',
                        '뭐', '더', '막상', '전혀', '내', '살', '현재', '지금', '이제',  '사', '인', '법',  '꼭', '간','향후', '당신', '손', 
                       '저', '경우', '전', '얼마', '일단', '걸', '안', '바로', '그냥', '위해', '때문', '은', '앞',  '볼', '자기', '처럼', '순간', '앞', '감정', 
                       '관련', '일', '가야', '살', '보','요', '보고', '수', '제', '두', '몇', '제', '죽', '때', '해', '이', '중', '내내', '후',   '감',
                       '여러','대한', '것', '시작', '래야', '진짜','또', '수도', '오히려', '니', '여기', '꼭', '과연', '나라', '자', '과거', '최후', '무엇',
                       '누가', '뒤', '얘기', '방식', '알', '그것', '탓', '계속', '방법', '대해', '마지막', '악', '처음', '기분', '의미', '놈', 
                       '역사'
             ]

from konlpy.tag import Okt
import re

t=Okt()

title_token = df['title'].astype('str')

for i in range(len(title_token)):
    #title_token = t.morphs(re.sub(r'[^\w]', ' ', str(line)))  # 형태소
    title_token[i] = t.nouns(re.sub(r'[^\w]', ' ', title_token[i]))  # 명사 저장
    title_token[i] = ' '.join(title_token[i])    # 토큰화 리스트를 문자열로
print(title_token) 

desc_token = df['desc'].astype('str')
for i in range(len(desc_token)):
    #title_token = t.morphs(re.sub(r'[^\w]', ' ', str(line)))  # 형태소
    desc_token[i] = t.nouns(re.sub(r'[^\w]', ' ', desc_token[i]))  # 명사 저장
    desc_token[i] = ' '.join(desc_token[i])
print(desc_token)


from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(stop_words=stop_words)  
tfidf_fit_trans = tfidf.fit_transform(title_token)
tfidf.vocabulary_   # 각 단어와 매핑된 인덱스 출력

tfidf_desc = TfidfVectorizer(stop_words=stop_words, max_features=100)
tfidf_desc_fit_trans = tfidf_desc.fit_transform(desc_token)
tfidf_desc.vocabulary_

print(tfidf_fit_trans.shape)  # (16, 100), 100은 16개의 제목에 있는 단어들을 분리한 개수
print(tfidf_desc_fit_trans.shape)

title_sim = tfidf_fit_trans.toarray()   # tfidf 값을 array로

# tfidf 행렬- 생성한 단어집합 행렬, 중요도가 높은 단어일수록 1에 가까움
# tfidf는 스크립트에 대해서 하는 게 좋을 듯
# 싶었는데 제목도 길이가 긴 경우는 괜찮은듯
tfidf_matrix = pd.DataFrame(
    title_sim, 
    columns=tfidf.get_feature_names()
)

desc_sim = tfidf_desc_fit_trans.toarray()
desc_matrix = pd.DataFrame(
    desc_sim,
    columns=tfidf_desc.get_feature_names()
)


maxidx = tfidf_matrix.idxmax()

print(maxidx)   # 해당 단어와 연관이 가장 높은 제목


#### 일치율 계산 - 일단 세 개 영상만 가지고..
#search_word = maxidx
search_word = '설현'
thumb = ['(마스크 피해자) 하핫~ 설현입니닷 "TV에서 못 본 것 같아요~" 설현 못 알아본 손님', 
         '미니 팬미팅 HOT한 알바생 설현 인기 폭발 설현 등신대 포즈',
         '5년만에 불편한 만남, 지코가 설현 만날때 했던 짓']

title_count = [int(title.count(search_word)) for title in title_token]
thumb_count = [int(th.count(search_word)) for th in thumb]
desc_count = [int(desc.count(search_word)) for desc in desc_token]

playtime = []
for i in range(len(df)):
    request = youtube.videos().list(
        part='contentDetails',
        id=df['videoId'][i]
    )
    response = request.execute()
    
    playtime.append(response['items'][0]['contentDetails']['duration'])

print(playtime)

df['playtime'] = playtime


# 일치율 계산 함수    
def calculation(title_count, thumb_count, desc_count, stt_count, playtime):
    result = []
    for i in range(len(thumb_count)):
        m = re.search('PT(.+?)M', playtime[i])
        if m:
            minute = m.group(1)   
        dura1 = int(minute)*2 ##1분당 count를 2로 계산(30초씩 자르기)
        
        s = re.search('M(.+?)S', playtime[i])
        if s:
            second = s.group(1)
    
        if ( 30<= int(second) <= 59):
            dura2 = 1    ##30초 이상이면 count1
        else :
            dura2 = 0.5    #30초 미만이면 count 0.5
        time = dura1 + dura2   #전제 나누기값 (영상길이)
        result.append((title_count[i]*60 + thumb_count[i]*20 + desc_count[i]*10 + stt_count[i]*40) / time)
    return result

stt_count=[20, 18, 10]   # stt는 임의로..
result = calculation(title_count, thumb_count, desc_count, stt_count, playtime)
