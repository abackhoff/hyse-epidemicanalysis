from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    name = request.form['name']
    age = request.form['age']
    return f'Hello, {name}! You are {age} years old.'

if __name__ == '__main__':
    app.run(debug=True)
