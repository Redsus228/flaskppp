print("Hello world") 
from flask import Flask
from flask import render_template
from config import BASE_URL
import requests
app = Flask(__name__) 

@app.route("/data_to")
def data_to():
    some_pars = {'user':'Ivan','color':'red'}
    some_str = 'Hello my dear friends!'
    some_value = 10
    return render_template('simple.html',some_str = some_str,some_value = some_value,some_pars=some_pars)
@app.route("/")
def hello(): 
    return " <html><head></head> <body> Hello World! </body></html>"




# r = requests.get('http://localhost:5000/')
# print(r.status_code)
# print(r.text)
# r = requests.get('http://localhost:5000/data_to')
# print(r.status_code)
# print(r.text)