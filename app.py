from dash import Dash, dash_table, html, dcc, Input, Output, State, callback
import math


app = Dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Under Construction"),
    html.H5("currently only calculates the power of each hourly entered LEQ and adds the Penalty Power together.  Need to sum all power values then perform the logarithmic average to get the 24-hour period.  Please make sure your 24-hour period is from 7am to 7am then the next day."),
    html.H1("Noise Calculation Check Page"),  # Title
    html.Div([
        html.Div([
            html.H3("LDEN"),  # Text box for LDEN
            html.H4("Change values in the Pale Blue boxes.")
        ], style={'width': '15%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            dash_table.DataTable(
                id='computed-table',
                columns=[
                    {'name': 'Hour', 'id': 'table-hour'},
                    {'name': 'Input LEQ', 'id': 'input-data'},
                    {'name': 'LEQ Power', 'id': 'output-data'},
                    {'name': 'Input LEQ Penalty', 'id': 'input-data-penalty'}
                ],
                data=[{'table-hour': i, 'input-data': 0, 'input-data-penalty': 10 if i <= 6 or i >= 22 else (5 if 19 <= i <= 21 else 0)} for i in range(24)],
                editable=True,
                style_data_conditional=[
                    {'if': {'column_id': 'table-hour', 'filter_query': '{table-hour} >= 22 || {table-hour} <=6'}, 'backgroundColor': 'cadetBlue', 'tooltip': 'Nighttime hours (10pm - 6am)'},
                    {'if': {'column_id': 'table-hour', 'filter_query': '{table-hour} >= 19 && {table-hour} <= 21'}, 'backgroundColor': 'cornsilk', 'tooltip': 'Evening hours (7pm - 9pm)'},
                    {'if': {'column_id': 'input-data'}, 'backgroundColor': 'azure'},
                    {'if': {'column_id': 'input-data-penalty'}, 'backgroundColor': 'azure'}
                ],
                style_header={
                    'backgroundColor': 'darkSlateGrey',
                    'color': 'white',
                }
            ),
        ], style={'width': '40%', 'display': 'inline-block'}),
    ]),
    dcc.Markdown('''**LDEN** stands for **'Level Day Evening Night,'** and it is a metric used to quantify the equivalent continuous noise level over a 24-hour period. LDEN is often employed in environmental noise assessment and is a weighted average of noise levels during the day, evening, and night periods.'''),  # Paragraph
    dcc.Markdown('''The purpose of **LDEN** is to account for the varying sensitivity of people to noise at different times of the day. The formula for LDEN typically involves applying specific weighting factors to the noise levels measured during daytime, evening, and nighttime hours. These factors reflect the increased sensitivity to noise during the evening and night.'''),
    dcc.Markdown('''**LDEN** is commonly used in the field of environmental noise impact assessment, especially for transportation noise studies (e.g., road traffic or aircraft noise). It helps provide a comprehensive picture of the noise exposure experienced by a community over a 24-hour period, considering the different activities and behaviors during the day and night.'''),
    html.P(" "),
    dcc.Markdown('''**Noise Levels:**'''),
    dcc.Markdown('''>**Equivalent Continuous Noise Level (Leq): **It measures the continuous noise level over a specific period, often 24 hours.'''),
    dcc.Markdown('''>**Day-Night Average Sound Level (Ldn):** Similar to LDEN, Ldn is a 24-hour average noise level with additional penalties for nighttime noise.'''),
    dcc.Markdown('''>**Maximum Noise Levels:** The loudest noise level produced during specific flight phases, such as takeoff or landing.'''),
    html.P(" "),
    html.P("Typically, LDEN is from 07:00:00 day 1, through to 06:59:59 day 2.  CNEL is from Midnight to Midnight (i.e. same day), therefore having two night periods.  DNL, is typically midnight to midnight, with no evening penalty, just a night time penalty is applied."),
    html.P(" "),
    html.H6("Page under construction.  Created by LP")  # Footer
])


@app.callback(
    Output('computed-table', 'data'),
    [Input('computed-table', 'data_timestamp')],
    [State('computed-table', 'data')]
)
def update_columns(timestamp, rows):
    for row in rows:
        try:
            total_power = 0
            value1_numeric = float(row['input-data'])
            value2_numeric = int(row['input-data-penalty'])
            if value1_numeric > 0:
                if value2_numeric > 0:
                    value_numeric = value1_numeric + float(value2_numeric)
                else:
                    value_numeric = value1_numeric
                row['output-data'] = 10 ** (value_numeric / 10)
            else:
                row['output-data'] = 0
        except:
            row['output-data'] = 'NA'

    total_row = next((row for row in rows if row['table-hour'] == 'Total'), None)
    if total_row:
        total_output_data = sum(row.get('output-data', 0) for row in rows)
        count_positive_output = sum(1 for row in rows if row.get('output-data', 0) > 0)
        if count_positive_output > 0:
            new_total = 10 * math.log10(total_output_data / count_positive_output)
        else:
            new_total = 0
        total_row['output-data'] = total_output_data
        total_row['input-data-penalty'] = new_total
    else:
        total_output_data = sum(row.get('output-data', 0) for row in rows)
        count_positive_output = sum(1 for row in rows if row.get('output-data', 0) > 0)
        if count_positive_output > 0:
            new_total = 10 * math.log10(total_output_data / count_positive_output)
        else:
            new_total = 0
        total_row = {'table-hour': 'Total', 'input-data': new_total, 'output-data': total_output_data, 'input-data-penalty': 0}
        rows.append(total_row)

    return rows




if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
