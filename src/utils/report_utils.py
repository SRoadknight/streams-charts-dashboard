
import plotly.graph_objects as go
import plotly.io as pio
import os
from jinja2 import Environment, FileSystemLoader


def generate_plotly_charts(data):
    """Generates multiple charts for the weekly report."""
    # Example charts
    if data.empty:
        print("No data available to generate charts.")
    
    aggregated_data = data.groupby('channel_country')['hours_watched'].sum().reset_index()

    fig = go.Figure(data=[go.Bar(x=aggregated_data['channel_country'], y=aggregated_data['hours_watched'])])

    fig.update_layout(
        title='Total Hours Watched by Channel Country',
        xaxis_title='Channel Country',
        yaxis_title='Total Hours Watched'
    )

    chart1_html = pio.to_html(fig, full_html=False)

    aggregated_peak_viewers = data.groupby('channel_country')['peak_viewers'].sum().reset_index()
    fig2 = go.Figure(data=[go.Bar(x=aggregated_peak_viewers['channel_country'], y=aggregated_peak_viewers['peak_viewers'])])
    fig2.update_layout(
        title='Total Peak Viewers by Channel Country',
        xaxis_title='Channel Country',
        yaxis_title='Total Peak Viewers'
    )
    chart2_html = pio.to_html(fig2, full_html=False)


    return chart1_html, chart2_html
    

def save_report(file_path, report_html):
    """Saves the report HTML to a .html file."""
    report_dir = os.path.dirname(file_path)

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    with open(file_path, "w") as file:
        file.write(report_html)
    print(f"Report saved to {file_path}.")


def create_report(data, year, week_number, overwirte): 
    """Creates the report HTML."""
    file_path = f"../docs/reports/{year}/{week_number}/{year}{week_number}.html"
    if os.path.exists(file_path) and not overwirte:
        print(f"Report already exists using existing data at {file_path}.")
        return 

    chart1, chart2 = generate_plotly_charts(data)
    env = Environment(loader=FileSystemLoader('../'))
    template = env.get_template('report_template.html')

    content = template.render(year=year, week_number=week_number, chart_html_1=chart1, chart_html_2=chart2)

    save_report(file_path, content)