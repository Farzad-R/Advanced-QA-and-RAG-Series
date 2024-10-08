import gradio as gr
from chatbot.chatbot_backend import ChatBot
from utils.ui_settings import UISettings


with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("AgentGraph"):
            ##############
            # First ROW:
            ##############
            with gr.Row() as row_one:
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    bubble_full_width=False,
                    height=500,
                    avatar_images=(
                        ("images/AI_RT.png"), "images/openai.png"),
                    # render=False
                )
                # **Adding like/dislike icons
                chatbot.like(UISettings.feedback, None, None)
            ##############
            # SECOND ROW:
            ##############
            with gr.Row():
                input_txt = gr.Textbox(
                    lines=3,
                    scale=8,
                    placeholder="Enter text and press enter, or upload PDF files",
                    container=False,
                )

            ##############
            # Third ROW:
            ##############
            with gr.Row() as row_two:
                text_submit_btn = gr.Button(value="Submit text")
                clear_button = gr.ClearButton([input_txt, chatbot])
            ##############
            # Process:
            ##############
            txt_msg = input_txt.submit(fn=ChatBot.respond,
                                       inputs=[chatbot, input_txt],
                                       outputs=[input_txt,
                                                chatbot],
                                       queue=False).then(lambda: gr.Textbox(interactive=True),
                                                         None, [input_txt], queue=False)

            txt_msg = text_submit_btn.click(fn=ChatBot.respond,
                                            inputs=[chatbot, input_txt],
                                            outputs=[input_txt,
                                                     chatbot],
                                            queue=False).then(lambda: gr.Textbox(interactive=True),
                                                              None, [input_txt], queue=False)


if __name__ == "__main__":
    demo.launch()
