from flask import Flask, render_template, request

app = Flask(_name_)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    name = request.form['name']
    age = request.form['age']
    return f'Hello, {name}! You are {age} years old.'

if _name_ == '_main_':
    app.run(debug=True)
