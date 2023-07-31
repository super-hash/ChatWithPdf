import gradio as gr
import os
import time
import shutil
import base64
from pdfquery import PDFQuery

pquery = PDFQuery()


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


title_html = f"<h1 align=\"center\">Chat With Pdf</h1>"

gr_L1 = lambda: gr.Row().style()
gr_L2 = lambda scale, elem_id: gr.Column(scale=scale, elem_id=elem_id)


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
    global pquery
    pquery.ingest(destination)
    with open(destination, "rb") as f:
        pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{pdf}" ' \
                    f'width="700" height="800" type="application/pdf">'
    return [pdf_display, gr.update(visible=False),gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),
            gr.update(visible=True),gr.update(visible=True)]

# 清空
cle = lambda :""

with gr.Blocks(title="Chat With Pdf") as demo:
    gr.HTML(title_html)
    file = gr.File()
    with gr_L1():
        with gr_L2(scale=1.5, elem_id="gpt-chat"):
            out = gr.Markdown()
        with gr_L2(scale=1, elem_id="gpt-chat"):
            title = gr.Markdown("""<h1><center><strong>文档问答 </strong></center></h1>
            """, visible=False)
            chatbot = gr.Chatbot(scale=3, height=600, visible=False)
            with gr_L1():
                message = gr.Textbox(placeholder="Input question here.", scale=10, visible=False)
                state = gr.State([])
                submit = gr.Button("发送", scale=1, visible=False)

        file.upload(pdf_to_markdown, file, [out, file, out, title, chatbot, message, submit])
        submit.click(chatgpt_clone, inputs=[message, state, chatbot], outputs=[chatbot, state, message])

demo.launch(share=True)