from flask import Flask, send_from_directory, request, abort, jsonify, make_response, send_file
import json, os, datetime, random
from PIL import Image
from flask import Flask,render_template,request,redirect,session
from pdf2image import convert_from_bytes
from flask_mail import Mail
import json

app = Flask(__name__)

def savelist(imgs, filename):
    min_img_width = min(i.width for i in imgs)
    total_height = 0
    for i, img in enumerate(imgs):
        if img.width > min_img_width:
            imgs[i] = img.resize((min_img_width, int(img.height / img.width * min_img_width)), Image.ANTIALIAS)
        total_height += imgs[i].height
    img_merge = Image.new(imgs[0].mode, (min_img_width, total_height), color=(230,230,230))
    y = 0
    for img in imgs:
        img_merge.paste(img, (0, y))
        y += img.height + 25
    img_merge.save(filename+'.png')


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
    savelist(images, filename)
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

if __name__ == '__main__':
    print("Listening...")
    app.config['SERVER_NAME']='botbox.dev'
    app.run(host='192.168.2.188', port=5001)
