import plotly.graph_objects as go
import plotly.express as px

COLOUR_MAP = {
    'Stagflation': '#E6A8D7',  # Pastel Orchid
    'Overheat': '#B3CDE0',  # Pastel Blue
    'Reccesion': '#B7D7B5',  # Pastel Mint Green
    'Recovery': '#F4C7A1',  # Pastel Peach
}

def plot_multi(to_plot):
    fig = px.line(to_plot, x='date' , y='value', color='label')

    # Apply background color dynamically based on OECD_CH values
    legend_patches = []
    seen_colors = set()  # To track which colors have already been added to the legend

    # Apply background color dynamically based on OECD_CH values
    previous_oecd_value = None
    start_date = None

    cycle = to_plot[to_plot['label'] == 'market']
    cycle.set_index('date', inplace=True)
    for date in cycle.index:
        oecd_value = cycle.loc[date, 'OECD_CH']  # Get the OECD_CH value at each date
        if oecd_value != previous_oecd_value:
            if start_date is not None:
                # Add a 'rect' shape for background coloring in Plotly
                bg_color = COLOUR_MAP.get(previous_oecd_value, 'white')
                fig.add_shape(type="rect", 
                            x0=start_date, x1=date, 
                            y0=0, y1=1, 
                            xref="x", yref="paper", 
                            fillcolor=bg_color, opacity=0.3,
                            line=dict(color='rgba(0,0,0,0)', width=0))

                # Create a dummy trace for the background color to appear in the legend, if not already added
                if bg_color not in seen_colors:
                    legend_patches.append(go.Scatter(
                        x=[None], y=[None], mode='markers',
                        marker=dict(color=bg_color, size=10),
                        name=f"OECD_CH {previous_oecd_value}"  # Add to legend
                    ))
                    seen_colors.add(bg_color)  # Mark the color as seen

            start_date = date  # Update the start date for the new period
        previous_oecd_value = oecd_value

    # Ensure the last region gets colored for background color
    if previous_oecd_value is not None:
        bg_color = COLOUR_MAP.get(previous_oecd_value, 'white')
        fig.add_shape(type="rect", 
                    x0=start_date, x1=cycle.index[-1], 
                    y0=0, y1=1, 
                    xref="x", yref="paper", 
                    fillcolor=bg_color, opacity=0.3,
                            line=dict(color='rgba(0,0,0,0)', width=0))

        # Create a dummy trace for the last background color to appear in the legend, if not already added
        if bg_color not in seen_colors:
            legend_patches.append(go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(color=bg_color, size=10),
                name=f"{previous_oecd_value}"  # Add to legend
            ))
            seen_colors.add(bg_color)  # Mark the color as seen

    # Add the dummy traces for background color to the figure to show in the legend
    fig.add_traces(legend_patches)

    # Add title and labels
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Cum Sum Return",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def plot(result_incl, result_excl, market):
    fig = go.Figure()

    # Add the first line plot (Favour, Avoid, and Market) for the first subplot
    fig.add_trace(go.Scatter(x=result_incl.loc[result_incl.index >= '2005-11-01'].index, 
                            y=result_incl.loc[result_incl.index >= '2005-11-01']['favour_mean'].cumsum(),
                            mode='lines', name='Favour'))

    fig.add_trace(go.Scatter(x=result_excl.loc[result_excl.index >= '2005-11-01'].index, 
                            y=result_excl.loc[result_excl.index >= '2005-11-01']['avoid_mean'].cumsum(),
                            mode='lines', name='Avoid'))

    fig.add_trace(go.Scatter(x=market.loc[market.index >= '2005-11-01'].index, 
                            y=market.loc[market.index >= '2005-11-01'].cumsum(),
                            mode='lines', name='Market'))  
    
    # Apply background color dynamically based on OECD_CH values
    legend_patches = []
    seen_colors = set()  # To track which colors have already been added to the legend

    # Apply background color dynamically based on OECD_CH values
    previous_oecd_value = None
    start_date = None

    for date in result_incl.index:
        oecd_value = result_incl.loc[date, 'OECD_CH']  # Get the OECD_CH value at each date
        if oecd_value != previous_oecd_value:
            if start_date is not None:
                # Add a 'rect' shape for background coloring in Plotly
                bg_color = COLOUR_MAP.get(previous_oecd_value, 'white')
                fig.add_shape(type="rect", 
                            x0=start_date, x1=date, 
                            y0=0, y1=1, 
                            xref="x", yref="paper", 
                            fillcolor=bg_color, opacity=0.3,
                            line=dict(color='rgba(0,0,0,0)', width=0))

                # Create a dummy trace for the background color to appear in the legend, if not already added
                if bg_color not in seen_colors:
                    legend_patches.append(go.Scatter(
                        x=[None], y=[None], mode='markers',
                        marker=dict(color=bg_color, size=10),
                        name=f"OECD_CH {previous_oecd_value}"  # Add to legend
                    ))
                    seen_colors.add(bg_color)  # Mark the color as seen

            start_date = date  # Update the start date for the new period
        previous_oecd_value = oecd_value

    # Ensure the last region gets colored for background color
    if previous_oecd_value is not None:
        bg_color = COLOUR_MAP.get(previous_oecd_value, 'white')
        fig.add_shape(type="rect", 
                    x0=start_date, x1=result_incl.index[-1], 
                    y0=0, y1=1, 
                    xref="x", yref="paper", 
                    fillcolor=bg_color, opacity=0.3,
                            line=dict(color='rgba(0,0,0,0)', width=0))

        # Create a dummy trace for the last background color to appear in the legend, if not already added
        if bg_color not in seen_colors:
            legend_patches.append(go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(color=bg_color, size=10),
                name=f"{previous_oecd_value}"  # Add to legend
            ))
            seen_colors.add(bg_color)  # Mark the color as seen

    # Add the dummy traces for background color to the figure to show in the legend
    fig.add_traces(legend_patches)

    # Add title and labels
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Cum Sum Return",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig
