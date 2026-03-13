import streamlit as st
import pandas as pd
import plotly.express as px
import PyPDF2
import requests
import json
import os

st.set_page_config(page_title="AI Productivity Suite", layout="wide")

OLLAMA_URL="http://localhost:11434/api/generate"
MODEL="phi3"

USERS_FILE="users.json"

# ---------- UI STYLE ----------

st.markdown("""
<style>

body{
background:#0f172a;
color:white;
}

.main-title{
font-size:36px;
font-weight:bold;
text-align:center;
margin-bottom:20px;
}

.chat-user{
background:#2563eb;
padding:10px;
border-radius:8px;
margin-bottom:6px;
color:white;
}

.chat-ai{
background:#1e293b;
padding:10px;
border-radius:8px;
margin-bottom:6px;
color:white;
}

.sidebar-section{
margin-bottom:20px;
}

</style>
""",unsafe_allow_html=True)

st.markdown("<div class='main-title'>AI Productivity Suite</div>",unsafe_allow_html=True)

# ---------- USER STORAGE ----------

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE,"r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USERS_FILE,"w") as f:
        json.dump(data,f,indent=2)

users=load_users()

# ---------- AI FUNCTION ----------

def ask_ai(prompt):

    payload={
        "model":MODEL,
        "prompt":prompt,
        "stream":False,
        "options":{
            "temperature":0.4,
            "num_predict":1200
        }
    }

    try:

        r=requests.post(OLLAMA_URL,json=payload)

        return r.json()["response"]

    except Exception as e:

        return f"⚠️ AI Error: {str(e)}"

# ---------- SESSION ----------

if "logged" not in st.session_state:
    st.session_state.logged=False

if "user" not in st.session_state:
    st.session_state.user=""

if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]

# ---------- AUTH ----------

def auth():

    st.header("Login / Signup")

    option=st.radio("Select",["Sign In","Sign Up"])

    username=st.text_input("Username")

    password=st.text_input("Password",type="password")

    if option=="Sign In":

        if st.button("Login"):

            if username in users and users[username]==password:

                st.session_state.logged=True
                st.session_state.user=username
                st.rerun()

            else:

                st.error("Invalid credentials")

    else:

        if st.button("Create Account"):

            if username in users:

                st.error("User exists")

            else:

                users[username]=password
                save_users(users)

                st.success("Account created")

if not st.session_state.logged:

    auth()
    st.stop()

# ---------- SIDEBAR ----------

st.sidebar.title("Navigation")

st.sidebar.write("User:",st.session_state.user)

if st.sidebar.button("Logout"):
    st.session_state.logged=False
    st.rerun()

tool=st.sidebar.selectbox("Select Tool",[

"AI Chat",
"Dashboard",
"AI Tutor",
"Dataset Analyzer",
"AI Data Insights",
"PDF QA",
"Code Generator",
"SQL Generator",
"Resume Analyzer",
"ATS Checker"

])

# ---------- CHAT ----------

if tool=="AI Chat":

    st.header("AI Chat Assistant")

    if st.button("New Chat"):
        st.session_state.chat_history=[]

    msg=st.text_input("Message")

    if st.button("Send"):

        response=ask_ai(msg)

        st.session_state.chat_history.append(("You",msg))
        st.session_state.chat_history.append(("AI",response))

    for sender,text in st.session_state.chat_history:

        if sender=="You":
            st.markdown(f"<div class='chat-user'><b>You:</b> {text}</div>",unsafe_allow_html=True)

        else:
            st.markdown(f"<div class='chat-ai'><b>AI:</b> {text}</div>",unsafe_allow_html=True)

# ---------- DASHBOARD ----------

elif tool=="Dashboard":

    st.header("Platform Analytics")

    col1,col2,col3=st.columns(3)

    col1.metric("Users",len(users))
    col2.metric("Tools",9)
    col3.metric("AI Model","phi3")

    df=pd.DataFrame({
        "Tool":["Chat","Tutor","Dataset","Insights","PDF","Code","SQL","Resume","ATS"],
        "Usage":[45,30,20,18,15,20,16,12,14]
    })

    fig=px.bar(df,x="Tool",y="Usage")

    st.plotly_chart(fig)

# ---------- TUTOR ----------

elif tool=="AI Tutor":

    topic=st.text_input("Topic")

    if st.button("Explain"):

        st.write(ask_ai(f"Explain clearly with examples: {topic}"))

# ---------- DATASET ----------

elif tool=="Dataset Analyzer":

    file=st.file_uploader("Upload CSV",type="csv")

    if file:

        df=pd.read_csv(file)

        st.dataframe(df.head())

        st.write(df.describe())

        num=df.select_dtypes(include="number").columns

        if len(num)>1:

            x=st.selectbox("X Axis",num)
            y=st.selectbox("Y Axis",num)

            fig=px.scatter(df,x=x,y=y)

            st.plotly_chart(fig)

# ---------- DATA INSIGHTS ----------

elif tool=="AI Data Insights":

    file=st.file_uploader("Upload dataset",type="csv")

    if file:

        df=pd.read_csv(file)

        summary=df.describe().to_string()

        if st.button("Generate Insights"):

            st.write(ask_ai(f"Generate business insights:\n{summary}"))

# ---------- PDF QA ----------

elif tool=="PDF QA":

    pdf=st.file_uploader("Upload PDF",type="pdf")

    question=st.text_input("Question")

    if st.button("Analyze"):

        reader=PyPDF2.PdfReader(pdf)

        text=""

        for p in reader.pages:
            text+=p.extract_text()

        st.write(ask_ai(f"Document:\n{text[:1000]}\nQuestion:{question}"))

# ---------- CODE ----------

elif tool=="Code Generator":

    problem=st.text_area("Describe program")

    lang=st.selectbox("Language",["Python","Java","C++","JavaScript"])

    if st.button("Generate"):

        st.code(ask_ai(f"Write {lang} code for {problem}"))

# ---------- SQL ----------

elif tool=="SQL Generator":

    schema=st.text_area("Database schema")

    task=st.text_input("Task")

    if st.button("Generate SQL"):

        st.code(ask_ai(f"Database schema:{schema} Task:{task}"))

# ---------- RESUME ----------

elif tool=="Resume Analyzer":

    resume=st.file_uploader("Resume",type="pdf")

    if st.button("Analyze"):

        reader=PyPDF2.PdfReader(resume)

        text=""

        for p in reader.pages:
            text+=p.extract_text()

        st.write(ask_ai(f"Analyze resume:\n{text[:1000]}"))

# ---------- ATS ----------

elif tool=="ATS Checker":

    resume=st.file_uploader("Resume",type="pdf")

    role=st.text_input("Target Role")

    if st.button("Evaluate"):

        reader=PyPDF2.PdfReader(resume)

        text=""

        for p in reader.pages:
            text+=p.extract_text()

        prompt=f"""
Evaluate resume for role {role}

Return:

ATS SCORE out of 100
Missing Keywords
Skill Gaps
Strengths
Improvements

{text[:1000]}
"""

        st.write(ask_ai(prompt))