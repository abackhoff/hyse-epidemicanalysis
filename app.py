# app.py
from flask import Flask, render_template, request, send_file
from email_utils import send_email
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home-page.html')

@app.route('/instructions')
def instructions():
    return render_template('Instructions-page.html')

@app.route('/create-spc-charts')
def create_spc_charts():
    return render_template('index.html')

@app.route('/send-mail', methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':
        recipient = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']

        send_email(recipient, subject, body)

        return 'Email sent successfully'
    else:
        return render_template('feedback.html')

@app.route('/feedback')
def feedback():
    return render_template('Feedback.html')

@app.route('/upload', methods=['POST'])
def upload():
    purpose_choice = request.form.get('purpose')
    data_type_choice = request.form.get('data_type')
    analysis_choice = request.form.get('analysis_type')
    ma_window_size = request.form.get('ma_window_size', type=int)
    excel_file = request.files.get('excel_file')

    if not excel_file:
        return 'No file uploaded', 400

    df = pd.read_excel(excel_file, engine='openpyxl')
    
    df['Infection Rate'] = df['Infection Count'] / df['Sample Size']

    if purpose_choice == 'new_outbreaks' and data_type_choice and analysis_choice:
        chart = generate_chart(analysis_choice, df, ma_window_size)
        chart_div = pio.to_html(chart, full_html=False)
        return render_template('index.html', chart_div=chart_div)
    else:
        return 'Invalid input', 400

import numpy as np
import plotly.express as px

def generate_chart(chart_type, data, ma_window_size=None):
    if chart_type == 'u-chart':
        cl_u_chart = data['Infection Rate'].mean()
        ucl_u_chart = cl_u_chart + 3 * np.sqrt(cl_u_chart / data['Sample Size'])
        lcl_u_chart = cl_u_chart - 3 * np.sqrt(cl_u_chart / data['Sample Size'])
        lcl_u_chart = np.where(lcl_u_chart < 0, 0, lcl_u_chart)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Infection Rate', title='U-chart', labels={'Infection Rate': 'Infections per Sample'})
        fig.add_scatter(x=data['Period'], y=data['Infection Rate'], mode='markers', marker=dict(color=np.where((data['Infection Rate'] > ucl_u_chart) | (data['Infection Rate'] < lcl_u_chart), 'red', 'rgba(0,0,0,0)')), name='Out of Control')
        fig.update_traces(selector=dict(type='scatter', mode='markers'), showlegend=False)
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=cl_u_chart, y1=cl_u_chart, yref='y', xref='x', line=dict(color='red'))

        fig.add_scatter(x=data['Period'], y=ucl_u_chart, mode='lines', line=dict(color='green'), name='UCL')
        fig.add_scatter(x=data['Period'], y=lcl_u_chart, mode='lines', line=dict(color='green'), name='LCL')

    elif chart_type == 'p-chart':
        pbar = data['Infection Rate'].mean()
        ucl_p_chart = pbar + 3 * np.sqrt(pbar * (1 - pbar) / data['Sample Size'])
        lcl_p_chart = pbar - 3 * np.sqrt(pbar * (1 - pbar) / data['Sample Size'])
        lcl_p_chart = np.where(lcl_p_chart < 0, 0, lcl_p_chart)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Infection Rate', title='P-chart', labels={'Infection Rate': 'Proportion of Infections'})
        fig.add_scatter(x=data['Period'], y=data['Infection Rate'], mode='markers', marker=dict(color=np.where((data['Infection Rate'] > ucl_p_chart) | (data['Infection Rate'] < lcl_p_chart), 'red', 'rgba(0,0,0,0)')), name='Out of Control')
        fig.update_traces(selector=dict(type='scatter', mode='markers'), showlegend=False)
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=pbar, y1=pbar, yref='y', xref='x', line=dict(color='red'))

        fig.add_scatter(x=data['Period'], y=ucl_p_chart, mode='lines', line=dict(color='green'), name='UCL')
        fig.add_scatter(x=data['Period'], y=lcl_p_chart, mode='lines', line=dict(color='green'), name='LCL')

    elif chart_type == 'ma-chart':
        data['Moving Average'] = data['Infection Rate'].rolling(window=ma_window_size).mean()

        mstd = data['Infection Rate'].rolling(window=ma_window_size).std()
        ucl_ma_chart = data['Moving Average'] + 3 * mstd
        lcl_ma_chart = data['Moving Average'] - 3 * mstd

        fig = px.line(data, x='Period', y='Infection Rate', title='MA-chart', labels={'Infection Rate': 'Infections'})
        fig.add_scatter(x=data['Period'], y=data['Moving Average'], mode='lines', line=dict(color='red'), name='Moving Average')

        fig.add_scatter(x=data['Period'], y=ucl_ma_chart, mode='lines', line=dict(color='green'), name='UCL')
        fig.add_scatter(x=data['Period'], y=lcl_ma_chart, mode='lines', line=dict(color='green'), name='LCL')

    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=-0.2))
    fig.show()


if __name__ == '__main__':
    app.run(debug=True)
