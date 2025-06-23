import gradio as gr
import os
from ai_service import AIService

ai_service = AIService()

def chat_with_bot(user_input, history):
    history = history or []

    try:
        intent_result = ai_service.detect_intent(user_input)
        bot_reply = f"🔍 Detected intent:\n{intent_result}"
    except Exception as e:
        bot_reply = f"❌ Error: {str(e)}"

    history.append((user_input, bot_reply))
    return history, history

def start_gradio_chat_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## 🏥 Healthcare Assistant Chatbot")
        chatbot = gr.Chatbot()
        msg = gr.Textbox(placeholder="Type your message and press Enter")
        state = gr.State([])

        msg.submit(chat_with_bot, [msg, state], [chatbot, state])
        msg.submit(lambda: "", None, msg)

    port = int(os.getenv("FE_PORT", 8080))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)

if __name__ == "__main__":
    start_gradio_chat_ui()
