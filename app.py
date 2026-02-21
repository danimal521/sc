import streamlit as st





left, right = st.columns([4, 1], vertical_alignment="center")

with left:
    st.title("SmartCatAI")

with right:
    st.image("assets/b553.png", use_container_width=True)


db_user = st.secrets["DB_USER"]
st.write(db_user)








fileTrade = st.file_uploader("eTrade Portfolio File", type=["csv"])