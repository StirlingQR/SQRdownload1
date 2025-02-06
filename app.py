# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from urllib.parse import quote
import random
import requests

# Configure page
st.set_page_config(
    page_title="Stirling Q&R Lead Generation",
    page_icon="📈",
    layout="centered"
)

# GitHub configuration
GITHUB_USER = "StirlingQR"
REPO_NAME = "SQRdownload1"  # Changed from "Lead-Gen"
BRANCH = "main"
PDF_FILENAME = "Why Job Adverts Fail.pdf"  # Verify exact filename matches your repo
ENCODED_FILENAME = quote(PDF_FILENAME)
PDF_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{ENCODED_FILENAME}"

# Session state setup
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'captcha' not in st.session_state:
    st.session_state.captcha = {'num1': random.randint(1,9), 'num2': random.randint(1,9)}

# Custom styles
st.markdown("""
<style>
    .logo-container {
        text-align: center;
        margin: 1rem 0;
    }
    .logo-img {
        width: 180px;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

def display_logo():
    try:
        st.markdown("""
        <div class="logo-container">
            <img class="logo-img" src="https://raw.githubusercontent.com/StirlingQR/Lead-Gen/main/Stirling_QR_Logo.png">
        </div>
        """, unsafe_allow_html=True)
    except:
        st.error("Error loading logo")

# Persistent admin button
admin_col, _ = st.columns([1, 5])
with admin_col:
    if st.session_state.logged_in:
        if st.button("Logout", key="logout-btn"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        if st.button("Admin Login", key="admin-btn"):
            st.session_state.show_login = True

# Login form
if 'show_login' in st.session_state and st.session_state.show_login:
    with st.form("Admin Login"):
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Authenticate"):
            if username == "chris@stirlingqr.com" and password == "Measure897!":
                st.session_state.logged_in = True
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("Invalid credentials")

if st.session_state.logged_in:
    st.title("🔐 Leads Dashboard")
    try:
        leads_df = pd.read_csv("leads.csv")
        
        # Delete functionality
        st.markdown("### Current Leads")
        for index, row in leads_df.iterrows():
            cols = st.columns([5,4,4,2,1])
            with cols[0]: st.write(row['Name'])
            with cols[1]: st.write(row['Email'])
            with cols[2]: st.write(row['Phone'])
            with cols[3]: 
                contacted = st.checkbox("Contacted", value=row.get('Contacted', False), 
                                      key=f"contacted_{index}")
                if contacted != row.get('Contacted', False):
                    leads_df.at[index, 'Contacted'] = contacted
            with cols[4]: 
                if st.button("❌", key=f"del_{index}"):
                    leads_df = leads_df.drop(index)
                    leads_df.to_csv("leads.csv", index=False)
                    st.rerun()
        
        # Save changes
        if st.button("Save All Changes"):
            leads_df.to_csv("leads.csv", index=False)
            st.success("Changes saved!")
            
        # Export
        st.download_button("Export CSV", data=leads_df.to_csv(index=False), 
                         file_name="stirling_leads.csv")
            
    except FileNotFoundError:
        st.warning("No leads collected yet")
    st.stop()

# Main Form
if not st.session_state.submitted:
    display_logo()
    st.title("Download Why Job Adverts Fail Guide")
    
    with st.form("lead_form", clear_on_submit=True):
        name = st.text_input("Full Name*")
        email = st.text_input("Email*")
        phone = st.text_input("Phone Number*")
        company = st.text_input("Company Name (optional)")
        
        # CAPTCHA
        st.markdown(f"**CAPTCHA:** What is {st.session_state.captcha['num1']} + {st.session_state.captcha['num2']}?")
        captcha_answer = st.number_input("Answer", step=1)
        
        submitted = st.form_submit_button("Get Your Copy Now →")
        
        if submitted:
            valid_captcha = (captcha_answer == st.session_state.captcha['num1'] + st.session_state.captcha['num2'])
            if valid_captcha:
                new_lead = pd.DataFrame({
                    "Name": [name],
                    "Email": [email],
                    "Phone": [phone.replace(" ", "")],
                    "Company": [company],
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Contacted": False
                })
                
                try:
                    existing = pd.read_csv("leads.csv")
                    updated = pd.concat([existing, new_lead])
                except FileNotFoundError:
                    updated = new_lead
                
                updated.to_csv("leads.csv", index=False)
                st.session_state.submitted = True
                st.session_state.captcha = {'num1': random.randint(1,9), 'num2': random.randint(1,9)}
                st.rerun()

# Success Page
else:
    display_logo()
    st.title("🎉 Your Guide is Ready!")
    
    # Get PDF content with verification
    try:
        response = requests.get(PDF_URL, allow_redirects=True)
        response.raise_for_status()  # Check for HTTP errors
        
        # Verify PDF magic number
        if not response.content.startswith(b'%PDF-'):
            st.error("Invalid PDF file detected")
            st.stop()
            
        st.download_button(
            label="Download Guide Now",
            data=response.content,
            file_name=PDF_FILENAME,
            mime="application/pdf"
        )
        
    except requests.RequestException as e:
        st.error(f"Download failed: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
    
    st.markdown("""
    **Next Steps:**
    - Expect contact within 48 hours
    - Save our details:  
      📧 talent@stirlingqr.com  
      📞 UK: +44 1293 307 201  
      📞 US: +1 415 808 5554
    """)
