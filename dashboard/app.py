import streamlit as st
import pandas as pd
import json
import time
import os
import altair as alt
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# Page Config
st.set_page_config(
    page_title="🛡️ MAS 'War Room'",
    page_icon="🛡️",
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

def build_graph(df):
    """Parses logs to build the current network topology."""
    G = nx.Graph()
    if df.empty:
        return G
        
    # Find neighbor definitions
    neighbor_logs = df[df['message'].str.contains("Neighbors set:", na=False)]
    
    for _, row in neighbor_logs.iterrows():
        agent = row['agent_id']
        try:
            # Parse list string: "Neighbors set: ['sensor2@prosody', 'sensor3@prosody']"
            msg = row['message']
            neighbors_str = msg.split("Neighbors set: ")[1].replace("'", "").replace("[","").replace("]","")
            neighbors = [n.strip().split('@')[0] for n in neighbors_str.split(",")]
            
            G.add_node(agent, title=agent, color="#00FFCC")
            for n in neighbors:
                G.add_node(n, title=n, color="#00FFCC")
                G.add_edge(agent, n, color="#444")
        except:
            pass
            
    # Check for severed connections
    sever_logs = df[df['action'] == 'sever']
    for _, row in sever_logs.iterrows():
        source = row['agent_id']
        try:
            target = row['peer'].split('@')[0]
            if G.has_edge(source, target):
                G.remove_edge(source, target)
        except:
            pass
            
    return G

# --- MISSION CONTROL (SIDEBAR) ---
st.sidebar.title("🚀 MISSION CONTROL")
st.sidebar.markdown("---")

if st.sidebar.button("🟢 INITIALIZE SYSTEM (20 AGENTS)"):
    job = {"command": "start", "agents": 20, "timestamp": time.time()}
    with open("/app/jobs/request.json", "w") as f:
        json.dump(job, f)
    st.sidebar.success("CMD SENT: START SIMULATION")

if st.sidebar.button("🔥 TRIGGER CHAOS MODE"):
    job = {"command": "chaos", "agents": 20, "timestamp": time.time()}
    with open("/app/jobs/request.json", "w") as f:
        json.dump(job, f)
    st.sidebar.warning("CMD SENT: UNLEASH CHAOS")

if st.sidebar.button("🛑 EMERGENCY STOP"):
    job = {"command": "stop", "timestamp": time.time()}
    with open("/app/jobs/request.json", "w") as f:
        json.dump(job, f)
    st.sidebar.error("CMD SENT: STOP SYSTEM")

st.sidebar.markdown("---")
st.sidebar.info("Ensure 'job_runner.py' is running on the host!")

# Main Loop
placeholder = st.empty()

while True:
    df = load_data()
    
    with placeholder.container():
        st.subheader("SYSTEM TELEMETRY")
        
        if df.empty:
            st.warning("⚠️ WAITING FOR TELEMETRY...")
            time.sleep(1)
            continue
            
        # --- TOP METRICS ---
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate Active Agents (Seen in last 15 seconds)
        # Handle timezone naive/aware if needed, but assuming simple comparison works or use max timestamp from df as reference
        if not df.empty:
            last_ts = df['timestamp'].max()
            recent_threshold = last_ts - pd.Timedelta(seconds=15)
            active_agents = df[df['timestamp'] > recent_threshold]['agent_id'].nunique()
        else:
            active_agents = 0
            
        anomalies = df[df['event_type'] == 'detection'].shape[0]
        votes = df[df['event_type'] == 'voting_response'].shape[0]
        
        col1.metric("ONLINE AGENTS", active_agents)
        col2.metric("ANOMALIES", anomalies, delta_color="inverse")
        col3.metric("VOTES CAST", votes)
        col4.metric("SYSTEM STATUS", "OPERATIONAL" if anomalies < 10 else "ALERT")
        
        st.markdown("---")
        
        # --- ROW 2: GRAPH & HEATMAP ---
        c1, c2 = st.columns([3, 2])
        
        with c1:
            st.subheader("🌐 LIVE TOPOLOGY")
            G = build_graph(df)
            if not nx.is_empty(G):
                net = Network(height="500px", width="100%", bgcolor="#161B22", font_color="white")
                net.from_nx(G)
                # Physics options for stability
                net.set_options("""
                var options = {
                  "physics": {
                    "hierarchicalRepulsion": { "nodeDistance": 150 },
                     "stabilization": { "iterations": 100 }
                  }
                }
                """)
                net.save_graph("graph.html")
                with open("graph.html", 'r', encoding='utf-8') as f:
                    source_code = f.read()
                components.html(source_code, height=500)
            else:
                st.info("Waiting for topology data...")

        with c2:
            st.subheader("🤖 FLEET STATUS")
            # Get latest status
            latest = df.sort_values('timestamp').groupby('agent_id').tail(1).copy()
            
            # Prepare data for clean table
            status_data = []
            for _, row in latest.iterrows():
                agent = row['agent_id']
                if agent in ['system', 'coordinator']: continue
                
                msg = str(row['message'])
                is_dead = "KILLED" in msg
                is_alert = "ANOMALY" in msg or "DETECTED" in msg
                
                status = "🔴 DEAD" if is_dead else ("🟠 ALERT" if is_alert else "🟢 ACTIVE")
                last_msg = msg[:40] + "..." if len(msg) > 40 else msg
                
                status_data.append({
                    "Agent": agent,
                    "Status": status,
                    "Last Log": last_msg
                })
            
            if status_data:
                st.dataframe(
                    pd.DataFrame(status_data).set_index("Agent"),
                    use_container_width=True,
                    height=500
                )

        st.markdown("---")
        
        # --- ROW 3: CHARTS ---
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("📈 ANOMALY SIGNALS")
            detections = df[df['event_type'].isin(['detection', 'injection'])].copy()
            if not detections.empty:
                chart = alt.Chart(detections).mark_circle(size=80).encode(
                    x='timestamp',
                    y='value',
                    color=alt.Color('agent_id', scale=alt.Scale(scheme='spectral')),
                    tooltip=['agent_id', 'value', 'score']
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
                
        with c4:
            st.subheader("📜 LIVE LOGS")
            st.dataframe(
                df[['timestamp', 'agent_id', 'message']].sort_values('timestamp', ascending=False).head(50),
                use_container_width=True,
                hide_index=True,
                height=300
            )

    time.sleep(REFRESH_RATE)
