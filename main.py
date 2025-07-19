import os
import logging
from flask import Flask, render_template, request, flash

try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
use_mock = os.environ.get("USE_MOCK", "false").lower() == "true"

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY and openai_available else None

def generate_instagram_captions(topic, tone):
    if not openai_client or use_mock:
        return f"""1. {topic} - Channeling some {tone} vibes! #SampleCaption\n2. Mocked caption for {topic} in a {tone} tone!\n3. Just a demo caption: \"{topic}\" [{tone}]"""

    prompt = f"""Generate 3 engaging Instagram captions for the topic: "{topic}" with a {tone} tone.

Requirements:
- Each caption should be unique and creative
- Include relevant hashtags
- Keep captions engaging and social media friendly
- Match the requested tone: {tone}
- Format as a numbered list"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative Instagram expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI error: {str(e)}")
        raise Exception("Failed to generate captions: " + str(e))

@app.route("/", methods=["GET", "POST"])
def index():
    captions = None
    error = None
    tutorial_mode = request.args.get("tutorial_mode", "false").lower() == "true"

    topic = request.form.get("topic", "")
    tone = request.form.get("tone", "")

    if request.method == "POST":
        if not topic:
            error = "Please enter a topic."
        elif not tone:
            error = "Please select a tone."
        else:
            try:
                captions = generate_instagram_captions(topic, tone)
                flash("Captions generated successfully!", "success")
            except Exception as e:
                error = str(e)
                flash(error, "error")

    return render_template("index.html",
                           captions=captions,
                           error=error,
                           topic=topic,
                           tone=tone,
                           tutorial_mode=tutorial_mode)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
