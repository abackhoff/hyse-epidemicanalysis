# app.py
from flask import Flask, render_template, request, send_file
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
        # Calculate control limits for u-chart
        cl_u_chart = data['Infection Rate'].mean()
        ucl_u_chart = cl_u_chart + 3 * np.sqrt(cl_u_chart / data['Sample Size'])
        lcl_u_chart = cl_u_chart - 3 * np.sqrt(cl_u_chart / data['Sample Size'])
        lcl_u_chart= np.where(lcl_u_chart < 0, 0, lcl_u_chart)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Infection Rate', title='U-chart', labels={'Infection Rate': 'Infections per Sample'})
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=cl_u_chart, y1=cl_u_chart, yref='y', xref='x', line=dict(color='red'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=ucl_u_chart, y1=ucl_u_chart, yref='y', xref='x', line=dict(color='green'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=lcl_u_chart, y1=lcl_u_chart, yref='y', xref='x', line=dict(color='green'))

    elif chart_type == 'p-chart':
        # Calculate control limits for p-chart
        pbar = data['Infection Rate'].mean()
        ucl_p_chart = pbar + 3 * np.sqrt(pbar * (1 - pbar) / data['Sample Size'])
        lcl_p_chart = pbar - 3 * np.sqrt(pbar * (1 - pbar) / data['Sample Size'])
        lcl_p_chart = np.where(lcl_p_chart < 0, 0, lcl_p_chart)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Infection Rate', title='P-chart', labels={'Infection Rate': 'Proportion of Infections'})
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=pbar, y1=pbar, yref='y', xref='x', line=dict(color='red'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=ucl_p_chart, y1=ucl_p_chart, yref='y', xref='x', line=dict(color='green'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=lcl_p_chart, y1=lcl_p_chart, yref='y', xref='x', line=dict(color='green'))

    elif chart_type == 'ma-chart':
        # Calculate control limits for MA-chart
        window_size = ma_window_size
        data['Moving Average'] = data['Infection Rate'].rolling(window=window_size).mean()
        data['Moving Range'] = data['Infection Rate'].rolling(window=2).apply(lambda x: np.abs(x[1] - x[0]), raw=True)
        mrbar = data['Moving Range'].mean()
        sigma = mrbar / (1.128 * np.sqrt(window_size))
        cl_ma_chart = data['Moving Average'].mean()
        ucl_ma_chart = cl_ma_chart + 3 * sigma
        lcl_ma_chart = cl_ma_chart - 3 * sigma
        lcl_ma_chart = np.where(lcl_ma_chart < 0, 0, lcl_ma_chart)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Moving Average', title='MA-chart', labels={'Moving Average': 'Moving Average of Infection Rate'})
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=cl_ma_chart, y1=cl_ma_chart, yref='y', xref='x', line=dict(color='red'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=ucl_ma_chart, y1=ucl_ma_chart, yref='y', xref='x', line=dict(color='green'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=lcl_ma_chart, y1=lcl_ma_chart, yref='y', xref='x', line=dict(color='green'))

    return fig

if __name__ == '__main__':
    app.run(debug=True)
