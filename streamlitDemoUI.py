import os
import streamlit as st
import base64
import numpy as np
import uuid
import tempfile
from pdf2image import convert_from_path
from inference import DonutInference
from PIL import Image
import pandas as pd

st.set_page_config(
    layout="wide",
    page_title="Invoice Extractor",
)
col1, col2 = st.columns([2, 3])

with st.spinner("Please wait loading model.."):
    MODEL = DonutInference(
        model_pth="katanaml-org/invoices-donut-model-v1", device="cuda"
    )


if "images" not in st.session_state:
    st.session_state.images = []


def save_uploadedfile(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(uploaded_file.read())
        return tf.name


with col1:
    st.markdown(
        "<h4 style='text-align: Left; color: orange;'>Invoice Extractor : </h4>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file:
        pdf_path = save_uploadedfile(uploaded_file)

        st.session_state.images = convert_from_path(pdf_path, dpi=300)

        for idx, image in enumerate(st.session_state.images):
            st.image(image, caption=f"Page {idx + 1}", use_column_width=True)

        # Remove the temporary file
        os.remove(pdf_path)


with col2:
    if len(st.session_state.images) >= 1:
        with st.spinner("Extracting.."):
            response = MODEL(image=st.session_state.images[0])
        st.markdown(
            "<h4 style='text-align: Left; color: purple;'>Extracted Info : </h4>",
            unsafe_allow_html=True,
        )

        table = response["items"]
        response = {k: v for k, v in response.items() if k != "items"}

        st.markdown(
            "<h4 style='text-align: Left; color: orange;'>Invoice Info : </h4>",
            unsafe_allow_html=True,
        )
        st.write(response)

        st.markdown(
            "<h4 style='text-align: Left; color: orange;'>Table : </h4>",
            unsafe_allow_html=True,
        )
        # Convert the 'items' list into a DataFrame
        df = pd.DataFrame(table)
        st.table(df)
