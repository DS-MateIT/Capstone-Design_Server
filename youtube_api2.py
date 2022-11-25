from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
import pandas as pd
import myconfig


# 생각해볼 점
# 1. 워드클라우드 zero divde오류 -> tfidf_script_matrix 값이 0이어서 나는 오류 해결
# 2. 일치율 수식 개선

search_word = ""
df = pd.Series()   # df도 전역변수로 유지
stt = []

# get_searchword(word): flask로부터 안드로이드 검색어 입력받음
def get_searchword(word):
    print("!get_searchword 시작!")
    global search_word
    search_word = word
    print(search_word)
    print("!get_searchword 끝!")


# get_youtube() youtube data api로 검색결과 가져오기 & df에 저장
def get_youtube():   
    API_KEY = myconfig.youtube_api_key # API Key
    YOUTUBE_API_SERVICE_NAME="youtube"
    YOUTUBE_API_VERSION="v3"
    youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=API_KEY)
    
    
    # 검색 결과 가져오기
    global search_word
    search_response = youtube.search().list(
        part="id,snippet",   # id빼고 snippet만 해도 되는지 확인해보기
        type='video',
        q=search_word,
        videoDuration='medium',   # 쇼츠는 제외, type을 지정하니까 됨...어이무
        maxResults=5
    ).execute()
    
    print(search_response)
    
    # 영상 title, description, thumbnail등의 정보는 items항목에 있으므로 items가져옴
    video_json = {}
    json_index = 0
    
    for item in search_response['items']:
  
        #if item['id']['kind'] == 'youtube#video' :  ### 쇼츠가 포함된 경우 오류가 발생하는데 쇼츠 어케 가져오지
        video_json[json_index] = {"videoId": item['id']['videoId'], 
                                  "title": item['snippet']['title'].replace('/', ' '), 
                                  "desc" : item['snippet']['description'], 
                                  "thumbnail": item['snippet']['thumbnails']['medium']['url']}
        #print(video_json[json_index])
        json_index += 1 
        
    # json을 데이터프레임으로 변환
    global videoId
    videoId = []
    title = []
    desc = []
    thumbnail = []
    
    for i in range(len(video_json)):
        videoId.append(video_json[i]['videoId'])
        title.append(video_json[i]['title'])
        desc.append(video_json[i]['desc'])
        thumbnail.append(video_json[i]['thumbnail'])
        
    global df 
    df = pd.DataFrame({"videoId": videoId,
                       "title": title,
                       "desc": desc,
                       "thumbnail": thumbnail})
    print(df['title'])
    df['script'] = pd.Series()    # 빈 script컬럼 만들어둠
    
    urls = []
    for i in range(len(df)):
        urls.append("https://www.youtube.com/watch?v="+str(df['videoId'][i]))
    
    #re.sub('/', '', df['title'][i])  # 슬래시는 공백으로 대체
    print(df)
    
    ######
    #get_pytube_mp3(youtube, urls)
    
    return youtube, urls


####pytube 영상 다운로드
from pytube import YouTube
import glob
import os.path

# get_pytube_mp3(youtube, urls): 유튜브 음성 로컬에 다운
def get_pytube_mp3(youtube, urls):
    #youtube, urls = get_youtube()    ###
    
    new_title = []
    #유튜브 전용 인스턴스 생성
    for i in range(len(urls)):
        yt = YouTube(urls[i])
        
        print(yt.streams.filter(only_audio=True).all())
        
        #특정영상 다운로드
        #yt.streams.filter(only_audio=True).first().download('./pytube_mp3')
        yt.streams.filter(only_audio=True).first().download()
        print('success')
        
        # 확장자 변경
        files = glob.glob("*.mp4")
        for x in files:
            if not os.path.isdir(x):
                filename = os.path.splitext(x)
                if filename not in new_title:
                    new_title.append(filename)
                try:
                    os.rename(x,filename[0] + '.mp3')

                except:
                    pass
    
            
    ######            
    #s3_upload(new_title, urls)
    return new_title, urls


####s3연동 

# s3_upload(new_title, urls): pytube로 다운받은 로컬 mp3파일을 s3에 업로드
def s3_upload(new_title, urls):
    import os
    import boto3

    from dotenv import load_dotenv
    load_dotenv(verbose=True)
    
    #new_title, urls = get_pytube_mp3()   ###
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
    
    
    #filepath =[]
    #key = []
    #for i in range(len(urls)):
    #    filepath.append("C:/Noggro/" + str(new_title[i][0]) + ".mp3")
    #    key.append(videoId[i]+"/"+ title[i]+".mp3")
        
    filepath =[]
    key = []
    uploaded_list = []
    global df
    
    for i in range(len(urls)):
        #filepath.append("C:/22_hg076_server/pytube_mp3/" + str(new_title[i][0]) + ".mp3")
        #df['title'][i] = re.sub('/', '', df['title'][i]) # 슬래시는 공백으로 대체

        filepath.append("C:/22_hg076_server/" + str(new_title[i][0]) + ".mp3")
        key.append("youtube_datas/"+df['videoId'][i]+"/"+ df['title'][i]+".mp3")
        
    
    #key 셍성할 파일 / 업로드할 파일명
    #key = 'V2OPlREZP5Y/본격 공개! 설현의 뷰티 노하우 ‘심쿵 꿀팁’ @본격연예 한밤 13회 20170228.mp3'
    
    s3 = boto3.client('s3')
    
    for i in range(len(filepath)):
        res = s3.upload_file(filepath[i], BUCKET_NAME, key[i])   #


    ### 로컬에 있는 영상 삭제(안 지우면 로컬에 있는 영상이 s3에 업로드됨..)
    files = glob.glob("*.mp3")
    for x in files:
        if not os.path.isdir(x):
            filename = os.path.splitext(x)
            os.remove(filename[0]+'.mp3')         

    ######
    #aws_transcribe()
        
##Python용 AWS SDK(Boto3) TR https://docs.aws.amazon.com/ko_kr/transcribe/latest/dg/tagging.html
#from __future__ import print_function
import time
import boto3
from urllib import request
import re

AWS_ACCESS_KEY = myconfig.AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = myconfig.AWS_SECRET_ACCESS_KEY
AWS_S3_BUCKET_REGION = myconfig.AWS_S3_BUCKET_REGION
AWS_S3_BUCKET_NAME = myconfig.AWS_S3_BUCKET_NAME

# aws_transcribe(): s3에 업로드한 mp3로 tr돌림 -> stt생성 -> s3에 업로드
def aws_transcribe():
    
    transcribe = boto3.client('transcribe', 'us-east-2')
    
    # conflict예외 발생할 때: transcribe.delete_transcription_job(TranscriptionJobName=job_name)
    # transcribe.delete_transcription_job(TranscriptionJobName=videoId[4])
    items = []
    #stt = []
    global stt

    global df
    for i in range(len(df['videoId'])):
        
        job_name = df['videoId'][i] + "dic"   #실행할 tr 이름 #dic반영할 경우 
        uri = "s3://mateityoutube/youtube_datas/" + df['videoId'][i]+ "/" + df['title'][i]+".mp3"  #Tr에 필요한 영상 주소
        job_uri = uri
    #job_uri = "s3://mateityoutube/V2OPlREZP5Y/본격 공개! 설현의 뷰티 노하우 ‘심쿵 꿀팁’ @본격연예 한밤 13회 20170228.mp3"
    
        # 같은 job_name tr이 올라가 있는지 확인(이전에 돌린 적이 있는지)
        if check_job_name(transcribe, job_name) == False:
            transcribe.delete_transcription_job(
                TranscriptionJobName = job_name
            )

        transcribe.start_transcription_job(
            TranscriptionJobName = job_name,
            Media = {
                'MediaFileUri': job_uri
            },
            OutputBucketName = 'mateityoutube',
            OutputKey = "youtube_datas/" +df['videoId'][i]+ "/" , 
            LanguageCode = 'ko-KR', 
            Tags = [
                {
                    'Key':'color',    #??
                    'Value':'blue'
                }
            ] ,
            Settings={
            #    'VocabularyName': 'SHonly',
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
                data = pd.read_json(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                print("! 가져온 tr ! {}".format(data))
                stt.append(data['results']['transcripts'][0]['transcript'])
                break
            print("Not ready yet...")
            time.sleep(15)
        print(status)

        #if status['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
        print("가져온 stt: {}".format(stt[i]))



    #for i in range(len(df['videoId'])):
        

    return "TR Upload SUCCESS"

# 중복 tr인지 체크하고 tr이름이 중복이면 삭제
def check_job_name(transcribe, job_name):
    existed_tr = transcribe.list_transcription_jobs(MaxResults=100)
    for job in existed_tr['TranscriptionJobSummaries']:
        if job_name == job['TranscriptionJobName']:
            return False
    return True


# S3에 위치한 json 파일(STT TR 파일) 을 읽어오기( 다운로드 없이 바로 )

import json
import boto3


#@@----------------------df에 script 추가
from konlpy.tag import Okt
import re

from sklearn.feature_extraction.text import TfidfVectorizer

# stt_tfidf(): title, desc, stt를 토큰화 & tfidf행렬 만들기
def stt_tfidf():
    #stt = get_stt()
    
    global df
    global stt
    for i in range(len(stt)):
        df['script'][i]=stt[i]
    #df['script'] = stt
    print("~df['script']~")
    print(df['script'])
    
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
    
    
    
    t=Okt()
    
    title_token = df[['videoId','title']].astype('str')
    
    for i in range(len(title_token)):
        #title_token = t.morphs(re.sub(r'[^\w]', ' ', str(line)))  # 형태소
        title_token.iloc[i, 1]  = t.nouns(re.sub(r'[^\w]', ' ', title_token.iloc[i, 1]))  # 명사 저장
    #print(title_token) 
    
    desc_token = df['desc'].astype('str')
    for i in range(len(desc_token)):
        #title_token = t.morphs(re.sub(r'[^\w]', ' ', str(line)))  # 형태소
        desc_token[i] = t.nouns(re.sub(r'[^\w]', ' ', desc_token[i]))  # 명사 저장
        desc_token[i] = ' '.join(desc_token[i])
    #print(desc_token)
    
    #@@----------------------script 
    script_token = df['script'].astype('str')
    for i in range(len(script_token)):
        #title_token = t.morphs(re.sub(r'[^\w]', ' ', str(line)))  # 형태소
        script_token[i] = t.nouns(re.sub(r'[^\w]', ' ', script_token[i]))  # 명사 저장
        script_token[i] = ' '.join(script_token[i])
    #print(script_token)
    
    
    
    
    
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
    print(len(tfidf_script_matrix))
    
    ######
    #wordcloud_upload(title_token, desc_token, script_token, tfidf_script_matrix)
    
    return title_token, desc_token, script_token, tfidf_script_matrix



import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS
#pip install wordcloud
from PIL import Image 
import numpy as np

# tfidf값이 0인 경우 예외처리하기!
# wordcloud_upload(): 앞에서 토큰화한 애들과 행렬을 이용해 워드 클라우드 생성
def wordcloud_upload(title_token, desc_token, script_token, tfidf_script_matrix):
    #title_token, desc_token, script_token, tfidf_script_matrix = stt_tfidf()
    global df
    #global isShorts

    for i in range(len(tfidf_script_matrix)):
        
        print(tfidf_script_matrix.iloc[i, :].sum())
        # 현재 tfidf 행렬 값이 모두 0이면 워드클라우드 오류가 발생하므로
        """if tfidf_script_matrix.iloc[i, :].sum() == 0.0:
            print("!주요 키워드가 없습니다!")
            isShorts[i] = True   # 스크립트가 없는 영상이므로 쇼츠로 판단
            continue
        """
        
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
        
        wc.to_file("C:/22_hg076_server/wordcloud/"+df['videoId'][i]+".png")
        
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
    for i in range(len(df['videoId'])):
        filepath = "C:/22_hg076_server/wordcloud/" + df['videoId'][i] +  ".png"
        #s3://mateityoutube/youtube_datas/776dS8Rmkhs/
        s3_put_object(s3, AWS_S3_BUCKET_NAME, filepath,"youtube_datas/"+ df['videoId'][i]+ "/" +df['videoId'][i]+".png")
    
    ######
    #get_tfidf_keyword(tfidf_script_matrix)
    #return title_token, desc_token, script_token, tfidf_script_matrix
    return tfidf_script_matrix
#--안드로이드 cognito로 워드클라우드 띄우기 테스트 성공 


#####--------- 영상별로 tf-idf값이 높은(중요도가 높은) 단어 추출
# 주요 단어 3개 추출
import collections
import numpy as np

#print(tfidf_matrix.iloc[0, :].idxmax())
#print(tfidf_matrix.iloc[0, :].values)

# get_tfidf_keyword(): 스크립트로 생성한 tfidf행렬에서 키워드 3개 추출
def get_tfidf_keyword(tfidf_script_matrix):
    keywords = pd.DataFrame(columns=['word', 'tf-idf'])
    #tfidf_script_matrix = wordcloud_upload()
    
    words = []
    values = []
    
    global df
    
    # 영상별로 tf-idf값이 가장 높은 단어(words)와 그 값(values)
    # stt로 한 번..
    #global isShorts
    for i in range(len(tfidf_script_matrix)):
        """if isShorts[i] == True:
            continue
        """
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
    print("keywords['word']: ",format(keywords['word']))
    keywords['tf-idf'] = values

    keywords['word'] = sum([], keywords['word'])
    print("sum한 결과: ", format(keywords['word']))

    df['주요 단어(제목)'] = keywords['word']
    print(df['주요 단어(제목)'])
    df['단어의 중요도(tf-idf)'] = keywords['tf-idf']
    
    ### 파이차트 그리
    ###video_id값과 stt단어 3개 db에 저장하기 
   
    
    #S3에 저장하기
    
    
    ######
    #stt_split(keywords)
    return keywords


#### sentence bert
# stt_split(): stt에서 마침표 기준으로 문장 나누기(초반, 중반, 후반)
def stt_split(keywords):
    #get_tfidf_keyword()
    
    stt_list = []
    global stt
    #global isShorts
    for i in range(len(stt)):
        #if len(stt[i]) == 0:
        #    continue
        stt[i]= '.\n'.join(stt[i].split(". "))   # 마침표(.) 기준으로 문장 나누고 엔터
        stt_list.append(stt[i].splitlines())   # 엔터 기준으로 문자 split해서 한 줄씩
    
    
    # stt를 (초반, 중반, 후반)으로 나누기
    def list_chunk(lst, n):   # 리스트를 n개의 원소를 가지도록 나눔
        return [lst[i:i+n] for i in range(0, len(lst), n)]
    
    start = []
    middle = []
    end = []
    
    for i in range(len(stt_list)):
        if len(stt_list[i])//3 == 0:
            print("!stt가 없습니다!")
            break
        else:
            length = len(stt_list[i])//3
            stt_list[i] = list_chunk(stt_list[i], length)
            
            start.append(stt_list[i][0])
            middle.append(stt_list[i][1])
            end.append(stt_list[i][2])
        
    ######
    #sbert_to_df(start, middle, end)
    return start, middle, end


   

import tensorflow as tf
import torch
from sentence_transformers import util

# GPU 사용 설정
import os

# gpu사용 설정
def gpu_setting():
    os.environ["CUDA_VISIBLE_DEVICES"]="0"
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.experimental.set_memory_growth(gpus[0], True)
        except RuntimeError as e:
            print(e)

# sbert_stt_rate(): 센텐스버트를 이용해 문장 간 유사도 계산            
def sbert_stt_rate(model, mylist, mylist2):   
    #gpu_setting()
    
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

# sbert_to_df(): sbert를 이용해 계산한 문장 간 유사도를 df로 저장
def sbert_to_df(start, middle, end):
    my_model = joblib.load('models/myklue-roberta-base.pkl')
    # FileNotFoundError: [Errno 2] No such file or directory: 'models/myklue-roberta-base.pkl'
    
    #start, middle, end = stt_split()
    #### (제목, 초반-중반)
    # 초반-중반 합치기 
    stt_start_middle = []
    for i in range(len(start)):
        stt_start_middle.append('\n'.join(start[i][:3])+'\n'.join(middle[i][:3]))
    
    
    global df
    titles = list(df['title'])
    
    top_results = sbert_stt_rate(my_model, titles, stt_start_middle)


    print(top_results)
    id_list = []
    title_list = []
    stt_list = []
    list_score = []
    
    #for i in range(len(stt_start_middle)):
    # 리스트로 바꾸니까 되는 거 어이없다
    for j, (score, idx) in enumerate(zip(top_results[0], top_results[1])):
        id_list.append(list(df['videoId'])[idx])
        title_list.append(list(df['title'])[idx])
        stt_list.append(stt_start_middle[idx])
        list_score.append(float(score))
        
    title_stt_df = pd.DataFrame(list(zip(id_list, title_list, stt_list, list_score)), columns=['videoId', 'title', 'stt(start-middle)', 'score'])
    print("!! title_stt_df!!")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(title_stt_df.iloc[:, 1:])

    return title_stt_df
    #global search_word
    #search_word_cal(search_word)


######## 일치율

from konlpy.tag import Okt #한글
import isodate 
import numpy as np
from sklearn.preprocessing import MinMaxScaler

   

#title_token['title'] = list(title_token['title'])


from gensim.models import Word2Vec

# search_word_cal(): 일치율 계산
def search_word_cal(word, mlkit_text):
    print("!search_word_cal 시작!")
    
    # 앞에서 정의한 함수들 모두 호출
    youtube, urls = get_youtube()
    new_title, urls = get_pytube_mp3(youtube, urls)
    s3_upload(new_title, urls)
    tr_upload = aws_transcribe()
    
    if tr_upload == "TR Upload SUCCESS":
        #get_stt()
        title_token, desc_token, script_token, tfidf_script_matrix = stt_tfidf()
        tfidf_script_matrix = wordcloud_upload(title_token, desc_token, script_token, tfidf_script_matrix)
        keywords = get_tfidf_keyword(tfidf_script_matrix)
        start, middle, end = stt_split(keywords)
        title_stt_df = sbert_to_df(start, middle, end)

    # 전처리
    script_token = list(script_token)
    for i in range(len(title_token)):
        #title_token.iloc[i, 1] = title_token.iloc[i, 1].split()
        desc_token[i] = desc_token[i].split()
        script_token[i] = script_token[i].split()
    #word='설현 한밤'
    thumb = [' '] #썸네일 없음
    
    ## mlkit 텍스트 가져오기!
    thumb = []
    for i in range(len(mlkit_text)):
        if len(mlkit_text[i]) == 0:
            mlkit_text[i] = ''
        thumb.append(mlkit_text[i])
    
    global search_word
    okt = Okt()
    search_word = okt.morphs(word) # 형태소로 추출
    print(search_word) 
    word_count = len(search_word) #search 키워드 명사의 개수

    global df
    
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
    
    print("!!! 텍스트 카운트 !!")
    print("검색어 길이: {}".format(word_count))
    print("title_count: {}".format(title_count))
    print("thumb_count:{} ".format(thumb_count))
    print("desc_count: {}".format(desc_count))
    print("script_count: {}".format(script_count))



    #title_weight = 30
    #thumb_weight = 15
    #desc_weight = 10
    #script_weight = 40
    
    title_weight = []
    script_weight = []
    thumb_weight = []
    desc_weight = []
    
    for i in range(len(title_token)):
        for j in range(word_count):
            if j <= word_count/4:   # 검색어 초반인 경우 ex) 검색어가 3단어 -> 0, 1 검색어가 6단어 -> 0, 1, 2
                if search_word[j] in title_token.iloc[i, 1]:    # 초반 검색어가 영상 제목에 있는 경우
                    print("title if-if")
                    title_weight.append(30)    # 15
                    break
                else:
                    print("title if-else")
                    title_weight.append(10)     # 5
                    break
            else:                   # 검색어가 초반이 아닌 경우
                if search_word[j] in title_token.iloc[i, 1]:   # 검색어가 제목에 있으면
                    print("title else-if")
                    title_weight.append(20)    # 10
                    break
                else:
                    print("title else-else")
                    title_weight.append(10)     # 5
                    break
                
    for i in range(len(desc_token)):
        for j in range(word_count):
            if j <= word_count/4:   # 검색어 초반인 경우 ex) 검색어가 3단어 -> 0, 1 검색어가 6단어 -> 0, 1, 2
                if search_word[j] in desc_token[i]:    # 초반 검색어가 영상 제목에 있는 경우
                    print("desc if-if")
                    desc_weight.append(10)       # 5
                    break
                else:
                    print("desc if-else")
                    desc_weight.append(3)       # 1
                    break
            else:                   # 검색어가 초반이 아닌 경우
                if search_word[j] in desc_token[i]:   # 검색어가 제목에 있으면
                    print("desc else-if")
                    desc_weight.append(5)       # 3
                    break
                else:
                    print("desc else-else")
                    desc_weight.append(3)       # 1
                    break
           
    ##################
    for i in range(len(thumb)):   # 썸네일
        for j in range(word_count):
            if j <= word_count/4:   # 검색어 초반인 경우 ex) 검색어가 3단어 -> 0, 1 검색어가 6단어 -> 0, 1, 2
                if search_word[j] in thumb[i]:    # 초반 검색어가 영상 제목에 있는 경우
                    print("thumb if-if")
                    thumb_weight.append(15)     # 5
                    break
                else:
                    print("thumb if-else")
                    thumb_weight.append(5)     # 1
                    break
            else:                   # 검색어가 초반이 아닌 경우
                if search_word[j] in thumb[i]:   # 검색어가 제목에 있으면
                    print("thumb else-if")
                    thumb_weight.append(10)     # 3
                    break
                else:
                    print("thumb else-else")
                    thumb_weight.append(5)     # 1
                    break
                
    for i in range(len(script_token)):   # 스크립트의 경우 초반 10개 단어에 대해
        for j in range(word_count):
            if j <= word_count/4:   # 검색어 초반인 경우 ex) 검색어가 3단어 -> 0, 1 검색어가 6단어 -> 0, 1, 2
                if search_word[j] in script_token[i]:    # 초반 검색어가 영상 제목에 있는 경우
                    print("script if-if")
                    script_weight.append(40)    # 10
                    break
                else:
                    print("script if-else")
                    script_weight.append(25)     # 3
                    break
            else:                   # 검색어가 초반이 아닌 경우
                if search_word[j] in script_token[i]:   # 검색어가 제목에 있으면
                    print("script else-if")
                    script_weight.append(30)     # 5
                    break
                else:
                    print("script else-else")
                    script_weight.append(25)     # 3
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
        
        log_title = np.log1p(title_count)
        log_desc = np.log1p(desc_count)
        #log_thumb = np.log1p(thumb_count)
        log_script = np.log1p(script_count)
        
        print("log_title은! {}".format(log_title))
        print("log_desc은! {}".format(log_desc))
        print("thumb은! {}".format(thumb_count))
        print("log_script는! {}".format(log_script))

        for i in range(len(title_count)):   
            
            # 영상 길이 30초 단위로
            time = playtime_second_list[i]/30

            #time = playtime_second_list[i]/10
            #print(time)
            result.append(((((log_title[i]*title_weight[i] + log_script[i]*script_weight[i])*sbert_score[i] + thumb_count[j]*thumb_weight[j] + log_desc[i]*desc_weight[i])) / time) / word_count)
            print("title_weight은 {}".format(title_weight[i]))
            print("script_weight은 {}".format(script_weight[i]))
            print("desc_weight은 {}".format(desc_weight[i]))
            print("thumb_weight은 {}".format(thumb_weight[i]))

            print("~time~")
            print(time)
            print("~sbert_score~")
            print(sbert_score[i])
            
        return result

    result = calculation(title_count, thumb_count, desc_count, script_count, playtime)
    
    ### result에 10을 곱함
    for i in range(len(result)):
        #result[i] *= 10
        result[i] = round(result[i],2)   # 소수점 둘째자리까지
        
        # 일치율 값이 100을 넘을 경우에 대한 예외처리
        if result[i] > 100:
            result[i] = 100 
    
    print("!search_word_cal 끝!")
    print(result)
    
    # tfidf_keyword 리턴
    new_keywords = []
    for wordList in keywords['word']:
        for word in wordList:
            new_keywords.append(word)
        
    #new_keywords = sum(new_keywords, [])
    
    print("## new_keywords: ", format(new_keywords))
        
    return result, df['videoId'], new_keywords