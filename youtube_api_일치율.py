from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
import pandas as pd
#import config
import myconfig

##### youtube data api

API_KEY =  myconfig.youtube_api_key # API Key
YOUTUBE_API_SERVICE_NAME="youtube"
YOUTUBE_API_VERSION="v3"
youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=API_KEY)


# 검색 결과 가져오기
search_response = youtube.search().list(
    q = "설현 한밤",   # 검색어 입력하기 (1개 이상 단어 가능) ex) 설현 한밤   
    order = "relevance",    # 관련성 순으로 보여줌
    part = "snippet",
    maxResults = 5
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
df['script'] = pd.Series()    # 빈 script컬럼 만들어둠


urls = []
for i in range(5):
    urls.append("https://www.youtube.com/watch?v="+str(videoId[i]))

####pytube 영상 다운로드
from pytube import YouTube
import glob
import os.path

new_title = []
#유튜브 전용 인스턴스 생성
for i in range(len(urls)):
    yt = YouTube(urls[i])
    
    print(yt.streams.filter(only_audio=True).all())
    
    #특정영상 다운로드
    yt.streams.filter(only_audio=True).first().download()
    print('success')
    
    # 확장자 변경
    files = glob.glob("*.mp4")
    for x in files:
        if not os.path.isdir(x):
            filename = os.path.splitext(x)
            new_title.append(filename)
            try:
                os.rename(x,filename[0] + '.mp3')
            except:
                pass
        
####s3연동 
import os
import boto3

from dotenv import load_dotenv
load_dotenv(verbose=True)

def aws_session(region_name='us-east-2'):
    return boto3.session.Session(aws_access_key_id=os.getenv('AKIA525DE7YW2DGHX3XQ'),
                                aws_secret_access_key=os.getenv('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'),
                                region_name=region_name)

aws_session('us-east-2')
#Amazon S3 연결확인
s3 = boto3.resource('s3')  # s3에 대한 권한 및 상태를 s3(변수)에 저장
for bucket in s3.buckets.all():
    print(bucket)

import boto3

BUCKET_NAME = "mateityoutube"

#filepath = "C:/Noggro/" + title[2]+".mp3"
#key = videoId[2]+"/+ title[2]+".mp3


#filepath =[]
#key = []
#for i in range(len(urls)):
#    filepath.append("C:/Noggro/" + str(new_title[i][0]) + ".mp3")
#    key.append(videoId[i]+"/"+ title[i]+".mp3")
    
filepath =[]
key = []
for i in range(len(urls)):
    filepath.append("C:/Users/leesw/Desktop/MATEIT_SERVER/" + str(new_title[i][0]) + ".mp3")
    key.append("youtube_datas/"+videoId[i]+"/"+ title[i]+".mp3")
    

#key 셍성할 파일 / 업로드할 파일명
#key = 'V2OPlREZP5Y/본격 공개! 설현의 뷰티 노하우 ‘심쿵 꿀팁’ @본격연예 한밤 13회 20170228.mp3'

s3 = boto3.client('s3')

for i in range(len(filepath)):
    #res = s3.upload_file(filepath[i], BUCKET_NAME, key[i])   #
    res = s3.upload_file(filepath[i], BUCKET_NAME, key[i])
    
##Python용 AWS SDK(Boto3) TR https://docs.aws.amazon.com/ko_kr/transcribe/latest/dg/tagging.html
from __future__ import print_function
import time
import boto3

#AWS_ACCESS_KEY = config.AWS_ACCESS_KEY
#AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
#AWS_S3_BUCKET_REGION = config.AWS_S3_BUCKET_REGION
#AWS_S3_BUCKET_NAME = config.AWS_S3_BUCKET_NAME

transcribe = boto3.client('transcribe', 'us-east-2')


# conflict예외 발생할 때: transcribe.delete_transcription_job(TranscriptionJobName=job_name)
# transcribe.delete_transcription_job(TranscriptionJobName=videoId[4])

###### transcribe 순서가 뒤죽박죽인 이유는?
# s3버킷에 올릴 때
# new_title과 title의 순서가 달라서 key랑 filepath가 가리키는 영상이 달라짐..
# 위의 pytube 부분 수정함
""" 파일 목록 확인
s3 = boto3.client('s3', region_name='us-east-2', verify=False)

filenames = []
for i in range(len(videoId)):
    result = s3.list_objects(Bucket=AWS_S3_BUCKET_NAME, Prefix=videoId[i]+"/"+title[i]+".mp3")
    print(result)
    for item in result['Contents']:
        files = item['Key']
        print(files)
        filenames.append(files)   #optional if you have more filefolders to got through.
"""        
for i in range(len(videoId)):
    job_name = videoId[i] + "dic"   #실행할 tr 이름 #dic반영할 경우 
    uri = "s3://mateityoutube/youtube_datas/" + videoId[i]+ "/" + title[i]+".mp3"  #Tr에 필요한 영상 주소
    job_uri = uri
#job_uri = "s3://mateityoutube/V2OPlREZP5Y/본격 공개! 설현의 뷰티 노하우 ‘심쿵 꿀팁’ @본격연예 한밤 13회 20170228.mp3"

    transcribe.start_transcription_job(
        TranscriptionJobName = job_name,
        Media = {
            'MediaFileUri': job_uri
        },
        OutputBucketName = 'mateityoutube',
        OutputKey = "youtube_datas/" +videoId[i]+ "/" , 
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

#파일 업/다운로드를 위한 S3 커넥션
AWS_ACCESS_KEY = "AKIA525DE7YW2DGHX3XQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_S3_BUCKET_REGION = "us-east-2"
AWS_S3_BUCKET_NAME = "mateityoutube"


# S3에 위치한 json 파일(STT TR 파일) 을 읽어오기( 다운로드 없이 바로 )

import json
import boto3
s3 = boto3.resource('s3', 'us-east-2')
#s3://mateityoutube/2DEDNW5Jq4Q/2DEDNW5Jq4Q.json

items = []
stt = []

for i in range(len(videoId)):
    obj = s3.Object(AWS_S3_BUCKET_NAME, "youtube_datas/" + videoId[i]+"/"+ videoId[i] + "dic.json")
    #읽기...
    data = obj.get()['Body'].read().decode('utf-8') 
    items.append(data)
    
#obj = s3.Object(AWS_S3_BUCKET_NAME, videoId[4]+"/"+ videoId[4] + ".json")
#data = obj.get()['Body'].read().decode('utf-8') 
#items.append(data)

for i in range(len(items)):
    items[i] = json.loads(items[i])
    stt.append(items[i]['results']['transcripts'][0]['transcript'])


#@@----------------------df에 script 추가
df['script']=stt

##df_to_csv = df.to_csv('./seolhyun_csv.csv', encoding='utf-8-sig')  # csv로 저장

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

title_token = df[['videoId','title']].astype('str')

for i in range(len(title_token)):
    #title_token = t.morphs(re.sub(r'[^\w]', ' ', str(line)))  # 형태소
    title_token.iloc[i, 1]  = t.nouns(re.sub(r'[^\w]', ' ', title_token.iloc[i, 1]))  # 명사 저장
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

print(tfidf_matrix.values)

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS
#pip install wordcloud
from PIL import Image 
import numpy as np



for i in range(len(tfidf_script_matrix)):
    
    fp = 'malgun'  #fp = 'Pretendard-Regular.otf' 예쁜 폰트,,
    mask = np.array(Image.open('./resources/cloud.png')) #구름모양
    wc = WordCloud(background_color="#1F1E1E", max_words=50, width=1000, height=800, font_path=fp ,
               mask=mask ,colormap='Set3').generate_from_frequencies(tfidf_script_matrix.iloc[i, :])
    
    #wc = WordCloud(background_color="#1F1E1E", max_words=3, width=1000, height=800, font_path=fp ,
    #           mask=mask ,colormap='Set3').generate_from_frequencies(tfidf_script_matrix.T.sum(axis=1))
    
    #test = tfidf_script_matrix.T(axis=1)
    #test2 = collections.Counter(test).most_common(3)
    #test2[0]
    plt.figure(figsize=(32, 15))
                   
    plt.imshow(wc)
    plt.axis('off')
    plt.show()     
    
    wc.to_file(videoId[i]+".png")
    
    #wc.to_file("C:/server/wordcloud/" + videoId[i]+".png") #이미지 파일로 저장
    #wc.to_file(videoId[0]+".png") #이미지 파일로 저장
#float division by zero 오류 
#로컬에 워드클라우드 이미지 저장

def s3_put_object(s3, bucket, filepath, access_key):  # access_key가 아니라 s3버킷에 들어갈 파일명이다
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

#@-------------워드클라우드 S3에 업로드 
s3 = boto3.client('s3')
#filepath = "C:/Noggro/" + videoId[2] +  ".png"
for i in range(len(videoId)):
    filepath = "C:/Users/leesw/Desktop/MATEIT_SERVER/" + videoId[i] +  ".png"
    #s3://mateityoutube/youtube_datas/776dS8Rmkhs/
    s3_put_object(s3, AWS_S3_BUCKET_NAME, filepath,"youtube_datas/"+ videoId[i]+ "/" +videoId[i]+".png")

#--안드로이드 cognito로 워드클라우드 띄우기 테스트 성공 


#####--------- 영상별로 tf-idf값이 높은(중요도가 높은) 단어 추출
# 주요 단어 3개 추출
import collections
import numpy as np

#print(tfidf_matrix.iloc[0, :].idxmax())
#print(tfidf_matrix.iloc[0, :].values)

keywords = pd.DataFrame(columns=['word', 'tf-idf'])

words = []
values = []


# 영상별로 tf-idf값이 가장 높은 단어(words)와 그 값(values)
# stt로 한 번..

for i in range(len(tfidf_script_matrix)):
    #words.append(sorted(tfidf_matrix.iloc[i, :].index, reverse=True))
    
    # tfidf matrix 내림차순 정렬
    sorted_tfidf = tfidf_script_matrix.iloc[i, :].sort_values(ascending=False)
    
    rows = list(sorted_tfidf.values)
    #word = sorted(tfidf_matrix.iloc[i, :].index, key=lambda row:row[0], reverse=True)

    values.append(rows[:3])   # 각 영상별 단어에 대한 tfidf값 3개씩
    
    # tfidf를 기준으로 내림차순 정렬
    word = list(sorted_tfidf.index)
    words.append(word[:3])


keywords['word'] = words
keywords['tf-idf'] = values

df['주요 단어(제목)'] = words
df['단어의 중요도(tf-idf)'] = values

##df_to_csv = df.to_csv('./seolhyun_hanbam_tfidf.csv', encoding='utf-8-sig')  # csv로 저장

##df = pd.read_csv('./seolhyun_csv2.csv')

    
# 결과 이미지
# 1) log1: count에 각각 로그 취함, 수식은 (15, 5, 3, 10), 시간은 /10
# -> 값의 범위는 고르게 잘 분포한 거 같은데 일치율이 그닥.. 정확하지 않음

# 2) log2: count 더해서 한번에 로그 취함, 수식'시간은 그대로
# -> 한번에 로그를 취해서 그런지 100을 곱했는데도 값이 크지 않음 최대가 31이고 보통 한자리..

# 3) MinMaxScaler -> 값 범위가 고르게 분포X
# 수식에서 scipt만 15로 변경
# 결과가 뭔가 맞는 거 같으면서도..? 100이 정말 많이 나옴
# 근데 앞의 log에서 결과가 잘 나오는 경우도 있음 -> '설현 입간판'
# 이게 배열의 원소들 간 비교하면서 스케일링을 하는 거라 맞는 건지는 잘 모르겠음


#### sentence bert
# stt에서 마침표 기준으로 문장 나누기
stt_list = []
for i in range(len(stt)):
    stt[i]= '.\n'.join(stt[i].split(". "))   # 마침표(.) 기준으로 문장 나누고 엔터
    stt_list.append(stt[i].splitlines())   # 엔터 기준으로 문자 split해서 한 줄씩


# stt를 (초반, 중반, 후반)으로 나누기
def list_chunk(lst, n):   # 리스트를 n개의 원소를 가지도록 나눔
    return [lst[i:i+n] for i in range(0, len(lst), n)]

start = []
middle = []
end = []

for i in range(len(stt_list)):
    length = len(stt_list[i])//3
    stt_list[i] = list_chunk(stt_list[i], length)
    
    start.append(stt_list[i][0])
    middle.append(stt_list[i][1])
    end.append(stt_list[i][2])
   
#pip intall tensorflow
#pip install torch
#pip install sentence_transformers
import tensorflow as tf
import torch
from sentence_transformers import util

# GPU 사용 설정
import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    except RuntimeError as e:
        print(e)
        
def sbert_stt_rate(model, mylist, mylist2):   
    # 인코딩
    embedding = model.encode(mylist)
    
    embedding2 = model.encode(mylist2)
    
    top_k = len(mylist)

    # 입력 문장 - 문장 후보군 간 코사인 유사도 계산 후,
    cos_scores = util.pytorch_cos_sim(embedding2, embedding)[0]

    # 코사인 유사도 순으로 `top_k` 개 문장 추출
    top_results = torch.topk(cos_scores, k=top_k)

    return top_results   # 유사도만 리턴




import joblib
# 모델 불러오기
my_model = joblib.load('models/myklue-roberta-base.pkl')
# FileNotFoundError: [Errno 2] No such file or directory: 'models/myklue-roberta-base.pkl'

#### (제목, 초반-중반)
# 초반-중반 합치기 
stt_start_middle = []
for i in range(len(start)):
    stt_start_middle.append('\n'.join(start[i][:3])+'\n'.join(middle[i][:3]))

top_results = []
#for i in range(len(stt_start_middle)):
#    top_results.append(sbert_stt_rate(my_model, title, stt_start_middle[i]))
top_results = sbert_stt_rate(my_model, title, stt_start_middle)

id_list = []
title_list = []
start_middle = []
list_score = []

#for i in range(len(stt_start_middle)):
for j, (score, idx) in enumerate(zip(top_results[0], top_results[1])):
    id_list.append(videoId[idx])
    title_list.append(title[idx])
    start_middle.append(stt_start_middle[idx])
    list_score.append(float(score))
    
title_stt_df = pd.DataFrame(list(zip(id_list, title_list, start_middle, list_score)), columns=['videoId', 'title', 'stt(start-middle)', 'score'])

# 3) log3: 1번 수식에 sentence bert 결과 곱하기
######## 일치율

from konlpy.tag import Okt #한글
import isodate 
import numpy as np
from sklearn.preprocessing import MinMaxScaler

search_word = ['설현', '설현 한밤', '김연아', '김연아 설현', 'AOA 설현 한밤', '김연아 한밤',
               '김연아 설현 레전드', '설현 입간판', '설현 한밤 입간판', 'AOA 설현 입간판',
               '쯔위 설현', '쯔위 설현 한밤', '설현 김연아', '설현 쯔위']
    
#title_token['title'] = list(title_token['title'])
script_token = list(script_token)
for i in range(len(title_token)):
    #title_token.iloc[i, 1] = title_token.iloc[i, 1].split()
    desc_token[i] = desc_token[i].split()
    script_token[i] = script_token[i].split()

from gensim.models import Word2Vec

def search_word_cal(word):
    #word='설현 한밤'
    thumb = [' '] #썸네일 없음
    
    okt = Okt()
    search_word = okt.morphs(word) # 형태소로 추출
    print(search_word) 
    word_count = len(search_word) #search 키워드 명사의 개수

    # 검색어 순서에 따라 가중치주기 1
    # 이 방법은 키워드가 나오면 count값이 바로 높아지는 경향..
    # 그래도 어느 정도 관련없는 검색어에 대해 일치율이 떨어지기는 함
    # 순서에 따른 일치율 차이가 크지는 않음
    """title_weight = [30, 15, 10, 5, 3]
    desc_weight = [10, 5, 3, 3, 3]
    script_weight = [20, 15, 10, 5, 3]
    title_count = [int(sum((title.count(search_word[j]) * title_weight[j]) for j in range(word_count))) for title in title_token] #2
    thumb_count = [int(sum((th.count(search_word[j])) for j in range(word_count))) for th in thumb] #0
    desc_count = [int(sum((desc.count(search_word[j])) for j in range(word_count))) for desc in desc_token]
    script_count = [int(sum((script.count(search_word[j]) * script_weight[j]) for j in range(word_count))) for script in script_token]
    # 이미지: 일치율_검색어순서1_count할때같이곱함.png
    """
    title_count = [int(sum((title.count(search_word[j])) for j in range(word_count))) for title in title_token['title']] #2
    print(title_count)
    thumb_count = [int(sum((th.count(search_word[j])) for j in range(word_count))) for th in thumb] #0
    desc_count = [int(sum((desc.count(search_word[j])) for j in range(word_count))) for desc in desc_token]
    script_count = [int(sum((script.count(search_word[j])) for j in range(word_count))) for script in script_token]
    
    # 검색어 순서에 따라 가중치주기 2
    # 바보야매코드
    # 이미지: 일치율_검색어순서2_if문이용해서weight값조정.png
    # 관련없는 검색어와 관련있는 검색어의 일치율 차이가 적절
    # 근데 100이 너무 허벌로 나옴..
    title_weight = []
    script_weight = []
    desc_weight = []
    
    for i in range(len(title_token)):
        for j in range(word_count):
            if j <= word_count/4:   # 검색어 초반인 경우 ex) 검색어가 3단어 -> 0, 1 검색어가 6단어 -> 0, 1, 2
                if search_word[j] in title_token.iloc[i, 1]:    # 초반 검색어가 영상 제목에 있는 경우
                    print("title if-if")
                    title_weight.append(15)
                    break
                else:
                    print("title if-else")
                    title_weight.append(5)
                    break
            else:                   # 검색어가 초반이 아닌 경우
                if search_word[j] in title_token.iloc[i, 1]:   # 검색어가 제목에 있으면
                    print("title else-if")
                    title_weight.append(10)
                    break
                else:
                    print("title else-else")
                    title_weight.append(5)
                    break
                
    for i in range(len(desc_token)):
        for j in range(word_count):
            if j <= word_count/4:   # 검색어 초반인 경우 ex) 검색어가 3단어 -> 0, 1 검색어가 6단어 -> 0, 1, 2
                if search_word[j] in desc_token[i]:    # 초반 검색어가 영상 제목에 있는 경우
                    print("desc if-if")
                    desc_weight.append(5)
                    break
                else:
                    print("desc if-else")
                    desc_weight.append(1)
                    break
            else:                   # 검색어가 초반이 아닌 경우
                if search_word[j] in desc_token[i]:   # 검색어가 제목에 있으면
                    print("desc else-if")
                    desc_weight.append(3)
                    break
                else:
                    print("desc else-else")
                    desc_weight.append(1)
                    break
                
    for i in range(len(script_token)):   # 스크립트의 경우 초반 10개 단어에 대해
        for j in range(word_count):
            if j <= word_count/4:   # 검색어 초반인 경우 ex) 검색어가 3단어 -> 0, 1 검색어가 6단어 -> 0, 1, 2
                if search_word[j] in script_token[i]:    # 초반 검색어가 영상 제목에 있는 경우
                    print("script if-if")
                    script_weight.append(10)
                    break
                else:
                    print("script if-else")
                    script_weight.append(3)
                    break
            else:                   # 검색어가 초반이 아닌 경우
                if search_word[j] in script_token[i]:   # 검색어가 제목에 있으면
                    print("script else-if")
                    script_weight.append(5)
                    break
                else:
                    print("script else-else")
                    script_weight.append(3)
                    break
    

    # 3. 2번 방법 + sentence bert
    # 관련없는 검색어에 대해서 일치율이 낮고, 관련있는 검색어에 대해서 일치율이 높고 아주 좋음
    # 근데 관련없는 검색어가 포함되어 있으면 일치율이 너무 낮은 느낌?
    sbert_score = []
    for i in range(len(title_token)):
        for j in range(len(title_stt_df)):
            if title_token.iloc[i, 0] == title_stt_df.iloc[j, 0]:   # videoId 비교
                #if title_stt_df.iloc[i, 3] not in sbert_score:
                sbert_score.append(round(title_stt_df.iloc[i, 3]*100, 2))
                

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
        
    #print(playtime) 
    #print(playtime_second_list)
    
    df['playtime'] = playtime

     # 일치율 계산 함수     인덱스 02 
    def calculation(title_count, thumb_count, desc_count, script_count, playtime):
        result = []
        #print(thumb_count)
        #scaler_ = MinMaxScaler()   # 값을 0~1사이로 스케일링
        #scaled_title = scaler_.fit_transform(np.reshape(title_count, (5, -1)))
        #scaled_desc = scaler_.fit_transform(np.reshape(desc_count, (5, -1)))
        #scaled_script = scaler_.fit_transform(np.reshape(script_count, (5, -1)))
        
        log_title = np.log1p(title_count)
        log_desc = np.log1p(desc_count)
        log_script = np.log1p(script_count)
        

        for i in range(len(title_count)):   
            
            # 영상 길이 30초 단위로
            time = playtime_second_list[i]/30

            #time = playtime_second_list[i]/10
            #print(time)
             
        
            
            # 검색어 순서 고려하는 방법
            # 1) word2vec -> 단어를 벡터화해서 가까운 위치의 단어들을 유사하다고 판단함
                # 근데 이 경우 데이터가 너무 조그매서 word2vec이 잘 학습을 못 함..
            # 2) 위에처럼 바보 야매코드1, 2
            # 3) sentence bert 결과를 가중치처럼 곱하기
            

            #result.append(((title_count[1]*30 + thumb_count[0]*10 + desc_count[1]*5 + script_count[1]*20) / time) / word_count)
            #result.append(((scaled_title[i]*40 + thumb_count[0]*20 + scaled_desc[i]*20 + scaled_script[i]*40) / time) / word_count)
            #result.append((((log_title[i]*15 + thumb_count[0]*5 + log_desc[i]*3 + log_script[i]*10)) / time) / word_count)
            result.append(((((log_title[i]*title_weight[i] + log_script[i]*script_weight[i])*sbert_score[i] + thumb_count[0]*5 + log_desc[i]*desc_weight[i])) / time) / word_count)
            #result.append(((list_score[i]*(log_title[i]*30 + thumb_count[0]*10 + log_desc[i]*5 + log_script[i]*20)) / time) / word_count)
            #100프로가 넘지 않기 위한 조치 ?? 가중치,,, 비율(비중) 조정 
            ##좀 더 추가요소 넣고싶어요 ㅜㅜ

            print(sbert_score[i])
            
        return result

    result = calculation(title_count, thumb_count, desc_count, script_count, playtime)
    
    ### result에 100을 곱함
    for i in range(len(result)):
        #result[i] *= 100
        result[i] = round(result[i],2)   # 소수점 둘째자리까지
        
        # result값이 100을 넘을 경우 일단은 그냥 100으로..
        if result[i] > 100:
            result[i] = 100 
    return result
    #print(result) 


result_list = []
for word in search_word:
    result_list.append((word, search_word_cal(word)))