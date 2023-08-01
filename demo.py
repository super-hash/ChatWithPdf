import gradio as gr
import os
import time
import shutil
import base64
from pdfquery import PDFQuery
import pandas as pd
import docx

pquery = PDFQuery()

# os.environ["http_proxy"]="127.0.0.1:7890"
# os.environ["https_proxy"]="127.0.0.1:7890"
def openai_create(s):
    global pquery
    return pquery.ask(s)

def chatgpt_clone(input, history, chatbot):
    if input == "":
        return chatbot, history, ""
    history = history or []
    s = list(sum(history, ()))
    s.append(input)
    inp = ' '.join(s)
    output = openai_create(input)
    history.append((inp, output))
    chatbot.append((input, output))
    return chatbot, history, ""


title_html = f"<h1 align=\"center\">Chat with Document</h1>"

gr_L = lambda scale, elem_id: gr.Column(scale=scale, elem_id=elem_id)


def pdf_to_markdown(file_obj):
    try:
        shutil.rmtree('./private_upload/')
    except:
        pass
    time_tag = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    os.makedirs(f'private_upload/{time_tag}', exist_ok=True)
    file_name = os.path.basename(file_obj.name)
    destination = f'private_upload/{time_tag}/{file_name}'
    shutil.copy(file_obj.name, destination)
    document = None
    print(destination)
    if file_name.lower().endswith(".md"):
        display = f'<embed src="data:application/pdf;base64,{document}" ' \
                    f'width="700" height="800" type="application/pdf">'
    elif file_name.lower().endswith(".txt"):
        with open(destination, "r", encoding='utf-8', errors='ignore') as f:
            display = f.read()
    elif file_name.lower().endswith(".pdf"):
        with open(destination, "rb") as f:
            document = base64.b64encode(f.read()).decode('utf-8')
        display = f'<embed src="data:application/pdf;base64,{document}" ' \
                    f'width="700" height="800" type="application/pdf">'
    elif file_name.lower().endswith(".csv"):
        df = pd.read_csv(destination, encoding='gbk')
        display = df.to_html()
    elif file_name.lower().endswith(".docx"):
        doc = docx.Document(destination)
        display = ''
        for para in doc.paragraphs:
            display += para.text + '\n'
    else :
        df = pd.read_excel(destination)
        display = df.to_html()
    
    global pquery
    pquery.ingest(destination)
    return [display, gr.update(visible=False),gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),
            gr.update(visible=True),gr.update(visible=True)]

# 清空
cle = lambda :""

with gr.Blocks(title="Chat With Pdf") as demo:
    gr.HTML(title_html)
    file = gr.File(label="添加文件",
                    file_types=['.txt', '.xlsx', '.docx', '.pdf', ".csv"],
                    file_count="single",
                    show_label=False)
    with  gr.Row():
        with gr_L(scale=1.5, elem_id="gpt-chat"):
            out = gr.Markdown(visible=False)
        with gr_L(scale=1, elem_id="gpt-chat"):
            title = gr.Markdown("""<h1><center><strong>文档问答 </strong></center></h1>
            """, visible=False)
            chatbot = gr.Chatbot(scale=3, height=600, visible=False)
            with  gr.Row():
                message = gr.Textbox(placeholder="Input question here.", scale=10, visible=False)
                state = gr.State([])
                submit = gr.Button("发送", scale=1, visible=False)

        file.upload(pdf_to_markdown, file, [out, file, out, title, chatbot, message, submit])
        submit.click(chatgpt_clone, inputs=[message, state, chatbot], outputs=[chatbot, state, message])

demo.launch(share=True)