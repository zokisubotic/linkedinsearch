# app.py
import streamlit as st
from ddgs import DDGS
import json, csv, time

st.title("LinkedIn Search Tool")
query = st.text_input("Search query:(ex: ('Owner' OR 'CEO' OR 'Managing Director' OR 'Founder') ('Logistics' OR 'Transport' OR 'Supply Chain' OR 'Warehousing') ('Rotterdam' OR 'Amsterdam' OR 'Eindhoven' OR 'Den Haag' OR 'Utrecht') Netherlands)")
site = st.text_input("Site filter (e.g., linkedin.com/in):", "linkedin.com/in")
max_results = st.number_input("Max results", 10, 500, 100, 10)
page_size = st.number_input("Results per page", 5, 50, 10, 5)
delay = st.number_input("Delay between pages (seconds)", 0.5, 10.0, 1.5, 0.5)

if st.button("Run Search"):
    full_query = f"{query} site:{site}"
    all_results = []
    offset = 0
    progress = st.progress(0)

    with DDGS() as ddgs_client:
        while len(all_results) < max_results:
            # Note: Cloud Run exposes the port 8080 to your container,
            # but Streamlit needs to be bound to 0.0.0.0 for external access.
            # The ddgs library is independent of the port setting.
            
            results = list(ddgs_client.text(full_query, max_results=page_size, s=offset))
            
            if not results:
                break
            all_results.extend(results)
            offset += page_size
            
            # Update progress bar
            progress.progress(min(len(all_results)/max_results, 1.0))
            time.sleep(delay)

    # Extract LinkedIn profiles
    profiles = [
        {
            "name_and_title": r.get("title",""),
            "linkedin_url": r.get("href",""),
            "search_snippet": r.get("body","")
        }
        for r in all_results if "linkedin.com/in/" in r.get("href","")
    ]

    st.success(f"Found {len(profiles)} LinkedIn profiles.")
    
    # Download buttons
    st.download_button("Download JSON", json.dumps(profiles, indent=2), "results.json", "application/json")
    csv_data = "name_and_title,linkedin_url,search_snippet\n" + "\n".join(
        [f'"{p["name_and_title"]}","{p["linkedin_url"]}","{p["search_snippet"]}"' for p in profiles]
    )
    st.download_button("Download CSV", csv_data, "results.csv", "text/csv")
