import os
import uuid
import torch
import streamlit as st
from PIL import Image
from stqdm import stqdm
from inference import DonutInference

from src.db_connector import DatabaseAgent
from src.database_utils import InvoiceDatabase
from src.llm import TextInference, SQLExtractor
from src.utils import PromptFormatterV1, get_data_from_query

st.set_page_config(layout="wide")
from config import connection_url, database_info_dict

with st.spinner("Please wait loading model.."):
    try:
        inference_model = DonutInference(
            model_pth="katanaml-org/invoices-donut-model-v1",
            device="cuda" if torch.cuda.is_available() else "cpu",
        )
        database_object = InvoiceDatabase(uri=connection_url)
        database_object.create_tables()
        db_agent = DatabaseAgent(**database_info_dict)
    except Exception as e:
        st.error(f"Error loading model or database: {e}")
        st.stop()

if "folder_path" not in st.session_state:
    st.session_state.folder_path = ""

if "conversion_done" not in st.session_state:
    st.session_state.conversion_done = False


def create_session_folder():
    session_id = str(uuid.uuid4())
    folder_path = os.path.join("uploaded_images", session_id)
    os.makedirs(folder_path, exist_ok=True)
    print("📰📰📰📰📰📰📰📰📰📰📰Saved at folder 📰📰📰📰📰📰📰📰📰📰 ", folder_path)
    return folder_path


def save_uploaded_images(uploaded_files, folder_path):
    for file in uploaded_files:
        if file.type in ["image/png", "image/jpeg"]:
            img = Image.open(file)
            img.save(os.path.join(folder_path, file.name))


col1, col2 = st.columns([1, 3])

with col1:
    st.markdown(
        """
    <div style="text-align: left;">
        <span style="font-size: 14px; color: orange;">
            Upload your invoice images:
        </span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Choose images", type=["png", "jpg"], accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Upload"):
            st.session_state.folder_path = create_session_folder()
            save_uploaded_images(uploaded_files, st.session_state.folder_path)

            try:
                st.markdown(
                    """
                <div style="text-align: left;">
                <span style="font-size: 14px; color: Red;">
                Processing the uploaded invoices:
                </span>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                for image_file in stqdm(
                    os.listdir(st.session_state.folder_path),
                    desc="Processing your Invoice.📰",
                ):
                    # read image from pth
                    img_pth = os.path.join(
                        str(st.session_state.folder_path), str(image_file)
                    )

                    # convert image
                    img = Image.open(img_pth)

                    # perform inference on image
                    dict_file = inference_model(image=img)

                    # log the images to database
                    database_object.push_data(data=dict_file)
                st.success("Invoices pushed to database.")
                st.session_state.conversion_done = True
            except Exception as e:
                st.error(f"Error processing invoices: {e}")


with col2:
    if st.session_state.conversion_done:

        del inference_model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        with st.expander("See Database Schema:"):
            tables = db_agent.grab_table_names()
            schema = db_agent.grab_table_schema(tables=tables)
            st.write(schema)

        text = st.text_input("Please Enter your Queries:")

        if st.button("Process"):
            formatter = PromptFormatterV1(tables=schema, db_type="PostgreSQL")
            prompt = formatter(question=text)

            inference_llm = TextInference()
            output = inference_llm.generate_text(input_text=prompt, max_length=1024)

            extractor = SQLExtractor(text=output)
            sql = extractor.extract_select_commands()[-1]

            if sql:
                with st.expander("Prompt and SQL"):
                    st.write(prompt)
                    st.write(sql)

            # execute the sql
            result_df = get_data_from_query(
                query=sql,
                db_url=db_agent.conn_str,  # get the connection string from sql agent.
            )

            st.dataframe(result_df, use_container_width=True)
