from flask import Flask, jsonify, request, Response
#from flask.templating import render_template
import DBcount_test

app = Flask (__name__)
app.config['JSON_AS_ASCII'] = False 

@app.route('/')
def hello_world():
    data = {'result' : 'rateeeee'}
    data = DBcount_test.DBtable().Getresult();
    print(data)
    return jsonify(data)
 
if __name__ == "__main__":
    app.run()