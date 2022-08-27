#안드로이드 앱에서 retrofit post로 서버에 받아오기
from flask import Flask, request, Response, jsonify
import json
import DBcount_test

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
        
        # 디비로 보내기 
        DBcount_test.DBtable().Insert(post_srch,'1')
        
        
        # 일치율 코드로 srch키워드 보내기
        youtube_api_일치율.get_searchword(post_srch)
        
        
        
        
        print(post_srch)
        return post_srch
        
    else :
        data = DBcount_test.DBtable().Getresult();
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
    
    
    

  
if __name__ == '__main__':
    app.run(host='0.0.0.0')