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
        
if __name__ == '__main__':
	#DBtable().Insert('앵무새','1')
    #DBtable().Update('앵무새')
    #DBtable().DelEmp('돌고래')
    #DBtable().MaxCount()
    test = DBtable().Getresult();
    print(test)
