# app.py
from flask import Flask, render_template, request, send_file
from flask_mail import Mail, Message
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)


# Configure Flask-Mail with your email server settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'albertobackhoff@gmail.com'
app.config['MAIL_PASSWORD'] = 'Boston2020'

mail = Mail(app)

@app.route('/send_feedback', methods=['POST'])
def send_feedback():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Create the email message
    msg = Message('Feedback from {}'.format(name),
                  sender=email,
                  recipients=['your_email_address'])

    msg.body = 'From: {}\nEmail: {}\n\n{}'.format(name, email, message)

    # Send the email
    mail.send(msg)

    # Redirect the user or display a success message
    flash('Feedback sent successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/')
def home():
    return render_template('home-page.html')

@app.route('/instructions')
def instructions():
    return render_template('Instructions-page.html')

@app.route('/create-spc-charts')
def create_spc_charts():
    return render_template('index.html')


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

    df = pd.read_excel(excel_file, engine='openpyxl', parse_dates=['Date'])
    
    start_date = pd.to_datetime(request.form.get('start-date'))
    end_date = pd.to_datetime(request.form.get('end-date'))
    
    if start_date is None:
        start_date = df['Date'].min()  # Default to the earliest date in the dataframe
    if end_date is None:
        end_date = df['Date'].max()

    if start_date is not None and end_date is not None:
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    else:
        error_message = "Invalid date range. Please ensure both start_date and end_date are valid."
        return render_template('index.html', error_message=error_message)

    df['Infection Rate'] = df['Infection Count'] / df['Sample Size']

    if purpose_choice == 'new_outbreaks' and data_type_choice and analysis_choice:
        chart = generate_chart(analysis_choice, df, ma_window_size)
        chart_div = pio.to_html(chart, full_html=False)
        return render_template('index.html', chart_div=chart_div)
    else:
        return 'Invalid input', 400
    
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df = df[(df['Period'] >= start_date) & (df['Period'] <= end_date)]

import numpy as np
import plotly.express as px

def generate_chart(chart_type, data, ma_window_size=None):
    if chart_type == 'u-chart':
        u_bar = data['Infection Count'].sum() / data['Sample Size'].sum()
        cl_u_chart = u_bar
        ucl_u_chart = u_bar + 3 * np.sqrt(u_bar/data['Sample Size'])
        lcl_u_chart = u_bar - 3 * np.sqrt(u_bar/data['Sample Size'])
        lcl_u_chart = np.where(lcl_u_chart < 0, 0, lcl_u_chart)

        fig = px.line(data, x='Period', y='Infection Rate', title='U-chart', labels={'Infection Rate': 'Infections per Sample'})
        fig.add_scatter(x=data['Period'], y=data['Infection Rate'], mode='markers', marker=dict(color=np.where((data['Infection Rate'] > ucl_u_chart) | (data['Infection Rate'] < lcl_u_chart), 'red', 'rgba(0,0,0,0)')), name='Out of Control')
        fig.update_traces(selector=dict(type='scatter', mode='markers'), showlegend=False)
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=cl_u_chart, y1=cl_u_chart, yref='y', xref='x', line=dict(color='red'))

        fig.add_scatter(x=data['Period'], y=ucl_u_chart, mode='lines', line=dict(color='green'), name='UCL')
        fig.add_scatter(x=data['Period'], y=lcl_u_chart, mode='lines', line=dict(color='green'), name='LCL')

    elif chart_type == 'p-chart':
        p_bar = data['Infection Count'].sum() / data['Sample Size'].sum()
        cl_p_chart = p_bar
        ucl_p_chart = p_bar + 3 * np.sqrt(p_bar * (1 - p_bar) / data['Sample Size'])
        lcl_p_chart = p_bar - 3 * np.sqrt(p_bar * (1 - p_bar) / data['Sample Size'])
        lcl_p_chart = np.where(lcl_p_chart < 0, 0, lcl_p_chart)

        fig = px.line(data, x='Period', y='Infection Rate', title='P-chart', labels={'Infection Rate': 'Proportion of Infections'})
        fig.add_scatter(x=data['Period'], y=data['Infection Rate'], mode='markers', marker=dict(color=np.where((data['Infection Rate'] > ucl_p_chart) | (data['Infection Rate'] < lcl_p_chart), 'red', 'rgba(0,0,0,0)')), name='Out of Control')
        fig.update_traces(selector=dict(type='scatter', mode='markers'), showlegend=False)
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=cl_p_chart, y1=cl_p_chart, yref='y', xref='x', line=dict(color='red'))

        fig.add_scatter(x=data['Period'], y=ucl_p_chart, mode='lines', line=dict(color='green'), name='UCL')
        fig.add_scatter(x=data['Period'], y=lcl_p_chart, mode='lines', line=dict(color='green'), name='LCL')

    elif chart_type == 'ma-chart':
        data['Moving Average'] = data['Infection Rate'].rolling(window=ma_window_size).mean()
        mean_ma = data['Moving Average'].mean()
        std_ma = data['Moving Average'].std()
        ucl_ma_chart = mean_ma + 3 * std_ma
        lcl_ma_chart = mean_ma - 3 * std_ma
        lcl_ma_chart = np.maximum(lcl_ma_chart, 0)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Moving Average', title='Moving Average Chart', labels={'Moving Average': 'Infection Rate'})
        fig.add_scatter(x=data['Period'], y=data['Infection Rate'], mode='lines', line=dict(color='grey', dash='dash'), name='Infection Rate')
        fig.add_scatter(x=data['Period'], y=np.full(len(data), ucl_ma_chart), mode='lines', line=dict(color='green'), name='UCL')
        fig.add_scatter(x=data['Period'], y=np.full(len(data), lcl_ma_chart), mode='lines', line=dict(color='green'), name='LCL')
        fig.add_scatter(x=data['Period'], y=np.full(len(data), mean_ma), mode='lines', line=dict(color='red'), name='CL')

    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=-0.5))
    return fig

if __name__ == '__main__':
    app.run(debug=True)
