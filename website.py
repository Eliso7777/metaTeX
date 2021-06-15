from flask import Flask, send_from_directory, request, abort, jsonify, make_response, send_file
import json, os, datetime
from flask import Flask,render_template,request,redirect,session
from flask_sqlalchemy import  SQLAlchemy
from flask_mail import Mail
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_string"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/calcus'

@app.route("/",subdomain="tex")
def commands():
    return '''Nothing here'''

if __name__ == '__main__':
    print("Listening...")
    app.config['SERVER_NAME']='botbox.dev'
    app.run(host='192.168.2.188', port=5001)
