
import os
import tempfile
import streamlit as st
from streamlit_chat import message
from pdfquery import PDFQuery
import fitz

# Set page title
st.set_page_config(page_title="ChatWithPDF")

def display_messages():
    """
    Display chat messages in the Streamlit app.
    """
    st.subheader("文档问答 :sunglasses:")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()

def process_input():
    """
    Process user input in the chat interface.
    """
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            query_text = st.session_state["pdfquery"].ask(user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((query_text, False))

def read_and_save_file():
    """
    Read and save files uploaded by the user.
    """
    st.session_state["pdfquery"].forget()  # to reset the knowledge base
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {file.name}"):
            st.session_state["pdfquery"].ingest(file_path)
        os.remove(file_path)

def is_openai_api_key_set() -> bool:
    """
    Check if the OpenAI API key is set.

    Returns:
    bool: True if the OpenAI API key is set, False otherwise.
    """
    return len(st.session_state["OPENAI_API_KEY"]) > 0

def main():
    """
    Main function to run the Streamlit app.
    """
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
        if is_openai_api_key_set():
            st.session_state["pdfquery"] = PDFQuery(st.session_state["OPENAI_API_KEY"])
        else:
            st.session_state["pdfquery"] = None

    st.header("ChatWithPDF")

    if st.text_input("请输入 OpenAI API Key :heartbeat:", value=st.session_state["OPENAI_API_KEY"], key="input_OPENAI_API_KEY", type="password"):
        if (
            len(st.session_state["input_OPENAI_API_KEY"]) > 0
            and st.session_state["input_OPENAI_API_KEY"] != st.session_state["OPENAI_API_KEY"]
        ):
            st.session_state["OPENAI_API_KEY"] = st.session_state["input_OPENAI_API_KEY"]
            if st.session_state["pdfquery"] is not None:
                st.warning("Please, upload the files again.")
            st.session_state["messages"] = []
            st.session_state["user_input"] = ""
            st.session_state["pdfquery"] = PDFQuery(st.session_state["OPENAI_API_KEY"])

    st.subheader("上传本地PDF文件	:yum:")
    pdf_file = st.file_uploader(
        "Upload document",
        type=["pdf"],
        key="file_uploader",
        on_change=read_and_save_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
        disabled=not is_openai_api_key_set(),
    )
    # --------------------------------------------------
    if len(pdf_file) > 0:
        import io
        import numpy as np
        from PIL import Image
        # 打开PDF文件
        pdf_doc = fitz.open(stream=pdf_file)

        # 获取页数
        num_pages = pdf_doc.page_count

        # 获取页面对象列表
        pages = pdf_doc.pages()
        # 创建一个图片列表
        images = []

        # 遍历每个页面对象
        for page in pages:
            # 转换为Pixmap对象
            pix = page.get_pixmap()

            # 转换为PNG格式的字节数据
            png_data = pix.getPNGData()

            # 转换为Image对象
            image = Image.open(io.BytesIO(png_data))

            # 添加到图片列表中
            images.append(image)
        # 显示图片列表
        st.image(images, caption=f"这是一个{num_pages}页的PDF文件", use_column_width=True)

    # --------------------------------------------------
    st.session_state["ingestion_spinner"] = st.empty()

    display_messages()
    st.text_input("Message :stuck_out_tongue_winking_eye:", key="user_input", disabled=not is_openai_api_key_set(), on_change=process_input)

    st.divider()

if __name__ == "__main__":
    main()
