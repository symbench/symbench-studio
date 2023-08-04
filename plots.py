import plotly.graph_objects as go
import numpy as np
import pandas as pd


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


def plot_trace(df, solver_name, config_name, alt_cols):
    trace = go.Scatter(
        x=df[alt_cols[0]],
        y=df[alt_cols[1]],
        mode='markers',
        name=f'{solver_name}: {config_name} (num sols={len(df)})'
    )
    return trace
    

def update_fig_layout(fig, problem_name, all_solvers, alt_cols, sliders):
    fig.update_layout(
        title=f'Solutions to {problem_name} solved with {all_solvers}',
        xaxis_title=alt_cols[0],
        yaxis_title=alt_cols[1],
        sliders=sliders
    )
    return fig


def plot_solutions(df, problem_name, all_solvers, alt_cols):

    # df = pd.DataFrame({
    #     'iter': [1, 2, 3, 4, 5, 6, 7],
    #     'x': [71.9408, 2.0229, 95.4568, 0.2627, 36.07, 2.4607, 7.7681],
    #     'y': [8.0124, 40.5086, 5.8351, 46.445, 16.5567, 40.5072, 32.2622]
    # })

    iterations = df['iter'].unique()
    iterations.sort()

    fig = go.Figure()

    for i in iterations:
        iteration_df = df[df['iter'] == i]
        fig.add_trace(
            go.Scatter(
                visible=False,
                mode='markers',
                name=f"Iteration {i}",
                x=iteration_df['x'],
                y=iteration_df['y']
            )
        )

    fig.data[0].visible = True

    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                {"title": f"Iteration: {iterations[i]}"}],
        )
        step["args"][0]["visible"][:i+1] = [True] * (i+1)  # Toggle visibility up to i'th trace
        steps.append(step)

    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Iteration: "},
        pad={"t": 50},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )

    fig.show()
