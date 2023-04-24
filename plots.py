import plotly.graph_objects as go

def plot_pareto_front(x, y, title='Pareto Front'):
    """
    Creates a plotly chart of the Pareto front for an optimization problem
    given the results of the optimization.

    Parameters:
        x (list): A list of x-axis values for the Pareto front.
        y (list): A list of y-axis values for the Pareto front.
        title (str): Optional title for the chart.

    Returns:
        A plotly figure object.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers', marker=dict(size=10)))
    fig.update_layout(
        title=title,
        xaxis_title='Objective 1',
        yaxis_title='Objective 2',
        margin=dict(l=50, r=50, t=50, b=50),
    )
    return fig
