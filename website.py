#important notes:
#ignore the files for calcu, those are hidden for this github page
from flask import Flask, send_from_directory, request, abort, jsonify, make_response, send_file
import json, os, datetime, botvotes, Graphs
from flask import Flask,render_template,request,redirect,session
from flask_sqlalchemy import  SQLAlchemy
from flask_mail import Mail
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, reply_to

#non-webpage functions:

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_string"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/calcus'

class Contacts(db.Model):
    id=db.Column(db.Integer,primary_key=True,nullable=True)
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False)
    message=db.Column(db.String(500),nullable=False)

def checktier(cents):
    if cents > 10000:
        return 5
    elif cents > 2000:
        return 4
    elif cents > 800:
        return 3
    elif cents > 400:
        return 2
    elif cents > 100:
        return 1
    else:
        return 0

#webpage functions (calcu):
      
@app.route('/favicon.ico',subdomain="calcu")
def favicon():
    return send_from_directory('.', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/file/<path:path>',subdomain="calcu")
def send_filepath(path):
    return send_from_directory('imgs', path)

@app.route('/graph',subdomain="calcu")
def graph():
    function = request.args.get('function')
    limits = request.args.get('limits')
    image = Graphs.FG.function(function, float(limits))
    return send_file(image, mimetype="image/png")

@app.route('/graph/post',methods=['POST'],subdomain="calcu")
def graphp():
    jsoninfo = request.json
    function = jsoninfo['function']
    limits = jsoninfo['limits']
    image = Graphs.FG.function(function, float(limits))
    return send_file(image, mimetype="image/png")

@app.route('/patlogs',methods=['POST'],subdomain="calcu")
def handle_push():
    d = request.data.decode("utf-8")
    rd = json.loads(d)
    fn = rd["data"]["attributes"]["full_name"]
    n = datetime.datetime.utcnow()
    f = open(f'patlogs/{fn}  {n}.txt','w')
    f.write(json.dumps(rd, indent=4))
    f.close()
    if rd["data"]["attributes"]["patron_status"] == "active_patron":
        if rd["included"][1]["attributes"]["discord_id"] != "null":
            with open(f'userinfo/{rd["included"][1]["attributes"]["discord_id"]}.txt') as file:
                c = dict(json.load(file))
                c["donor"] = str(checktier(int(rd["data"]["attributes"]["pledge_amount_cents"])))
            with open(f'userinfo/{rd["included"][1]["attributes"]["discord_id"]}.txt', 'w') as file:
                json.dump(c, file)
    return('Success'), 200

@app.route('/dblwebhook',methods=['POST'],subdomain="calcu")
def vote():
    botvotes.vote.send(json.loads(request.data.decode("utf-8")))
    return('Success'), 200

with open('config.json','r')as c:
    params=json.load(c)["params"]

@app.route("/",subdomain="calcu")
def home():
    print(request)
    return render_template('website.html')

@app.route("/contact",methods=["GET","POST"],subdomain="calcu")
def contact():
    if request.method=="POST":
        id=request.form.get('id')
        name=request.form.get('name')
        email=request.form.get('email')
        message=request.form.get('message')
        #entry=Contacts(id=id,name=name,email=email,message=message)
        #db.session.add(entry)
        #db.session.commit()
        mmessage = Mail(
            from_email='support@botbox.dev',
            to_emails=email,
            subject='NEW REPORT RECEIVED FROM CALCUBOTOR SITE BY '+name,
            html_content='Please wait from a reply from our staff.<br>'+message)
        mmessage.reply_to = 'botboxemail@gmail.com'
        mmessage.bcc = 'botboxemail@gmail.com'
        sg = SendGridAPIClient(api_key='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')
        response = sg.send(mmessage)
        return render_template('contact.html',params=params)
    return render_template('contact.html',params=params)

@app.route("/about",subdomain="calcu")
def about():
    return render_template('about.html')

@app.route("/login",methods=["GET","POST"],subdomain="calcu")
def login():
    if 'uname' in session and session['uname']==params['admin-user']:
        return render_template('dashboard.html',params=params)
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if username==params['admin-user'] and password==params['admin-pass']:
            session['uname']=username
            return render_template('dashboard.html',params=params)
        else:
            return render_template('login.html')
        return render_template('login.html')
    return render_template('login.html')


@app.route("/logout",subdomain="calcu")
def logout():
    if 'uname' in session and session['uname']==params['admin-user']:
        session.pop('uname')
        return redirect("/login")
    return redirect('/login')


@app.route("/dashboard",methods=["POST"],subdomain="calcu")
def dashboard():
    if 'uname' in session and session['uname']==params['admin-user']:
        n1=Contacts.query.all()
        return render_template('dashboard.html',n1=n1,params=params)


@app.route("/commands",subdomain="calcu")
def commands():
    return render_template('commands.html')

#webpage functions (tex):
  
if __name__ == '__main__':
    print("Listening...")
    app.config['SERVER_NAME']='botbox.dev'
    app.run(host='192.168.2.188', port=5000)
