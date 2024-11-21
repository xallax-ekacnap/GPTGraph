import streamlit as st
import openai
import netrc
import ast
import pandas as pd

starting_prompt = """You are a helpful assistant. If you are asked to create a chart or graph, 
                    use the format of a Pandas dataframe (e.g. {'x_axis': [1, 2], 'y_axis': [3, 4]}). 
                    If this is the case, respond ONLY with the dataframe, with no other text, formatting, or explanation.
                    Make sure to respond with only literal values, not an expression.
                    """
if 'convo' not in st.session_state or st.session_state.convo == []:
    st.session_state.convo = [{"role": "system", "content": starting_prompt}]

def askgpt(convo, client):
    print(convo)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=convo
    )

    convo.append({'role': 'assistant', 'content': response.choices[0].message.content})
    st.session_state.convo = convo

def create_graph(message, messages):
    graph_type = st.session_state.graph_type
    # messages = st.session_state.messages
    formatted_dict = ast.literal_eval(message['content'])
    df = pd.DataFrame(formatted_dict)
    if graph_type == "line":
        messages.chat_message("assistant").line_chart(df, x=df.columns[0], y=df.columns[1])
    elif graph_type == "area":
        messages.chat_message("assistant").area_chart(df, x=df.columns[0], y=df.columns[1])
    elif graph_type == "scatter":
        messages.chat_message("assistant").scatter_chart(df, x=df.columns[0], y=df.columns[1])
    elif graph_type == "bar":
        messages.chat_message("assistant").bar_chart(df, x=df.columns[0], y=df.columns[1])

__, __, api_key = netrc.netrc().authenticators('openai')
client = openai.OpenAI(api_key=api_key)

graph_details = st.sidebar.container(height=500)

prompt = st.chat_input("Say something")
messages = st.container(height=500, key="messages")

with graph_details:
    st.subheader("Graph Details")
    st.text_area("Y-axis", height=68, placeholder="describe the y-axis...")
    st.text_area("X-axis", height=68, placeholder="describe the x-axis...")
    graph_type = st.selectbox("Graph Type", ["line", "bar", "area", "scatter"], key="graph_type")

if prompt:  
    convo = st.session_state.convo
    convo.append({"role": "user", "content": prompt})
    askgpt(convo, client)
    print(st.session_state.convo)
    for message in st.session_state.convo:
        if message['role'] == 'assistant':
            try:
                create_graph(message, messages)
            except Exception as e:
                print(e)
                messages.chat_message("assistant").write(message['content'])
        elif message['role'] == 'user':
            messages.chat_message("user").write(message['content'])
   #messages.chat_message("assistant").write(convo[-1]['content'])
    prompt = None

st.button('Clear', on_click=lambda: st.session_state.convo.clear())
