import openai
import streamlit as st
import ast
import pandas as pd

starting_prompt = """You are a helpful assistant, specialized in creating graphs. ONLY use the format of a Pandas dataframe (e.g. {'x_axis': [1, 2], 'y_axis': [3, 4]}). 
                    Respond ONLY with the dataframe, with no other text, formatting, or explanation.
                    Make sure to respond with only literal values, not an expression.
                    """
if 'convo' not in st.session_state or st.session_state.convo == []:
    st.session_state.convo = [{"role": "system", "content": starting_prompt}]

graph_details = st.sidebar.container(height=700)
with graph_details:
    st.subheader("Graph Details")
    st.text_area("Y-axis", height=68, placeholder="describe the y-axis...", key="y_axis")
    st.text_area("X-axis", height=68, placeholder="describe the x-axis...", key="x_axis")
    graph_type = st.selectbox("Graph Type", ["line", "bar", "area", "scatter"], key="graph_type")
    prompt = st.text_area("Prompt", height=68, placeholder="describe the graph...")
    st.button('Clear and Submit', on_click=lambda: st.session_state.convo.clear())
    st.text_input('API Key', placeholder="Type your OpenAI API key...", key="api_key", type='password')


# __, __, api_key = netrc.netrc().authenticators('openai') 
client = openai.OpenAI(api_key=st.session_state.api_key)

def askgpt():
    convo = st.session_state.convo
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=convo
    )
    st.session_state.convo.append({"role": "assistant", "content": response.choices[0].message.content})
    print(st.session_state.convo)

def create_graph():
    for message in st.session_state.convo:
        if message['role'] == 'assistant':
            prompt = message['content']
            break

    graph_type = st.session_state.graph_type
    messages = st.session_state.messages
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





# prompt = st.chat_input("Say something")
messages = st.container(height=700, key="messages")
st.session_state.messages = messages




if prompt and st.session_state.api_key:  
    prompt += " The user describes the x-axis as: " + st.session_state.x_axis + "." if st.session_state.x_axis else "The user does not describe the x-axis." 
    prompt += " The user describes the y-axis as: " + st.session_state.y_axis + "." if st.session_state.y_axis else "The user does not describe the y-axis."
    st.session_state.convo.append({"role": "user", "content": prompt})
    try:
        askgpt()
    except openai.AuthenticationError as e:
        print(e)
    messages = st.session_state.messages
    for message in st.session_state.convo:
        if message['role'] == 'assistant':
            try:
                create_graph()
            except Exception as e:
                print(e)
                messages.chat_message("assistant").write(message['content'])
        elif message['role'] == 'user':
            messages.chat_message("user").write(message['content'])
   #messages.chat_message("assistant").write(convo[-1]['content'])
    prompt = None


