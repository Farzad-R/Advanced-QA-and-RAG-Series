import uuid
import gradio as gr
from datetime import datetime
from dotenv import load_dotenv
# Import all RAG techniques
from rag_techniques.standard_rag import StandardRAG
from rag_techniques.conversational_rag import ConversationalRAG
from rag_techniques.fusion_rag import FusionRAG
from rag_techniques.hyde_rag import HydeRAG
from rag_techniques.self_rag import SelfRAG
from rag_techniques.adaptive_rag import AdaptiveRAG
from rag_techniques.corrective_rag import CorrectiveRAG
from rag_techniques.agentic_rag import AgenticRAG
from rag_techniques.speculative_rag import SpeculativeRAG

load_dotenv()


class RAGPlayground:
    def __init__(self):
        # Initialize all RAG techniques
        self.techniques = {
            "Standard (Naive) RAG": StandardRAG(),
            "RAG with Memory (Conversational)": ConversationalRAG(),
            "Fusion RAG": FusionRAG(),
            "HyDE (Hypothetical Doc Embedding)": HydeRAG(),
            "Self-RAG": SelfRAG(),
            "Adaptive RAG": AdaptiveRAG(),
            "Corrective RAG (CRAG)": CorrectiveRAG(),
            "Agentic RAG": AgenticRAG(),
            "Speculative RAG": SpeculativeRAG()
        }

        self.current_logs = []
        self.conversation_history = {}

        self.rag_techniques = [
            "Standard (Naive) RAG",
            "RAG with Memory (Conversational)",
            "Fusion RAG",
            "HyDE (Hypothetical Doc Embedding)",
            "Self-RAG",
            "Adaptive RAG",
            "Corrective RAG (CRAG)",
            "Agentic RAG",
            "Speculative RAG"
        ]

    def get_response(self, history, message, technique, dataset, session_id):
        if not message.strip():
            return "", history

        try:
            # Check if technique is implemented
            if technique in self.techniques:
                # Get the technique instance and process query
                technique_instance = self.techniques[technique]

                # Handle different method signatures for different techniques
                if hasattr(technique_instance, 'process_query'):
                    if technique == "RAG with Memory (Conversational)":
                        # Conversational RAG needs session history
                        session_history = self.conversation_history.get(
                            session_id, [])
                        response, logs = technique_instance.process_query(
                            message, dataset, session_history)

                        # Update conversation history
                        session_history.append(
                            {"user": message, "assistant": response})
                        self.conversation_history[session_id] = session_history
                    else:
                        # Standard process_query method
                        response, logs = technique_instance.process_query(
                            message, dataset)
                else:
                    # Fallback method name
                    response, logs = technique_instance.generate_response(
                        message, dataset)

            else:
                # Technique not implemented yet
                response = f"🚧 {technique} coming soon..."
                logs = [
                    f"[{datetime.now().strftime('%H:%M:%S')}] INFO: {technique} not implemented yet"]

            self.current_logs = logs

        except Exception as e:
            response = f"Error: {str(e)}"
            error_log = f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {str(e)}"
            self.current_logs = [error_log]
            print(f"Error in RAG processing: {e}")  # Debug print

        history.append([message, response])
        return "", history

    def clear_conversation_history(self, session_id):
        """Clear conversation history for a specific session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
        return "<div class='logs-panel'>Logs will appear here after processing...</div>"


rag_playground = RAGPlayground()

# Updated CSS with dark theme for logs
custom_css = """
.tall-button { 
    height: 85px !important; 
    font-size: 16px !important; 
}
.logs-panel {
    max-height: 400px !important; 
    overflow-y: auto !important; 
    font-family: 'Courier New', monospace !important; 
    font-size: 13px !important;
    background-color: #1a1a1a !important; 
    color: #00ff00 !important; 
    padding: 15px !important; 
    border-radius: 8px !important; 
    border: 2px solid #333333 !important;
    line-height: 1.4 !important;
    white-space: pre-wrap !important;
}
.logs-panel * {
    color: #00ff00 !important;
    background-color: transparent !important;
    margin-bottom: 3px !important;
}
"""

with gr.Blocks(css=custom_css, title="RAG Playground") as demo:
    session_id = gr.State(str(uuid.uuid4()))

    with gr.Tabs():
        with gr.TabItem("🔬 RAG Playground"):
            # Session info
            session_display = gr.Markdown()
            demo.load(
                lambda s: f"**Session ID:** `{s}`", inputs=session_id, outputs=session_display)

            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        [],
                        height=500,
                        show_copy_button=True,
                        label="RAG Response",
                        avatar_images=None
                    )
                with gr.Column(scale=2):
                    logs_output = gr.HTML(
                        value='<div class="logs-panel">Logs will appear here...</div>',
                        label="Process Logs"
                    )

            with gr.Row():
                input_txt = gr.Textbox(
                    lines=3,
                    scale=8,
                    placeholder="Ask a question about your documents...",
                    label="Your Question"
                )

            with gr.Row():
                text_submit_btn = gr.Button(
                    "Ask Question",
                    elem_classes="tall-button",
                    variant="primary"
                )
                technique_dropdown = gr.Dropdown(
                    choices=rag_playground.rag_techniques,
                    value="Standard (Naive) RAG",
                    label="RAG Technique",
                    scale=2
                )
                dataset_dropdown = gr.Dropdown(
                    choices=["tech_docs", "faq_data", "news_articles"],
                    value="tech_docs",
                    label="Dataset",
                    scale=1
                )
                clear_button = gr.ClearButton(
                    [input_txt, chatbot],
                    elem_classes="tall-button",
                    value="Clear Chat"
                )

            # Function to process query and update logs
            def process_and_update_logs(history, message, technique, dataset, session_id):
                new_message, new_history = rag_playground.get_response(
                    history, message, technique, dataset, session_id)

                # Create simple text content for logs (no nested divs)
                if rag_playground.current_logs:
                    logs_text = "\n".join(rag_playground.current_logs)
                    log_html = f'<div class="logs-panel">{logs_text}</div>'
                else:
                    log_html = '<div class="logs-panel">No logs available</div>'

                return new_message, new_history, log_html

            # Function to clear everything
            def clear_session_and_logs(session_id):
                rag_playground.clear_conversation_history(session_id)
                return '<div class="logs-panel">Logs and conversation history cleared.</div>'

            # Event handlers
            text_submit_btn.click(
                process_and_update_logs,
                inputs=[chatbot, input_txt, technique_dropdown,
                        dataset_dropdown, session_id],
                outputs=[input_txt, chatbot, logs_output],
                queue=False
            )

            input_txt.submit(
                process_and_update_logs,
                inputs=[chatbot, input_txt, technique_dropdown,
                        dataset_dropdown, session_id],
                outputs=[input_txt, chatbot, logs_output],
                queue=False
            )

            clear_button.click(
                clear_session_and_logs,
                inputs=[session_id],
                outputs=logs_output
            )

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        inbrowser=True,
        show_error=True
    )
