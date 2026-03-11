import streamlit as st
import pandas as pd
import json
import time
import os
import altair as alt

# Page Config
st.set_page_config(
    page_title="Smart Grid Telemetry",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants
LOG_FILE = "/app/results/logs/agent_activity.jsonl"
REFRESH_RATE = 2 # seconds

# --- MINIMAL THEME ---
st.markdown("""
<style>
    /* Global Reset */
    .stApp {
        background-color: #0E1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-weight: 300 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Metrics - Clean & Flat */
    div[data-testid="metric-container"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 8px;
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #58A6FF;
    }
    
    /* Status Cards - Minimal Pills */
    .status-card {
        background-color: #161B22;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #30363D;
        margin-bottom: 6px;
        font-size: 0.85em;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .status-dot {
        height: 8px;
        width: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .ok-dot { background-color: #3FB950; box-shadow: 0 0 5px rgba(63,185,80,0.4); }
    .alert-dot { background-color: #F85149; box-shadow: 0 0 5px rgba(248,81,73,0.4); }
    
    /* DataFrame - Clean Table */
    div[data-testid="stDataFrame"] {
        border: 1px solid #30363D;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=REFRESH_RATE)
def load_data():
    data = []
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()
    
    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
                
    df = pd.DataFrame(data)
    
    # Ensure required columns exist
    required_cols = ['event_type', 'value', 'score', 'sender', 'vote', 'action', 'peer']
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
            
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# --- MISSION CONTROL (SIDEBAR) ---
st.sidebar.title("GRID CONTROL")
st.sidebar.markdown("---")

if st.sidebar.button("INITIALIZE GRID MONITORING (20 Nodes)"):
    job = {"command": "start", "agents": 20, "timestamp": time.time()}
    with open("/app/jobs/request.json", "w") as f:
        json.dump(job, f)
    st.sidebar.success("CMD SENT: START GRID MONITOR")

if st.sidebar.button("SIMULATE GRID FAILURE (STORM)"):
    job = {"command": "chaos", "agents": 20, "timestamp": time.time()}
    with open("/app/jobs/request.json", "w") as f:
        json.dump(job, f)
    st.sidebar.warning("CMD SENT: STORM SCENARIO")

if st.sidebar.button("EMERGENCY SHUTDOWN"):
    job = {"command": "stop", "timestamp": time.time()}
    with open("/app/jobs/request.json", "w") as f:
        json.dump(job, f)
    st.sidebar.error("CMD SENT: STOP GRID")

st.sidebar.markdown("---")
st.sidebar.info("Ensure 'job_runner.py' is running on the host!")

# Main Loop
placeholder = st.empty()

while True:
    df = load_data()
    
    with placeholder.container():
        st.subheader("SMART GRID TELEMETRY")
        
        if df.empty:
            st.warning("WAITING FOR TELEMETRY...")
            time.sleep(1)
            continue
            
        # --- TOP METRICS ---
        col1, col2, col3, col4 = st.columns(4)
        
        if not df.empty:
            last_ts = df['timestamp'].max()
            recent_threshold = last_ts - pd.Timedelta(seconds=15)
            active_agents = df[df['timestamp'] > recent_threshold]['agent_id'].nunique()
        else:
            active_agents = 0
            
        anomalies = df[df['event_type'] == 'detection'].shape[0]
        votes = df[df['event_type'] == 'voting_response'].shape[0]
        
        col1.metric("ACTIVE TRANSFORMERS", active_agents)
        col2.metric("VOLTAGE ANOMALIES", anomalies, delta_color="inverse")
        col3.metric("CONSENSUS VOTES", votes)
        col4.metric("GRID STATUS", "NOMINAL" if anomalies < 10 else "CRITICAL")
        
        st.markdown("---")
        
        # --- FLEET STATUS ---
        st.subheader("ACTIVE SECTOR TRANSFORMERS")
        
        # Get latest status per agent
        latest = df.sort_values('timestamp').groupby('agent_id').tail(1).copy()
        
        # Calculate trust scores from voting behavior
        trust_data = {}
        for agent_id in df['agent_id'].unique():
            if agent_id in ['system', 'coordinator']: continue
            agent_votes = df[(df['agent_id'] == agent_id) & (df['event_type'] == 'voting_response')]
            agrees = len(agent_votes[agent_votes['vote'] == 'AGREE'])
            # We no longer penalize DISAGREE votes visually, matching the backend localized fault logic
            total_votes = len(agent_votes)
            
            if total_votes > 0:
                trust_score = 0.5 + (agrees * 0.05) 
                trust_score = max(0.0, min(1.0, trust_score))
                trust_data[agent_id] = trust_score
            else:
                trust_data[agent_id] = 0.5
        
        # Build status table with trust scores
        status_data = []
        for _, row in latest.iterrows():
            agent = row['agent_id']
            if agent in ['system', 'coordinator']: continue
            
            msg = str(row['message'])
            is_dead = "KILLED" in msg
            is_alert = "ANOMALY" in msg or "DETECTED" in msg
            
            status = "DEAD" if is_dead else ("ALERT" if is_alert else "ACTIVE")
            last_msg = msg[:30] + "..." if len(msg) > 30 else msg
            
            trust = trust_data.get(agent, 0.5)
            
            status_data.append({
                "Agent": agent,
                "Status": status,
                "Trust": f"{trust:.2f}",
                "Last Log": last_msg
            })
        
        if status_data:
            st.dataframe(
                pd.DataFrame(status_data).set_index("Agent"),
                use_container_width=True,
                height=400
            )

        st.markdown("---")
        
        # --- AGENT TRUST SCORES ---
        st.subheader("NODE RELIABILITY SCORES")
        
        trust_chart_data = []
        for agent_id in df['agent_id'].unique():
            if agent_id in ['system', 'coordinator']: continue
            agent_votes = df[(df['agent_id'] == agent_id) & (df['event_type'] == 'voting_response')]
            agrees = len(agent_votes[agent_votes['vote'] == 'AGREE'])
            total_votes = len(agent_votes)
            
            if total_votes > 0:
                trust_score = 0.5 + (agrees * 0.05)
                trust_score = max(0.0, min(1.0, trust_score))
            else:
                trust_score = 0.5
                
            trust_chart_data.append({
                'Agent': agent_id,
                'Trust Score': trust_score,
                'Votes': total_votes
            })
        
        if trust_chart_data:
            trust_df = pd.DataFrame(trust_chart_data)
            
            chart = alt.Chart(trust_df).mark_bar().encode(
                x=alt.X('Agent:N', sort='-y'),
                y=alt.Y('Trust Score:Q', scale=alt.Scale(domain=[0, 1])),
                color=alt.Color('Trust Score:Q', 
                    scale=alt.Scale(
                        domain=[0, 0.4, 0.7, 1],
                        range=['#F85149', '#FFA657', '#3FB950', '#00FF88']
                    ),
                    legend=None
                ),
                tooltip=['Agent', 'Trust Score', 'Votes']
            ).properties(height=200)
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No trust data available yet. Trust scores build up as agents vote on anomalies.")
        
        st.markdown("---")
        
        # --- CHARTS ---
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("VOLTAGE ANOMALY SIGNALS (V)")
            detections = df[df['event_type'].isin(['detection', 'injection'])].copy()
            if not detections.empty:
                chart = alt.Chart(detections).mark_circle(size=80).encode(
                    x='timestamp',
                    y='value',
                    color=alt.Color('agent_id', scale=alt.Scale(scheme='spectral')),
                    tooltip=['agent_id', 'value', 'score']
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No anomalies detected yet. Waiting for ML detections or injections...")
                
        with c4:
            st.subheader("LIVE LOGS")
            st.dataframe(
                df[['timestamp', 'agent_id', 'message']].sort_values('timestamp', ascending=False).head(50),
                use_container_width=True,
                hide_index=True,
                height=300
            )

    time.sleep(REFRESH_RATE)
