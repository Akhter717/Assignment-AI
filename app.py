import streamlit as st
import requests
import subprocess
import os
import json
import time
import base64
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Selenium AI Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Hero banner */
  .hero-banner {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(99,102,241,0.3);
    position: relative;
    overflow: hidden;
  }
  .hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 40%, rgba(99,102,241,0.15) 0%, transparent 60%),
                radial-gradient(circle at 70% 60%, rgba(168,85,247,0.1) 0%, transparent 60%);
    pointer-events: none;
  }
  .hero-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #e0e7ff;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .hero-title span { color: #818cf8; }
  .hero-sub {
    color: #94a3b8;
    font-size: 0.9rem;
    margin-top: 0.4rem;
    font-weight: 300;
  }

  /* Pipeline steps */
  .pipeline {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin: 1rem 0;
    flex-wrap: wrap;
  }
  .pipe-step {
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 8px;
    padding: 0.35rem 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #a5b4fc;
    white-space: nowrap;
  }
  .pipe-arrow { color: #6366f1; font-size: 1rem; }

  /* Section cards */
  .section-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
  }
  .section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #6366f1;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
  }

  /* Status badges */
  .badge-success {
    background: rgba(16,185,129,0.15);
    border: 1px solid rgba(16,185,129,0.4);
    color: #34d399;
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
  }
  .badge-fail {
    background: rgba(239,68,68,0.15);
    border: 1px solid rgba(239,68,68,0.4);
    color: #f87171;
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
  }
  .badge-running {
    background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.4);
    color: #fbbf24;
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
  }

  /* Code block */
  .code-block {
    background: #020617;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #e2e8f0;
    overflow-x: auto;
    max-height: 420px;
    overflow-y: auto;
    white-space: pre;
  }

  /* Test result rows */
  .test-pass {
    background: rgba(16,185,129,0.08);
    border-left: 3px solid #10b981;
    padding: 0.5rem 1rem;
    border-radius: 0 6px 6px 0;
    margin-bottom: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #a7f3d0;
  }
  .test-fail {
    background: rgba(239,68,68,0.08);
    border-left: 3px solid #ef4444;
    padding: 0.5rem 1rem;
    border-radius: 0 6px 6px 0;
    margin-bottom: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #fca5a5;
  }
  .test-skip {
    background: rgba(100,116,139,0.08);
    border-left: 3px solid #64748b;
    padding: 0.5rem 1rem;
    border-radius: 0 6px 6px 0;
    margin-bottom: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #94a3b8;
  }

  /* Metric tiles */
  .metric-row { display: flex; gap: 1rem; margin: 1rem 0; flex-wrap: wrap; }
  .metric-tile {
    flex: 1;
    min-width: 100px;
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    text-align: center;
  }
  .metric-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1;
  }
  .metric-lbl { font-size: 0.72rem; color: #64748b; margin-top: 0.25rem; }
  .num-green { color: #34d399; }
  .num-red   { color: #f87171; }
  .num-blue  { color: #818cf8; }
  .num-amber { color: #fbbf24; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #060b16;
    border-right: 1px solid #1e293b;
  }
  .sidebar-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    color: #818cf8;
    font-weight: 600;
    padding: 0.5rem 0 1rem 0;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 1rem;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: #0f172a; }
  ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }

  /* Streamlit overrides */
  .stButton>button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    padding: 0.5rem 1.5rem;
    transition: all 0.2s;
  }
  .stButton>button:hover {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(99,102,241,0.3);
  }
  .stTextInput>div>div>input,
  .stTextArea>div>div>textarea,
  .stSelectbox>div>div>div {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
  }
  .stProgress > div > div > div {
    background: linear-gradient(90deg, #4f46e5, #7c3aed) !important;
  }
  div[data-testid="stExpander"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
  }
  .stTabs [data-baseweb="tab-list"] {
    background: #0f172a;
    border-bottom: 1px solid #1e293b;
    gap: 0.25rem;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #64748b;
    border-radius: 6px 6px 0 0;
  }
  .stTabs [aria-selected="true"] {
    color: #818cf8 !important;
    border-bottom: 2px solid #6366f1 !important;
  }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GITHUB_API_URL = "https://api.github.com"

# ─── Session State ──────────────────────────────────────────────────────────
for key, default in {
    "generated_code": "",
    "test_results": [],
    "run_log": "",
    "phase": "idle",
    "repo_files": [],
    "selected_file": "",
    "file_content": "",
    "diff_content": "",
    "project_path": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helper Functions ────────────────────────────────────────────────────────

def call_groq(api_key: str, prompt: str, system: str = "") -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 4096
    }
    resp = requests.post(GROQ_API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def github_get(endpoint: str, token: str):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get(f"{GITHUB_API_URL}{endpoint}", headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.json()


def get_repo_tree(owner: str, repo: str, branch: str, token: str):
    data = github_get(f"/repos/{owner}/{repo}/git/trees/{branch}?recursive=1", token)
    return [f["path"] for f in data.get("tree", []) if f["type"] == "blob" and f["path"].endswith(".java")]


def get_file_content(owner: str, repo: str, path: str, token: str) -> str:
    data = github_get(f"/repos/{owner}/{repo}/contents/{path}", token)
    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")


def get_pr_diff(owner: str, repo: str, pr_number: int, token: str) -> str:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    resp = requests.get(
        f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls/{pr_number}",
        headers=headers, timeout=20
    )
    resp.raise_for_status()
    return resp.text


def generate_selenium_tests(groq_key: str, source_code: str, class_name: str,
                             base_url: str, browser: str, context: str = "") -> str:
    system = """You are an expert Selenium + TestNG Java automation engineer.
Generate complete, compilable Java test classes. Always:
- Use WebDriverManager for driver setup (no hardcoded paths)
- Include @BeforeClass / @AfterClass for driver lifecycle  
- Use explicit waits (WebDriverWait), never Thread.sleep
- Follow Page Object Model structure when appropriate
- Include @Test annotations with descriptive names
- Handle browser selection via a parameter (chrome/firefox/edge)
- Add meaningful assertions
- Output ONLY valid Java code, no markdown fences, no explanation
"""
    prompt = f"""Generate a complete Selenium TestNG test class for the following:

TARGET CLASS / SOURCE CODE:
{source_code[:3000]}

CLASS NAME TO TEST: {class_name}
BASE URL: {base_url}
BROWSER: {browser}
EXTRA CONTEXT: {context if context else 'None'}

Requirements:
1. Class name: {class_name}Test
2. Package: com.qastudio.tests
3. Use WebDriverManager (io.github.bonigarcia.wdm)
4. Browser selection based on: "{browser}" (support chrome, firefox, edge)
5. At least 4 meaningful @Test methods
6. Proper assertions using TestNG Assert
7. Screenshot on failure using TakesScreenshot
8. Include all necessary imports

Output ONLY the Java source code.
"""
    return call_groq(groq_key, prompt, system)


def build_maven_project(project_dir: str, java_code: str, class_name: str, browser: str) -> dict:
    """Creates a full Maven project structure, writes test, and runs mvn test."""
    result = {"success": False, "output": "", "error": "", "report_path": ""}

    # Create directory tree
    src = os.path.join(project_dir, "src", "test", "java", "com", "qastudio", "tests")
    resources = os.path.join(project_dir, "src", "test", "resources")
    os.makedirs(src, exist_ok=True)
    os.makedirs(resources, exist_ok=True)

    # Write Java test file
    java_file = os.path.join(src, f"{class_name}Test.java")
    with open(java_file, "w") as f:
        f.write(java_code)

    # Write pom.xml
    pom = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.qastudio</groupId>
  <artifactId>selenium-ai-studio</artifactId>
  <version>1.0-SNAPSHOT</version>
  <packaging>jar</packaging>

  <properties>
    <maven.compiler.source>11</maven.compiler.source>
    <maven.compiler.target>11</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <selenium.version>4.18.1</selenium.version>
    <testng.version>7.9.0</testng.version>
    <webdrivermanager.version>5.8.0</webdrivermanager.version>
  </properties>

  <dependencies>
    <dependency>
      <groupId>org.seleniumhq.selenium</groupId>
      <artifactId>selenium-java</artifactId>
      <version>${{selenium.version}}</version>
    </dependency>
    <dependency>
      <groupId>io.github.bonigarcia</groupId>
      <artifactId>webdrivermanager</artifactId>
      <version>${{webdrivermanager.version}}</version>
    </dependency>
    <dependency>
      <groupId>org.testng</groupId>
      <artifactId>testng</artifactId>
      <version>${{testng.version}}</version>
    </dependency>
    <dependency>
      <groupId>com.aventstack</groupId>
      <artifactId>extentreports</artifactId>
      <version>5.1.1</version>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.2.5</version>
        <configuration>
          <suiteXmlFiles>
            <suiteXmlFile>src/test/resources/testng.xml</suiteXmlFile>
          </suiteXmlFiles>
          <systemPropertyVariables>
            <browser>{browser}</browser>
          </systemPropertyVariables>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>"""
    with open(os.path.join(project_dir, "pom.xml"), "w") as f:
        f.write(pom)

    # Write testng.xml
    testng_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="SeleniumAIStudio" verbose="1">
  <test name="AIGeneratedTests">
    <parameter name="browser" value="{browser}"/>
    <classes>
      <class name="com.qastudio.tests.{class_name}Test"/>
    </classes>
  </test>
</suite>"""
    with open(os.path.join(resources, "testng.xml"), "w") as f:
        f.write(testng_xml)

    # Run mvn test
    mvn_cmd = shutil.which("mvn") or "mvn"
    try:
        proc = subprocess.run(
            [mvn_cmd, "test", "-B", f"-Dbrowser={browser}"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        result["output"] = proc.stdout + proc.stderr
        result["success"] = proc.returncode == 0
        result["error"] = proc.stderr if proc.returncode != 0 else ""

        # Check for surefire report
        report_dir = os.path.join(project_dir, "target", "surefire-reports")
        if os.path.exists(report_dir):
            result["report_path"] = report_dir
    except FileNotFoundError:
        result["error"] = "Maven (mvn) not found on PATH. Please install Maven and ensure it's in your system PATH."
        result["output"] = result["error"]
    except subprocess.TimeoutExpired:
        result["error"] = "Maven test execution timed out after 5 minutes."
        result["output"] = result["error"]

    return result


def parse_surefire_results(report_path: str) -> list:
    """Parse TestNG/Surefire XML reports."""
    results = []
    if not report_path or not os.path.exists(report_path):
        return results

    import xml.etree.ElementTree as ET
    for xml_file in Path(report_path).glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for testcase in root.findall(".//testcase"):
                name = testcase.get("name", "unknown")
                classname = testcase.get("classname", "")
                time_taken = testcase.get("time", "0")
                failure = testcase.find("failure")
                error = testcase.find("error")
                skipped = testcase.find("skipped")

                if failure is not None:
                    status = "FAIL"
                    msg = failure.get("message", "")
                elif error is not None:
                    status = "ERROR"
                    msg = error.get("message", "")
                elif skipped is not None:
                    status = "SKIP"
                    msg = "Skipped"
                else:
                    status = "PASS"
                    msg = ""

                results.append({
                    "name": name,
                    "class": classname,
                    "time": float(time_taken),
                    "status": status,
                    "message": msg
                })
        except Exception:
            pass
    return results


def parse_maven_output(output: str) -> list:
    """Fallback: parse test results from Maven console output."""
    results = []
    lines = output.split("\n")
    for line in lines:
        line = line.strip()
        if "PASSED" in line or "Tests run:" in line:
            if "PASSED" in line:
                name = line.replace("[INFO]", "").replace("PASSED", "").strip()
                if name:
                    results.append({"name": name, "status": "PASS", "time": 0, "class": "", "message": ""})
        elif "FAILED" in line and "Tests run:" not in line:
            name = line.replace("[ERROR]", "").replace("FAILED", "").strip()
            if name:
                results.append({"name": name, "status": "FAIL", "time": 0, "class": "", "message": line})
    return results


# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ Selenium AI Studio</div>', unsafe_allow_html=True)

    st.markdown("### 🔑 API Keys")
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    github_token = st.text_input("GitHub Token", type="password", placeholder="ghp_... (repo scope)")

    st.markdown("---")
    st.markdown("### 🌐 Browser")
    browser = st.selectbox("Target Browser", ["chrome", "firefox", "edge"],
                           format_func=lambda x: {"chrome": "🟡 Chrome", "firefox": "🦊 Firefox", "edge": "🔵 Edge"}[x])
    headless = st.checkbox("Headless Mode", value=False,
                           help="Uncheck to see browser open during test execution")

    st.markdown("---")
    st.markdown("### 🔗 GitHub Repo")
    repo_owner = st.text_input("Owner / Org", placeholder="e.g. Akhter717")
    repo_name = st.text_input("Repository", placeholder="e.g. my-web-app")
    branch = st.text_input("Branch", value="main")
    pr_number = st.number_input("PR Number (optional)", min_value=0, value=0, step=1)

    st.markdown("---")
    st.markdown("### ⚙️ Test Config")
    base_url = st.text_input("Base URL", placeholder="https://your-app.com")
    extra_context = st.text_area("Extra Context", placeholder="Login flow, special selectors...", height=80)

    st.markdown("---")
    st.markdown('<small style="color:#475569">Selenium AI Studio v1.0<br>Powered by Groq + GitHub MCP</small>',
                unsafe_allow_html=True)

# ─── Main Header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <div class="hero-title">🤖 Selenium <span>AI</span> Studio</div>
  <div class="hero-sub">GitHub MCP → AI Code Generation → Browser Test Execution</div>
  <div class="pipeline">
    <div class="pipe-step">📡 GitHub MCP</div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">🔍 Diff / Source</div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">🧠 Groq LLM</div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">☕ Selenium TestNG</div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">🌐 Browser Execution</div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">📊 Results</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📁 Repository", "🧠 Generate Tests", "▶️ Run Tests", "📊 Results"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Repository Explorer (GitHub MCP)
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-label">GitHub MCP — Repository Explorer</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("🔗 Connect & Fetch Repository", use_container_width=True):
            if not github_token:
                st.error("GitHub Token required.")
            elif not repo_owner or not repo_name:
                st.error("Owner and Repository name required.")
            else:
                with st.spinner("Connecting to GitHub MCP server..."):
                    try:
                        tree = get_repo_tree(repo_owner, repo_name, branch, github_token)
                        st.session_state.repo_files = tree
                        st.success(f"✅ Connected! Found **{len(tree)}** Java files.")
                    except Exception as e:
                        st.error(f"GitHub API error: {e}")

        if st.session_state.repo_files:
            selected = st.selectbox(
                "Select Java File to Analyze",
                st.session_state.repo_files,
                key="file_picker"
            )

            if st.button("📄 Load File Content", use_container_width=True):
                with st.spinner("Fetching via GitHub MCP..."):
                    try:
                        content = get_file_content(repo_owner, repo_name, selected, github_token)
                        st.session_state.selected_file = selected
                        st.session_state.file_content = content
                        st.success(f"Loaded: `{selected}` ({len(content)} chars)")
                    except Exception as e:
                        st.error(f"Error loading file: {e}")

    with col2:
        if pr_number > 0 and github_token:
            if st.button("🔄 Fetch PR Diff", use_container_width=True):
                with st.spinner("Fetching PR diff..."):
                    try:
                        diff = get_pr_diff(repo_owner, repo_name, int(pr_number), github_token)
                        st.session_state.diff_content = diff
                        st.success(f"PR #{pr_number} diff loaded ({len(diff)} chars)")
                    except Exception as e:
                        st.error(f"PR fetch error: {e}")

        st.markdown("---")
        st.markdown("**MCP Integration Info**")
        st.markdown("""
<small style="color:#64748b">
This tab uses the GitHub REST API as an MCP-compatible server to:<br>
• List repository files<br>
• Fetch source code contents<br>
• Retrieve PR diffs for impact analysis
</small>
""", unsafe_allow_html=True)

    # Show loaded content
    if st.session_state.file_content:
        with st.expander(f"📄 {st.session_state.selected_file}", expanded=False):
            st.code(st.session_state.file_content, language="java")

    if st.session_state.diff_content:
        with st.expander(f"🔄 PR #{pr_number} Diff", expanded=False):
            st.code(st.session_state.diff_content[:5000], language="diff")

    # Manual paste fallback
    st.markdown("---")
    st.markdown('<div class="section-label">— or paste source code manually —</div>', unsafe_allow_html=True)
    manual_code = st.text_area(
        "Paste Java source code here",
        placeholder="public class LoginPage {\n    public void login(String user, String pass) {...}\n}",
        height=150,
        key="manual_source"
    )
    if manual_code:
        st.session_state.file_content = manual_code
        st.session_state.selected_file = "ManualInput"

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Generate Tests
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">AI Test Generation — Groq LLaMA 3.3 70B</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        class_name = st.text_input(
            "Class Name (under test)",
            value=st.session_state.selected_file.replace(".java", "").split("/")[-1] if st.session_state.selected_file else "",
            placeholder="e.g. LoginPage"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        gen_btn = st.button("🧠 Generate Tests", use_container_width=True)

    if gen_btn:
        if not groq_key:
            st.error("Groq API Key required.")
        elif not st.session_state.file_content and not st.session_state.diff_content:
            st.error("Load a file from GitHub or paste source code first.")
        elif not class_name:
            st.error("Class name required.")
        elif not base_url:
            st.error("Base URL required in sidebar.")
        else:
            source = st.session_state.file_content or st.session_state.diff_content
            progress = st.progress(0, text="Initializing Groq LLM...")

            with st.spinner("Generating Selenium TestNG tests..."):
                try:
                    progress.progress(20, text="Sending to Groq LLaMA 3.3 70B...")
                    time.sleep(0.3)
                    progress.progress(50, text="AI analyzing source code...")
                    java_code = generate_selenium_tests(
                        groq_key, source, class_name, base_url, browser,
                        context=extra_context
                    )
                    progress.progress(80, text="Cleaning up generated code...")
                    # Strip any markdown fences if present
                    java_code = java_code.replace("```java", "").replace("```", "").strip()
                    st.session_state.generated_code = java_code
                    progress.progress(100, text="Done!")
                    st.success(f"✅ Generated `{class_name}Test.java` — {len(java_code.splitlines())} lines")
                except Exception as e:
                    st.error(f"Generation failed: {e}")
                    progress.empty()

    if st.session_state.generated_code:
        st.markdown("---")

        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f'<div class="section-label">Generated: {class_name}Test.java</div>', unsafe_allow_html=True)
        with col_b:
            # Edit toggle
            edit_mode = st.checkbox("✏️ Edit", key="edit_toggle")

        if edit_mode:
            edited = st.text_area(
                "Edit test code",
                value=st.session_state.generated_code,
                height=450,
                key="code_editor"
            )
            if st.button("💾 Save Edits"):
                st.session_state.generated_code = edited
                st.success("Saved!")
        else:
            st.code(st.session_state.generated_code, language="java")

        # Regenerate
        if st.button("🔄 Regenerate with Different Prompt"):
            st.session_state.generated_code = ""
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Run Tests
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-label">Test Execution — Maven + WebDriverManager</div>', unsafe_allow_html=True)

    if not st.session_state.generated_code:
        st.info("👈 Generate tests first in the **Generate Tests** tab.")
    else:
        # Show execution plan
        class_display = st.session_state.selected_file.replace(".java","").split("/")[-1] if st.session_state.selected_file else "Unknown"

        st.markdown(f"""
<div class="section-card">
  <div class="section-label">Execution Plan</div>
  <table style="width:100%; font-size:0.85rem; color:#94a3b8; border-collapse:collapse;">
    <tr><td style="padding:0.3rem 0; color:#64748b; width:40%">Test Class</td>
        <td style="color:#e2e8f0">{class_display}Test.java</td></tr>
    <tr><td style="padding:0.3rem 0; color:#64748b">Browser</td>
        <td style="color:#e2e8f0">🌐 {browser.title()} {"(headless)" if headless else "(visible — browser window will open)"}</td></tr>
    <tr><td style="padding:0.3rem 0; color:#64748b">Runner</td>
        <td style="color:#e2e8f0">Maven Surefire + TestNG</td></tr>
    <tr><td style="padding:0.3rem 0; color:#64748b">Driver Mgmt</td>
        <td style="color:#e2e8f0">WebDriverManager (auto-downloads driver)</td></tr>
    <tr><td style="padding:0.3rem 0; color:#64748b">Target URL</td>
        <td style="color:#e2e8f0">{base_url or "Not set"}</td></tr>
  </table>
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            run_btn = st.button("▶️ Run Tests Now — Open Browser!", use_container_width=True)
        with col2:
            save_btn = st.button("💾 Save Project to Disk", use_container_width=True)

        if save_btn:
            save_path = st.text_input("Save project to path", value=os.path.expanduser("~/selenium-ai-studio"))
            if save_path and st.button("Confirm Save"):
                java_dir = os.path.join(save_path, "src", "test", "java", "com", "qastudio", "tests")
                os.makedirs(java_dir, exist_ok=True)
                fname = f"{class_display}Test.java"
                with open(os.path.join(java_dir, fname), "w") as f:
                    f.write(st.session_state.generated_code)
                st.success(f"Saved to {java_dir}/{fname}")

        if run_btn:
            st.session_state.phase = "running"
            st.session_state.test_results = []
            st.session_state.run_log = ""

            progress_bar = st.progress(0, text="Setting up Maven project...")

            with tempfile.TemporaryDirectory(prefix="selenium_ai_") as tmpdir:
                st.session_state.project_path = tmpdir

                # If headless, patch the generated code
                java_code = st.session_state.generated_code
                if headless and "headless" not in java_code.lower():
                    java_code = java_code.replace(
                        "new ChromeOptions()", "new ChromeOptions(); chromeOptions.addArguments(\"--headless=new\")"
                    )

                progress_bar.progress(15, text="Writing Maven project structure...")
                time.sleep(0.3)
                progress_bar.progress(30, text="Writing pom.xml, testng.xml...")

                result = {"success": False, "output": "", "error": "", "report_path": ""}

                # Setup structure
                src = os.path.join(tmpdir, "src", "test", "java", "com", "qastudio", "tests")
                resources = os.path.join(tmpdir, "src", "test", "resources")
                os.makedirs(src, exist_ok=True)
                os.makedirs(resources, exist_ok=True)

                java_file = os.path.join(src, f"{class_display}Test.java")
                with open(java_file, "w") as f:
                    f.write(java_code)

                pom_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.qastudio</groupId>
  <artifactId>selenium-ai-studio</artifactId>
  <version>1.0-SNAPSHOT</version>

  <properties>
    <maven.compiler.source>11</maven.compiler.source>
    <maven.compiler.target>11</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <dependencies>
    <dependency>
      <groupId>org.seleniumhq.selenium</groupId>
      <artifactId>selenium-java</artifactId>
      <version>4.18.1</version>
    </dependency>
    <dependency>
      <groupId>io.github.bonigarcia</groupId>
      <artifactId>webdrivermanager</artifactId>
      <version>5.8.0</version>
    </dependency>
    <dependency>
      <groupId>org.testng</groupId>
      <artifactId>testng</artifactId>
      <version>7.9.0</version>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.2.5</version>
        <configuration>
          <suiteXmlFiles>
            <suiteXmlFile>src/test/resources/testng.xml</suiteXmlFile>
          </suiteXmlFiles>
          <systemPropertyVariables>
            <browser>{browser}</browser>
            <headless>{'true' if headless else 'false'}</headless>
          </systemPropertyVariables>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>"""

                with open(os.path.join(tmpdir, "pom.xml"), "w") as f:
                    f.write(pom_content)

                testng_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="SeleniumAIStudio" verbose="2">
  <test name="AIGeneratedTests">
    <parameter name="browser" value="{browser}"/>
    <classes>
      <class name="com.qastudio.tests.{class_display}Test"/>
    </classes>
  </test>
</suite>"""
                with open(os.path.join(resources, "testng.xml"), "w") as f:
                    f.write(testng_xml)

                progress_bar.progress(50, text=f"Running mvn test — {browser.title()} browser opening...")

                mvn_cmd = shutil.which("mvn") or "mvn"
                env = os.environ.copy()
                env["BROWSER"] = browser

                try:
                    proc = subprocess.run(
                        [mvn_cmd, "test", "-B", f"-Dbrowser={browser}"],
                        cwd=tmpdir,
                        capture_output=True,
                        text=True,
                        timeout=300,
                        env=env
                    )
                    progress_bar.progress(85, text="Parsing test results...")
                    output = proc.stdout + "\n" + proc.stderr
                    result["output"] = output
                    result["success"] = proc.returncode == 0

                    report_dir = os.path.join(tmpdir, "target", "surefire-reports")
                    if os.path.exists(report_dir):
                        result["report_path"] = report_dir
                        parsed = parse_surefire_results(report_dir)
                    else:
                        parsed = parse_maven_output(output)

                    st.session_state.test_results = parsed
                    st.session_state.run_log = output
                    st.session_state.phase = "done"

                except FileNotFoundError:
                    result["output"] = "❌ Maven not found. Install Maven: https://maven.apache.org/install.html"
                    st.session_state.run_log = result["output"]
                    st.session_state.phase = "done"
                except subprocess.TimeoutExpired:
                    result["output"] = "❌ Test execution timed out after 5 minutes."
                    st.session_state.run_log = result["output"]
                    st.session_state.phase = "done"
                except Exception as e:
                    result["output"] = f"❌ Unexpected error: {e}"
                    st.session_state.run_log = result["output"]
                    st.session_state.phase = "done"

                progress_bar.progress(100, text="Complete!")

            if st.session_state.phase == "done":
                if result.get("success"):
                    st.success("✅ All tests passed! Check Results tab.")
                elif "not found" in st.session_state.run_log or "TimeoutExpired" in st.session_state.run_log:
                    st.error(st.session_state.run_log)
                else:
                    st.warning("⚠️ Tests ran — some failures detected. Check Results tab.")

        # Show console log
        if st.session_state.run_log:
            with st.expander("📋 Maven Console Output", expanded=False):
                st.markdown(f'<div class="code-block">{st.session_state.run_log[:6000]}</div>',
                            unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Results Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-label">Test Results Dashboard</div>', unsafe_allow_html=True)

    if not st.session_state.test_results and not st.session_state.run_log:
        st.info("Run tests first to see results here.")
    else:
        results = st.session_state.test_results
        passed  = sum(1 for r in results if r["status"] == "PASS")
        failed  = sum(1 for r in results if r["status"] == "FAIL")
        errored = sum(1 for r in results if r["status"] == "ERROR")
        skipped = sum(1 for r in results if r["status"] == "SKIP")
        total   = len(results)

        # Determine status from log if no parsed results
        run_success = "BUILD SUCCESS" in st.session_state.run_log
        run_failure = "BUILD FAILURE" in st.session_state.run_log

        if total > 0:
            pass_rate = int((passed / total) * 100)
        else:
            pass_rate = 0

        # Overall status
        if run_success:
            st.markdown('<span class="badge-success">✅ BUILD SUCCESS</span>', unsafe_allow_html=True)
        elif run_failure:
            st.markdown('<span class="badge-fail">❌ BUILD FAILURE</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-running">⚙️ Status Unknown</span>', unsafe_allow_html=True)

        # Metrics
        st.markdown(f"""
<div class="metric-row">
  <div class="metric-tile">
    <div class="metric-num num-blue">{total}</div>
    <div class="metric-lbl">Total Tests</div>
  </div>
  <div class="metric-tile">
    <div class="metric-num num-green">{passed}</div>
    <div class="metric-lbl">Passed</div>
  </div>
  <div class="metric-tile">
    <div class="metric-num num-red">{failed + errored}</div>
    <div class="metric-lbl">Failed</div>
  </div>
  <div class="metric-tile">
    <div class="metric-num num-amber">{skipped}</div>
    <div class="metric-lbl">Skipped</div>
  </div>
  <div class="metric-tile">
    <div class="metric-num num-{'green' if pass_rate >= 80 else 'amber' if pass_rate >= 50 else 'red'}">{pass_rate}%</div>
    <div class="metric-lbl">Pass Rate</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Individual test results
        if results:
            st.markdown("---")
            st.markdown('<div class="section-label">Test Case Breakdown</div>', unsafe_allow_html=True)
            for r in results:
                icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥", "SKIP": "⏭️"}.get(r["status"], "•")
                css_class = {"PASS": "test-pass", "FAIL": "test-fail", "ERROR": "test-fail", "SKIP": "test-skip"}.get(r["status"], "test-skip")
                time_str = f"{r['time']:.2f}s" if r["time"] else ""
                msg = f" — {r['message'][:80]}" if r["message"] else ""
                st.markdown(
                    f'<div class="{css_class}">{icon} {r["name"]} {time_str}{msg}</div>',
                    unsafe_allow_html=True
                )
        else:
            # Show fallback summary from log
            st.markdown("---")
            st.markdown('<div class="section-label">Maven Summary</div>', unsafe_allow_html=True)
            log_lines = [l for l in st.session_state.run_log.split("\n")
                         if any(k in l for k in ["Tests run:", "BUILD", "ERROR", "PASSED", "FAILED", "[INFO] ---"])]
            summary = "\n".join(log_lines[-30:])
            if summary:
                st.code(summary, language="text")

        # Download generated test
        if st.session_state.generated_code:
            st.markdown("---")
            class_display2 = st.session_state.selected_file.replace(".java","").split("/")[-1] if st.session_state.selected_file else "Generated"
            st.download_button(
                label="⬇️ Download Generated Test (.java)",
                data=st.session_state.generated_code,
                file_name=f"{class_display2}Test.java",
                mime="text/plain",
                use_container_width=True
            )

        if st.session_state.run_log:
            st.download_button(
                label="⬇️ Download Maven Log (.txt)",
                data=st.session_state.run_log,
                file_name="maven_test_output.txt",
                mime="text/plain",
                use_container_width=True
            )
