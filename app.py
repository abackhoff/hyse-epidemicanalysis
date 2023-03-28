# app.py
from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    chart_choice = request.form.get('chart_type')
    excel_file = request.files.get('excel_file')

    if not excel_file:
        return 'No file uploaded', 400

    df = pd.read_excel(excel_file, engine='openpyxl')

    if chart_choice not in ['u-chart', 'p-chart', 'ma-chart']:
        return 'Invalid chart type', 400

    chart = generate_chart(chart_choice, df)  # Call the generate_chart function here
    chart_file = f"{chart_choice}.html"
    pio.write_html(chart, file=chart_file, full_html=False)
    return send_file(chart_file, as_attachment=True)

import numpy as np
import plotly.express as px

def generate_chart(chart_type, data):
    if chart_type == 'u-chart':
        # Calculate control limits for u-chart
        cl-u-chart = data['Infection Rate'].mean()
        ucl-u-chart = cl-u-chart + 3 * np.sqrt(cl-u-chart / data['Sample Size'])
        lcl-u-chart = cl-u-chart - 3 * np.sqrt(cl-u-chart / data['Sample Size'])
        lcl -u-chart= np.where(lcl < 0, 0, lcl)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Infection Rate', title='U-chart', labels={'Infection Rate': 'Infections per Sample'})
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=cl-u-chart, y1=cl-u-chart, yref='y', xref='x', line=dict(color='red'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=ucl-u-chart, y1=ucl-u-chart, yref='y', xref='x', line=dict(color='green'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=lcl-u-chart, y1=lcl-u-chart, yref='y', xref='x', line=dict(color='green'))

    elif chart_type == 'p-chart':
        # Calculate control limits for p-chart
        pbar = data['Infection Rate'].mean()
        ucl-p-chart = pbar + 3 * np.sqrt(pbar * (1 - pbar) / data['Sample Size'])
        lcl-p-chart = pbar - 3 * np.sqrt(pbar * (1 - pbar) / data['Sample Size'])
        lcl-p-chart = np.where(lcl < 0, 0, lcl)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Infection Rate', title='P-chart', labels={'Infection Rate': 'Proportion of Infections'})
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=pbar, y1=pbar, yref='y', xref='x', line=dict(color='red'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=ucl-p-chart, y1=ucl-p-chart, yref='y', xref='x', line=dict(color='green'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=lcl-p-chart, y1=lcl-p-chart, yref='y', xref='x', line=dict(color='green'))

    elif chart_type == 'ma-chart':
        # Calculate control limits for MA-chart
        window_size = 10
        data['Moving Average'] = data['Infection Rate'].rolling(window=window_size).mean()
        data['Moving Range'] = data['Infection Rate'].rolling(window=2).apply(lambda x: np.abs(x[1] - x[0]), raw=True)
        mrbar = data['Moving Range'].mean()
        sigma = mrbar / (1.128 * np.sqrt(window_size))
        cl-ma-chart = data['Moving Average'].mean()
        ucl-ma-chart = cl-ma-chart + 3 * sigma
        lcl-ma-chart = cl-ma-chart - 3 * sigma
        lcl-ma-chart = np.where(lcl < 0, 0, lcl)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Moving Average', title='MA-chart', labels={'Moving Average': 'Moving Average of Infection Rate'})
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=cl-ma-chart, y1=cl-ma-chart, yref='y', xref='x', line=dict(color='red'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=ucl-ma-chart, y1=ucl-ma-chart, yref='y', xref='x', line=dict(color='green'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=lcl-ma-chart, y1=lcl-ma-chart, yref='y', xref='x', line=dict(color='green'))

    return fig

if __name__ == '__main__':
    app.run(debug=True)
