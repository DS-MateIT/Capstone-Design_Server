#안드로이드 앱에서 retrofit post로 서버에 받아오기
from flask import Flask, request, Response, jsonify
import json
import DBcount_test
import keywordtool_crawling
import youtube_api2
import pymysql


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 

search_word = ""

@app.route('/')
def root():
    return 'test test'

#GET
#POST
@app.route('/mlkit', methods=['GET','POST'])
def postData2():
    if request.method == 'POST' :
        post_mlkit = request.form['mlkitText']
        DBcount_test.DBtable().Insert(post_mlkit,'1')
        print(post_mlkit)
        return post_mlkit
        
    else :
        data = DBcount_test.DBtable().Getresult();
        print(data)
        return jsonify(data)
    
    
    
@app.route('/srch', methods=['GET','POST'])
def srch():
    if request.method == 'POST' :
        post_srch = request.form['srchText']
       
        # 디비 - 검색어 디비로 보내기 
        DBcount_test.DBtable().Insert2(post_srch)
        
        
        
        # 일치율 코드에 srch키워드 적용하기
        #print(get_searchword(post_srch))
        
        
        ### 연관검색어 크롤링
        keywords = keywordtool_crawling.youtube_keyword(post_srch)
        

        print(keywords) #연관검색어 3개 추출 결과  # type : list
        srch_craw1 = keywords[0] # print(srch_craw1)
        srch_craw2 = keywords[1]
        srch_craw3 = keywords[2]
        
        # 디비로 보내기 
        #DBcount_test.DBtable().Insert(post_srch,'1')
            
            
        # 일치율 코드로 srch키워드 보내기
        #youtube_api_일치율.get_searchword(post_srch)
            
        #### youtube_api코드 흐름 제어

        """word = "설현 인터뷰"
        youtube_api2.get_searchword(word)  
        result, video_id = youtube_api2.search_word_cal(word)

        #result = youtube_api2.result_to_list()
        print("######## 일치율 타입 ##########")
        result = list(map(float, result))      # float로 변환
        print(type(word))
        
        video_id = list(video_id)
        #global rate_result
        #for i in range(len(result)):
            #rate_result.append(result[i])
        
        ## db Video_rate에 일치율 저장
        DBcount_test.DBtable().rate_insert(word, video_id[0], result[0])
        DBcount_test.DBtable().rate_insert(word, video_id[1], result[1])
        DBcount_test.DBtable().rate_insert(word, video_id[2], result[2])
        DBcount_test.DBtable().rate_insert(word, video_id[3], result[3])
        DBcount_test.DBtable().rate_insert(word, video_id[4], result[4])
        """
        
        ### 디비 - word 테이블로 보내기 / workbench new_word테이블로 테스트 확인
        DBcount_test.DBtable().Relatedword_insert(post_srch, srch_craw1, srch_craw2, srch_craw3)
        
       
        
        #지금 문제점 이름순으로 정렬되는 듯 함 : 내 검색 순 : 돈까스 개강 학식 초코바 / 테이블 출력 순 : 개강 돈까스 초코바 학식
        #자동 인덱스 생성 -> 정렬완료함 
        return post_srch


        
    else : # get했을 경우 : 연관검색어 db -> 안드로이드스튜디오
       
        data = DBcount_test.DBtable().Relatedword_result();
        print(data) 
        # db에 저장된 일치율 불러온다
        
        #return jsonify(ret)
        return jsonify(data)





    
    
#시청한 영상 video_id - DB에 넣기
'''
@app.route('/videoid', methods=['GET','POST'])
def videoId():
    if request.method == 'POST' :
        post_videoid = request.form['videoId']
        DBcount_test.DBtable().Insert(post_videoid,'test1','test2','test3')
        print(post_videoid)
        return post_videoid
        
    else :
        
        
        DBcount_test.DBtable().Video_id_insert('abc1','a1','b1','c1')
        DBcount_test.DBtable().Video_id_insert('abc2','a1','b1','c1')
        DBcount_test.DBtable().Video_id_insert('abc3','a1','b1','c1')
        DBcount_test.DBtable().Video_id_insert('abc4','a1','b1','c1')
        DBcount_test.DBtable().Video_id_insert('abc5','a1','b1','c1')
        DBcount_test.DBtable().Video_id_insert('abc6','a1','b1','c1')
        
        
        DBcount_test.DBtable().Video_id_del('abc1')
        DBcount_test.DBtable().Video_id_del('abc2')
        DBcount_test.DBtable().Video_id_del('abc3')
        DBcount_test.DBtable().Video_id_del('abc4')
        DBcount_test.DBtable().Video_id_del('abc5')
        DBcount_test.DBtable().Video_id_del('abc6')
     
        
        
        
        testdb = DBcount_test.DBtable().Recent_Video();
        print(testdb)
        
        
        data = DBcount_test.DBtable().Getresult();
        print(data)
        
        return jsonify(testdb)     #jsonify(data) 
'''    
    
# 시청한 영상 video_id post - id값 출력 확인 O
@app.route('/videoid', methods=['POST'])
def videoId():
    video_id = request.form['videoId']
    email = request.form['email']
        
    
    data = DBcount_test.DBtable().Recent_Video_Select(email, video_id)
    print(data[0]['success'])
    
     
    # if 문 - email 과 video id 없으면 insert
    if data[0]['success'] == 0 :
        #최근 시청 DB에 insert - recent_id, user_email, video_id
        DBcount_test.DBtable().Recent_Video_insert(email, video_id)
        
        #같은 video id 있으면 delete 해서 가장 최신 것만 남기기
        #DELETE FROM new_schema.new_recentVideo WHERE recent_id IN (select * from (SELECT MIN(recent_id) FROM new_schema.new_recentVideo GROUP BY user_email, video_id HAVING COUNT(*) > 1) as tmp);
    
        
        return video_id
    
    
    # 있으면 update하고
    elif data[0]['success'] == 1 :
        # update 
        DBcount_test.DBtable().Recent_Video_Update(email,video_id)
        return video_id
    
    
    
    # insert id값 같은거되면 delete 코드
    
    
    
    
    
    
    print(video_id) 
    return video_id
        

# 최근 시청한 영상 get 
@app.route('/videoid', methods=['GET'])
def videoIdget():
    email = request.args.get('email')
    video_id = DBcount_test.DBtable().Recent_Video_Getresult(email) 
    
    
    
    
    jsonify(video_id)
    print(video_id)
    return jsonify(video_id)
    


 

## 북마크
#useremail video_id post
@app.route('/BMvideoid', methods=['POST'])
def BMvideoId():
    user_email = request.form['useremail']
    videoid = request.form['videoid']
    print(user_email, videoid) 
    
    data = DBcount_test.DBtable().Bookmark_select(user_email, videoid)
    print(data[0]['success'])
    
    # 북마크 테이블에 기록이 없으면
    if data[0]['success'] == 0 :
        #Bookmark_info 테이블에 넣기
        DBcount_test.DBtable().Bookmark_insert(user_email, videoid)
        return videoid
    # 북마크 테이블에 기록이 있으면
    elif data[0]['success'] == 1 : 
        #Bookmark_info 테이블에서 삭
        DBcount_test.DBtable().Bookmark_del(user_email, videoid)
        return videoid
    
    return videoid
        
    
## 북마크
#useremail video_id get    
@app.route('/BMvideoid', methods=['GET'])
def BMvideoId2():
    data = DBcount_test.DBtable().bookmark_Getresult();
    print(data)
    return jsonify(data) 

 
# 회원가입 할때 User 정보 저장
@app.route('/user', methods=['POST'])
def user():
    #global useremail
    useremail = request.form['useremail']
    userpw = request.form['userpw']
    userbirth = request.form['userbirth']

    # 생년월일 그대로 받은거 성인/ 미성인 처리 여기서 해서 디비로 저장 ?  

    # DB - user 정보 User_info 테이블로 보내기 (연속으로 회원가입해도 정상적으로 가입, 저장됨)
    DBcount_test.DBtable().userinfo_insert(useremail, userpw, userbirth)
    
    userid = DBcount_test.DBtable().user_id_get(useremail)

    
    print("이메일 : " + useremail + " 비밀번호 : " + userpw + " 생일"+ userbirth)
    
    return userid
    
# 로그인 할때 User 정보 조회   
@app.route('/user', methods=['GET'])
def user2():
    email = request.args.get('email')
    userid = DBcount_test.DBtable().user_id_get(email)
    jsonify(userid)
    return jsonify(userid)
        
### 일치율 가져오기
"""@app.route('/srch-rate', methods=['POST'])
def post_srch():
    #global result_rate
    
    

        #result_rate = json.dumps(result_rate, ensure_ascii=False).encode('utf8')
        #Response(result_rate, content_type='application/json; charset=utf-8')
        
        #return jsonify(Response)
        #print(post_srch)
    
    return jsonify(result_rate)
        
    """
@app.route('/srch-rate', methods=['GET'])
def get_srch():
    #data = DBcount_test.DBtable().Getresult();
    #print(data)

    # db에 저장된 일치율 불러온다
    search_keyword= request.args.get('srch_word')
    video_id = request.args.get('video_id')
    
    rate = DBcount_test.DBtable().rate_get(search_keyword, video_id)
    

    #return jsonify(ret)

    #return "GET"
    #return rate[0]
    #print(rate[0]['result'])
    
    return jsonify(rate)
        
if __name__ == '__main__':
    app.run(host='0.0.0.0') 
    
    #app.run(host='192.168.11.156') # 미정

        