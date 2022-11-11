import pymysql

'''
db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
curs = db.cursor()
 
sql = "select * from new_table";
 
curs.execute(sql)
 
rows = curs.fetchall()
print(rows)
 
db.commit()
db.close()
'''
class DBtable:
    def __init__(self):
       pass
   
    def Getresult(self):
        ret = []
            
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
             
        sql = "select * from new_test";
             
        curs.execute(sql)
             
        rows = curs.fetchall()

        for e in rows:
            temp = {'word':e[0],'count':e[1]}
            ret.append(temp)
            
        db.commit()
        db.close()
        return ret
        
    def Insert(self, word, count):
        
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        sql = '''insert into new_test (word, count) values(%s,%s)'''
        curs.execute(sql,(word, count))
        db.commit()
        db.close()
        
    def Insert2(self, word):
        
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        sql = '''insert into new_word2 (word) values(%s)'''
        curs.execute(sql, word)
        db.commit()
        db.close()
        
    def Update(self, word): 
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
        
        sql = "update new_test set count=count+1 where word=%s"
        curs.execute(sql,word)
        db.commit()
        db.close()
        
    def DelEmp(self, word):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
        
        sql = "delete from new_test where word=%s"
        curs.execute(sql,word)
        db.commit()
        db.close()
        
    def MaxCount(self):
        ret = []
            
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
             
        sql = "select * from new_test ORDER BY count DESC LIMIT 3";
             
        curs.execute(sql)
             
        rows = curs.fetchall()

        for e in rows:
            temp = {'word':e[0],'count':e[1]}
            ret.append(temp)
            
        db.commit()
        db.close()
        return ret
    
    
    #video_id DB
    def Video_id_insert(self, video_id, stt1, stt2, stt3):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        sql = '''insert into Video (video_id, stt_word1,stt_word2,stt_word3) values(%s,%s,%s,%s)'''
        curs.execute(sql,(video_id, stt1,stt2, stt3))
        db.commit()
        db.close()
        
        
        
    def Video_id_del(self, video_id):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
        
        sql = "delete from Video where video_id=%s"
        curs.execute(sql,video_id)
        db.commit()
        db.close()
        
    

    ## 최근 본 영상 insert
    def Recent_Video_insert(self, user_email,video_id):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
        
        sql = '''insert into new_recentVideo (user_email,video_id,count) values(%s,%s,%s) ON DUPLICATE KEY UPDATE count=count+1'''
        curs.execute(sql,(user_email,video_id,1))
        db.commit()
        db.close()
    
    
    ## 최근 본 영상 get result  select
    def Recent_Video_Getresult(self,user_email):
        ret = []
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
             
        sql = "select video_id from new_recentVideo where user_email=%s ORDER BY recent_id DESC LIMIT 3";

        curs.execute(sql,user_email)
             
        rows = curs.fetchall()

        for e in rows:
            temp = {'video_id':e[0]}
            ret.append(temp)
            
        db.commit()
        db.close()
        return ret
    
    
    ## 최근 본 영상 count update 
    def Recent_Video_Update(self, user_email, video_id): 
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
        
        sql = "update new_recentVideo set count=count+1 where video_id=%s"
        curs.execute(sql,video_id)
        db.commit()
        db.close()
        
    ## 최근 본 영상 select
    def Recent_Video_Select(self, user_email, video_id):
        ret = []
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
        
        sql = '''select EXISTS (select * from new_schema.new_recentVideo where user_email=%s AND video_id=%s) as success;'''
        curs.execute(sql,(user_email,video_id))
        
        rows = curs.fetchall()
        
        for e in rows:
            temp = {'success':e[0]}
            ret.append(temp)
            
        db.commit()
        db.close()
        
        return ret
    
    
    
    ## 파이차트용- 자주 언급된 단어 insert
    def video_sttword_Insert(self,video_id,stt_word1,stt_word2,stt_word3,user_email):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
                            
        sql = '''insert into new_video (video_id, stt_word1, stt_word2, stt_word3, user_email) values(%s,%s,%s,%s,%s)'''
        curs.execute(sql,(video_id,stt_word1,stt_word2,stt_word3,user_email))
        db.commit()
        db.close()
    
    
    
    ## 파이차트용- 자주 언급된 단어 select
    def video_sttword_Getresult(self,user_email,video_id):
        ret = []
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
             
        sql = "select * from new_video where user_email=%s AND video_id=%s desc LIMIT 3";
        curs.execute(sql,(user_email,video_id))
             
        rows = curs.fetchall()

        for e in rows:
            temp = {'video_id':e[0],'stt_word1':e[1], 'stt_word2':e[2], 'stt_word3':e[3]}
            ret.append(temp)
            
            
            
        db.commit()
        db.close()
        return ret
    
    
    

    ## bookmark - testDB Bookmark_info
    def Bookmark_insert(self, user_email, videoid,title):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        sql = '''insert into Bookmark_info (user_email, videoid, title) values(%s,%s,%s)'''
        curs.execute(sql,(user_email,videoid,title))
        db.commit()
        db.close()
        
    ## bookmark - testDB Bookmark_info
    def Bookmark_select(self, user_email, videoid,title):
        ret = []
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
        
        sql = '''select EXISTS (select * from testDB.Bookmark_info where user_email=%s AND videoid=%s AND title=%s limit 1) as success;'''
        curs.execute(sql,(user_email,videoid,title))
        
        rows = curs.fetchall()
        
        for e in rows:
            temp = {'success':e[0]}
            ret.append(temp)
            
        db.commit()
        db.close()
        
        return ret
        
        
    ## bookmark - testDB Bookmark_info    
    def Bookmark_del(self, user_email, videoid, title):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
        
        sql = "delete from testDB.Bookmark_info where user_email=%s AND videoid=%s AND title=%s"
        curs.execute(sql,(user_email, videoid, title))
        db.commit()
        db.close()
        
    def bookmark_Getresult(self, email):
        ret = []
            
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
             
        sql = "select videoid,title from testDB.Bookmark_info where user_email=%s";
             
        curs.execute(sql,(email))
             
        rows = curs.fetchall()

        for e in rows:
            temp = {'videoid':e[0],'title':e[1]}
            ret.append(temp)
            
        db.commit()
        db.close()
        return ret
    
    
    
    
    ## 연관검색어 
    # 연관검색어 insert
    def Relatedword_insert(self, srch_keyword, srch_craw1, srch_craw2, srch_craw3):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        sql = '''insert into new_word (srch_keyword, srch_craw1, srch_craw2, srch_craw3) values(%s,%s,%s,%s)'''
        curs.execute(sql,(srch_keyword, srch_craw1, srch_craw2,  srch_craw3))
        db.commit()
        db.close()
        
    
    # 연관검색어 select
    def Relatedword_result(self):
        ret = []
            
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
             
        sql = "select * from new_schema.new_word order by word_no desc LIMIT 3";
             
        curs.execute(sql)
             
        rows = curs.fetchall()

        for e in rows:
            temp = {'word_no':e[0],'srch_keyword':e[1], 'srch_craw1':e[2], 'srch_craw2':e[3], 'srch_craw3':e[4]}
            ret.append(temp)
            
        db.commit()
        db.close()
        return ret
    
    
    ## user 
    # user insert
    def user_insert(self, user_email, user_password, user_age):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='new_schema', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        
        sql = '''insert into new_user (user_email, user_password, user_age) values(%s,%s,%s)'''
        curs.execute(sql,(user_email, user_password, user_age))
        db.commit()
        db.close()
        
    ## user 
    # user insert
    def userinfo_insert(self, user_email, user_password, user_age):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        
        sql = '''insert into User_info (user_email, user_password, user_age) values(%s,%s,%s)'''
        curs.execute(sql,(user_email, user_password, user_age))
        db.commit()
        db.close()
        
    ## user 
    # user insert
    def user_id_get(self, user_email):
        ret = []
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        #sql = "select user_id from testDB.User_info ORDER BY user_id DESC LIMIT 1"
        sql = "select user_id from testDB.User_info where user_email=%s"
        curs.execute(sql,user_email)
        
        rows = curs.fetchall()
        
        for e in rows:
            temp = {'user_id':e[0]}
            ret.append(temp)
        
        db.commit()
        db.close()
        return ret
    
    def rate_insert(self,  srch_word, video_id, rate):
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        
        sql = '''insert into Video_rate (srch_word, video_id, rate) values(%s,%s,%s)'''
        curs.execute(sql,(srch_word, video_id, rate))
        db.commit()
        db.close()
        
    def rate_get(self, srch_word, video_id):
        ret = []
        db = pymysql.connect(host='database-1.cwwua8swoe2v.ap-northeast-2.rds.amazonaws.com', user='admin', db='testDB', port=3306, password='ds83418341!', charset='utf8')
        curs = db.cursor()
            
        #sql = "select user_id from testDB.User_info ORDER BY user_id DESC LIMIT 1"
        sql = "select rate from Video_rate where srch_word=%s and video_id=%s"
        curs.execute(sql, (srch_word, video_id))
        
        rows = curs.fetchall()
        
        for e in rows:
            temp = {'rate':e[0]}
            ret.append(temp)
        
        db.commit()
        db.close()
        return ret
    
        
if __name__ == '__main__':
    #DBtable().Insert('앵무새','1')
    #DBtable().Update('앵무새')
    #DBtable().DelEmp('돌고래')
    #DBtable().MaxCount()
    test = DBtable().Getresult();
    print(test)