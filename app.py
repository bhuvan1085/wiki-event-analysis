import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="WikiPulse — Edit Intelligence",
    page_icon="⚡",
    layout="wide"
)

# ── Global CSS (Your beautiful dark theme) ─────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6f0;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f0f1a;
    border-right: 1px solid #1e1e2e;
}
[data-testid="stSidebar"] .stRadio label {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #888;
    letter-spacing: 0.05em;
    padding: 6px 0;
    cursor: pointer;
    transition: color 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #c084fc; }

/* Sidebar brand */
.sidebar-brand {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.4rem;
    color: #c084fc;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.sidebar-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #444;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Page title */
.page-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    letter-spacing: -0.03em;
    line-height: 1.1;
    background: linear-gradient(135deg, #c084fc 0%, #818cf8 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
}
.page-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #555;
    letter-spacing: 0.08em;
    margin-bottom: 2.5rem;
}

/* Metric cards */
.metric-card {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #c084fc44; }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #c084fc, #818cf8);
}
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.6rem;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.2rem;
    color: #e8e6f0;
    letter-spacing: -0.02em;
    line-height: 1;
}
.metric-accent { color: #c084fc; }

/* Section headers */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 2.5rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e1e2e;
}

/* Insight cards */
.insight-card {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}
.insight-tag {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}
.tag-before { background: #1a2e1a; color: #4ade80; }
.tag-after  { background: #2e1a1a; color: #f87171; }
.tag-same   { background: #2e2a1a; color: #fbbf24; }
.insight-text {
    font-size: 0.9rem;
    color: #aaa;
    line-height: 1.5;
}
.insight-corr {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #c084fc;
    margin-top: 0.4rem;
}

/* Download button */
.download-btn {
    background: linear-gradient(135deg, #1e1e2e 0%, #0f0f1a 100%);
    border: 1px solid #c084fc44;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: #c084fc;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    cursor: pointer;
    transition: all 0.2s;
}
.download-btn:hover {
    border-color: #c084fc;
    color: #e8e6f0;
}

/* Selectbox */
[data-testid="stSelectbox"] label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Multiselect */
[data-testid="stMultiSelect"] label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    overflow: hidden;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background-color: #0f0f1a;
    padding: 0.5rem;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #666;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #c084fc20 0%, #818cf820 100%);
    color: #c084fc;
}

/* Expander */
.streamlit-expanderHeader {
    background-color: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #888;
}

/* Divider */
hr { border-color: #1e1e2e; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme (Your dark theme) ────────────────────────
PLOT_THEME = dict(
    paper_bgcolor='#0a0a0f',
    plot_bgcolor='#0f0f1a',
    font=dict(family='Space Mono, monospace', color='#888', size=11),
    xaxis=dict(gridcolor='#1e1e2e', linecolor='#1e1e2e', tickcolor='#333'),
    yaxis=dict(gridcolor='#1e1e2e', linecolor='#1e1e2e', tickcolor='#333'),
    margin=dict(l=40, r=20, t=50, b=40)
)

# ── Load data ─────────────────────────────────────────────
@st.cache_data
def load_data():
    conn = sqlite3.connect('data/database/wiki_edits.db')
    daily_df = pd.read_sql_query("SELECT * FROM daily_edits", conn)
    conn.close()
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    results_df = pd.read_csv('data/processed/lag_analysis_results.csv')
    results_df['event_date'] = pd.to_datetime(results_df['event_date'])
    events_df = pd.read_csv('data/processed/events.csv')
    events_df['event_date'] = pd.to_datetime(events_df['event_date'])
    return daily_df, results_df, events_df

daily_df, results_df, events_df = load_data()

# ── Sidebar (Your design + Compare Topics option) ─────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⚡ WikiPulse</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Edit Intelligence Dashboard</div>', unsafe_allow_html=True)
    page = st.radio("Navigate", ["Overview", "Topic Explorer", "Compare Topics", "Findings"], label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family: Space Mono, monospace; font-size: 0.62rem; color: #333; line-height: 1.8;'>
    DATA SOURCE<br>Wikipedia API<br><br>
    TOPICS<br>8 tracked<br><br>
    METHOD<br>Lag correlation<br>±5 days window
    </div>
    """, unsafe_allow_html=True)

sig = results_df[results_df['significant'] == True]

# ============================================================================
# OVERVIEW (Your design)
# ============================================================================
if page == "Overview":
    st.markdown('<div class="page-title">Do editors see it coming?</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">WIKIPEDIA EDIT SPIKES VS REAL-WORLD EVENTS — LAG CORRELATION ANALYSIS</div>', unsafe_allow_html=True)

    # KPI cards
    before_count = len(sig[sig['lag_days'] < 0]['event'].unique())
    after_count  = len(sig[sig['lag_days'] > 0]['event'].unique())
    same_count   = len(sig[sig['lag_days'] == 0]['event'].unique())
    total_edits  = f"{daily_df['edit_count'].sum():,}"

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("TOPICS TRACKED",       daily_df['topic'].nunique(), "accent"),
        ("ANTICIPATION SIGNALS", before_count,                "accent"),
        ("REACTION SIGNALS",     after_count,                 ""),
        ("TOTAL EDITS ANALYZED", total_edits,                 ""),
    ]
    for col, (label, val, cls) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value {'metric-accent' if cls else ''}">{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Correlation Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.8rem;color:#555;margin-bottom:1rem;">Negative lag = edits spike <b style="color:#4ade80">before</b> event &nbsp;·&nbsp; Positive = <b style="color:#f87171">after</b></p>', unsafe_allow_html=True)

    pivot = results_df.pivot_table(index='topic', columns='lag_days', values='correlation', aggfunc='mean')
    fig = px.imshow(
        pivot,
        color_continuous_scale=[[0, '#f87171'], [0.5, '#0f0f1a'], [1, '#4ade80']],
        color_continuous_midpoint=0,
        text_auto='.2f'
    )
    fig.update_layout(**PLOT_THEME, height=380,
                      coloraxis_colorbar=dict(tickfont=dict(color='#555')))
    fig.update_xaxes(title="Lag Days", title_font=dict(color='#555'))
    fig.update_yaxes(title="")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Timing Breakdown</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 2])

    with col_a:
        before = len(sig[sig['lag_days'] < 0])
        same   = len(sig[sig['lag_days'] == 0])
        after  = len(sig[sig['lag_days'] > 0])

        fig2 = go.Figure(go.Bar(
            x=['Before', 'Same Day', 'After'],
            y=[before, same, after],
            marker_color=['#4ade80', '#fbbf24', '#f87171'],
            text=[before, same, after],
            textposition='outside',
            textfont=dict(color='#888', size=11)
        ))
        fig2.update_layout(**PLOT_THEME, height=300, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="insight-card">
            <span class="insight-tag tag-before">Anticipation</span>
            <div class="insight-text">{before} significant correlations where Wikipedia edit activity spiked <b style="color:#4ade80">before</b> the event occurred.</div>
        </div>
        <div class="insight-card">
            <span class="insight-tag tag-same">Same Day</span>
            <div class="insight-text">{same} events where the spike matched the event date exactly — real-time community response.</div>
        </div>
        <div class="insight-card">
            <span class="insight-tag tag-after">Reaction</span>
            <div class="insight-text">{after} correlations where edits followed the event — classic information cascade pattern.</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TOPIC EXPLORER (Your design + CSV download)
# ============================================================================
elif page == "Topic Explorer":
    st.markdown('<div class="page-title">Topic Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">SELECT A TOPIC AND EVENT TO EXPLORE EDIT PATTERNS</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 3])
    with col_l:
        topic = st.selectbox("Topic", sorted(daily_df['topic'].unique()))
        topic_events = events_df[events_df['topic'] == topic]
        if not topic_events.empty:
            event_choice = st.selectbox("Event", topic_events['event_name'].tolist())

    if topic_events.empty:
        st.warning("No events found for this topic.")
    else:
        selected_event = topic_events[topic_events['event_name'] == event_choice].iloc[0]
        event_date = selected_event['event_date']
        topic_edits = daily_df[daily_df['topic'] == topic].sort_values('date')

        mask = (
            (topic_edits['date'] >= event_date - pd.Timedelta(days=30)) &
            (topic_edits['date'] <= event_date + pd.Timedelta(days=30))
        )
        window = topic_edits[mask]

        st.markdown('<div class="section-header">Edit Activity Timeline</div>', unsafe_allow_html=True)

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=window['date'], y=window['edit_count'],
            mode='lines', name='Daily Edits',
            line=dict(color='#818cf8', width=2),
            fill='tozeroy',
            fillcolor='rgba(129,140,248,0.08)'
        ))
        fig3.add_shape(
            type="line", x0=event_date, x1=event_date,
            y0=0, y1=1, xref="x", yref="paper",
            line=dict(color="#c084fc", width=1.5, dash="dash")
        )
        fig3.add_annotation(
            x=event_date, y=0.97, xref="x", yref="paper",
            text=f"⚡ {event_choice}", showarrow=False,
            font=dict(color="#c084fc", size=11, family="Space Mono"),
            xanchor="left", bgcolor="#0a0a0f", borderpad=4
        )
        fig3.update_layout(**PLOT_THEME, height=360,
                           title=dict(text=f"{topic} — ±30 days", font=dict(color='#444', size=12)))
        fig3.update_xaxes(title="Date")
        fig3.update_yaxes(title="Daily Edits")
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown('<div class="section-header">Lag Correlation</div>', unsafe_allow_html=True)

        topic_results = results_df[
            (results_df['topic'] == topic) &
            (results_df['event'] == event_choice)
        ]

        if not topic_results.empty:
            colors = ['#4ade80' if l < 0 else '#f87171' if l > 0 else '#fbbf24'
                      for l in topic_results['lag_days']]

            fig4 = go.Figure(go.Bar(
                x=topic_results['lag_days'],
                y=topic_results['correlation'],
                marker_color=colors,
                text=topic_results['correlation'].round(3),
                textposition='outside',
                textfont=dict(size=10, color='#888')
            ))
            fig4.update_layout(**PLOT_THEME, height=320, showlegend=False,
                               title=dict(text="Correlation at each lag day", font=dict(color='#444', size=12)))
            fig4.update_xaxes(title="Lag Days", tickmode='linear', dtick=1)
            fig4.update_yaxes(title="Correlation")
            st.plotly_chart(fig4, use_container_width=True)

            best = topic_results.loc[topic_results['correlation'].abs().idxmax()]
            direction = "BEFORE" if best['lag_days'] < 0 else "AFTER" if best['lag_days'] > 0 else "SAME DAY"
            tag_class = "tag-before" if best['lag_days'] < 0 else "tag-after" if best['lag_days'] > 0 else "tag-same"

            st.markdown(f"""
            <div class="insight-card">
                <span class="insight-tag {tag_class}">{direction}</span>
                <div class="insight-text">{best['interpretation']}</div>
                <div class="insight-corr">r = {best['correlation']:.4f} &nbsp;·&nbsp; p = {best['p_value']:.4f} &nbsp;·&nbsp; lag = {int(best['lag_days'])} days</div>
            </div>
            """, unsafe_allow_html=True)

            # CSV Download Button (NEW FEATURE)
            csv_data = topic_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download correlation data (CSV)",
                data=csv_data,
                file_name=f"{topic}_{event_choice}_correlation.csv",
                mime="text/csv"
            )

            with st.expander("Full results table"):
                st.dataframe(
                    topic_results[['lag_days', 'correlation', 'p_value', 'significant', 'interpretation']]
                    .style.format({'correlation': '{:.4f}', 'p_value': '{:.4f}'}),
                    use_container_width=True
                )

# ============================================================================
# COMPARE TOPICS (NEW PAGE - From my Day 7)
# ============================================================================
elif page == "Compare Topics":
    st.markdown('<div class="page-title">Compare Topics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">SIDE-BY-SIDE COMPARISON OF EDIT PATTERNS</div>', unsafe_allow_html=True)

    compare_topics = st.multiselect(
        "Select topics to compare",
        options=sorted(daily_df['topic'].unique()),
        default=sorted(daily_df['topic'].unique())[:3]
    )

    if len(compare_topics) > 0:
        comparison_data = daily_df[daily_df['topic'].isin(compare_topics)]
        
        # Daily edit trends comparison
        st.markdown('<div class="section-header">Daily Edit Trends</div>', unsafe_allow_html=True)
        fig_compare = px.line(
            comparison_data,
            x='date',
            y='edit_count',
            color='topic',
            title="",
            labels={'edit_count': 'Number of Edits', 'date': 'Date', 'topic': 'Topic'}
        )
        fig_compare.update_layout(**PLOT_THEME, height=450)
        fig_compare.update_traces(line=dict(width=2))
        st.plotly_chart(fig_compare, use_container_width=True)
        
        # Box plot comparison
        st.markdown('<div class="section-header">Edit Distribution</div>', unsafe_allow_html=True)
        fig_box = px.box(
            comparison_data,
            x='topic',
            y='edit_count',
            color='topic',
            title="",
            labels={'edit_count': 'Number of Edits', 'topic': 'Topic'}
        )
        fig_box.update_layout(**PLOT_THEME, height=450, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        
        # Statistics table with download
        st.markdown('<div class="section-header">Summary Statistics</div>', unsafe_allow_html=True)
        stats_df = comparison_data.groupby('topic')['edit_count'].agg([
            ('Total Edits', 'sum'),
            ('Daily Average', 'mean'),
            ('Peak Edits', 'max'),
            ('Std Dev', 'std')
        ]).round(1)
        st.dataframe(stats_df, use_container_width=True)
        
        # Download comparison data
        csv_compare = comparison_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download comparison data (CSV)",
            data=csv_compare,
            file_name="topic_comparison.csv",
            mime="text/csv"
        )
    else:
        st.warning("Please select at least one topic to compare")

# ============================================================================
# FINDINGS (Your design + CSV download)
# ============================================================================
elif page == "Findings":
    st.markdown('<div class="page-title">Key Findings</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">STRONGEST SIGNALS ACROSS ALL TOPICS AND EVENTS</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Top 10 Strongest Correlations</div>', unsafe_allow_html=True)
    top10 = sig.nlargest(10, 'correlation')[
        ['topic', 'event', 'lag_days', 'correlation', 'p_value', 'interpretation']
    ].reset_index(drop=True)
    st.dataframe(
        top10.style.format({'correlation': '{:.4f}', 'p_value': '{:.6f}'}),
        use_container_width=True, height=320
    )
    
    # Download top 10
    csv_top10 = top10.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download top 10 correlations (CSV)",
        data=csv_top10,
        file_name="top10_correlations.csv",
        mime="text/csv"
    )

    st.markdown('<div class="section-header">Correlation vs Lag</div>', unsafe_allow_html=True)
    fig5 = px.scatter(
        sig, x='lag_days', y='correlation',
        color='severity', size='correlation',
        hover_data=['topic', 'event', 'interpretation'],
        color_discrete_map={'high': '#c084fc', 'medium': '#818cf8'}
    )
    fig5.add_vline(x=0, line_dash="dot", line_color="#333")
    fig5.update_layout(**PLOT_THEME, height=380,
                       legend=dict(font=dict(color='#555')))
    fig5.update_xaxes(title="Lag Days")
    fig5.update_yaxes(title="Correlation")
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown('<div class="section-header">Breakdown</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    sev = sig.groupby('severity').size().reset_index(name='count')
    fig6 = go.Figure(go.Pie(
        labels=sev['severity'], values=sev['count'],
        marker_colors=['#c084fc', '#818cf8'],
        hole=0.6,
        textfont=dict(family='Space Mono', size=10)
    ))
    fig6.update_layout(**PLOT_THEME, height=280,
                       title=dict(text="By Severity", font=dict(color='#444', size=12)),
                       showlegend=True,
                       legend=dict(font=dict(color='#555')))
    col1.plotly_chart(fig6, use_container_width=True)

    timing = pd.DataFrame({
        'Direction': ['Before', 'Same Day', 'After'],
        'Count': [len(sig[sig['lag_days'] < 0]),
                  len(sig[sig['lag_days'] == 0]),
                  len(sig[sig['lag_days'] > 0])]
    })
    fig7 = go.Figure(go.Pie(
        labels=timing['Direction'], values=timing['Count'],
        marker_colors=['#4ade80', '#fbbf24', '#f87171'],
        hole=0.6,
        textfont=dict(family='Space Mono', size=10)
    ))
    fig7.update_layout(**PLOT_THEME, height=280,
                       title=dict(text="Timing", font=dict(color='#444', size=12)),
                       showlegend=True,
                       legend=dict(font=dict(color='#555')))
    col2.plotly_chart(fig7, use_container_width=True)

    st.markdown('<div class="section-header">All Significant Results</div>', unsafe_allow_html=True)
    
    all_sig = sig[['topic', 'event', 'lag_days', 'correlation', 'p_value', 'interpretation']]
    all_sig_sorted = all_sig.sort_values('correlation', ascending=False).reset_index(drop=True)
    st.dataframe(all_sig_sorted, use_container_width=True)
    
    # Download all results
    csv_all = all_sig_sorted.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download all significant results (CSV)",
        data=csv_all,
        file_name="all_significant_correlations.csv",
        mime="text/csv"
    )

# ── Footer ────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:4rem; padding-top:1.5rem; border-top:1px solid #1e1e2e;
font-family:Space Mono,monospace; font-size:0.62rem; color:#333;
display:flex; justify-content:space-between;'>
<span>WIKIPULSE · EDIT INTELLIGENCE</span>
<span>DATA: WIKIPEDIA API · METHOD: LAG CORRELATION ±5 DAYS · SIG: p &lt; 0.05</span>
</div>
""", unsafe_allow_html=True)