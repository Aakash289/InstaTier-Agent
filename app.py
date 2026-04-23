import streamlit as st
import pandas as pd
import json
import anthropic
import io
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InstaTier · CRM Enrichment Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Manrope:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, html, body { box-sizing: border-box; }

.stApp, [class*="css"] {
    background: #f5f6fa !important;
    color: #1a1d2e !important;
    font-family: 'Manrope', sans-serif !important;
}

/* ── Hero ── */
.hero-wrap {
    background: linear-gradient(135deg, #1a1d2e 0%, #2d3561 100%);
    border-radius: 16px;
    padding: 2.5rem 2.5rem 2rem 2.5rem;
    margin-bottom: 2rem;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #7eb3ff;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem;
    line-height: 0.92;
    letter-spacing: 0.04em;
    color: #ffffff;
    margin-bottom: 0.6rem;
}
.hero-title span { color: #5b9cf6; }
.hero-desc {
    font-size: 0.95rem;
    color: #a8b4cc;
    font-weight: 400;
    max-width: 560px;
    line-height: 1.65;
}

/* ── ICP Panel ── */
.icp-panel {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin: 1rem 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.icp-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #3a7bd5;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}
.icp-tag {
    display: inline-block;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.72rem;
    color: #2563eb;
    font-family: 'JetBrains Mono', monospace;
    margin: 0.2rem 0.2rem 0.2rem 0;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

/* ── Stats ── */
.stat-row { display: flex; gap: 0.75rem; margin: 1.5rem 0; }
.stat-box {
    flex: 1;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.stat-box .num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.8rem;
    line-height: 1;
    color: #1a1d2e;
}
.stat-box .num.hot  { color: #dc2626; }
.stat-box .num.warm { color: #d97706; }
.stat-box .num.cold { color: #2563eb; }
.stat-box .lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-top: 0.2rem;
}

/* ── Table ── */
div[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #2563eb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 2rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.3) !important;
}
.stDownloadButton > button {
    background: #ffffff !important;
    color: #2563eb !important;
    border: 1.5px solid #2563eb !important;
    border-radius: 8px !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

/* ── How to export box ── */
.export-guide {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-top: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.export-guide h4 {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    color: #2563eb !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.8rem !important;
}
.step {
    display: flex;
    gap: 0.8rem;
    margin-bottom: 0.6rem;
    align-items: flex-start;
}
.step-num {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #2563eb;
    flex-shrink: 0;
    margin-top: 1px;
}
.step-text { font-size: 0.82rem; color: #475569; line-height: 1.5; }
.step-text code {
    background: #f1f5f9;
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #2563eb;
    border: 1px solid #e2e8f0;
}

/* ── Section headers ── */
.sec-hdr {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
    margin-top: 1.5rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
section[data-testid="stSidebar"] * {
    font-family: 'Manrope', sans-serif !important;
    color: #1a1d2e !important;
}

/* ── Expander ── */
details {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
summary {
    background: #ffffff !important;
    border-radius: 10px !important;
    padding: 0.7rem 1rem !important;
    color: #1a1d2e !important;
}

.stProgress > div > div { background: linear-gradient(90deg, #2563eb, #5b9cf6) !important; }
.stSelectbox label, .stTextInput label { color: #475569 !important; font-size: 0.8rem !important; }
.stSelectbox div[data-baseweb="select"] { background: #ffffff !important; border-color: #e2e8f0 !important; }
[data-testid="stMarkdownContainer"] p { color: #334155 !important; }
h1, h2, h3, h4 { color: #1a1d2e !important; }
</style>
""", unsafe_allow_html=True)

# ── ICP Definitions per Startup Type ──────────────────────────────────────────
ICP_PROFILES = {
    "HR SaaS": {
        "icon": "👥",
        "desc": "HR software, HRIS, payroll, recruiting tools",
        "target_titles": ["CHRO", "Chief People Officer", "VP HR", "Head of People", "HR Director", "People Operations", "Talent Acquisition"],
        "target_industries": ["SaaS", "FinTech", "MarTech", "AI/ML", "E-commerce", "HealthTech"],
        "target_sizes": ["Mid-Market", "Enterprise"],
        "primary_industries": ["SaaS", "FinTech", "AI/ML", "MarTech", "HealthTech", "Cloud"],
        "secondary_industries": ["E-commerce", "Consulting", "EdTech", "Analytics"],
        "pitch": "HR leaders at growing tech companies (50–2000 employees) who are scaling their people ops",
    },
    "FinTech / Payments": {
        "icon": "💳",
        "desc": "Payments, lending, treasury, accounting tools",
        "target_titles": ["CFO", "VP Finance", "Controller", "Finance Director", "Head of Treasury", "Financial Operations"],
        "target_industries": ["SaaS", "E-commerce", "Retail", "Manufacturing", "Healthcare"],
        "target_sizes": ["Mid-Market", "Enterprise", "Small Business"],
        "primary_industries": ["SaaS", "E-commerce", "Retail", "Manufacturing"],
        "secondary_industries": ["Healthcare", "Logistics", "Consulting", "Analytics"],
        "pitch": "Finance leaders at companies processing significant transaction volume",
    },
    "MarTech / Analytics": {
        "icon": "📊",
        "desc": "Marketing automation, BI, data analytics platforms",
        "target_titles": ["CMO", "VP Marketing", "Head of Growth", "Demand Gen", "Marketing Director", "Growth Manager"],
        "target_industries": ["SaaS", "E-commerce", "MarTech", "FinTech", "Retail"],
        "target_sizes": ["Mid-Market", "Enterprise", "Small Business"],
        "primary_industries": ["SaaS", "MarTech", "E-commerce", "FinTech"],
        "secondary_industries": ["Retail", "Analytics", "EdTech", "Consulting"],
        "pitch": "Marketing and growth leaders who need better data to drive pipeline",
    },
    "Sales Enablement": {
        "icon": "🚀",
        "desc": "CRM, sales tools, outreach, revenue intelligence",
        "target_titles": ["VP Sales", "CRO", "Head of Revenue", "Sales Director", "RevOps", "Sales Operations"],
        "target_industries": ["SaaS", "FinTech", "MarTech", "AI/ML", "Consulting"],
        "target_sizes": ["Mid-Market", "Enterprise", "Startup"],
        "primary_industries": ["SaaS", "FinTech", "AI/ML", "MarTech"],
        "secondary_industries": ["Consulting", "Analytics", "Cloud", "CyberSecurity"],
        "pitch": "Revenue leaders at B2B companies with 5+ person sales teams",
    },
    "CyberSecurity": {
        "icon": "🔒",
        "desc": "Security platforms, compliance, identity management",
        "target_titles": ["CISO", "CTO", "VP Engineering", "IT Director", "Head of Security", "Security Engineer"],
        "target_industries": ["FinTech", "Healthcare", "SaaS", "Enterprise", "Government"],
        "target_sizes": ["Enterprise", "Mid-Market"],
        "primary_industries": ["FinTech", "HealthTech", "SaaS", "Cloud", "CyberSecurity"],
        "secondary_industries": ["Manufacturing", "Logistics", "Consulting", "Analytics"],
        "pitch": "Security and IT leaders at regulated or high-compliance industries",
    },
    "Custom ICP": {
        "icon": "⚙️",
        "desc": "Define your own target customer profile",
        "target_titles": [],
        "target_industries": [],
        "target_sizes": [],
        "primary_industries": [],
        "secondary_industries": [],
        "pitch": "",
    },
}

# ── Column Normalisation ──────────────────────────────────────────────────────
COLUMN_ALIASES = {
    "name":       ["name","full name","fullname","first name","contact name","lead name"],
    "email":      ["email","email address","work email","business email","e-mail"],
    "title":      ["title","job title","position","role","current title","designation"],
    "company":    ["company","company name","organization","employer","current company"],
    "location":   ["location","city","region","country","geography"],
    "linkedin":   ["linkedin","profile url","linkedin url","profile link"],
}

def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for std, aliases in COLUMN_ALIASES.items():
        for col in df.columns:
            if col.lower().strip() in aliases:
                mapping[col] = std
                break
    df = df.rename(columns=mapping)
    for col in ["name","email","title","company","location"]:
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("")
    return df

# ── Scoring Logic (local Python) ──────────────────────────────────────────────
def score_seniority(title: str, icp: dict) -> tuple[int, str]:
    title_l = title.lower()
    target = [t.lower() for t in icp["target_titles"]]

    # Direct ICP title match → bonus
    if any(t in title_l for t in target):
        return 30, "🎯 ICP Title Match"
    if any(k in title_l for k in ["ceo","cto","cfo","coo","cpo","ciso","founder","owner","president","chief","managing director"]):
        return 28, "C-Suite"
    if any(k in title_l for k in ["vp","vice president","head of","director"]):
        return 23, "Senior Leader"
    if any(k in title_l for k in ["manager","lead","principal","senior","partner"]):
        return 14, "Mid-Level"
    if any(k in title_l for k in ["analyst","associate","coordinator","intern","engineer","specialist","consultant","scientist"]):
        return 7,  "Individual Contributor"
    return 8, "Unknown"

def score_email(email: str) -> tuple[int, str]:
    personal = {"gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com","aol.com","live.com","me.com"}
    if "@" not in email or len(email) < 5:
        return 0, "Invalid"
    domain = email.split("@")[-1].lower()
    if domain in personal:
        return 2, "Personal"
    return 14, "Professional"

def score_company_size(size: str) -> int:
    return {"Enterprise": 20, "Mid-Market": 25, "Small Business": 15,
            "Startup": 10, "Individual": 3, "Unknown": 5}.get(size, 5)

def score_industry(industry: str, icp: dict) -> int:
    if industry in icp["primary_industries"]:   return 25
    if industry in icp["secondary_industries"]: return 18
    if industry in ["Healthcare","Retail","Manufacturing","Logistics"]: return 10
    if industry == "Unknown": return 7
    return 7

def calculate_score(lead: dict, icp: dict) -> dict:
    s1, sen_label = score_seniority(lead.get("title",""), icp)
    s2, email_label = score_email(lead.get("email",""))
    s3 = score_company_size(lead.get("company_size","Unknown"))
    s4 = score_industry(lead.get("industry","Unknown"), icp)
    total = min(s1 + s2 + s3 + s4, 100)
    return {
        "icp_score": total,
        "seniority_label": sen_label,
        "email_quality": email_label,
        "score_breakdown": {"seniority": s1, "email": s2, "size": s3, "industry": s4}
    }

def assign_tiers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("icp_score", ascending=False).reset_index(drop=True)
    n   = len(df)
    t1  = max(1, round(n * 0.20))
    t2  = max(2, round(n * 0.70))
    tiers = ["🔥 HOT" if i < t1 else "🟡 WARM" if i < t2 else "🔵 COLD" for i in range(n)]
    df["priority_tier"] = tiers
    return df

# ── Claude Enrichment ─────────────────────────────────────────────────────────
def enrich_with_claude(leads: list[dict], icp_name: str, icp: dict) -> list[dict]:
    client = anthropic.Anthropic()

    batch = json.dumps([
        {"id": i,
         "name":    l.get("name",""),
         "email":   l.get("email",""),
         "title":   l.get("title",""),
         "company": l.get("company",""),
        } for i, l in enumerate(leads)
    ])

    prompt = f"""You are a B2B firmographic enrichment engine for a {icp_name} startup.

For each lead, infer from the email domain, company name, and job title:

1. company_name     — full proper name (e.g. "Stripe, Inc.")
2. industry         — pick ONE: SaaS | FinTech | HealthTech | AI/ML | Cloud | CyberSecurity | MarTech | Consulting | EdTech | HRTech | E-commerce | Analytics | Data | Healthcare | Retail | Manufacturing | Logistics | Unknown
3. company_size     — pick ONE: Enterprise | Mid-Market | Small Business | Startup | Individual | Unknown
4. enrichment_confidence — Low | Medium | High
5. fit_reason       — one short sentence (max 12 words) explaining why this lead fits or doesn't fit a {icp_name} product. Be specific.

Rules:
- Well-known companies (stripe, salesforce, hubspot, openai, databricks, shopify, twilio, deloitte, mckinsey, unitedhealth, notion, google, microsoft, apple, amazon, netflix, uber, airbnb, etc.) → High confidence
- Personal emails (gmail, yahoo, hotmail) → Individual size, Unknown industry, Low confidence, fit_reason = "Personal email — likely not a business lead"
- Small/unknown domains → Startup or Small Business, Low confidence
- Use the job title to confirm industry fit

Return ONLY valid JSON array, no markdown, no backticks:
[{{"id":0,"company_name":"...","industry":"...","company_size":"...","enrichment_confidence":"...","fit_reason":"..."}}]

Leads:
{batch}"""

    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    enriched_list = json.loads(msg.content[0].text.strip())
    enriched_map  = {item["id"]: item for item in enriched_list}

    result = []
    for i, lead in enumerate(leads):
        merged = {**lead, **enriched_map.get(i, {})}
        scores = calculate_score(merged, icp)
        merged.update(scores)
        result.append(merged)
    return result



# ═══════════════════════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════════════════════

# Hero
st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">// B2B Lead Intelligence</div>
  <div class="hero-title">INSTA<span>TIER</span></div>
  <div class="hero-desc">Upload your lead CSV. The agent infers firmographics, scores each lead against your startup's ICP, and instantly tiers your pipeline into HOT · WARM · COLD.</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("#### InstaTier")
    st.caption("B2B Lead Enrichment Agent")
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown("""
1. Select your startup type  
2. Download the sample CSV or export from LinkedIn  
3. Upload your leads file  
4. Click **Run Enrichment**  
5. Download your scored pipeline
    """)
    st.markdown("---")

# ── STEP 1: Startup Type ──────────────────────────────────────────────────────
st.markdown('<div class="sec-hdr">Step 01 · Select Your Startup Type</div>', unsafe_allow_html=True)

startup_type = st.selectbox(
    "What kind of startup are you?",
    options=list(ICP_PROFILES.keys()),
    format_func=lambda x: f"{ICP_PROFILES[x]['icon']}  {x} — {ICP_PROFILES[x]['desc']}"
)

icp = ICP_PROFILES[startup_type]

# Custom ICP input
if startup_type == "Custom ICP":
    st.markdown("**Define your ICP:**")
    c1, c2 = st.columns(2)
    with c1:
        custom_titles = st.text_input("Target job titles (comma-separated)", "VP Sales, CRO, Head of Revenue")
        custom_primary = st.text_input("Primary industries (comma-separated)", "SaaS, FinTech")
    with c2:
        custom_secondary = st.text_input("Secondary industries (comma-separated)", "Consulting, Analytics")
        custom_pitch = st.text_input("Your ICP in one sentence", "Revenue leaders at B2B SaaS companies")

    icp = {
        "target_titles": [t.strip() for t in custom_titles.split(",")],
        "primary_industries": [i.strip() for i in custom_primary.split(",")],
        "secondary_industries": [i.strip() for i in custom_secondary.split(",")],
        "target_sizes": ["Mid-Market","Enterprise"],
        "pitch": custom_pitch,
    }

# ICP panel
if startup_type != "Custom ICP":
    tags_html = "".join(f'<span class="icp-tag">{t}</span>' for t in icp["target_titles"][:6])
    ind_html  = "".join(f'<span class="icp-tag">{i}</span>' for i in icp["primary_industries"])
    st.markdown(f"""
    <div class="icp-panel">
        <div class="icp-title">Your ICP Profile — {startup_type}</div>
        <div style="font-size:0.82rem;color:#9ca3af;margin-bottom:0.8rem;">🎯 {icp['pitch']}</div>
        <div style="margin-bottom:0.5rem"><span style="font-size:0.7rem;color:#4b5563;text-transform:uppercase;letter-spacing:0.1em">Target Titles · </span>{tags_html}</div>
        <div><span style="font-size:0.7rem;color:#4b5563;text-transform:uppercase;letter-spacing:0.1em">Best Fit Industries · </span>{ind_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ── STEP 2: Upload ────────────────────────────────────────────────────────────
st.markdown('<div class="sec-hdr">Step 02 · Generate Your Lead CSV — Then Upload It</div>', unsafe_allow_html=True)

# Generate leads instructions
st.markdown("""
<div class="export-guide">
<h4>Option A · Use generate_leads.py (Recommended for testing)</h4>
<div class="step"><div class="step-num">1</div><div class="step-text">Open your terminal in the project folder</div></div>
<div class="step"><div class="step-num">2</div><div class="step-text">Run: <code>python generate_leads.py --type "HR SaaS" --count 15</code></div></div>
<div class="step"><div class="step-num">3</div><div class="step-text">A file like <code>leads_hr_saas_20240411_120000.csv</code> will appear in your folder</div></div>
<div class="step"><div class="step-num">4</div><div class="step-text">Upload that file below ↓</div></div>
<div class="step"><div class="step-num">→</div><div class="step-text">Other type options: <code>FinTech / Payments</code> · <code>MarTech / Analytics</code> · <code>Sales Enablement</code> · <code>CyberSecurity</code></div></div>
</div>
""", unsafe_allow_html=True)

with st.expander("📋  Option B — Export from LinkedIn / Sales Navigator instead"):
    st.markdown("""
<div class="export-guide">
<h4>LinkedIn Sales Navigator</h4>
<div class="step"><div class="step-num">1</div><div class="step-text">Run your lead search with filters (title, company size, industry)</div></div>
<div class="step"><div class="step-num">2</div><div class="step-text">Select leads → click <code>Save to List</code></div></div>
<div class="step"><div class="step-num">3</div><div class="step-text">Go to <code>Lists</code> → open your list → click <code>Export</code> (CSV)</div></div>
<div class="step"><div class="step-num">4</div><div class="step-text">Upload that CSV below — InstaTier auto-detects all column names</div></div>
</div>
<div class="export-guide" style="margin-top:0.8rem">
<h4>Other sources that work</h4>
<div class="step"><div class="step-num">→</div><div class="step-text">Apollo.io exports · HubSpot exports · Event registration CSVs · Webinar sign-ups</div></div>
<div class="step"><div class="step-num">→</div><div class="step-text">Required columns (any order): <code>name</code> · <code>email</code> · <code>title</code> · <code>company</code> · <code>location</code></div></div>
</div>
    """, unsafe_allow_html=True)

uploaded = st.file_uploader("⬆  Upload your leads CSV", type="csv", help="Generated by generate_leads.py or exported from LinkedIn / Apollo / HubSpot")

if uploaded:
    raw_df = pd.read_csv(uploaded)
    raw_df = normalise_columns(raw_df)

    st.markdown('<div class="sec-hdr">Preview — Raw Uploaded Leads</div>', unsafe_allow_html=True)

    preview_cols = [c for c in ["name","email","title","company","location"] if c in raw_df.columns]
    st.dataframe(raw_df[preview_cols].head(20), use_container_width=True, height=280)
    st.caption(f"{len(raw_df)} leads loaded · Showing first 20")

    # ── STEP 3: Run ───────────────────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Step 03 · Run Enrichment & Scoring</div>', unsafe_allow_html=True)

    max_leads = min(15, len(raw_df))
    st.caption(f"Processing {max_leads} leads  ·  Estimated cost: ~${max_leads * 0.0004:.3f}  ·  Single batched API call")

    if st.button("🎯  Enrich & Score Leads", use_container_width=True):
        leads_to_process = raw_df.head(max_leads).to_dict("records")

        progress = st.progress(0, text="Sending leads to Claude for firmographic inference...")
        t0 = time.time()
        enriched = enrich_with_claude(leads_to_process, startup_type, icp)
        progress.progress(70, text="Scoring against your ICP...")
        time.sleep(0.3)
        enriched_df = pd.DataFrame(enriched)
        enriched_df = assign_tiers(enriched_df)
        progress.progress(100, text="Done!")
        elapsed = round(time.time() - t0, 1)

        st.session_state["enriched_df"] = enriched_df
        st.session_state["elapsed"] = elapsed
        st.session_state["startup_type"] = startup_type

# ── STEP 4: Results ───────────────────────────────────────────────────────────
if "enriched_df" in st.session_state:
    df      = st.session_state["enriched_df"]
    elapsed = st.session_state.get("elapsed","—")
    stype   = st.session_state.get("startup_type","")

    st.markdown("---")
    st.markdown(f'<div class="sec-hdr">Results · {stype} ICP Scoring</div>', unsafe_allow_html=True)

    # Stats
    hot  = len(df[df["priority_tier"]=="🔥 HOT"])
    warm = len(df[df["priority_tier"]=="🟡 WARM"])
    cold = len(df[df["priority_tier"]=="🔵 COLD"])
    avg  = round(df["icp_score"].mean(), 1)
    top  = df["icp_score"].max()

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="num">{len(df)}</div><div class="lbl">Total Leads</div></div>
        <div class="stat-box"><div class="num hot">{hot}</div><div class="lbl">🔥 Hot Leads</div></div>
        <div class="stat-box"><div class="num warm">{warm}</div><div class="lbl">🟡 Warm Leads</div></div>
        <div class="stat-box"><div class="num cold">{cold}</div><div class="lbl">🔵 Cold Leads</div></div>
        <div class="stat-box"><div class="num">{avg}</div><div class="lbl">Avg ICP Score</div></div>
        <div class="stat-box"><div class="num">{top}</div><div class="lbl">Top Score</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Full table — seniority_label before priority_tier
    st.markdown('<div class="sec-hdr">Enriched Lead Table</div>', unsafe_allow_html=True)
    display_cols = [c for c in ["name","email","title","company_name","industry",
                                 "company_size","enrichment_confidence","seniority_label",
                                 "email_quality","icp_score","priority_tier","fit_reason"] if c in df.columns]

    styled = df[display_cols].style.background_gradient(
        subset=["icp_score"], cmap="RdYlGn", vmin=0, vmax=100
    ).format({"icp_score": "{:.0f}"})
    st.dataframe(styled, use_container_width=True, height=500)

    # Score breakdown — top 5
    st.markdown('<div class="sec-hdr">Score Breakdown · Top Leads</div>', unsafe_allow_html=True)
    for _, row in df.head(5).iterrows():
        bd = row.get("score_breakdown", {})
        with st.expander(f"{row['priority_tier']}  ·  {row.get('name','—')}  ·  {row.get('company_name','—')}  ·  Score: {row['icp_score']}/100"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Email:** {row.get('email','—')}")
                st.markdown(f"**Title:** {row.get('title','—')}")
                st.markdown(f"**Industry:** {row.get('industry','—')}")
                st.markdown(f"**Size:** {row.get('company_size','—')}")
                st.markdown(f"**Confidence:** {row.get('enrichment_confidence','—')}")
                st.markdown(f"**Fit reason:** _{row.get('fit_reason','—')}_")
            with c2:
                st.markdown("**Score Breakdown:**")
                st.progress(bd.get("seniority",0)/30, text=f"Seniority / Title match:  {bd.get('seniority',0)}/30")
                st.progress(bd.get("size",0)/25,      text=f"Company size fit:         {bd.get('size',0)}/25")
                st.progress(bd.get("industry",0)/25,  text=f"Industry fit:             {bd.get('industry',0)}/25")
                st.progress(bd.get("email",0)/20,     text=f"Email quality:            {bd.get('email',0)}/20")

    # Download
    st.markdown("---")
    export_cols = [c for c in ["priority_tier","name","email","title","company_name","industry",
                                "company_size","enrichment_confidence","seniority_label",
                                "email_quality","icp_score","fit_reason"] if c in df.columns]
    csv_out = df[export_cols].to_csv(index=False).encode()

    st.download_button(
        "⬇  Download Enriched & Scored CSV — CRM Ready",
        data=csv_out,
        file_name=f"enriched_leads_{startup_type.lower().replace(' ','_').replace('/','_')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.caption("Import this directly into HubSpot · Salesforce · Notion · Airtable · Any CRM")
