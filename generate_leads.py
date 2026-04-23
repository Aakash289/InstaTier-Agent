"""
generate_leads.py
─────────────────
Generates a realistic lead CSV that mimics a LinkedIn / Sales Navigator export.
Run this first, then upload the output CSV into the LeadLens app.

Usage:
    python generate_leads.py                     # defaults to HR SaaS, 15 leads
    python generate_leads.py --type "FinTech / Payments" --count 15
    python generate_leads.py --type "MarTech / Analytics" --count 20
    python generate_leads.py --list              # show all available startup types

Available startup types:
    HR SaaS
    FinTech / Payments
    MarTech / Analytics
    Sales Enablement
    CyberSecurity
"""

import csv
import random
import argparse
import os
from datetime import datetime

# ── Lead pools per startup type ───────────────────────────────────────────────
# Each pool has strong leads (ICP match), weak leads, and noise (personal emails)
# so the scoring in the app feels realistic and differentiated.

LEAD_POOLS = {

    "HR SaaS": [
        # ── Strong ICP leads (HR titles, tech companies) ──
        {"name": "Rachel Kim",       "email": "rachel.kim@rippling.com",      "title": "Chief People Officer",      "company": "Rippling",           "location": "San Francisco, CA"},
        {"name": "James Okafor",     "email": "j.okafor@lattice.com",         "title": "VP of People Operations",  "company": "Lattice",            "location": "New York, NY"},
        {"name": "Priya Menon",      "email": "priya.menon@gusto.com",        "title": "Head of HR",               "company": "Gusto",              "location": "Denver, CO"},
        {"name": "Daniel Thornton",  "email": "dthornton@deel.com",           "title": "Director of People Ops",   "company": "Deel",               "location": "Austin, TX"},
        {"name": "Sofia Reyes",      "email": "sofia.reyes@greenhouse.io",    "title": "CHRO",                     "company": "Greenhouse",         "location": "Chicago, IL"},
        # ── Secondary / adjacent leads ──
        {"name": "Marcus Webb",      "email": "mwebb@hubspot.com",            "title": "Talent Acquisition Lead",  "company": "HubSpot",            "location": "Boston, MA"},
        {"name": "Nina Patel",       "email": "nina.p@stripe.com",            "title": "HR Business Partner",      "company": "Stripe",             "location": "Seattle, WA"},
        {"name": "Leo Huang",        "email": "leo.huang@notion.so",          "title": "People Operations Manager","company": "Notion",             "location": "Los Angeles, CA"},
        {"name": "Aisha Osei",       "email": "aisha@databricks.com",         "title": "Senior Recruiter",         "company": "Databricks",         "location": "San Francisco, CA"},
        {"name": "Tom Bridger",      "email": "t.bridger@shopify.com",        "title": "Compensation Analyst",     "company": "Shopify",            "location": "Toronto, Canada"},
        # ── Weak / noise leads ──
        {"name": "Kevin Mills",      "email": "kevin.mills@deloitte.com",     "title": "Management Consultant",    "company": "Deloitte",           "location": "Dallas, TX"},
        {"name": "Sarah Johansson",  "email": "sarah.j@gmail.com",            "title": "",                         "company": "",                   "location": ""},
        {"name": "Robert Finch",     "email": "rfinch@yahoo.com",             "title": "HR Manager",               "company": "",                   "location": "Phoenix, AZ"},
        {"name": "Claire Dupont",    "email": "claire.dupont@mckinsey.com",   "title": "Associate",                "company": "McKinsey & Company", "location": "Paris, France"},
        {"name": "Raj Nair",         "email": "raj.nair@tinyhr.io",           "title": "Founder",                  "company": "TinyHR",             "location": "Remote"},
    ],

    "FinTech / Payments": [
        # ── Strong ICP leads ──
        {"name": "Amanda Torres",    "email": "a.torres@brex.com",            "title": "CFO",                      "company": "Brex",               "location": "San Francisco, CA"},
        {"name": "Michael Chang",    "email": "m.chang@ramp.com",             "title": "VP of Finance",            "company": "Ramp",               "location": "New York, NY"},
        {"name": "Fatima Al-Rashid", "email": "fatima@mercoa.com",            "title": "Head of Finance Ops",      "company": "Mercoa",             "location": "Los Angeles, CA"},
        {"name": "James Okonkwo",    "email": "j.okonkwo@stripe.com",         "title": "Finance Director",         "company": "Stripe",             "location": "Dublin, Ireland"},
        {"name": "Lisa Chen",        "email": "lchen@plaid.com",              "title": "Controller",               "company": "Plaid",              "location": "San Francisco, CA"},
        # ── Secondary leads ──
        {"name": "David Reyes",      "email": "d.reyes@shopify.com",          "title": "Treasury Manager",         "company": "Shopify",            "location": "Ottawa, Canada"},
        {"name": "Sandra Mills",     "email": "smills@wayfair.com",           "title": "VP Accounting",            "company": "Wayfair",            "location": "Boston, MA"},
        {"name": "Tom Nakamura",     "email": "t.nakamura@doordash.com",      "title": "Senior Finance Analyst",   "company": "DoorDash",           "location": "San Francisco, CA"},
        {"name": "Priya Agarwal",    "email": "p.agarwal@coinbase.com",       "title": "Financial Operations Lead","company": "Coinbase",           "location": "Remote"},
        {"name": "Carlos Ruiz",      "email": "c.ruiz@paypal.com",            "title": "Finance Business Partner", "company": "PayPal",             "location": "Austin, TX"},
        # ── Noise ──
        {"name": "Mark Johnson",     "email": "markj@hotmail.com",            "title": "",                         "company": "",                   "location": ""},
        {"name": "Helen Walker",     "email": "h.walker@kpmg.com",            "title": "Senior Auditor",           "company": "KPMG",               "location": "Chicago, IL"},
        {"name": "Dan Park",         "email": "dan@gmail.com",                "title": "Accountant",               "company": "",                   "location": ""},
        {"name": "Grace Liu",        "email": "grace.liu@accenture.com",      "title": "Strategy Consultant",      "company": "Accenture",          "location": "New York, NY"},
        {"name": "Omar Hassan",      "email": "omar@tinyledger.io",           "title": "CEO",                      "company": "TinyLedger",         "location": "Remote"},
    ],

    "MarTech / Analytics": [
        # ── Strong ICP leads ──
        {"name": "Vanessa Ortiz",    "email": "v.ortiz@segment.com",          "title": "CMO",                      "company": "Segment (Twilio)",   "location": "San Francisco, CA"},
        {"name": "Brian Nakamura",   "email": "b.nakamura@klaviyo.com",       "title": "VP of Marketing",          "company": "Klaviyo",            "location": "Boston, MA"},
        {"name": "Zoe Adamson",      "email": "z.adamson@amplitude.com",      "title": "Head of Growth",           "company": "Amplitude",          "location": "San Francisco, CA"},
        {"name": "Ethan Cole",       "email": "ethan.cole@mixpanel.com",      "title": "Director of Demand Gen",   "company": "Mixpanel",           "location": "San Francisco, CA"},
        {"name": "Layla Hassan",     "email": "l.hassan@hubspot.com",         "title": "Marketing Director",       "company": "HubSpot",            "location": "Cambridge, MA"},
        # ── Secondary leads ──
        {"name": "Ryan Choi",        "email": "rchoi@shopify.com",            "title": "Growth Manager",           "company": "Shopify",            "location": "Ottawa, Canada"},
        {"name": "Anna Schultz",     "email": "a.schultz@canva.com",          "title": "Performance Marketing Lead","company": "Canva",             "location": "Sydney, Australia"},
        {"name": "Marcus Bell",      "email": "m.bell@figma.com",             "title": "Marketing Operations",     "company": "Figma",              "location": "San Francisco, CA"},
        {"name": "Nina Rossi",       "email": "nina.rossi@notion.so",         "title": "Content Marketing Manager","company": "Notion",             "location": "New York, NY"},
        {"name": "Jake Torres",      "email": "j.torres@stripe.com",          "title": "SEO Lead",                 "company": "Stripe",             "location": "Remote"},
        # ── Noise ──
        {"name": "Phil Watson",      "email": "philwatson@gmail.com",         "title": "",                         "company": "",                   "location": ""},
        {"name": "Sandra Gomez",     "email": "sgomez@yahoo.com",             "title": "Social Media Manager",     "company": "",                   "location": ""},
        {"name": "Chris Leung",      "email": "c.leung@pwc.com",              "title": "Digital Strategist",       "company": "PwC",                "location": "Chicago, IL"},
        {"name": "Monica Ray",       "email": "m.ray@deloittedigital.com",    "title": "UX Consultant",            "company": "Deloitte Digital",   "location": "New York, NY"},
        {"name": "Sam Obi",          "email": "sam@growthhackr.io",           "title": "Founder",                  "company": "GrowthHackr",        "location": "Remote"},
    ],

    "Sales Enablement": [
        # ── Strong ICP leads ──
        {"name": "Carter Flynn",     "email": "c.flynn@gong.io",              "title": "CRO",                      "company": "Gong",               "location": "San Francisco, CA"},
        {"name": "Diana Okafor",     "email": "d.okafor@outreach.io",         "title": "VP of Sales",              "company": "Outreach",           "location": "Seattle, WA"},
        {"name": "Raj Kapoor",       "email": "r.kapoor@salesloft.com",       "title": "Head of Revenue",          "company": "Salesloft",          "location": "Atlanta, GA"},
        {"name": "Mia Torres",       "email": "m.torres@apollo.io",           "title": "Director of Sales Ops",    "company": "Apollo.io",          "location": "Remote"},
        {"name": "Ben Wheeler",      "email": "b.wheeler@hubspot.com",        "title": "Revenue Operations Lead",  "company": "HubSpot",            "location": "Boston, MA"},
        # ── Secondary leads ──
        {"name": "Lily Zhang",       "email": "l.zhang@salesforce.com",       "title": "Senior AE",                "company": "Salesforce",         "location": "San Francisco, CA"},
        {"name": "Jake Morrison",    "email": "j.morrison@zendesk.com",       "title": "Sales Director",           "company": "Zendesk",            "location": "San Francisco, CA"},
        {"name": "Amy Nguyen",       "email": "a.nguyen@intercom.com",        "title": "VP Sales APAC",            "company": "Intercom",           "location": "Singapore"},
        {"name": "Tom Walsh",        "email": "t.walsh@drift.com",            "title": "SDR Manager",              "company": "Drift",              "location": "Boston, MA"},
        {"name": "Paula Mercer",     "email": "p.mercer@clearbit.com",        "title": "RevOps Analyst",           "company": "Clearbit",           "location": "Remote"},
        # ── Noise ──
        {"name": "Gary White",       "email": "garywhite@hotmail.com",        "title": "",                         "company": "",                   "location": ""},
        {"name": "Diane Ross",       "email": "d.ross@gmail.com",             "title": "Sales Rep",                "company": "",                   "location": ""},
        {"name": "Henry Liu",        "email": "h.liu@pwc.com",                "title": "Business Analyst",         "company": "PwC",                "location": "Chicago, IL"},
        {"name": "Kim Nakamura",     "email": "kim.n@accenture.com",          "title": "Strategy Consultant",      "company": "Accenture",          "location": "Tokyo, Japan"},
        {"name": "Olu Benson",       "email": "olu@tinysales.io",             "title": "Co-founder",               "company": "TinySales",          "location": "Lagos, Nigeria"},
    ],

    "CyberSecurity": [
        # ── Strong ICP leads ──
        {"name": "Victor Crane",     "email": "v.crane@crowdstrike.com",      "title": "CISO",                     "company": "CrowdStrike",        "location": "Austin, TX"},
        {"name": "Alicia Stern",     "email": "a.stern@paloaltonetworks.com", "title": "VP of Security Engineering","company": "Palo Alto Networks", "location": "Santa Clara, CA"},
        {"name": "Kwame Asante",     "email": "k.asante@sentinelone.com",     "title": "Head of Security Ops",     "company": "SentinelOne",        "location": "Mountain View, CA"},
        {"name": "Yuki Tanaka",      "email": "y.tanaka@okta.com",            "title": "IT Director",              "company": "Okta",               "location": "San Francisco, CA"},
        {"name": "Brooke Walters",   "email": "b.walters@zscaler.com",        "title": "Director of Infosec",      "company": "Zscaler",            "location": "San Jose, CA"},
        # ── Secondary leads ──
        {"name": "Ian McGregor",     "email": "i.mcgregor@microsoft.com",     "title": "Security Architect",       "company": "Microsoft",          "location": "Redmond, WA"},
        {"name": "Rosa Delgado",     "email": "r.delgado@ibm.com",            "title": "Cybersecurity Consultant", "company": "IBM",                "location": "New York, NY"},
        {"name": "Finn O'Neill",     "email": "f.oneill@unitedhealth.com",    "title": "VP IT Infrastructure",     "company": "UnitedHealth Group", "location": "Minneapolis, MN"},
        {"name": "Zara Ahmed",       "email": "z.ahmed@jpmorgan.com",         "title": "Head of Cyber Risk",       "company": "JPMorgan Chase",     "location": "New York, NY"},
        {"name": "Lucas Park",       "email": "l.park@deloitte.com",          "title": "Security Risk Consultant", "company": "Deloitte",           "location": "Washington, DC"},
        # ── Noise ──
        {"name": "Bob Singh",        "email": "bobsingh@gmail.com",           "title": "",                         "company": "",                   "location": ""},
        {"name": "Tara Miles",       "email": "tara.miles@yahoo.com",         "title": "IT Support",               "company": "",                   "location": ""},
        {"name": "Nate Fox",         "email": "n.fox@kpmg.com",               "title": "Risk Analyst",             "company": "KPMG",               "location": "Chicago, IL"},
        {"name": "Jade Wu",          "email": "jade.wu@accenture.com",        "title": "Cloud Consultant",         "company": "Accenture",          "location": "Singapore"},
        {"name": "Omar Diallo",      "email": "omar@tinysec.io",              "title": "Founder & CEO",            "company": "TinySec",            "location": "Remote"},
    ],
}

STARTUP_TYPES = list(LEAD_POOLS.keys())


def generate_csv(startup_type: str, count: int, output_path: str):
    pool = LEAD_POOLS[startup_type]

    # Fixed seed = same order every run → consistent scoring in the app
    random.seed(42)
    shuffled = pool[:10]
    noise    = pool[10:]
    random.shuffle(shuffled)
    random.shuffle(noise)

    leads = (shuffled + noise)[:count]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name","email","title","company","location"])
        writer.writeheader()
        writer.writerows(leads)

    print(f"\n✅  Generated {len(leads)} leads → {output_path}")
    print(f"   Startup type : {startup_type}")
    print(f"   Strong leads : ~{min(count, 10)} (real companies, real titles)")
    print(f"   Noise leads  : ~{max(0, count - 10)} (personal emails, missing data)")
    print(f"\n👉  Upload this file into the LeadLens app to run enrichment & scoring.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a realistic B2B lead CSV for the LeadLens app."
    )
    parser.add_argument(
        "--type", "-t",
        type=str,
        default="HR SaaS",
        help=f"Startup type. Options: {', '.join(STARTUP_TYPES)}"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=15,
        help="Number of leads to generate (max 15, default 15)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (default: leads_<type>_<timestamp>.csv)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available startup types and exit"
    )
    args = parser.parse_args()

    if args.list:
        print("\nAvailable startup types:")
        for t in STARTUP_TYPES:
            print(f"  · {t}")
        print()
        return

    # Validate type
    if args.type not in LEAD_POOLS:
        close = [t for t in STARTUP_TYPES if args.type.lower() in t.lower()]
        if close:
            print(f"\n⚠️  '{args.type}' not found. Did you mean: {close[0]}?")
            print(f"   Run with --list to see all options.\n")
        else:
            print(f"\n❌  Unknown startup type: '{args.type}'")
            print(f"   Available: {', '.join(STARTUP_TYPES)}\n")
        return

    # Clamp count
    count = max(5, min(args.count, 15))
    if count != args.count:
        print(f"⚠️  Count clamped to {count} (range: 5–15)")

    # Output path
    if args.output:
        output_path = args.output
    else:
        ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug  = args.type.lower().replace(" ","_").replace("/","").replace("__","_")
        output_path = f"leads_{slug}_{ts}.csv"

    generate_csv(args.type, count, output_path)


if __name__ == "__main__":
    main()
