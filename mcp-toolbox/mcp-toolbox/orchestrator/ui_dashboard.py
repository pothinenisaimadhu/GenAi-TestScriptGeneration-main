"""
Dashboard component for the Multi-Agent RAG Test Case Generator UI
Provides analytics, monitoring, and system health information
"""
import streamlit as st
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

def display_system_health():
    """Display system health dashboard"""
    st.markdown("### 🏥 System Health")
    
    # Check system components
    health_data = check_system_components()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "🟢" if health_data['database'] else "🔴"
        st.metric("Database", status)
    
    with col2:
        status = "🟢" if health_data['vector_store'] else "🔴"
        st.metric("Vector Store", status)
    
    with col3:
        status = "🟢" if health_data['llm_service'] else "🔴"
        st.metric("LLM Service", status)
    
    with col4:
        status = "🟢" if health_data['jira_integration'] else "🔴"
        st.metric("Jira Integration", status)
    
    # Overall health score
    health_score = sum(health_data.values()) / len(health_data) * 100
    st.progress(health_score / 100)
    st.write(f"Overall Health: {health_score:.1f}%")

def check_system_components() -> Dict[str, bool]:
    """Check the health of system components"""
    health = {
        'database': bool(os.getenv('GOOGLE_PROJECT_ID') and os.getenv('BIGQUERY_DATASET')),
        'vector_store': bool(os.getenv('CHROMA_API_KEY') or os.path.exists('chroma')),
        'llm_service': True,  # Assume local LLM is available
        'jira_integration': bool(os.getenv('JIRA_API_URL') and os.getenv('JIRA_TOKEN'))
    }
    return health

def display_performance_metrics():
    """Display performance metrics and analytics"""
    st.markdown("### 📊 Performance Analytics")
    
    # Load historical data
    metrics_data = load_performance_data()
    
    if not metrics_data:
        st.info("No performance data available yet. Run some test case generations to see metrics.")
        return
    
    # Create tabs for different metrics
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🎯 Quality", "⚡ Performance"])
    
    with tab1:
        display_trend_charts(metrics_data)
    
    with tab2:
        display_quality_metrics(metrics_data)
    
    with tab3:
        display_performance_charts(metrics_data)

def load_performance_data() -> List[Dict[str, Any]]:
    """Load real performance data from various sources"""
    data = []
    
    # Load from traceability logs
    traceability_dir = Path("traceability_logs")
    if traceability_dir.exists():
        for log_file in traceability_dir.glob("*.json"):
            try:
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
                    data.append({
                        'timestamp': log_data.get('timestamp', time.time()),
                        'test_case_id': log_data.get('test_case_id', ''),
                        'quality_score': log_data.get('quality_score', 0.8),
                        'processing_time': log_data.get('processing_time', 0),
                        'source': 'traceability'
                    })
            except Exception as e:
                continue
    
    # Load from performance logs
    performance_dir = Path("performance_logs")
    if performance_dir.exists():
        for perf_file in performance_dir.glob("*.json"):
            try:
                with open(perf_file, 'r') as f:
                    perf_data = json.load(f)
                    data.append({
                        'timestamp': perf_data.get('timestamp', time.time()),
                        'test_case_id': perf_data.get('test_case_id', ''),
                        'quality_score': perf_data.get('quality_score', 0.8),
                        'processing_time': perf_data.get('processing_time', 0),
                        'source': 'performance'
                    })
            except Exception as e:
                continue
    
    # Load from feedback data
    feedback_dir = Path("user_feedback")
    if feedback_dir.exists():
        for feedback_file in feedback_dir.glob("*.json"):
            try:
                with open(feedback_file, 'r') as f:
                    feedback_data = json.load(f)
                    responses = feedback_data.get('feedback_responses', {})
                    data.append({
                        'timestamp': feedback_data.get('timestamp', time.time()),
                        'quality_rating': responses.get('quality_rating', responses.get('overall_rating', 3)),
                        'completeness': responses.get('completeness', 3),
                        'clarity': responses.get('clarity', 3),
                        'time_efficiency': responses.get('time_efficiency', 3),
                        'source': 'feedback'
                    })
            except Exception as e:
                continue
    
    return data

def display_trend_charts(data: List[Dict[str, Any]]):
    """Display trend charts with real data only"""
    if not data:
        st.info("No trend data available yet. Generate some test cases to see trends.")
        return
    
    # Process data for trends
    daily_stats = {}
    for item in data:
        timestamp = item.get('timestamp', time.time())
        if isinstance(timestamp, str):
            try:
                timestamp = float(timestamp)
            except:
                timestamp = time.time()
        
        date = datetime.fromtimestamp(timestamp).date()
        if date not in daily_stats:
            daily_stats[date] = {'count': 0, 'quality_sum': 0}
        
        daily_stats[date]['count'] += 1
        quality = item.get('quality_score', item.get('quality_rating', 3))
        daily_stats[date]['quality_sum'] += quality
    
    # Create trend chart
    dates = list(daily_stats.keys())
    counts = [stats['count'] for stats in daily_stats.values()]
    avg_quality = [stats['quality_sum'] / stats['count'] for stats in daily_stats.values()]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=counts, mode='lines+markers', name='Test Cases Generated', line=dict(color='#1f77b4')))
    fig.add_trace(go.Scatter(x=dates, y=avg_quality, mode='lines+markers', name='Average Quality', yaxis='y2', line=dict(color='#ff7f0e')))
    
    fig.update_layout(
        title='Test Case Generation Trends',
        xaxis_title='Date',
        yaxis_title='Test Cases Count',
        yaxis2=dict(title='Quality Score (1-5)', overlaying='y', side='right', range=[0, 5]),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def generate_sample_trend_data() -> List[Dict[str, Any]]:
    """Generate sample trend data for demonstration"""
    import random
    
    sample_data = []
    base_time = time.time() - (7 * 24 * 3600)  # 7 days ago
    
    for i in range(7):
        day_timestamp = base_time + (i * 24 * 3600)
        daily_count = random.randint(2, 8)
        
        for j in range(daily_count):
            sample_data.append({
                'timestamp': day_timestamp + (j * 3600),
                'quality_score': random.uniform(3.5, 4.8),
                'quality_rating': random.randint(3, 5),
                'processing_time': random.uniform(5, 25),
                'source': 'sample'
            })
    
    return sample_data

def display_quality_metrics(data: List[Dict[str, Any]]):
    """Display quality metrics"""
    feedback_data = [item for item in data if item.get('source') == 'feedback']
    
    if not feedback_data:
        st.info("No quality feedback data available")
        return
    
    # Quality distribution
    quality_ratings = [item.get('quality_rating', 3) for item in feedback_data]
    completeness_ratings = [item.get('completeness', 3) for item in feedback_data]
    clarity_ratings = [item.get('clarity', 3) for item in feedback_data]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality distribution pie chart
        quality_counts = {i: quality_ratings.count(i) for i in range(1, 6)}
        fig = px.pie(
            values=list(quality_counts.values()),
            names=[f"{i} Stars" for i in quality_counts.keys()],
            title="Quality Rating Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average scores
        avg_quality = sum(quality_ratings) / len(quality_ratings) if quality_ratings else 0
        avg_completeness = sum(completeness_ratings) / len(completeness_ratings) if completeness_ratings else 0
        avg_clarity = sum(clarity_ratings) / len(clarity_ratings) if clarity_ratings else 0
        
        st.metric("Average Quality", f"{avg_quality:.2f}/5")
        st.metric("Average Completeness", f"{avg_completeness:.2f}/5")
        st.metric("Average Clarity", f"{avg_clarity:.2f}/5")

def display_performance_charts(data: List[Dict[str, Any]]):
    """Display performance charts"""
    perf_data = [item for item in data if item.get('processing_time', 0) > 0]
    
    if not perf_data:
        st.info("No performance data available")
        return
    
    processing_times = [item['processing_time'] for item in perf_data]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Processing time histogram
        fig = px.histogram(
            x=processing_times,
            title="Processing Time Distribution",
            labels={'x': 'Processing Time (seconds)', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance metrics
        avg_time = sum(processing_times) / len(processing_times)
        min_time = min(processing_times)
        max_time = max(processing_times)
        
        st.metric("Average Processing Time", f"{avg_time:.2f}s")
        st.metric("Fastest Processing", f"{min_time:.2f}s")
        st.metric("Slowest Processing", f"{max_time:.2f}s")

def display_recent_activity():
    """Display recent system activity"""
    st.markdown("### 📋 Recent Activity")
    
    activities = get_recent_activities()
    
    if not activities:
        st.info("No recent activity")
        return
    
    for activity in activities[:10]:  # Show last 10 activities
        timestamp = datetime.fromtimestamp(activity['timestamp'])
        
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.write(timestamp.strftime("%Y-%m-%d %H:%M"))
            
            with col2:
                st.write(activity['description'])
            
            with col3:
                status_icon = "✅" if activity['status'] == 'success' else "❌"
                st.write(status_icon)

def get_recent_activities() -> List[Dict[str, Any]]:
    """Get recent system activities"""
    activities = []
    
    # Check traceability logs
    traceability_dir = Path("traceability_logs")
    if traceability_dir.exists():
        for log_file in traceability_dir.glob("*.json"):
            try:
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
                    activities.append({
                        'timestamp': log_data.get('timestamp', os.path.getmtime(log_file)),
                        'description': f"Generated test case {log_data.get('test_case_id', 'Unknown')}",
                        'status': 'success'
                    })
            except Exception:
                continue
    
    # Check feedback files
    feedback_dir = Path("user_feedback")
    if feedback_dir.exists():
        for feedback_file in feedback_dir.glob("*.json"):
            try:
                activities.append({
                    'timestamp': os.path.getmtime(feedback_file),
                    'description': f"Received user feedback",
                    'status': 'success'
                })
            except Exception:
                continue
    
    # Sort by timestamp (newest first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return activities

def display_configuration_status():
    """Display current configuration status"""
    st.markdown("### ⚙️ Configuration Status")
    
    config_items = [
        ("Google Cloud Project", os.getenv('GOOGLE_PROJECT_ID')),
        ("GCS Bucket", os.getenv('GCS_BUCKET')),
        ("BigQuery Dataset", os.getenv('BIGQUERY_DATASET')),
        ("ChromaDB API Key", "***" if os.getenv('CHROMA_API_KEY') else None),
        ("ChromaDB Tenant", os.getenv('CHROMA_TENANT')),
        ("ChromaDB Database", os.getenv('CHROMA_DATABASE')),
        ("Jira URL", os.getenv('JIRA_API_URL')),
        ("Jira User", os.getenv('JIRA_USER')),
        ("Jira Project", os.getenv('JIRA_PROJECT_KEY'))
    ]
    
    for name, value in config_items:
        status = "✅" if value else "❌"
        display_value = value if value else "Not configured"
        if name == "ChromaDB API Key" and value:
            display_value = "***configured***"
        
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            st.write(name)
        with col2:
            st.write(display_value)
        with col3:
            st.write(status)

def display_storage_usage():
    """Display storage usage information"""
    st.markdown("### 💾 Storage Usage")
    
    directories = {
        "Generated Test Cases": "generated_testcases",
        "User Feedback": "user_feedback", 
        "Traceability Logs": "traceability_logs",
        "Temporary Files": "temp"
    }
    
    for name, directory in directories.items():
        path = Path(directory)
        if path.exists():
            file_count = len(list(path.glob("*")))
            total_size = sum(f.stat().st_size for f in path.glob("*") if f.is_file())
            size_mb = total_size / (1024 * 1024)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(name)
            with col2:
                st.write(f"{file_count} files")
            with col3:
                st.write(f"{size_mb:.2f} MB")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(name)
            with col2:
                st.write("0 files")
            with col3:
                st.write("0 MB")

def main_dashboard():
    """Main dashboard function"""
    st.markdown("# 📊 System Dashboard")
    
    # Create tabs for different dashboard sections
    tab1, tab2, tab3, tab4 = st.tabs(["🏥 Health", "📊 Analytics", "📋 Activity", "⚙️ Config"])
    
    with tab1:
        display_system_health()
        st.markdown("---")
        display_storage_usage()
    
    with tab2:
        display_performance_metrics()
    
    with tab3:
        display_recent_activity()
    
    with tab4:
        display_configuration_status()

if __name__ == "__main__":
    main_dashboard()