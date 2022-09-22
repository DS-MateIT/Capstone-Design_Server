#안드로이드 앱에서 retrofit post로 서버에 받아오기
from flask import Flask, request, Response, jsonify
import json
import DBcount_test
import keywordtool_crawling



app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 


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
        
        
        ### 디비 - word 테이블로 보내기 / workbench new_word테이블로 테스트 확인
        DBcount_test.DBtable().Relatedword_insert(post_srch, srch_craw1, srch_craw2, srch_craw3)
        
        
        #지금 문제점 이름순으로 정렬되는 듯 함 : 내 검색 순 : 돈까스 개강 학식 초코바 / 테이블 출력 순 : 개강 돈까스 초코바 학식
        #자동 인덱스 생성 -> 정렬완료함 
    
             
        print(post_srch) #검색어 추출  
        return post_srch
        
    else : # get했을 경우 : 연관검색어 db -> 안드로이드스튜디오
       
        data = DBcount_test.DBtable().Relatedword_result();
        print(data) 
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
    
#시청한 영상 video_id - id값 출력 확인 O
@app.route('/videoid', methods=['GET','POST'])
def videoId():
    if request.method == 'POST' :
        post_videoid = request.form['videoId']
        
        #DB에 넣기 - stt wordcloud 세개 단어 추출 코드 합치기
        print(post_videoid) 
        return post_videoid
        
        
    else : 
        return post_videoid
 



#북마크용 video_id 받기 - 버튼 클릭시 id값 출력 확인 O
@app.route('/BMvideoid', methods=['GET','POST'])
def BMvideoId():
    if request.method == 'POST' :
        bm_videoid = request.form['videoId']
        print(bm_videoid) 
        
        #test 테이블에 넣기
        DBcount_test.DBtable.Insert('1',bm_videoid,'user1')
        
        
        return bm_videoid
        
        
    else : 
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
        
        
if __name__ == '__main__':
    app.run(host='0.0.0.0') 
    
    #app.run(host='192.168.11.156') # 미정

        