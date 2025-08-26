import streamlit as st

# --- Helper functions ---
def q(term: str) -> str:
    t = term.strip()
    if any(c in t for c in ' -"()|'):
        return f'"{t}"'
    return t

def or_group(terms):
    terms = [q(t) for t in terms if t.strip()]
    if not terms:
        return ""
    return "(" + " OR ".join(terms) + ")" if len(terms) > 1 else terms[0]

def and_join(chunks):
    return " AND ".join([c for c in chunks if c])

def not_group(terms):
    terms = [q(t) for t in terms if t.strip()]
    if not terms:
        return ""
    return "-" + " -".join(terms)

def intitle_group(terms):
    if not terms:
        return ""
    return "(" + " OR ".join([f'intitle:{q(t)}' for t in terms]) + ")"

def site_group(sites):
    if not sites:
        return ""
    return "(" + " OR ".join([f"site:{s.strip()}" for s in sites if s.strip()]) + ")"

# --- Builders ---
def build_generic(cfg):
    chunks = [
        or_group(cfg["must_have"]),
        or_group(cfg["titles"]),
        or_group(cfg["companies"]),
        or_group(cfg["locations"]),
        or_group(cfg["phrases"])
    ]
    s = and_join(chunks)
    neg = not_group(cfg["exclude"])
    return f"{s} {neg}".strip()

def build_google(cfg):
    chunks = [
        site_group(cfg["sites"]),
        or_group(cfg["must_have"]),
        intitle_group(cfg["titles"]),
        or_group(cfg["companies"]),
        or_group(cfg["locations"]),
        or_group(cfg["phrases"])
    ]
    s = and_join(chunks)
    neg = not_group(cfg["exclude"])
    return f"{s} {neg}".strip()

def build_linkedin(cfg):
    chunks = [
        "site:linkedin.com/in",
        intitle_group(cfg["titles"]),
        or_group(cfg["must_have"]),
        or_group(cfg["companies"]),
        or_group(cfg["locations"]),
        or_group(cfg["phrases"])
    ]
    s = and_join(chunks)
    neg = not_group(cfg["exclude"])
    return f"{s} {neg}".strip()

def build_github(cfg):
    chunks = [
        "site:github.com",
        or_group(cfg["must_have"]),
        or_group(cfg["titles"]),
        or_group(cfg["companies"]),
        or_group(cfg["locations"])
    ]
    s = and_join(chunks)
    neg = not_group(cfg["exclude"])
    return f"{s} {neg}".strip()

# --- Streamlit UI ---
st.set_page_config(page_title="Boolean Search Builder", layout="wide")
st.title("🔍 Automated Boolean Search Builder")

with st.sidebar:
    st.header("⚙️ Input Parameters")
    role = st.text_input("Role / Job Title", "Battery Engineer")
    must_have = st.text_area("Must-have Keywords (comma separated)", "battery, BMS, lithium-ion, cell*, pack").split(",")
    titles = st.text_area("Job Titles (comma separated)", "Battery Engineer, BMS Engineer, Energy Storage Engineer").split(",")
    companies = st.text_area("Target Companies (comma separated)", "Caterpillar, CAT").split(",")
    locations = st.text_area("Locations (comma separated)", "India, Bengaluru, Pune").split(",")
    phrases = st.text_area("Exact Phrases (comma separated)", "open to work, seeking opportunities").split(",")
    sites = st.text_area("Sites for Google search (comma separated)", "linkedin.com/in, github.com").split(",")
    exclude = st.text_area("Exclude Keywords (comma separated)", "intern, sales, manager").split(",")

# Build config
data = {
    "role": role,
    "must_have": must_have,
    "titles": titles,
    "companies": companies,
    "locations": locations,
    "phrases": phrases,
    "sites": sites,
    "exclude": exclude
}

# Generate queries
results = {
    "Generic (ATS)": build_generic(data),
    "Google (multi-site)": build_google(data),
    "LinkedIn X-Ray": build_linkedin(data),
    "GitHub X-Ray": build_github(data)
}

# Display outputs
for k, v in results.items():
    st.subheader(k)
    st.code(v, language="text")

# Optional download
import pandas as pd
csv = pd.DataFrame([[k, v] for k, v in results.items()], columns=["Channel", "Query"]).to_csv(index=False)
st.download_button("⬇️ Download CSV", data=csv, file_name="boolean_searches.csv", mime="text/csv")