# In the success page section, replace the download code with:

else:
    display_logo()
    st.title("🎉 Your Guide is Ready!")
    
    # Get PDF content properly
    try:
        pdf_content = requests.get(PDF_URL, allow_redirects=True).content
    except Exception as e:
        st.error(f"Failed to load PDF: {str(e)}")
        st.stop()
    
    # Download button with verified content
    st.download_button(
        label="Download Guide Now",
        data=pdf_content,
        file_name=PDF_FILENAME,
        mime="application/pdf"
    )
    
    st.markdown("""
    **Next Steps:**
    - Expect contact within 48 hours
    - Save our details:  
      📧 talent@stirlingqr.com  
      📞 UK: +44 1293 307 201  
      📞 US: +1 415 808 5554
    """)
