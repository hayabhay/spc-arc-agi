import random
import time
import json
import streamlit as st
from config import get_page_config, init_session, ORIG_DATASET, EVAL_FPATHS, EVAL_TASKIDS, TRAIN_FPATHS, TRAIN_TASKIDS

# Set up page config & init session
st.set_page_config(**get_page_config())
init_session(st.session_state)

st.write("### 🧭 Data Explorer")
st.write("---")

st.write("> ##### *ARC-AGI consists of unique training and evaluation tasks. Each task contains input-output examples. The puzzle-like inputs and outputs present a grid where each square can be one of ten colors. A grid can be any height or width between 1x1 and 30x30.*")

# Get query params if passed
if "task" in st.query_params:
    task_id = st.query_params["task"]
else:
    task_id = "6150a2bd"

random_selector, task_selector = st.sidebar.tabs(["Load Random", "Load by ID"])

with random_selector:
    # Add a radio button to select the dataset
    dataset = st.radio("Select a dataset", ["Training", "Evaluation"])
    fpath = random.choice(EVAL_FPATHS) if dataset == "Original Evaluation" else random.choice(TRAIN_FPATHS)
    # Button to load a random file
    load = st.button("Load Random File")
    if load:
        task_id = fpath.name.split(".")[0]
        st.query_params["task"] = task_id

with task_selector:
    task_id = st.text_input("Task ID", task_id)
    submitted = st.button("Load Task")
    if submitted:
        st.query_params["task"] = task_id

# Check if the task id is in training or evaluation and load it
dirname = "training" if task_id in TRAIN_TASKIDS else "evaluation"
fpath = ORIG_DATASET / dirname / f"{task_id}.json"

# Load the json directly
fdata = json.load(open(fpath))
# Get only the file name from the path
fname = fpath.name

# Render file name & id
st.write(f"### Filename: `{fname}`")

with st.expander(f"#### View raw json"):
    st.json(fdata)

# Render iframe
play_url = f"https://arcprize.org/play?task={fpath.stem}"
st.components.v1.iframe(src=play_url, height=2000, scrolling=True)
