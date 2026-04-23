# InstaTier

**AI-Powered CRM Lead Enrichment and Scoring Agent**

InstaTier is a Streamlit web application that takes a raw list of B2B leads and turns it into a fully enriched, scored, and prioritized sales pipeline using the Claude AI API. Upload a CSV with just names and emails, and within 30 seconds you get back a CRM-ready file where every lead has a company profile, an ICP fit score out of 100, and a priority label telling your sales team exactly who to call first.

---

## The Problem This Solves

Every B2B startup collects leads from LinkedIn exports, event sign-ups, webinar registrations, and contact forms. The raw data looks like this:

```
Marcus Webb    | m.webb@hubspot.com  | Director of Sales
Priya Patel    | priya@stripe.com    | VP Engineering
Sarah Chen     | sarah@gmail.com     | (no title)
```

Before a sales rep can prioritize outreach, they have to manually Google every person, figure out if the company is the right size, decide whether the job title has real buying power, and rank who is worth a personal call versus an automated email. For a list of 100 leads, that is an entire day of work before a single outreach email is sent.

InstaTier eliminates that process entirely. It reads the email domain and job title, asks Claude to infer the company profile, runs a scoring calculation across four dimensions, and ranks every lead in the list by how closely they match your startup's ideal customer. The output is a downloadable CSV you can import directly into HubSpot, Salesforce, Notion, or any CRM.

---

## How It Was Built

The project uses three core technologies:

**Streamlit** handles the entire user interface. It provides the file uploader, dropdown menus, data tables, progress bars, and download buttons without requiring any frontend code. The whole UI is defined in Python.

**Anthropic Claude API** handles the intelligence layer. When leads are uploaded, all of them are sent to Claude in a single batched API call. Claude reads each email domain and job title and infers the company name, industry, company size, confidence level, and a one-sentence reason why the lead fits or does not fit the product. Using a single batched call instead of one call per lead keeps the cost under one cent per run.

**Pandas** handles all CSV reading, column detection, data merging, and the final export. The scoring calculations run entirely in Python with no additional API calls, which keeps both cost and latency low.

---

## Project Files

### `app.py`

This is the main application file and contains everything the Streamlit app needs to run. It is organized into four functional layers:

**ICP Profile Definitions** at the top of the file define the ideal customer for each supported startup type. Each profile lists target job titles, primary industries, secondary industries, and company sizes. When a user selects a startup type from the dropdown, these definitions control how points are distributed across the scoring dimensions.

**Column Normalisation** handles the reality that different CSV exports use different column names. A LinkedIn export might say "Full Name" while an Apollo export says "Contact Name." The normalisation function maps any common variation to the standard field names the app expects. If a column is missing entirely, it creates an empty column rather than crashing.

**Claude API Layer** sends all leads in one prompt and receives structured JSON back. The prompt instructs Claude to return only a JSON array with no extra text, which makes parsing reliable. Temperature is set to zero so the output is deterministic, meaning the same leads will always receive the same enrichment and the same score on every run.

**Scoring Engine** runs entirely in Python after Claude returns the enrichment data. Four functions calculate the seniority score, email quality score, company size score, and industry fit score. A fifth function sorts all leads by their total score and assigns HOT, WARM, or COLD labels based on where each lead falls in the percentile distribution of the uploaded list.

### `generate_leads.py`

This is a standalone command-line script that generates realistic test CSV files. It has nothing to do with AI. It contains five pools of pre-written leads, one for each supported startup type. Each pool has 15 leads split into three quality groups: strong ICP matches with real company domains and relevant titles, adjacent leads that partially fit the profile, and noise leads with personal Gmail addresses and missing data.

The script uses a fixed random seed so the same CSV is generated every time. This matters because the tier assignment is based on the relative rank of leads within the uploaded list, so if the row order changed between runs, the same lead could end up in a different tier even with an identical score.

### `requirements.txt`

Contains the three dependencies: streamlit, anthropic, and pandas. No other packages are required.

## Supported Startup Types

InstaTier ships with pre-configured ICP profiles for five categories. Selecting your type adjusts the scoring weights automatically so the same lead is evaluated differently depending on whether it is relevant to your product.

| Startup Type | Target Buyer | Best Fit Industries |
|---|---|---|
| HR SaaS | CHRO, VP HR, Head of People, People Ops | SaaS, FinTech, AI/ML, HealthTech |
| FinTech / Payments | CFO, Finance Director, Controller, VP Finance | SaaS, E-commerce, Retail, Manufacturing |
| MarTech / Analytics | CMO, Head of Growth, Demand Gen, VP Marketing | SaaS, MarTech, E-commerce, FinTech |
| Sales Enablement | CRO, VP Sales, RevOps, Sales Director | SaaS, FinTech, AI/ML, MarTech |
| CyberSecurity | CISO, IT Director, Head of Security, CTO | FinTech, HealthTech, SaaS, Cloud |
| Custom ICP | You define the titles and industries | You define the industries |

---

## What the AI Agent Does

The Claude API call is the only intelligent step in the pipeline. Everything else is deterministic Python logic.

When you click Enrich and Score Leads, the app assembles a prompt that includes all uploaded leads formatted as a JSON array. The prompt tells Claude what startup type you selected, what fields to return for each lead, what industry and company size categories to use, and that it must return only valid JSON with no extra text or markdown.

Claude then uses its knowledge of company domains to make inferences. It knows that stripe.com is a FinTech company of Enterprise size. It knows that amplitude.com is an Analytics company of Mid-Market size. It knows that gmail.com is a personal email that indicates an individual contact with unknown company affiliation. For less well-known domains, it reads signals in the domain name itself to make a best guess and assigns a Low confidence rating.

For each lead, Claude returns:

- **company_name**: The full proper name of the company inferred from the domain
- **industry**: One category from the supported list
- **company_size**: Enterprise, Mid-Market, Small Business, Startup, or Individual
- **enrichment_confidence**: High for well-known brands, Medium for recognizable domains, Low for unknown or personal domains
- **fit_reason**: A single sentence explaining why this lead does or does not fit the selected startup type

The entire response for 15 leads comes back in one API call, typically within 10 to 15 seconds, at a cost of approximately half a cent.

---

## ICP Scoring System

After Claude returns the enrichment data, the scoring engine calculates a score from 0 to 100 for every lead using four dimensions. This runs in Python with no additional API cost.

### Dimension 1: Job Seniority (30 points maximum)

This dimension carries the most weight because seniority directly correlates with buying power. A VP can approve a software purchase. An intern cannot.

| Detected Title | Label | Points |
|---|---|---|
| CEO, CTO, CFO, Founder, CHRO, CISO, President | C-Suite or Founder | 28 |
| VP, Vice President, Head of, Director | Senior Leader | 23 |
| Manager, Lead, Principal, Senior, Partner | Mid-Level | 14 |
| Analyst, Associate, Engineer, Consultant | Individual Contributor | 7 |
| No title available | Unknown | 8 |

There is also an ICP Title Match bonus. If the job title directly matches one of the target titles for the selected startup type (for example, "Head of People" for HR SaaS or "CISO" for CyberSecurity), the lead receives the full 30 points and is labeled with an ICP Title Match badge. This rewards leads who are not just senior but specifically the right kind of senior for your product.

### Dimension 2: Company Size (25 points maximum)

Mid-Market companies score the highest because they are large enough to have real budgets but small enough to make purchasing decisions quickly. Enterprise companies score slightly lower because longer sales cycles reduce their immediate conversion value for most early-stage startups.

| Company Size | Points |
|---|---|
| Mid-Market (51 to 999 employees) | 25 |
| Enterprise (1,000 or more employees) | 20 |
| Small Business (11 to 50 employees) | 15 |
| Startup (1 to 10 employees) | 10 |
| Individual or Freelancer | 3 |
| Unknown | 5 |

### Dimension 3: Industry Fit (25 points maximum)

Not all industries are equally likely to buy your product. Each startup type has a defined list of primary industries (strong fit), secondary industries (partial fit), and neutral industries (weak fit).

| Match Level | Points |
|---|---|
| Primary ICP industry | 25 |
| Secondary or adjacent industry | 18 |
| Neutral industry | 10 |
| Unknown or poor fit | 7 |

A Marketing Director at a SaaS company scores 25 points on industry fit for a MarTech startup. The same person at a Manufacturing company scores 10 points.

### Dimension 4: Email Quality (20 points maximum)

A professional domain email is a strong signal that the lead is a real business contact. A personal Gmail or Yahoo address suggests the lead may be a consumer contact, a mis-sourced entry, or someone who did not provide their work email.

| Email Type | Points |
|---|---|
| Professional domain | 14 |
| Personal email (Gmail, Yahoo, Hotmail, etc.) | 2 |
| Invalid or malformed | 0 |

### Final Score Formula

```
ICP Score = Seniority + Company Size + Industry Fit + Email Quality
Maximum possible = 100
```

Example calculation:

```
Lead: Layla Hassan, Marketing Director, l.hassan@hubspot.com
Startup type selected: MarTech / Analytics

Seniority:    "Marketing Director" matches ICP target titles    = 30 pts
Company Size: HubSpot is Enterprise                             = 20 pts
Industry:     hubspot.com = MarTech = primary industry          = 25 pts
Email:        Professional domain                               = 14 pts

Total ICP Score: 89 / 100
```

---

## Priority Tier Assignment

After every lead has a score, tiers are assigned by percentile rank within the uploaded list. This means the tier boundaries shift depending on who is in the list, not on fixed score cutoffs.

| Tier | Percentile | Label | Recommended Action |
|---|---|---|---|
| Top 20% | Highest ranked | HOT | Personal email or phone call this week |
| Next 50% | Middle ranked | WARM | Automated nurture sequence |
| Bottom 30% | Lowest ranked | COLD | Bulk newsletter or remove from list |

The reason for percentile-based tiers rather than fixed cutoffs is that lead quality varies by source. If you upload a highly curated Sales Navigator export, most leads will score above 70. A fixed cutoff of 70 for HOT would label nearly everyone as HOT, which gives the sales team no useful prioritization. Percentile ranking always produces a meaningful top 20% to act on regardless of the overall quality of the list.

---

## Input and Output

### Input

A CSV file with any of the following columns in any order:

| Field | Accepted Column Names |
|---|---|
| Name | name, full name, contact name, lead name |
| Email | email, email address, work email, business email |
| Job Title | title, job title, position, role, current title |
| Company | company, company name, organization, employer |
| Location | location, city, region, country |

The only required column is email. All other columns are optional. If a column is missing, the app fills it with an empty value and scores accordingly.

Compatible sources include LinkedIn Sales Navigator CSV exports, Apollo.io contact exports, HubSpot contact exports, event and webinar registration files, and any spreadsheet saved as CSV.

### Output

The enriched CSV contains all original columns plus the following new columns:

| Column | Description |
|---|---|
| company_name | Full company name inferred from the email domain |
| industry | Classified industry category |
| company_size | Enterprise, Mid-Market, Small Business, Startup, or Individual |
| enrichment_confidence | High, Medium, or Low depending on how well-known the domain is |
| seniority_label | ICP Title Match, C-Suite, Senior Leader, Mid-Level, or Individual Contributor |
| email_quality | Professional, Personal, or Invalid |
| icp_score | Composite score from 0 to 100 |
| priority_tier | HOT, WARM, or COLD |
| fit_reason | One sentence explaining why this lead fits or does not fit the product |

---

## Project Flow

```
User selects startup type
        |
        v
ICP profile loads (target titles, industries, sizes)
        |
        v
User uploads CSV file
        |
        v
Column normalisation maps headers to standard names
        |
        v
All leads sent to Claude in one batched API call
Claude returns: company_name, industry, company_size,
                enrichment_confidence, fit_reason
        |
        v
Python scoring engine runs for each lead:
  score_seniority()     = 0 to 30 points
  score_company_size()  = 0 to 25 points
  score_industry()      = 0 to 25 points
  score_email()         = 0 to 20 points
  Total ICP Score       = 0 to 100
        |
        v
assign_tiers() sorts all leads by score
and assigns HOT / WARM / COLD by percentile
        |
        v
Streamlit renders results:
  Stats bar (total leads, HOT, WARM, COLD, avg score, top score)
  Enriched table with color-coded ICP scores
  Score breakdown expanders for top 5 leads
  Download button for enriched CSV
```

---

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- An Anthropic API key from console.anthropic.com

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/instatier.git
cd instatier
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set your API key

On Mac or Linux:
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

On Windows Command Prompt:
```cmd
set ANTHROPIC_API_KEY=your_api_key_here
```

On Windows PowerShell:
```powershell
$env:ANTHROPIC_API_KEY="your_api_key_here"
```

Never paste your API key directly into any Python file. Always use an environment variable.

### Step 4: Generate a test lead CSV

```bash
# Default: HR SaaS, 15 leads
python generate_leads.py

# Specific startup type
python generate_leads.py --type "MarTech / Analytics" --count 15
python generate_leads.py --type "FinTech / Payments" --count 15
python generate_leads.py --type "Sales Enablement" --count 15
python generate_leads.py --type "CyberSecurity" --count 15

# See all available options
python generate_leads.py --list
```

This creates a file like `leads_martech_analytics_20240411_120000.csv` in your project folder.

### Step 5: Launch the app

```bash
streamlit run app.py
```

If streamlit is not recognized as a command:

```bash
python -m streamlit run app.py
```

The app opens at `http://localhost:8501` in your browser.

### Step 6: Use the app

1. Select your startup type from the dropdown
2. Upload the CSV file you generated in Step 4 or your own LinkedIn export
3. Click Enrich and Score Leads
4. Review the enriched table and score breakdowns for the top leads
5. Download the enriched CSV and import it into your CRM

---

## Token Cost

InstaTier uses one Claude API call per run regardless of how many leads are uploaded. This keeps costs extremely low.

| Leads | API Calls | Estimated Cost |
|---|---|---|
| 15 leads | 1 | approximately $0.005 |
| 20 leads | 1 | approximately $0.008 |
| 50 leads | 1 | approximately $0.020 |

The scoring math runs locally in Python and has no API cost.

---

## Where This Can Be Used

**Startup sales teams** who receive batches of leads from events, referrals, or LinkedIn outreach can run InstaTier before each outreach cycle to rank and prioritize their pipeline automatically.

**SDR teams** who work from large exported lists can use InstaTier to identify the top 20% worth a personal touch versus the leads that go into an automated sequence.

**Founders doing outbound** can upload a scraped or purchased list and immediately know who is worth writing a personalized email to this week.

**Marketing operations** can pre-score all inbound form submissions before routing them to the sales team, so reps only receive leads above a minimum threshold.

**Portfolio demonstration** for data analysts and AI engineers who want to show end-to-end pipeline thinking, prompt engineering, Streamlit UI development, and business domain knowledge in a single working product.

---

## Limitations

Claude infers firmographics from its training knowledge, not from a live database. Very new companies, recently rebranded companies, or highly niche businesses may receive a Low confidence rating. The enrichment is most accurate for well-known companies with recognizable domains.

The app is designed for lists of up to 50 leads per run to keep response time under 20 seconds and cost under $0.02. Larger lists can be split into batches.

Industry classification uses 17 predefined categories. Companies in very niche industries may be classified as Unknown.

The app does not scrape LinkedIn or any other platform. It works entirely from data the user provides in their uploaded CSV.

---

## Security

The only sensitive value in this project is the Anthropic API key. It is read from an environment variable at runtime and never written to any file. The sample CSV files contain fictional lead data and are safe to commit and share publicly. All lead processing happens in memory for the duration of the Streamlit session and is discarded when the session ends.

---

## Tech Stack

| Layer | Technology |
|---|---|
| User interface | Streamlit |
| AI enrichment | Anthropic Claude API |
| Data processing | Pandas |
| Scoring engine | Python |
| Lead generation | Python standard library |

---

## Author

Built by Aakash Bhanushali
