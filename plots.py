import plotly.graph_objects as go
import numpy as np


def plot_pareto_front(title='Pareto Front'):
    
    np.random.seed(42)
    x = np.random.rand(30)
    y = np.random.rand(30)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers', marker=dict(size=10)))
    fig.update_layout(
        title=title,
        xaxis_title='Objective 1',
        yaxis_title='Objective 2',
        margin=dict(l=50, r=50, t=50, b=50),
    )
    return fig
