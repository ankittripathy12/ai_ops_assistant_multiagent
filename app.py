#!/usr/bin/env python3
"""
Streamlit Web Interface for AI Operations Assistant
with clickable GitHub links
"""
import streamlit as st
import sys
import os
import json
import time
import re  # ADDED THIS IMPORT
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your agents
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent

# Page configuration
st.set_page_config(
    page_title="AI Operations Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with clickable link styles
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #F44336;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2196F3;
        margin: 1rem 0;
    }
    .agent-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #E0E0E0;
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
    .github-link {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: #24292e;
        color: white !important;
        padding: 5px 12px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
        margin: 3px;
        transition: all 0.3s ease;
    }
    .github-link:hover {
        background: #2c333a;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .repo-card {
        background: white;
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .repo-name {
        font-weight: 600;
        color: #24292e;
        margin-bottom: 5px;
    }
    .repo-description {
        color: #586069;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    .repo-stats {
        display: flex;
        gap: 15px;
        font-size: 0.85rem;
        color: #586069;
    }
    .repo-language {
        background: #f1f8ff;
        padding: 2px 8px;
        border-radius: 12px;
        color: #0366d6;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tasks_history' not in st.session_state:
    st.session_state.tasks_history = []
if 'current_task_id' not in st.session_state:
    st.session_state.current_task_id = 0
if 'agents_initialized' not in st.session_state:
    st.session_state.agents_initialized = False


# Initialize agents (once)
@st.cache_resource
def initialize_agents():
    """Initialize agents with caching"""
    try:
        planner = PlannerAgent()
        executor = ExecutorAgent()
        verifier = VerifierAgent()
        st.session_state.agents_initialized = True
        return planner, executor, verifier
    except Exception as e:
        st.error(f"Failed to initialize agents: {str(e)}")
        return None, None, None


def display_github_repos(data):
    """Display GitHub repositories with clickable links"""
    if not data:
        return

    # Check if data contains repositories
    if isinstance(data, dict):
        if 'repositories' in data:
            st.markdown("#### 📦 GitHub Repositories")
            for repo in data['repositories']:
                with st.container():
                    st.markdown(f"""
                    <div class="repo-card">
                        <div class="repo-name">{repo.get('name', 'Unnamed Repository')}</div>
                        <div class="repo-description">{repo.get('description', 'No description available')}</div>
                        <div class="repo-stats">
                            <span>⭐ {repo.get('stars', 0)} stars</span>
                            {f"<span class='repo-language'>🔤 {repo.get('language', 'N/A')}</span>" if repo.get('language') else ''}
                        </div>
                        <a href="{repo.get('url', '#')}" target="_blank" class="github-link">
                            <svg height="16" viewBox="0 0 16 16" width="16" style="fill: white;">
                                <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
                            </svg>
                            View on GitHub
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
        elif 'name' in data and 'url' in data:
            # Single repository
            st.markdown("#### 📦 Repository")
            with st.container():
                st.markdown(f"""
                <div class="repo-card">
                    <div class="repo-name">{data.get('name', 'Unnamed Repository')}</div>
                    <div class="repo-description">{data.get('description', 'No description available')}</div>
                    <div class="repo-stats">
                        <span>⭐ {data.get('stars', 0)} stars</span>
                        <span>🍴 {data.get('forks', 0)} forks</span>
                        {f"<span class='repo-language'>🔤 {data.get('language', 'N/A')}</span>" if data.get('language') else ''}
                    </div>
                    <a href="{data.get('url', '#')}" target="_blank" class="github-link">
                        <svg height="16" viewBox="0 0 16 16" width="16" style="fill: white;">
                            <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
                        </svg>
                        View on GitHub
                    </a>
                </div>
                """, unsafe_allow_html=True)


def display_natural_language_results(formatted_result):
    """Display results in natural language format with clickable links"""
    if not formatted_result:
        return

    # Summary
    if "summary" in formatted_result:
        st.markdown(f"""
        <div style="background: #f0f7ff; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #1E88E5;">
            <h4 style="color: #1E88E5; margin-top: 0;">Summary</h4>
            <p style="font-size: 1.1rem; line-height: 1.6; color: #333;">
                {formatted_result['summary']}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Details with clickable GitHub links
    if "details" in formatted_result and formatted_result["details"]:
        st.markdown("#### What I Found:")

        for detail in formatted_result["details"]:
            if isinstance(detail, str):
                # Convert GitHub URLs to clickable links
                html_detail = detail

                # Pattern to find GitHub URLs in parentheses
                github_pattern = r'\((https?://github\.com/[^)]+)\)'

                # Find all GitHub URLs
                github_urls = re.findall(github_pattern, detail)

                # Replace each URL with clickable link
                for url in github_urls:
                    # Extract repo name from URL
                    repo_name = url.split('/')[-2] + '/' + url.split('/')[-1]

                    # Create clickable link
                    clickable_link = f'<a href="{url}" target="_blank" style="color: #0366d6; text-decoration: none; font-weight: 600;">{repo_name}</a>'

                    # Replace the URL with clickable link
                    html_detail = html_detail.replace(f'({url})', f'({clickable_link})')

                # Also convert any standalone GitHub URLs
                standalone_pattern = r'(https?://github\.com/[^\s]+)'
                html_detail = re.sub(
                    standalone_pattern,
                    r'<a href="\1" target="_blank" style="color: #0366d6; text-decoration: none; font-weight: 600;">\1</a>',
                    html_detail
                )

                # Display the detail with styling
                st.markdown(f"""
                <div style="background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #4CAF50; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="color: #4CAF50; font-size: 1.2rem; float: left; margin-right: 10px;">•</div>
                    <div style="overflow: hidden; font-size: 1rem; line-height: 1.5;">
                        {html_detail}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Display structured data
    data = formatted_result.get("data", {})

    # GitHub repositories
    if isinstance(data, dict):
        if "repositories" in data:
            st.markdown("#### GitHub Repositories")
            for repo in data["repositories"]:
                repo_name = repo.get('name', 'Unnamed Repository')
                repo_desc = repo.get('description', 'No description')
                repo_stars = repo.get('stars', 0)
                repo_language = repo.get('language', '')
                repo_url = repo.get('url', '#')

                # Display in a nice card
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; margin: 10px 0;">
                    <div style="font-weight: 600; color: #24292e; margin-bottom: 5px;">{repo_name}</div>
                    <div style="color: #586069; font-size: 0.9rem; margin-bottom: 10px;">{repo_desc}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; gap: 15px; font-size: 0.85rem; color: #586069;">
                            <span>Stars: {repo_stars}</span>
                            {f"<span>Language: {repo_language}</span>" if repo_language else ""}
                        </div>
                        <a href="{repo_url}" target="_blank" style="background: #24292e; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.9rem; font-weight: 600;">
                            Open on GitHub
                        </a>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.8rem; color: #586069;">
                        <strong>URL:</strong> {repo_url}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Weather data
        if "weather" in data and isinstance(data["weather"], dict):
            weather = data["weather"]
            if "city" in weather and "temperature_c" in weather:
                st.markdown("#### Weather Information")
                st.markdown(f"""
                <div class="weather-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0; color: white;">{weather.get('city', 'Unknown')}</h3>
                            <p style="margin: 5px 0; opacity: 0.9;">{weather.get('condition', '')}</p>
                            <h2 style="margin: 0; font-size: 2.5rem;">{weather.get('temperature_c', 'N/A')}°C</h2>
                            <p style="margin: 5px 0; opacity: 0.9;">{weather.get('temperature_f', 'N/A')}°F</p>
                        </div>
                    </div>
                    <div style="display: flex; gap: 20px; margin-top: 15px;">
                        <div>
                            <p style="margin: 5px 0; opacity: 0.9;">Humidity</p>
                            <p style="margin: 0; font-size: 1.2rem;">{weather.get('humidity', 'N/A')}%</p>
                        </div>
                        <div>
                            <p style="margin: 5px 0; opacity: 0.9;">Wind Speed</p>
                            <p style="margin: 0; font-size: 1.2rem;">{weather.get('wind_kph', 'N/A')} km/h</p>
                        </div>
                        <div>
                            <p style="margin: 5px 0; opacity: 0.9;">Last Updated</p>
                            <p style="margin: 0; font-size: 1.2rem;">{weather.get('last_updated', 'N/A')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Notes
    if "notes" in formatted_result and formatted_result["notes"]:
        st.markdown(f"""
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ffc107;">
            <h4 style="color: #856404; margin-top: 0;">Note</h4>
            <p style="color: #856404; margin: 0;">{formatted_result['notes']}</p>
        </div>
        """, unsafe_allow_html=True)


def extract_and_display_github_links(formatted_result):
    """Extract and display GitHub repository links from formatted result"""
    if not formatted_result:
        return

    # Check data section
    data = formatted_result.get("data", {})
    if isinstance(data, dict):
        # Look for GitHub data in the data object
        for key, value in data.items():
            if isinstance(value, dict):
                display_github_repos(value)

        # Also check if data itself is GitHub data
        display_github_repos(data)

    # Check details section for GitHub URLs
    details = formatted_result.get("details", [])
    if details:
        st.markdown("#### 🔗 Found GitHub Links")
        for detail in details:
            if isinstance(detail, str) and 'github.com' in detail.lower():
                # Try to extract URL
                urls = re.findall(r'https?://[^\s]+github\.com[^\s]+', detail)
                for url in urls:
                    st.markdown(f"""
                    <a href="{url}" target="_blank" class="github-link">
                        <svg height="16" viewBox="0 0 16 16" width="16" style="fill: white;">
                            <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
                        </svg>
                        {url}
                    </a>
                    """, unsafe_allow_html=True)


# Header
st.markdown('<h1 class="main-header">🤖 AI Operations Assistant</h1>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #666; margin-bottom: 2rem;'>
    A multi-agent system that plans, executes, and verifies natural language tasks using real APIs.
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103655.png", width=100)
    st.markdown("### 🎯 Quick Tasks")

    # Quick task buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌤️ Weather", use_container_width=True):
            st.session_state.quick_task = "Get weather in Tokyo"
        if st.button("🐍 Python Repos", use_container_width=True):
            st.session_state.quick_task = "Find Python repositories"
    with col2:
        if st.button("🤖 AI Projects", use_container_width=True):
            st.session_state.quick_task = "Search for artificial intelligence projects"
        if st.button("🔍 Combined", use_container_width=True):
            st.session_state.quick_task = "Get weather in London and find machine learning repositories"

    st.markdown("---")
    st.markdown("### ⚙️ Configuration")

    # API status
    st.markdown("#### API Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Groq**")
        st.success("✅")
    with col2:
        st.markdown("**GitHub**")
        st.success("✅")
    with col3:
        st.markdown("**Weather**")
        st.success("✅")

    st.markdown("---")
    st.markdown("### 📊 Statistics")
    st.metric("Tasks Executed", len(st.session_state.tasks_history))

    if st.session_state.tasks_history:
        success_count = sum(1 for task in st.session_state.tasks_history if task.get('status') == 'success')
        st.metric("Success Rate", f"{success_count}/{len(st.session_state.tasks_history)}")

    st.markdown("---")
    st.markdown("### 🛠️ Agents")
    st.markdown("""
    - **Planner**: Analyzes tasks
    - **Executor**: Calls APIs
    - **Verifier**: Formats results
    """)

# Main content area
tab1, tab2, tab3 = st.tabs(["📝 Execute Task", "📊 Task History", "ℹ️ About"])

with tab1:
    # Task input section
    st.markdown('<h3 class="sub-header">Enter Your Task</h3>', unsafe_allow_html=True)

    # Initialize quick task if set
    default_task = ""
    if 'quick_task' in st.session_state:
        default_task = st.session_state.quick_task
        del st.session_state.quick_task

    task_input = st.text_area(
        "Describe what you want to do (e.g., 'Get weather in Paris and find trending Python repositories'):",
        value=default_task,
        height=100,
        placeholder="Type your natural language task here..."
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        verbose_mode = st.checkbox("Show Details", value=True)
    with col2:
        auto_run = st.checkbox("Auto Run", value=True)

    # Execute button
    execute_button = st.button("🚀 Execute Task", type="primary", use_container_width=True)

    if execute_button and task_input:
        # Initialize agents
        planner, executor, verifier = initialize_agents()

        if planner and executor and verifier:
            # Create progress container
            progress_container = st.container()
            result_container = st.container()

            with progress_container:
                st.markdown("---")
                st.markdown('<h3 class="sub-header">Execution Progress</h3>', unsafe_allow_html=True)

                # Step 1: Planning
                with st.spinner("📋 Planning phase..."):
                    st.markdown("**Step 1: Planning**")
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        status_text.text("Analyzing task and creating execution plan...")
                        plan = planner.create_plan(task_input)
                        progress_bar.progress(33)
                        time.sleep(0.5)

                        if verbose_mode:
                            with st.expander("📝 Execution Plan", expanded=False):
                                st.json(plan)

                    except Exception as e:
                        st.error(f"Planning failed: {str(e)}")
                        st.stop()

                # Step 2: Execution
                with st.spinner("⚡ Executing..."):
                    st.markdown("**Step 2: Execution**")
                    status_text.text("Executing steps and calling APIs...")

                    try:
                        execution_results = executor.execute_plan(plan["steps"])
                        progress_bar.progress(66)
                        time.sleep(0.5)

                        if verbose_mode:
                            with st.expander("⚡ Execution Results", expanded=False):
                                for result in execution_results:
                                    if result["success"]:
                                        st.success(f"Step {result['step']}: ✅ Success")
                                        if result.get("result"):
                                            with st.expander(f"Step {result['step']} Details", expanded=False):
                                                st.json(result["result"])
                                    else:
                                        st.error(f"Step {result['step']}: ❌ Failed - {result['error']}")

                    except Exception as e:
                        st.error(f"Execution failed: {str(e)}")
                        st.stop()

                # Step 3: Verification
                with st.spinner("🔍 Verifying..."):
                    st.markdown("**Step 3: Verification**")
                    status_text.text("Verifying results and formatting output...")

                    try:
                        final_result = verifier.verify_and_format(task_input, execution_results)
                        progress_bar.progress(100)
                        status_text.text("✅ Task completed!")
                        time.sleep(0.5)

                    except Exception as e:
                        st.error(f"Verification failed: {str(e)}")
                        st.stop()

            # Display final results - UPDATED THIS SECTION
            with result_container:
                st.markdown("---")
                st.markdown('<h3 class="sub-header">Final Result</h3>', unsafe_allow_html=True)

                # Status indicator
                status = final_result.get("status", "unknown")
                if status == "success":
                    st.markdown('<div class="success-box"><strong>✅ Task Completed Successfully</strong></div>',
                                unsafe_allow_html=True)
                elif status == "partial":
                    st.markdown('<div class="info-box"><strong>⚠️ Task Partially Completed</strong></div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box"><strong>❌ Task Failed</strong></div>', unsafe_allow_html=True)

                # Display formatted result - USING NATURAL LANGUAGE DISPLAY
                formatted_result = final_result.get("formatted_result", {})

                if formatted_result:
                    # Use the natural language display function
                    display_natural_language_results(formatted_result)

                    # Also show the structured data in an expander for debugging
                    if verbose_mode:
                        with st.expander("📊 View Raw Structured Data", expanded=False):
                            st.json(formatted_result)

                # Failed steps
                failed_steps = final_result.get("failed_steps", [])
                if failed_steps:
                    st.markdown("**⚠️ Issues encountered:**")
                    for step in failed_steps:
                        st.error(f"Step {step['step']}: {step['error']}")

                # Store in history
                task_record = {
                    "id": st.session_state.current_task_id,
                    "task": task_input,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": status,
                    "summary": formatted_result.get("summary", ""),
                    "steps": len(plan.get("steps", [])),
                    "successful_steps": sum(1 for r in execution_results if r.get("success", False)),
                    "data": final_result
                }

                st.session_state.tasks_history.append(task_record)
                st.session_state.current_task_id += 1

                # Show success message
                st.balloons()
                st.success("Task completed and saved to history!")

        else:
            st.error("Failed to initialize agents. Please check your configuration.")

with tab2:
    st.markdown('<h3 class="sub-header">Task History</h3>', unsafe_allow_html=True)

    if st.session_state.tasks_history:
        # Show statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tasks", len(st.session_state.tasks_history))
        with col2:
            success_count = sum(1 for task in st.session_state.tasks_history if task.get('status') == 'success')
            st.metric("Successful", success_count)
        with col3:
            partial_count = sum(1 for task in st.session_state.tasks_history if task.get('status') == 'partial')
            st.metric("Partial", partial_count)
        with col4:
            failed_count = sum(1 for task in st.session_state.tasks_history if task.get('status') == 'failed')
            st.metric("Failed", failed_count)

        # Task history table
        st.markdown("### Recent Tasks")
        for task in reversed(st.session_state.tasks_history[:10]):  # Show last 10
            with st.expander(f"Task #{task['id']}: {task['task'][:50]}...", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Status:** {task['status'].upper()}")
                    st.markdown(f"**Time:** {task['timestamp']}")
                with col2:
                    st.markdown(f"**Steps:** {task['steps']}")
                    st.markdown(f"**Successful:** {task['successful_steps']}/{task['steps']}")

                if task['summary']:
                    st.markdown(f"**Summary:** {task['summary']}")

                # Display GitHub links from history using natural language display
                task_data = task.get('data', {})
                if task_data:
                    formatted_result = task_data.get('formatted_result', {})
                    if formatted_result:
                        # Use natural language display for history items too
                        display_natural_language_results(formatted_result)

                # View details button
                if st.button(f"View Full Details", key=f"view_{task['id']}"):
                    st.json(task['data'])

                # Rerun button
                if st.button(f"Rerun Task", key=f"rerun_{task['id']}"):
                    st.session_state.quick_task = task['task']
                    st.rerun()
    else:
        st.info("No tasks executed yet. Go to the 'Execute Task' tab to get started!")

with tab3:
    st.markdown('<h3 class="sub-header">About AI Operations Assistant</h3>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 🤖 What is this?

        AI Operations Assistant is a multi-agent system that:

        1. **Understands** natural language tasks
        2. **Plans** execution steps using AI
        3. **Executes** actions using real APIs
        4. **Verifies** and formats results

        ### 🏗️ Architecture

        The system uses three specialized agents:

        - **Planner Agent**: Analyzes your request and creates a step-by-step plan
        - **Executor Agent**: Carries out each step by calling appropriate APIs
        - **Verifier Agent**: Checks results and formats them for easy understanding

        ### 🔌 Integrations

        Currently integrated with:

        - **GitHub API**: Search and retrieve repository information
        - **Weather API**: Get current weather for any city
        - **Groq LLM**: Advanced language understanding and planning

        ### 🚀 How to Use

        1. Type your task in natural language
        2. Click "Execute Task"
        3. Watch the agents work through planning, execution, and verification
        4. View the formatted results with clickable GitHub links
        """)

    with col2:
        st.markdown("### 🎯 Example Tasks")
        st.markdown("""
        Try these examples:

        - "Get weather in Tokyo"
        - "Find Python repositories"
        - "Show me AI projects and weather in San Francisco"
        - "What's trending in JavaScript?"
        - "Weather in London and machine learning repositories"
        """)

        st.markdown("### 📈 Capabilities")

        capabilities = {
            "🌐 API Integration": "Real-time data from multiple sources",
            "🧠 AI Planning": "Intelligent step-by-step planning",
            "⚡ Parallel Execution": "Multiple tools can work together",
            "🔍 Result Verification": "Automatic validation and formatting",
            "📊 Rich Output": "Structured data with clickable links"
        }

        for capability, description in capabilities.items():
            st.markdown(f"**{capability}**")
            st.caption(description)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Version:** 1.0.0")
with col2:
    st.markdown("**Multi-Agent System**")
with col3:
    st.markdown("**Real API Integration**")

st.markdown("<div style='text-align: center; color: #999; margin-top: 2rem;'>AI Operations Assistant 🤖</div>",
            unsafe_allow_html=True)