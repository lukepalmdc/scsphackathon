import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import fitz  # PyMuPDF
import json
from openai import OpenAI
import tempfile
import speech_recognition as sr
from st_audiorec import st_audiorec

# --- Set your OpenAI API Key ---
client = OpenAI(api_key="your-api-key-here")

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Supply Chain Risk Dashboard", layout="wide")

# --- Tabs ---
tab1, tab2 = st.tabs(["Risk Dashboard", "Chatbot"])

# --- Tab 1: Risk Dashboard ---
with tab1:
    st.title("Supply Chain Risk Dashboard")
    st.markdown("Select a commodity and year to view the top risk countries.")

    commodity = st.selectbox("Choose Commodity", [
        "Semiconductors", "Rare Earth Metals", "Petroleum", "Fertilizers", "Wheat"
    ])

    year = st.selectbox("Select Year", list(range(2015, 2024)))
    top_n = st.slider("Number of Top Risky Countries", min_value=1, max_value=10, value=3)

    if st.button("Get Risk Data"):
        with st.spinner("Fetching data..."):
            response = requests.get(
                f"{API_URL}/top-risk-countries/",
                params={"commodity": commodity, "year": year, "top_n": top_n}
            )
            if response.status_code == 200:
                data = response.json()
                top_risks = pd.DataFrame(data["top_risks"])
                st.success(f"Top {top_n} Risky Countries for {commodity} in {year}")
                st.dataframe(top_risks)

                fig = px.bar(top_risks, x="Country", y="RiskPercentage",
                             title=f"Top {top_n} Risky Countries ({commodity}, {year})",
                             labels={"RiskPercentage": "Risk (%)"},
                             color="RiskPercentage", color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("No data found or API error.")

# --- Tab 2: Chatbot ---
with tab2:
    st.title("🤖 Chat with RiskBot")

    option = st.radio("Choose input method:", ["Ask a Question", "Upload a PDF", "Voice Query"])

    def handle_risk_fetch(commodity, year, title_prefix="", only_political=True):
        res = requests.get(
            f"{API_URL}/risk-score/",
            params={"commodity": commodity, "year": year, "only_political": only_political}
        )
        if res.status_code == 200:
            risk_data = pd.DataFrame(res.json()["all_countries"])
            st.dataframe(risk_data)
            fig = px.bar(risk_data.head(10), x="Country", y="RiskPercentage",
                         title=f"{title_prefix}{commodity} ({year})",
                         labels={"RiskPercentage": "Political Risk (%)"},
                         color="RiskPercentage", color_continuous_scale="OrRd")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Risk data not found for extracted parameters.")


    if option == "Ask a Question":
        user_query = st.text_area("Enter your question:")

        if st.button("Ask"):
            if not user_query.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Thinking..."):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": (
                                    "You are a helpful assistant for supply chain risk analysis. "
                                    "If the user asks about commodities or years, try to extract a JSON with keys 'commodity' and 'year'. "
                                    "Otherwise, answer their question normally.")},
                                {"role": "user", "content": user_query}
                            ]
                        )

                        answer = response.choices[0].message.content
                        st.markdown("### 🤖 Response")
                        st.markdown(answer)

                        # Try parsing JSON if present
                        try:
                            result = json.loads(answer)
                            if "commodity" in result and "year" in result:
                                st.info(f"Detected Commodity: {result['commodity']} | Year: {result['year']}")
                                handle_risk_fetch(result['commodity'], int(result['year']),
                                                  title_prefix="Top Risk Countries by Political Risk: ")
                        except json.JSONDecodeError:
                            pass

                    except Exception as e:
                        st.error(f"Error: {str(e)}")


    elif option == "Upload a PDF":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            with st.spinner("Extracting text from PDF..."):
                pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = "".join(page.get_text() for page in pdf)

            st.text_area("Extracted Text (Preview)", full_text[:1000], height=200)

            if st.button("Analyze PDF"):
                with st.spinner("Analyzing..."):
                    try:
                        prompt = f"""
You are a supply chain expert. A user has uploaded a document. Extract the commodity type and year mentioned in the document. 
Return only a JSON with keys 'commodity' and 'year'.
Text: {full_text[:3000]}
                        """
                        chat_response = client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "You extract commodity and year from documents."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        content = chat_response.choices[0].message.content
                        st.markdown("**ChatGPT Response:**")
                        st.code(content, language="json")

                        result = json.loads(content)
                        handle_risk_fetch(result["commodity"], int(result["year"]), title_prefix="Risk Report: ")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    elif option == "Voice Query":
        st.subheader("🎤 Speak Your Query")

        wav_audio_data = st_audiorec()

        if wav_audio_data is not None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(wav_audio_data)
                file_path = f.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(file_path) as source:
                audio = recognizer.record(source)

            try:
                transcript = recognizer.recognize_google(audio)
                st.success(f"Transcribed: {transcript}")

                if st.button("Ask from Voice"):
                    with st.spinner("Thinking..."):
                        response = client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "You answer supply chain risk questions. Extract commodity and year if available and return JSON."},
                                {"role": "user", "content": transcript}
                            ]
                        )
                        content = response.choices[0].message.content
                        st.markdown("### 🤖 Response")
                        st.markdown(content)

                        try:
                            result = json.loads(content)
                            handle_risk_fetch(result["commodity"], int(result["year"]), title_prefix="Voice Risk Report: ")
                        except json.JSONDecodeError:
                            pass

            except Exception as e:
                st.error(f"Voice recognition error: {e}")
