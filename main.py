import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize OpenAI client if API key is available
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = None

if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logging.info("OpenAI client initialized successfully")
    except ImportError:
        logging.warning("OpenAI library not available, using mock fallback")
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")
else:
    logging.info("No OpenAI API key found, using mock fallback")

def generate_instagram_captions(topic, tone):
    """Generate Instagram captions using OpenAI API or mock fallback"""
    
    # Handle multiple tones
    if ',' in tone:
        tones = [t.strip() for t in tone.split(',')]
        tone_description = f"blend of {', '.join(tones[:-1])}, and {tones[-1]}" if len(tones) > 1 else tone
    else:
        tone_description = tone
    
    # Try OpenAI API first if available
    if openai_client:
        try:
            prompt = f"""Generate 3 engaging Instagram captions about {topic} with a {tone_description} tone. 
            Each caption should be creative, include relevant emojis, and be suitable for social media.
            Format the response as a numbered list (1., 2., 3.)."""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a creative social media caption writer who creates engaging Instagram captions with emojis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            # Fall back to mock if API fails
            pass
    
    # Mock fallback function
    return f"""1. This is a cool {tone} caption about {topic}! 📸
2. Keeping it {tone} while vibing with {topic}. 🎯
3. {topic} never looked this {tone} before! 🚀"""

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route that handles both GET and POST requests"""
    
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic', '').strip()
        tone = request.form.get('tone', '').strip()
        
        # Validate inputs
        if not topic:
            flash('Please enter a topic for your Instagram caption.', 'error')
            return redirect(url_for('index'))
        
        if not tone:
            flash('Please select a tone for your Instagram caption.', 'error')
            return redirect(url_for('index'))
        
        try:
            # Generate captions
            captions = generate_instagram_captions(topic, tone)
            flash('Captions generated successfully!', 'success')
            
            return render_template('index.html', 
                                 captions=captions, 
                                 topic=topic, 
                                 tone=tone)
            
        except Exception as e:
            logging.error(f"Error generating captions: {e}")
            flash('An error occurred while generating captions. Please try again.', 'error')
            return redirect(url_for('index'))
    
    # GET request - show the form
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
