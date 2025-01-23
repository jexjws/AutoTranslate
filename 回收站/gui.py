import gradio as gr

with gr.Blocks(title="AutoTranslate for Mediawiki") as demo:
    gr.Markdown("## AutoTranslate for Mediawiki")

    with gr.Row(equal_height=True):
        site = gr.Dropdown(["ArchWikiCN"], label="站点", scale=0)
        page_id = gr.Textbox("安装指南", label="条目名")

    with gr.Column():
        mode = gr.Radio(
            choices=["✨Yes", "No"], label="是否分块编辑"
        )

        alignment_mode = gr.Dropdown(
            choices=["wikitext - 按章节分割、对齐"], label="切分、对齐方法", visible=False
        )

        mode.change(
            fn=lambda x: gr.update(visible=x == "✨Yes"),
            inputs=mode,
            outputs=alignment_mode,
        )

    def start(food):
        if food > 0:
            return food - 1, "full"
        else:
            return 0, "hungry"
    
    gr.Button("开始翻译", variant="primary").click(
        fn=start, inputs=[page_id,mode], outputs=[page_id]
    )

    with gr.Row(equal_height=True):
        gr.Textbox(label="log", lines=10, interactive=False)
        gr.Textbox(label="译文", lines=10, interactive=True)

demo.launch()
