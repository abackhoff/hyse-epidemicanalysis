# app.py
from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import os

app = Flask(_name_)

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

    if chart_choice == 'u_chart':
        chart = create_u_chart(df)
    elif chart_choice == 'p_chart':
        chart = create_p_chart(df)
    elif chart_choice == 'ma_chart':
        chart = create_ma_chart(df)
    else:
        return 'Invalid chart type', 400

    chart_file = f"{chart_choice}.html"
    pio.write_html(chart, file=chart_file, full_html=False)
    return send_file(chart_file, as_attachment=True)

import numpy as np
import plotly.express as px

def generate_chart(chart_type, data):
    if chart_type == 'u-chart':
        # Calculate control limits for u-chart
        cl = data['Infection Rate'].mean()
        ucl = cl + 3 * np.sqrt(cl / data['Sample Size'])
        lcl = cl - 3 * np.sqrt(cl / data['Sample Size'])
        lcl = np.where(lcl < 0, 0, lcl)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Infection Rate', title='U-chart', labels={'Infection Rate': 'Infections per Sample'})
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=cl, y1=cl, yref='y', xref='x', line=dict(color='red'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=ucl, y1=ucl, yref='y', xref='x', line=dict(color='green'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=lcl, y1=lcl, yref='y', xref='x', line=dict(color='green'))

    elif chart_type == 'p-chart':
        # Calculate control limits for p-chart
        pbar = data['Infection Rate'].mean()
        ucl = pbar + 3 * np.sqrt(pbar * (1 - pbar) / data['Sample Size'])
        lcl = pbar - 3 * np.sqrt(pbar * (1 - pbar) / data['Sample Size'])
        lcl = np.where(lcl < 0, 0, lcl)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Infection Rate', title='P-chart', labels={'Infection Rate': 'Proportion of Infections'})
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=pbar, y1=pbar, yref='y', xref='x', line=dict(color='red'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=ucl, y1=ucl, yref='y', xref='x', line=dict(color='green'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=lcl, y1=lcl, yref='y', xref='x', line=dict(color='green'))

    elif chart_type == 'ma-chart':
        # Calculate control limits for MA-chart
        window_size = 10
        data['Moving Average'] = data['Infection Rate'].rolling(window=window_size).mean()
        data['Moving Range'] = data['Infection Rate'].rolling(window=2).apply(lambda x: np.abs(x[1] - x[0]), raw=True)
        mrbar = data['Moving Range'].mean()
        sigma = mrbar / (1.128 * np.sqrt(window_size))
        cl = data['Moving Average'].mean()
        ucl = cl + 3 * sigma
        lcl = cl - 3 * sigma
        lcl = np.where(lcl < 0, 0, lcl)  # LCL should not be negative

        fig = px.line(data, x='Period', y='Moving Average', title='MA-chart', labels={'Moving Average': 'Moving Average of Infection Rate'})
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=cl, y1=cl, yref='y', xref='x', line=dict(color='red'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=ucl, y1=ucl, yref='y', xref='x', line=dict(color='green'))
        fig.add_shape(type='line', x0=data['Period'].min(), x1=data['Period'].max(), y0=lcl, y1=lcl, yref='y', xref='x', line=dict(color='green'))

    fig.show()

if _name_ == '_main_':
    app.run(debug=True)
[1:40 PM, 3/28/2023] Pato Gutierrez: <!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Excel Chart Generator</title>
</head>
<body>
    <h1>Upload Excel file and choose chart type</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <label for="excel_file">Excel File:</label>
        <input type="file" name="excel_file" accept=".xls,.xlsx" required>
        <br><br>
        <label for="chart_type">Chart Type:</label>
        <select name="chart_type" required>
            <option value="">--Please choose a chart type--</option>
            <option value="u_chart">U-Chart</option>
            <option value="p_chart">P-Chart</option>
            <option value="ma_chart">MA-Chart</option>
        </select>
        <br><br>
        <button type="submit">Generate Chart</button>
    </form>
</body>
</html>
