import gradio as gr
from transformers import pipeline

# Load model
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment"
)

# Emoji mapping
emoji_map = {
    "LABEL_0": "😞 Negative",
    "LABEL_1": "😐 Neutral",
    "LABEL_2": "😊 Positive"
}

# Function
def analyze_sentiment(text):
    if not text.strip():
        return "⚠️ Please enter some text."

    result = sentiment_pipeline(text)[0]

    label = result["label"]
    score = result["score"]

    emoji_label = emoji_map.get(label, label)

    return f"{emoji_label} (Confidence: {score:.2f})"

# UI
with gr.Blocks() as app:
    gr.Markdown("## 🧠 Sentiment Analysis with Emojis")
    gr.Markdown("Enter text and see its sentiment instantly.")

    user_input = gr.Textbox(
        placeholder="Type your sentence...",
        label="Input Text",
        lines=3
    )

    output = gr.Textbox(label="Result")

    btn = gr.Button("Analyze")

    btn.click(
        fn=analyze_sentiment,
        inputs=user_input,
        outputs=output
    )

# Launch
app.launch()