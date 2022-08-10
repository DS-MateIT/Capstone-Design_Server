# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 20:15:58 2022

@author: leesw
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 15:54:22 2022

@author: maincom
"""

#googleapiclient 오류시   $ pip install --upgrade google-api-python-client

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
import pandas as pd

##### youtube data api

API_KEY = "AIzaSyBxI9rBVDEieKc0FmBJKdTJDtG4vWD_4Zc"    # API Key
YOUTUBE_API_SERVICE_NAME="youtube"
YOUTUBE_API_VERSION="v3"
youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=API_KEY)


# 검색 결과 가져오기
search_response = youtube.search().list(
    q = "설현한밤",   # 검색어 입력하기 (1개 이상 단어 가능) ex) 설현 한밤   
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


#####spyder Variable explorer에서 df 확인 

print(videoId[0])
print(videoId[1])
print(videoId[2])

url0 = "https://www.youtube.com/watch?v="+videoId[0]
url1 = "https://www.youtube.com/watch?v="+videoId[1]
url2 = "https://www.youtube.com/watch?v="+videoId[2]

#영상 길이 상 url2 로 테스트 

print(url2)
#####트와이스 쯔위, “내가 설현보다 부족해” 거짓말탐지기 결과 @한밤의 TV연예 545회 20160302

####pytube 영상 다운로드
from pytube import YouTube
import glob
import os.path

#유튜브 전용 인스턴스 생성
yt = YouTube(url2)

print(yt.streams.filter(only_audio=True).all())

#특정영상 다운로드
yt.streams.filter(only_audio=True).first().download()
print('success')

# 확장자 변경
files = glob.glob("*.mp4")
for x in files:
   if not os.path.isdir(x):
      filename = os.path.splitext(x)
      try:
         os.rename(x,filename[0] + '.mp3')
      except:
         pass
   

##로컬에 mp3 파일 다운 확인        
## pytube 다운 시 파일명에 , 가 누락???

####s3연동 


import os
import boto3

from dotenv import load_dotenv
load_dotenv(verbose=True)

def aws_session(region_name='us-east-2'):
    return boto3.session.Session(aws_access_key_id=os.getenv('AKIA525DE7YW2DGHX3XQ'),
                                aws_secret_access_key=os.getenv('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'),
                                region_name=region_name)


#Amazon S3 연결확인
s3 = boto3.resource('s3')  # s3에 대한 권한 및 상태를 s3(변수)에 저장
for bucket in s3.buckets.all():
    print(bucket)

#결과 s3.Bucket(name='mateityoutube')


######로컬에서 s3로 파일 업로드
import boto3
##filepath = "C:/Users/maincom/Desktop/졸프/22_hg076_server/20220719 청룡 어워즈 설현 실물.mp4"
#"C:/Users/maincom/Desktop/졸프/김연아의 첫만남 스토리.mp3"
BUCKET_NAME = "mateityoutube"
print(videoId[2])

filepath = "C:/Users/maincom/Desktop/졸프/" + title[2]+".mp3"

#filepath = "C:/Noggro/" + title[2]+".mp3"

key = videoId[2]+"/"+ title[2]+".mp3"

#key 셍성할 폴더 / 업로드할 파일명
#key = 'V2OPlREZP5Y/본격 공개! 설현의 뷰티 노하우 ‘심쿵 꿀팁’ @본격연예 한밤 13회 20170228.mp3'

s3 = boto3.client('s3')
res = s3.upload_file(filepath, BUCKET_NAME, key)

#s3 업로드 완료


##Python용 AWS SDK(Boto3) TR https://docs.aws.amazon.com/ko_kr/transcribe/latest/dg/tagging.html
from __future__ import print_function
import time
import boto3
transcribe = boto3.client('transcribe', 'us-east-2')
job_name = videoId[2] + "dic"   #실행할 tr 이름
uri = "s3://mateityoutube/" + videoId[2]+ "/" + title[2]+".mp3"  #Tr에 필요한 영상 주소
job_uri = uri
#job_uri = "s3://mateityoutube/V2OPlREZP5Y/본격 공개! 설현의 뷰티 노하우 ‘심쿵 꿀팁’ @본격연예 한밤 13회 20170228.mp3"

transcribe.start_transcription_job(
    TranscriptionJobName = job_name,
    Media = {
        'MediaFileUri': job_uri
    },
    OutputBucketName = 'mateityoutube',
    OutputKey = videoId[2]+ "/" , 
    LanguageCode = 'ko-KR', 
    Tags = [
        {
            'Key':'color',    #??
            'Value':'blue'
        }
    ] ,
    Settings={
        'VocabularyName': 'SHonly',
        #딕셔너리 추가 반영
    #    'ShowSpeakerLabels': True|False,
    #    'MaxSpeakerLabels': 123,
    #    'ChannelIdentification': True|False,
    #    'ShowAlternatives': True|False,
    #    'MaxAlternatives': 123,
    #    'VocabularyFilterName': 'string',
    #    'VocabularyFilterMethod': 'remove'|'mask'|'tag'
    },
      
)

while True:
    status = transcribe.get_transcription_job(TranscriptionJobName = job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    print("Not ready yet...")
    time.sleep(5)
print(status)

##TR 실행 완료 - 추후에 Custom Voca 추가하기 




#파일 업/다운로드를 위한 S3 커넥션
AWS_ACCESS_KEY = "AKIA525DE7YW2DGHX3XQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_S3_BUCKET_REGION = "us-east-2"
AWS_S3_BUCKET_NAME = "mateityoutube"


def s3_connection():
    '''
    s3 bucket에 연결
    :return: 연결된 s3 객체
    '''
    try:
        s3 = boto3.client(
            service_name='s3',
            region_name=AWS_S3_BUCKET_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    except Exception as e:
        print(e)
        #exit(ERROR_S3_CONNECTION_FAILED)
    else:
        print("s3 bucket connected!")
        return s3

def s3_put_object(s3, bucket, filepath, access_key):
    '''
    s3 bucket에 지정 파일 업로드
    :param s3: 연결된 s3 객체(boto3 client)
    :param bucket: 버킷명
    :param filepath: 파일 위치
    :param access_key: 저장 파일명
    :return: 성공 시 True, 실패 시 False 반환
    '''
    try:
        s3.upload_file(filepath, bucket, access_key)
    except Exception as e:
        print(e)
        return False
    return "SUCCESS"
    
def s3_get_object(s3, bucket, object_name, file_name):
    '''
    s3 bucket에서 지정 파일 다운로드
    :param s3: 연결된 s3 객체(boto3 client)
    :param bucket: 버킷명
    :param object_name: s3에 저장된 object 명
    :param file_name: 저장할 파일 명(path)
    :return: 성공 시 True, 실패 시 False 반환
    '''
    try:
        s3.download_file(bucket, object_name, file_name)
    except Exception as e:
        print(e)
        return False
    return True


# S3에 위치한 json 파일(STT TR 파일) 을 읽어오기( 다운로드 없이 바로 )

import json
import boto3
s3 = boto3.resource('s3')
#s3://mateityoutube/2DEDNW5Jq4Q/2DEDNW5Jq4Q.json
obj = s3.Object(AWS_S3_BUCKET_NAME, videoId[2]+"/"+ videoId[2] + ".json")
#obj = s3.Object(AWS_S3_BUCKET_NAME, videoId[2]+"/"+ videoId[2] + "dic.json")
#읽기...
data = obj.get()['Body'].read().decode('utf-8') 

stt = json.loads(data)
stt = stt['results']['transcripts'][0]['transcript']


#@@----------------------df에 script 추가 (임의로 하나의 스크립트만)
for i in range(len(video_json)):
    df['script']=stt











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
                       '역사', '씨', '요' , '중' , '약간','또', '때', '이제', '이', '그', '처럼'
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

#@@----------------------script 
script_token = df['script'].astype('str')
for i in range(len(script_token)):
    #title_token = t.morphs(re.sub(r'[^\w]', ' ', str(line)))  # 형태소
    script_token[i] = t.nouns(re.sub(r'[^\w]', ' ', script_token[i]))  # 명사 저장
    script_token[i] = ' '.join(script_token[i])
print(script_token)




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
#print(tfidf_script_matrix)

#matrix.sort(reverse=True)

print()

#@@-------------------------스크립트 적용 
tfidf_script = TfidfVectorizer(stop_words=stop_words, max_features=100)
tfidf_script_fit_trans = tfidf_script.fit_transform(script_token)
tfidf_script.vocabulary_


print(tfidf_script_fit_trans.shape)

script_sim = tfidf_script_fit_trans.toarray()   # tfidf 값을 array로

# tfidf 행렬- 생성한 단어집합 행렬, 중요도가 높은 단어일수록 1에 가까움
tfidf_script_matrix = pd.DataFrame(
    script_sim, 
    columns=tfidf_script.get_feature_names()
)


import nltk

import collections
collections.Counter(maxidx).most_common(3)


#ko = nltk.Text(tokens_ko)
#ko.vocab().most_common(50)


maxidx_sc = tfidf_script_matrix.idxmax()

print(maxidx_sc)   # 해당 단어와 연관이 가장 높은 





#@@----------------워드클라우드 
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS
from PIL import Image 
import numpy as np


# 2. 유사도 결과 단어로 ? - 행렬
tfidf_script_matrix.T.sum(axis=1) #용어당 빈도
tfidf_script_matrix

fp = 'malgun'  #fp = 'Pretendard-Regular.otf' 예쁜 폰트,,
mask = np.array(Image.open('cloud.png')) #구름모양
wc = WordCloud(background_color="#1F1E1E", max_words=50, width=1000, height=800, font_path=fp ,
           mask=mask ,colormap='Set3').generate_from_frequencies(tfidf_script_matrix.T.sum(axis=1))

#wc = WordCloud(background_color="#1F1E1E", max_words=3, width=1000, height=800, font_path=fp ,
#           mask=mask ,colormap='Set3').generate_from_frequencies(tfidf_script_matrix.T.sum(axis=1))

#test = tfidf_script_matrix.T(axis=1)
#test2 = collections.Counter(test).most_common(3)
#test2[0]
plt.figure(figsize=(32, 15))
               
plt.imshow(wc)
plt.axis('off')
plt.show()     

wc.to_file(videoId[2]+".png") #이미지 파일로 저장

#로컬에 워드클라우드 이미지 저장



#@-------------워드클라우드 S3에 업로드 
s3 = boto3.client('s3')
#filepath = "C:/Noggro/" + videoId[2] +  ".png"
filepath = "C:/Users/maincom/Desktop/졸프/" + videoId[2] +  ".png"
s3_put_object(s3, AWS_S3_BUCKET_NAME, filepath, videoId[2]+ "/" +videoId[2]+".png")

#--안드로이드 cognito로 워드클라우드 띄우기 테스트 성공 



##########################일치율 계산 함수
from konlpy.tag import Okt #한글
import isodate 

def search_word_cal(word) :
    #word='설현 한밤'
    thumb = [' '] #썸네일 없음
    
    okt = Okt()
    search_word = okt.morphs(word) # 형태소로 추출

    print(search_word) 
    word_count = len(search_word) #search 키워드 명사의 개수
    
    title_count = [int(sum((title.count(search_word[j])) for j in range(word_count))) for title in title_token] #2
    thumb_count = [int(sum((th.count(search_word[j])) for j in range(word_count))) for th in thumb] #0
    desc_count = [int(sum((desc.count(search_word[j])) for j in range(word_count))) for desc in desc_token]
    script_count = [int(sum((script.count(search_word[j])) for j in range(word_count))) for script in script_token]
    
    
    playtime = [] #PTnMnS 형식
    playtime_second_list = [] #초로 변환한 형식
    
    for i in range(len(df)):
        request = youtube.videos().list(
            part='contentDetails',
            id=df['videoId'][i]
        )
        response = request.execute()
        
        playtime.append(response['items'][0]['contentDetails']['duration'])
            
        
        #playtime 초로 변환하기 #pip install isodate 설치하고 import 실행
        dur = isodate.parse_duration(playtime[i])
        playtime_second = int(dur.total_seconds()) #초로 변환
        #print(playtime_second)
        #print(type(playtime_second))
        
        playtime_second_list.append(playtime_second)
        
    print(playtime) 
    print(playtime_second_list)
    
    df['playtime'] = playtime
    
    
    
     # 일치율 계산 함수     인덱스 02 
    def calculation(title_count, thumb_count, desc_count, script_count, playtime):
        result = []
        #print(thumb_count)
        for i in range(len(thumb_count)): 
            
            # 영상 길이 30초 단위로
            time = playtime_second_list[2]/30 
            print(time)
            
            result.append(((title_count[2]*30 + thumb_count[0]*10 + desc_count[2]*5 + script_count[2]*20) / time) / word_count)
            
            #100프로가 넘지 않기 위한 조치 ?? 가중치,,, 비율(비중) 조정 
            ##좀 더 추가요소 넣고싶어요 ㅜㅜ
            
            print(title_count[2]) 
            print(desc_count[2]) 
            print(script_count[2]) 
            
        return result


    result = calculation(title_count, thumb_count, desc_count, script_count, playtime)

    print(result) 

search_word_cal('설현한밤')


search_word_cal('AOA 설현 한밤') #[16.666666666666668] 


search_word_cal('김연아') #[16.666666666666668] 


    
   

'''
- 지금은 스크립트가 1개만 반영되는데 스크립트가 5개까지 반영되도록 변경(TR도 5번)
- 일치율코드 - 시간/수식 수정
- result.append(((title_count[2]*30 + thumb_count[0]*10 + desc_count[2]*5 + script_count[2]*20) / time) / word_count)
ㅎ
30 + 10 + 5 + 20 = 65 

title_count[2]*30 값의 범위가  - 40 넘지 않도록 비율로? 환산

thumb_count[0]*10 값의 범위가 - 20

desc_count[2]*5 값의 범위가 - 20

script_count[2]*20 값의 범위가 -  40

(썸네일과 디스크립션이 불필요한 정보가 많다 )

time을 15초마다 / 20초마다 나누기로 했는데 

영상에 시간 나누는거 분이나 초 없을때 오류 잡기 ( 먼저하는사람 공유좀 ) 

**영상 5개정도 돌려서 일치율 값 여러개 돌려보기** - **기록해놔!** 

( 검색어는 아무거나 하는데 기록은 잘 해놔야 한다 )

영상 아이디값 - 영상길이 - 수식(15초단위로 나누었는지 20초 단위로 나누었는지 등 특별사항) - 일치율값

'''

'''
결과 기록하기 예시
search_word_cal('설현') #30초단위 #일치율값 [23.333333333333332]
search_word_cal('설현') #[23.333333333333332]
search_word_cal('설현 한밤') #[25.0]
search_word_cal('설현한밤') #[25.0]
search_word_cal('AOA 설현 한밤') #[16.666666666666668] 
search_word_cal('AOA설현한밤') #[16.666666666666668]

search_word_cal('한밤 떡볶이') #[13.333333333333334] #OX - 어그로성 ? 
search_word_cal('설현 노하우') #[23.333333333333332] #OO
search_word_cal('pretty 설현 한밤') #[16.666666666666668] # OOX  - 어그로성 ? 
search_word_cal('한밤 덕새 라이언') #[8.88888888888889] # OXX  - 어그로성 ? 
search_word_cal('노하우') #[23.333333333333332]
search_word_cal('화장실') #[13.333333333333334] #스크립트 하나만 나온 단어 
# 하나도 안나온 단어 - 0