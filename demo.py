import gradio as gr
import os
import time
import shutil
import base64
from pdfquery import DocumentQuery
import pandas as pd
import docx
from pdfquery import xlsx_to_csv_pd
pquery = DocumentQuery()


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
    # try:
    #     shutil.rmtree('./private_upload/')
    # except:
    #     pass
    time_tag = time.strftime("%Y-%m-%d-%H", time.localtime())
    os.makedirs(f'private_upload/{time_tag}', exist_ok=True)
    file_name = os.path.basename(file_obj.name)
    destination = f'private_upload/{time_tag}/{file_name}'
    shutil.copy(file_obj.name, destination)
    # 解决使用window系统文件出现乱码问题
    cmd = f"""file -i '{destination}'"""
    r = os.popen(cmd)
    line = r.readline()
    print(line.split('=')[1])
    # if line.split('=')[1] != 'utf-8' and line.split('=')[1] != 'binary':
    if file_name.lower().endswith(".csv"):
        cmd = f"""iconv -f gbk -t utf-8 '{destination}' > private_upload/new.{destination.split('.')[1]}"""
        os.system(cmd)
        destination = "private_upload/new."+destination.split('.')[1]
    
    document = None
    global pquery
    print(destination)
    pquery.ingest(destination)
    if file_name.lower().endswith(".txt"):
        with open(destination, "r", encoding='utf-8', errors='ignore') as f:
            display = f.read()
        return [None,display,None, gr.update(visible=False),gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),
            gr.update(visible=True)]
    elif file_name.lower().endswith(".pdf"):
        with open(destination, "rb") as f:
            document = base64.b64encode(f.read()).decode('utf-8')
        display = f'<embed src="data:application/pdf;base64,{document}" ' \
                    f'width="850" height="800" type="application/pdf">'
        return [display,None,None, gr.update(visible=False),gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),
            gr.update(visible=True)]
    elif file_name.lower().endswith(".csv"):
        # 传csv文件的路径到gr.DataFrame
        display = destination
        return [None,None,display, gr.update(visible=False),gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),
            gr.update(visible=True)]
    elif file_name.lower().endswith(".docx"):
        doc = docx.Document(destination)
        display = ''
        for para in doc.paragraphs:
            display += para.text + '\n'
        return [None,display,None, gr.update(visible=False),gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),
            gr.update(visible=True)]
    elif file_name.lower().endswith(".xlsx"):
        print(destination[:-5]+'.csv')
        xlsx_to_csv_pd(destination[:-5])
        display = destination[:-5]+'.csv'
        return [None,None,display, gr.update(visible=False),gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),gr.update(visible=True),
            gr.update(visible=True)]
# 清空
cle = lambda :""
with gr.Blocks(title="Chat With Pdf") as demo:
    gr.HTML(title_html)
    file = gr.File(label="添加文件",
                    file_types=['.txt', '.xlsx', '.docx', '.pdf', ".csv"],
                    file_count="single",
                    show_label=False,visible=True)
    with  gr.Row():
        with gr_L(scale=1.5, elem_id="gpt-chat"):
            title_1 = gr.Markdown("""<h1><center><strong>文档内容 </strong></center></h1>""", visible=False)
            out_1 = gr.Markdown(visible=False)
            out_2 = gr.TextArea(lines=15,visible=False,max_lines=25)
            out_3 = gr.DataFrame(row_count=(1,"dynamic"),visible=False,max_rows=10)
        with gr_L(scale=1, elem_id="gpt-chat"):
            title_2 = gr.Markdown("""<h1><center><strong>文档问答 </strong></center></h1>
            """, visible=False)
            chatbot = gr.Chatbot(scale=3, height=600, visible=False)
            with  gr.Row():
                message = gr.Textbox(placeholder="Input question here.", scale=10, visible=False)
                state = gr.State([])
                submit = gr.Button("发送", scale=1, visible=False)

        file.upload(pdf_to_markdown, file, [out_1, out_2, out_3, file, out_1, out_2, out_3, title_1, title_2, chatbot, message, submit])
        submit.click(chatgpt_clone, inputs=[message, state, chatbot], outputs=[chatbot, state, message])

demo.launch(share=True)
