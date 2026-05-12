from flask import Flask
from flask import render_template
from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from config import BASE_URL
import requests
from flask_bootstrap import Bootstrap
import net as neuronet
from werkzeug.utils import secure_filename
import os
import base64
from PIL import Image
from io import BytesIO
import json
from flask import request
from flask import Response

app = Flask(__name__)
print("Hello world")
@app.route("/data_to")
def data_to():
    some_pars = {'user':'Ivan','color':'red'}
    some_str = 'Hello my dear friends!'
    some_value = 10
    return render_template('simple.html',some_str = some_str,some_value = some_value,some_pars=some_pars)
@app.route("/")
def hello(): 
    return " <html><head></head> <body> Hello World! </body></html>"

SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY

# используем капчу и полученные секретные ключи с сайта Google
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcTseUsAAAAAD69w9dnTpVq3UI4RjS9MczMr7Bg'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcTseUsAAAAAJDYYlZP1jaBjBJ7wbRMYUE6Erzc'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
bootstrap = Bootstrap(app)

openid = StringField('openid', validators = [DataRequired()])
# поле загрузки файла
# здесь валидатор укажет ввести правильные файлы
upload = FileField('Load image', validators=[FileRequired(),FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
# поле формы с capture
recaptcha = RecaptchaField()
#кнопка submit, для пользователя отображена как send
submit = SubmitField('send')

class NetForm(FlaskForm):
    openid = StringField('openid', validators=[DataRequired()])
    upload = FileField('Load image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    submit = SubmitField('send')


@app.route("/net", methods=['GET', 'POST'])
def net():
    form = NetForm()
    filename = None
    neurodic = {}

    if form.validate_on_submit():
        filename = os.path.join('./static', secure_filename(form.upload.data.filename))
        form.upload.data.save(filename)
        fcount, fimage = neuronet.read_image_files(10, './static')
        decode = neuronet.getresult(fimage)

        if decode and len(decode) > 0:
            for item in decode[0]:  # decode[0] – список предсказаний для первого изображения
                neurodic[item['class']] = item['prob']

    return render_template('net.html', form=form, image_name=filename, neurodic=neurodic)

@app.route("/apinet", methods=['GET', 'POST'])
def apinet():
    if request.mimetype != 'application/json':
        return Response("Bad request: need JSON", status=400)

    data = request.get_json()
    if 'imagebin' not in data:
        return Response("Missing 'imagebin' field", status=400)

    filebytes = data['imagebin'].encode('utf-8')
    cfile = base64.b64decode(filebytes)
    img = Image.open(BytesIO(cfile))

    decode = neuronet.getresult([img])
    neurodic = {}

    if decode and len(decode) > 0:
        predictions = decode[0]          # предсказания для первого (и единственного) изображения
        if isinstance(predictions, list):
            for pred in predictions:
                if isinstance(pred, (tuple, list)) and len(pred) >= 3:
                    # формат (class_id, class_name, prob)
                    neurodic[pred[1]] = str(pred[2])
                elif isinstance(pred, dict) and 'class' in pred and 'prob' in pred:
                    neurodic[pred['class']] = str(pred['prob'])
                elif isinstance(predictions, dict):
                    neurodic[predictions['class']] = str(predictions['prob'])
# пример сохранения переданного файла
# handle = open('./static/f.png','wb')
# handle.write(cfile)
# handle.close()
# преобразуем словарь в json-строку
    ret = json.dumps(neurodic)
# готовим ответ пользователю
    resp = Response(response=ret, status=200, mimetype="application/json")
# возвращаем ответ
    return resp



# r = requests.get('http://localhost:5000/')
# print(r.status_code)
# print(r.text)
# r = requests.get('http://localhost:5000/data_to')
# print(r.status_code)
# print(r.text)