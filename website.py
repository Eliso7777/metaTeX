from flask import Flask, send_from_directory, request, abort, jsonify, make_response, send_file
import json, os, datetime, random
from flask import Flask,render_template,request,redirect,session
from pdf2image import convert_from_bytes
from flask_mail import Mail
import json

app = Flask(__name__)

@app.route('/favicon.ico',subdomain="tex")
def favicon():
    return send_from_directory('.','favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/latex",subdomain="tex",methods=['POST'])
def api():
    tc = 'black'
    bc = 'white'
    old = '/home/eli/Downloads/BotBox/LaTeX'
    os.chdir(old+'/tex_files')
    filename = str(random.randint(0,2**31))
    with open(filename+'.tex', 'w') as f:
        f.write(request.json['body'])
    os.system(f'xelatex {filename}.tex')
    pdf = open(f'{filename}.pdf','rb').read()
    images = convert_from_bytes(bytes(pdf))
    images[0].save(f'{filename}.png')
    img = images[0]
    img.save(f'{filename}.png')
    os.system(f'convert {filename}.png -fuzz 70% -fill {tc} -opaque \'black\' {filename}.png')
    os.system(f'convert {filename}.png -fill {bc} +transparent \'{tc}\' {filename}.png')
    image = open(filename+'.png', 'rb')
    os.chdir(old)
    return jsonify({'body':f'https://tex.botbox.dev/texf/{filename}'})

@app.route("/texf/<path:path>",subdomain="tex")
def texs(path):
    return send_from_directory('tex_files',path)

@app.route("/file/<path:path>",subdomain="tex")
def temps(path):
    return send_from_directory('templates',path)

@app.route("/editor",subdomain="tex")
def editor():
    return render_template('texteditor.html')

@app.route("/",subdomain="tex")
def main():
    return render_template('websitefront.html')

@app.errorhandler(404)
def not_found(e):
  return render_template('404error.html'), 404

#DO NOT CHANGE THESE! THEY ARE FOR HOSTING THE WEBSITE.
if __name__ == '__main__':
    print("Listening...")
    app.config['SERVER_NAME']='botbox.dev'
    app.run(host='192.168.2.188', port=5001)
