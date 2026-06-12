# 🤖 Selenium AI Studio

> **AI Assignment** — AI Tool + MCP Server + Selenium Test Automation

---

## What This Does

**End-to-end pipeline:**
```
GitHub Repo (MCP) → Diff/Source Code → Groq LLaMA 3.3 70B → Java TestNG Code → Maven → Browser Opens → Tests Execute → Results Dashboard
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| AI | Groq API (LLaMA 3.3 70B) |
| MCP Server | GitHub REST API (MCP-compatible) |
| Test Framework | Selenium 4 + TestNG 7 |
| Driver Management | WebDriverManager (auto-downloads) |
| Build Tool | Maven 3.x |
| Browser Support | Chrome / Firefox / Edge |

---

## Prerequisites

### 1. Python 3.9+
```bash
pip install -r requirements.txt
```

### 2. Java 11+
```bash
java -version  # must be 11 or higher
```

### 3. Maven 3.6+
```bash
# Windows (Chocolatey)
choco install maven

# macOS
brew install maven

# Ubuntu/Debian
sudo apt install maven
```
Verify: `mvn -version`

### 4. Browser installed
- Chrome: https://www.google.com/chrome/
- Firefox: https://www.mozilla.org/firefox/
- Edge: Pre-installed on Windows

> **WebDriverManager automatically downloads the correct driver — no manual chromedriver setup needed!**

---

## API Keys Required

### Groq API Key (free)
1. Go to https://console.groq.com
2. Create account → API Keys → Create Key
3. Paste into app sidebar

### GitHub Personal Access Token
1. GitHub → Settings → Developer Settings → Personal Access Tokens
2. Create token with `repo` scope (read access)
3. Paste into app sidebar

---

## Run Locally

```bash
cd selenium_ai_studio
streamlit run app.py
```

Opens at: http://localhost:8501

---

## How to Use — Step by Step

### Step 1 — Repository Tab
- Enter GitHub Owner, Repo name, Branch
- Click **Connect & Fetch Repository**
- Select a Java file → **Load File Content**
- (Optional) Enter PR number → **Fetch PR Diff** for impact analysis

### Step 2 — Generate Tests Tab
- Enter the class name
- Click **Generate Tests**
- AI generates a complete `ClassName Test.java` with:
  - `@BeforeClass` WebDriverManager setup
  - `@AfterClass` driver quit
  - 4+ `@Test` methods with assertions
  - Explicit waits, Screenshot on failure
  - Browser selection (Chrome/Firefox/Edge)

### Step 3 — Run Tests Tab
- Verify execution plan (browser, class, URL)
- Click **▶️ Run Tests Now — Open Browser!**
- **Browser window opens** and tests execute live
- Maven output streams to console log

### Step 4 — Results Tab
- Pass/Fail/Skip metrics
- Individual test case breakdown
- Download generated `.java` file
- Download Maven log

---

## Streamlit Cloud Deployment

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "gsk_..."
GITHUB_TOKEN = "ghp_..."
```

> Note: Browser execution requires a local machine (not Streamlit Cloud). For cloud deployment, use headless mode + a CI/CD runner.

---

## Assignment Coverage

| Requirement | Implementation |
|-------------|---------------|
| ✅ AI Tool | Groq LLaMA 3.3 70B generates Java TestNG code |
| ✅ MCP Server | GitHub REST API (MCP-compatible integration) |
| ✅ Use Case | Automated Selenium test generation from repo source |
| ✅ GIT Integration | PR diff analysis → targeted test generation |
| ✅ Browser Execution | Chrome / Firefox / Edge via WebDriverManager |
| ✅ Agentic Flow | Source → Analysis → Code Gen → Execution → Report |

---

## Project Structure (Generated Maven Project)

```
/tmp/selenium_ai_XXXX/
├── pom.xml                          ← Auto-generated
├── src/
│   └── test/
│       ├── java/com/qastudio/tests/
│       │   └── ClassNameTest.java   ← AI-generated
│       └── resources/
│           └── testng.xml           ← Auto-generated
└── target/
    └── surefire-reports/            ← Test results XML
```
