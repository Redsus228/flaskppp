import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, RadioField
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-for-wtf'

app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lc7rrMtAAAAAHd6sEtPx6YpcKQj3L5Pabyfprf2'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lc7rrMtAAAAACbD7rn1-ttCRg0b1tKuPEiTPAmg'


bootstrap = Bootstrap(app)

# Папка для сохранения загрузок и результатов внутри static
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Новая Форма 1: Для страницы с капчей
class CaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField('Подтвердить')


# Новая Форма 2: Склейка картинок и графики
class CollageForm(FlaskForm):
    image1 = FileField('Первое изображение', validators=[
        FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Только картинки!')
    ])
    image2 = FileField('Второе изображение', validators=[
        FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Только картинки!')
    ])
    direction = RadioField('Направление склейки', choices=[
        ('horizontal', 'По горизонтали'),
        ('vertical', 'По вертикали')
    ], default='horizontal')
    submit = SubmitField('Склеить и построить графики')


# Вспомогательная функция: генерация гистограммы цветов RGB
def generate_rgb_histogram(image_path, output_name):
    img = Image.open(image_path).convert('RGB')

    plt.figure(figsize=(4, 3))
    colors = ('r', 'g', 'b')

    for i, color in enumerate(colors):
        histogram = img.histogram()[i * 256:(i + 1) * 256]
        plt.plot(histogram, color=color, linewidth=1.5)
        plt.xlim([0, 256])

    plt.title('Распределение цветов')
    plt.xlabel('Яркость')
    plt.ylabel('Пиксели')
    plt.tight_layout()

    hist_path = os.path.join(UPLOAD_FOLDER, output_name)
    plt.savefig(hist_path)
    plt.close()
    return output_name


# Вспомогательная функция: склейка двух картинок
def merge_images(img1_path, img2_path, direction):
    img1 = Image.open(img1_path).convert('RGB')
    img2 = Image.open(img2_path).convert('RGB')

    if direction == 'horizontal':
        img2_resized = img2.resize((int(img2.width * (img1.height / img2.height)), img1.height))
        new_width = img1.width + img2_resized.width
        combined = Image.new('RGB', (new_width, img1.height))
        combined.paste(img1, (0, 0))
        combined.paste(img2_resized, (img1.width, 0))
    else:
        img2_resized = img2.resize((img1.width, int(img2.height * (img1.width / img2.width))))
        new_height = img1.height + img2_resized.height
        combined = Image.new('RGB', (img1.width, new_height))
        combined.paste(img1, (0, 0))
        combined.paste(img2_resized, (0, img1.height))

    res_name = 'result_collage.png'
    combined.save(os.path.join(UPLOAD_FOLDER, res_name))
    return res_name


# Маршрут 1: Страница авторизации (Капча)
@app.route("/", methods=['GET', 'POST'])
def index():
    form = CaptchaForm()
    if form.validate_on_submit():
        session['passed_captcha'] = True
        return redirect(url_for('collage_view'))
    return render_template('captcha.html', form=form)


# Маршрут 2: Функционал склейки (Доступен только после успешной капчи)
@app.route("/collage", methods=['GET', 'POST'])
def collage_view():
    if not session.get('passed_captcha'):
        return redirect(url_for('index'))

    form = CollageForm()
    result_image = None
    hist1, hist2, hist_res = None, None, None

    if form.validate_on_submit():
        f1 = form.image1.data
        f2 = form.image2.data
        path1 = os.path.join(UPLOAD_FOLDER, secure_filename(f1.filename))
        path2 = os.path.join(UPLOAD_FOLDER, secure_filename(f2.filename))
        f1.save(path1)
        f2.save(path2)

        result_image = merge_images(path1, path2, form.direction.data)

        hist1 = generate_rgb_histogram(path1, 'hist1.png')
        hist2 = generate_rgb_histogram(path2, 'hist2.png')
        hist_res = generate_rgb_histogram(os.path.join(UPLOAD_FOLDER, result_image), 'hist_res.png')

    return render_template('collage.html', form=form, result_image=result_image,
                           hist1=hist1, hist2=hist2, hist_res=hist_res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

##############################################################################
# СТАРЫЙ КОД (ЗАКОММЕНТИРОВАН, ЧТОБЫ НЕ ПОТЕРЯТЬ)
####################################################################
# from flask import Flask
# from flask import render_template
# from flask_wtf import FlaskForm,RecaptchaField
# from wtforms import StringField, SubmitField, TextAreaField
# from wtforms.validators import DataRequired
# from flask_wtf.file import FileField, FileAllowed, FileRequired
# from config import BASE_URL
# import requests
# from flask_bootstrap import Bootstrap
# import net as neuronet
# from werkzeug.utils import secure_filename
# import os
# import base64
# from PIL import Image
# from io import BytesIO
# import json
# from flask import request
# from flask import Response
# 
# print("Hello world")
# @app.route("/data_to")
# def data_to():
#     some_pars = {'user':'Ivan','color':'red'}
#     some_str = 'Hello my dear friends!'
#     some_value = 10
#     return render_template('simple.html',some_str = some_str,some_value = some_value,some_pars=some_pars)
# 
# openid = StringField('openid', validators = [DataRequired()])
# upload = FileField('Load image', validators=[FileRequired(),FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
# recaptcha = RecaptchaField()
# submit = SubmitField('send')
# 
# class NetForm(FlaskForm):
#     openid = StringField('openid', validators=[DataRequired()])
#     upload = FileField('Load image', validators=[
#         FileRequired(),
#         FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
#     ])
#     submit = SubmitField('send')
# 
# @app.route("/net", methods=['GET', 'POST'])
# def net():
#     form = NetForm()
#     filename = None
#     neurodic = {}
#     if form.validate_on_submit():
#         filename = os.path.join('./static', secure_filename(form.upload.data.filename))
#         form.upload.data.save(filename)
#         fcount, fimage = neuronet.read_image_files(10, './static')
#         decode = neuronet.getresult(fimage)
#         if decode and len(decode) > 0:
#             for item in decode[0]:
#                 neurodic[item['class']] = item['prob']
#     return render_template('net.html', form=form, image_name=filename, neurodic=neurodic)
# 
# @app.route("/apinet", methods=['GET', 'POST'])
# def apinet():
#     if request.mimetype != 'application/json':
#         return Response("Bad request: need JSON", status=400)
#     data = request.get_json()
#     if 'imagebin' not in data:
#         return Response("Missing 'imagebin' field", status=400)
#     filebytes = data['imagebin'].encode('utf-8')
#     cfile = base64.b64decode(filebytes)
#     img = Image.open(BytesIO(cfile))
#     decode = neuronet.getresult([img])
#     neurodic = {}
#     if decode and len(decode) > 0:
#         predictions = decode[0]
#         if isinstance(predictions, list):
#             for pred in predictions:
#                 if isinstance(pred, (tuple, list)) and len(pred) >= 3:
#                     neurodic[pred[1]] = str(pred[2])
#                 elif isinstance(pred, dict) and 'class' in pred and 'prob' in pred:
#                     neurodic[pred['class']] = str(pred['prob'])
#                 elif isinstance(predictions, dict):
#                     neurodic[predictions['class']] = str(predictions['prob'])
#     ret = json.dumps(neurodic)
#     resp = Response(response=ret, status=200, mimetype="application/json")
#     return resp
