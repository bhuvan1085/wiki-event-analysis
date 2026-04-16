"""
Wikipedia Edit Event Visualization
Creates charts to visualize lag correlations and event timelines
"""

import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Create directories
import os
os.makedirs('data/visualizations', exist_ok=True)

def load_data():
    """Load processed data and analysis results"""
    # Load daily edit data
    conn = sqlite3.connect('data/database/wiki_edits.db')
    daily_df = pd.read_sql_query("SELECT * FROM daily_edits", conn)
    conn.close()
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    
    # Load lag analysis results
    results_df = pd.read_csv('data/processed/lag_analysis_results.csv')
    results_df['event_date'] = pd.to_datetime(results_df['event_date'])
    
    # Load events
    events_df = pd.read_csv('data/processed/events.csv')
    events_df['event_date'] = pd.to_datetime(events_df['event_date'])
    
    return daily_df, results_df, events_df

def create_lag_bar_chart(results_df, topic_name=None):
    """
    Create bar chart showing correlation by lag day for a specific topic or all topics
    """
    if topic_name:
        # Filter for specific topic
        topic_results = results_df[results_df['topic'] == topic_name]
        title = f"Lag Correlation: {topic_name}"
    else:
        # Average across all topics
        topic_results = results_df.groupby('lag_days').agg({
            'correlation': 'mean',
            'significant': 'mean'
        }).reset_index()
        title = "Average Lag Correlation Across All Topics"
    
    # Create bar chart
    colors = ['red' if x < 0 else 'blue' if x > 0 else 'green' for x in topic_results['lag_days']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=topic_results['lag_days'],
        y=topic_results['correlation'],
        marker_color=colors,
        text=topic_results['correlation'].round(3),
        textposition='outside',
        name='Correlation'
    ))
    
    # Add significance threshold line
    fig.add_hline(y=0.2, line_dash="dash", line_color="gray", 
                  annotation_text="Significant threshold (r=0.2)")
    fig.add_hline(y=-0.2, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title=title,
        xaxis_title="Lag Days (negative = edits before event, positive = edits after event)",
        yaxis_title="Correlation (point-biserial r)",
        template="plotly_white",
        height=500,
        showlegend=False
    )
    
    return fig

def create_event_timeline(daily_df, events_df, topic_name, event_name=None):
    """Create timeline plot showing edit counts with event markers using shapes"""
    topic_data = daily_df[daily_df['topic'] == topic_name].copy()

    if event_name:
        event_data = events_df[(events_df['topic'] == topic_name) &
                                (events_df['event_name'] == event_name)]
    else:
        event_data = events_df[events_df['topic'] == topic_name]

    if len(event_data) == 0:
        print(f"No events found for {topic_name}")
        return None

    min_date = event_data['event_date'].min() - pd.Timedelta(days=30)
    max_date = event_data['event_date'].max() + pd.Timedelta(days=30)

    timeline_data = topic_data[(topic_data['date'] >= min_date) &
                                (topic_data['date'] <= max_date)]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=timeline_data['date'],
        y=timeline_data['edit_count'],
        mode='lines',
        name='Daily Edits',
        line=dict(color='blue', width=2),
        fill='tozeroy',
        fillcolor='rgba(0,0,255,0.1)'
    ))

    # Use shapes + annotations instead of add_vline
    shapes = []
    annotations = []
    for _, event in event_data.iterrows():
        event_date = event['event_date']
        shapes.append(dict(
            type="line",
            x0=event_date, x1=event_date,
            y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(color="red", width=2, dash="dash")
        ))
        annotations.append(dict(
            x=event_date,
            y=1,
            xref="x", yref="paper",
            text=event['event_name'],
            showarrow=False,
            font=dict(size=10, color="red"),
            xanchor="left"
        ))

    fig.update_layout(
        title=f"Wikipedia Edit Activity: {topic_name}",
        xaxis_title="Date",
        yaxis_title="Number of Edits per Day",
        template="plotly_white",
        height=500,
        hovermode='x unified',
        shapes=shapes,
        annotations=annotations
    )

    return fig

def create_heatmap(results_df):
    """
    Create heatmap of correlations by topic and lag
    """
    # Pivot table for heatmap
    pivot_df = results_df.pivot_table(
        index='topic', 
        columns='lag_days', 
        values='correlation',
        fill_value=0
    )
    
    # Sort by topic name
    pivot_df = pivot_df.sort_index()
    
    fig = px.imshow(
        pivot_df,
        text_auto='.2f',
        aspect="auto",
        color_continuous_scale='RdBu_r',
        title="Correlation Heatmap: Topic vs Lag Days",
        labels=dict(x="Lag Days", y="Topic", color="Correlation")
    )
    
    fig.update_layout(height=500, width=800)
    
    return fig

def create_severity_comparison(results_df):
    """
    Compare high vs medium severity events
    """
    severity_stats = results_df[results_df['significant'] == True].groupby('severity').size().reset_index(name='count')
    
    fig = px.pie(
        severity_stats,
        values='count',
        names='severity',
        title='Significant Correlations by Event Severity',
        color='severity',
        color_discrete_map={'high': 'red', 'medium': 'orange'}
    )
    
    return fig

def create_lag_distribution(results_df):
    """
    Distribution of optimal lag days for significant correlations
    """
    sig_results = results_df[results_df['significant'] == True]
    lag_counts = sig_results['lag_days'].value_counts().sort_index()
    
    fig = go.Figure()
    
    colors = ['red' if x < 0 else 'blue' if x > 0 else 'green' for x in lag_counts.index]
    
    fig.add_trace(go.Bar(
        x=lag_counts.index,
        y=lag_counts.values,
        marker_color=colors,
        text=lag_counts.values,
        textposition='outside'
    ))
    
    fig.update_layout(
        title="When Do Edit Spikes Happen? (Significant Correlations Only)",
        xaxis_title="Lag Days",
        yaxis_title="Number of Significant Correlations",
        template="plotly_white",
        height=500
    )
    
    return fig

def create_top_performers(results_df):
    """
    Create bar chart of strongest correlations
    """
    sig_results = results_df[results_df['significant'] == True]
    top_correlations = sig_results.nlargest(10, 'correlation')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_correlations['correlation'],
        y=top_correlations['event'] + " (" + top_correlations['topic'] + ")",
        orientation='h',
        marker_color=top_correlations['lag_days'].apply(
            lambda x: 'red' if x < 0 else 'blue' if x > 0 else 'green'
        ),
        text=top_correlations['correlation'].round(3),
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Top 10 Strongest Correlations",
        xaxis_title="Correlation (point-biserial r)",
        yaxis_title="Event",
        template="plotly_white",
        height=600,
        showlegend=False
    )
    
    return fig

def save_figure(fig, filename):
    """Save figure as HTML"""
    fig.write_html(f"data/visualizations/{filename}.html")
    print(f"  Saved: data/visualizations/{filename}.html")

def main():
    """Generate all visualizations"""
    print("=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    daily_df, results_df, events_df = load_data()
    print(f"Loaded {len(daily_df)} daily records, {len(results_df)} lag results, {len(events_df)} events")
    
    # 1. Overall lag bar chart (average across all topics)
    print("\n1. Creating overall lag bar chart...")
    fig1 = create_lag_bar_chart(results_df)
    save_figure(fig1, "overall_lag_correlation")
    
    # 2. Heatmap
    print("2. Creating correlation heatmap...")
    fig2 = create_heatmap(results_df)
    save_figure(fig2, "correlation_heatmap")
    
    # 3. Lag distribution
    print("3. Creating lag distribution chart...")
    fig3 = create_lag_distribution(results_df)
    save_figure(fig3, "lag_distribution")
    
    # 4. Severity comparison
    print("4. Creating severity comparison pie chart...")
    fig4 = create_severity_comparison(results_df)
    save_figure(fig4, "severity_comparison")
    
    # 5. Top performers
    print("5. Creating top correlations chart...")
    fig5 = create_top_performers(results_df)
    save_figure(fig5, "top_correlations")
    
    # 6-13. Individual topic lag charts
    print("\n6. Creating individual topic lag charts...")
    topics = daily_df['topic'].unique()
    for topic in topics:
        print(f"  Creating chart for {topic}...")
        fig = create_lag_bar_chart(results_df, topic)
        save_figure(fig, f"lag_{topic.replace(',', '').replace(' ', '_')}")
    
    # 14-21. Event timelines for each topic
    print("\n7. Creating event timelines...")
    for topic in topics:
        print(f"  Creating timeline for {topic}...")
        fig = create_event_timeline(daily_df, events_df, topic)
        if fig:
            save_figure(fig, f"timeline_{topic.replace(',', '').replace(' ', '_')}")
    
    print("\n" + "=" * 60)
    print("VISUALIZATIONS COMPLETE!")
    print("=" * 60)
    print(f"\nAll visualizations saved to: data/visualizations/")
    print("\nFiles created:")
    print("  - overall_lag_correlation.html")
    print("  - correlation_heatmap.html")
    print("  - lag_distribution.html")
    print("  - severity_comparison.html")
    print("  - top_correlations.html")
    print("  - lag_*.html (one per topic)")
    print("  - timeline_*.html (one per topic)")
    print("\nTo view: Open any .html file in your browser")

if __name__ == "__main__":
    main()