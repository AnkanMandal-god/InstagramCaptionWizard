import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, session

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# No preloaded API key - users must provide their own
openai_client = None

try:
    from openai import OpenAI
    logging.info("OpenAI library available - users can provide their own API keys")
except ImportError:
    logging.warning("OpenAI library not available, using mock fallback")

def clean_caption_content(content):
    """Remove tone headers and number prefixes from caption content"""
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip tone headers like "**Serious Tone:**" or "**Motivational Tone:**"
        if line.startswith('**') and line.endswith('Tone:**'):
            continue
        # Remove number prefixes like "1. ", "2. ", "3. " etc.
        if line and len(line) > 3:
            # Check if line starts with number followed by dot and space
            if line[0].isdigit() and line[1:3] == '. ':
                line = line[3:]  # Remove "1. " prefix
            elif len(line) > 4 and line[0].isdigit() and line[1].isdigit() and line[2:4] == '. ':
                line = line[4:]  # Remove "10. " prefix for double digits
        # Keep clean caption content
        if line:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def mock_generate_instagram_captions(topic, tone):
    """Mock fallback function for generating Instagram captions that blend multiple tones"""
    
    # Handle multiple tones
    tones = [t.strip().lower() for t in tone.split(',') if t.strip()]
    
    # Create tone description for hashtags
    tone_hashtags = ''.join([f"#{t.title()}" for t in tones])
    
    # Generate 3 captions that blend all selected tones
    if 'funny' in tones and 'romantic' in tones:
        captions = f"""1. When {topic} makes you laugh until you fall in love all over again 😂💕 #FunnyLove #{topic.replace(' ', '')}Moments {tone_hashtags}
2. Found someone who thinks my {topic} jokes are actually romantic... keeper! 🤪❤️ #LaughingTogether #{topic.replace(' ', '')}Love {tone_hashtags}
3. They say laughter is the best medicine, but {topic} with you is pure magic 😍🎭 #RomanticComedy #{topic.replace(' ', '')}Life {tone_hashtags}"""
    
    elif 'adventurous' in tones and 'chill' in tones:
        captions = f"""1. Finding adventure in {topic} while keeping my zen intact 🏔️☮️ #AdventurousZen #{topic.replace(' ', '')}Balance {tone_hashtags}
2. Sometimes the best adventures happen when you're completely relaxed about {topic} 🌊✨ #ChillAdventure #{topic.replace(' ', '')}Vibes {tone_hashtags}
3. Peaceful exploration of {topic} - because not all adventures need adrenaline 🧘‍♀️🗺️ #MindfulAdventure #{topic.replace(' ', '')}Journey {tone_hashtags}"""
    
    elif 'professional' in tones and 'funny' in tones:
        captions = f"""1. Bringing humor to the workplace: {topic} edition 💼😄 #ProfessionallyFunny #{topic.replace(' ', '')}Success {tone_hashtags}
2. When {topic} meets corporate comedy - productivity through laughter! 📈🎭 #BusinessHumor #{topic.replace(' ', '')}Growth {tone_hashtags}
3. Serious about success, silly about everything else - especially {topic} 🎯😂 #WorkHardLaughHard #{topic.replace(' ', '')}Life {tone_hashtags}"""
    
    elif len(tones) > 2:
        # For multiple complex tones
        tone_blend = ', '.join(tones[:-1]) + f', and {tones[-1]}'
        captions = f"""1. {topic} hits different when you blend {tone_blend} energy together ✨ #{topic.replace(' ', '')}Fusion {tone_hashtags} #Authentic
2. Why choose one vibe when {topic} can be {tone_blend} all at once? 🌟 #{topic.replace(' ', '')}Multifaceted {tone_hashtags} #RealTalk
3. Embracing every shade of {topic} - {tone_blend} and unapologetically me 💫 #{topic.replace(' ', '')}Journey {tone_hashtags} #BeYou"""
    
    else:
        # Default blended approach for any two tones
        tone_blend = ' and '.join(tones)
        captions = f"""1. When {topic} meets {tone_blend} energy - pure magic happens ✨ #{topic.replace(' ', '')}Magic {tone_hashtags} #Authentic
2. Blending {tone_blend} vibes with {topic} for the perfect mood 🌟 #{topic.replace(' ', '')}Vibes {tone_hashtags} #RealTalk
3. {topic} through a {tone_blend} lens - this is how I see the world 💫 #{topic.replace(' ', '')}Perspective {tone_hashtags} #BeYou"""
    
    return clean_caption_content(captions)

def generate_instagram_captions(topic, tone, api_key=None):
    """Generate Instagram captions using OpenAI GPT-4o API that blend multiple tones"""
    
    # Handle multiple tones
    tones = [t.strip() for t in tone.split(',') if t.strip()]
    
    if not api_key:
        # If no API key provided, require user to provide one
        raise Exception("API key required. Please provide your OpenAI API key to generate captions.")
    
    # Create OpenAI client with provided API key
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except ImportError:
        raise Exception("OpenAI library not available.")
    except Exception as e:
        raise Exception(f"Failed to initialize OpenAI client: {e}")
    
    try:
        # Build tone description for multiple tones
        if len(tones) == 1:
            tone_description = tones[0]
        elif len(tones) == 2:
            tone_description = f"{tones[0]} and {tones[1]} combined"
        else:
            tone_description = f"{', '.join(tones[:-1])}, and {tones[-1]} blended together"
        
        # Create comprehensive prompt for blended tone caption generation
        prompt = f"""Generate Instagram captions for the topic "{topic}" that seamlessly blend {tone_description} into each caption.

Requirements:
- Create exactly 3 unique captions where EACH caption embodies ALL selected tones simultaneously
- Each caption should be a fusion of {tone_description}, not separate tones
- Include relevant hashtags that capture the blended mood and topic
- Add appropriate emojis that enhance the combined message
- Make each caption Instagram-ready (engaging, shareable, authentic)
- Keep captions concise but impactful

Selected tones to blend: {', '.join(tones)}

IMPORTANT: Generate 3 captions that each contain elements of ALL selected tones blended together.

Format your response as exactly 3 numbered captions:
1. [blended caption with emojis and hashtags]
2. [blended caption with emojis and hashtags] 
3. [blended caption with emojis and hashtags]"""
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert social media content creator specializing in Instagram captions. You create engaging, authentic captions that drive engagement and match specific tones perfectly."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.8
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean the content to remove tone headers
        cleaned_captions = clean_caption_content(content)
        
        return cleaned_captions
        
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        # Check for quota exceeded or other specific errors
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            raise Exception("OpenAI API quota exceeded. Please check your usage limits and try again later.")
        elif "authentication" in str(e).lower():
            raise Exception("OpenAI API authentication failed. Please check your API key.")
        else:
            raise Exception(f"OpenAI API error: {str(e)}")

@app.route('/setup-api-key', methods=['POST'])
def setup_api_key():
    """Handle initial API key setup and save to session"""
    
    # Get form data
    api_key = request.form.get('api_key', '').strip()
    topic = request.form.get('topic', '').strip()
    tone = request.form.get('tone', '').strip()
    
    if not api_key:
        flash('Please enter a valid OpenAI API key.', 'error')
        return render_template('index.html', 
                             api_key_required=True,
                             topic=topic,
                             tone=tone,
                             has_session_key=False)
    
    # Save the API key to session
    session['api_key'] = api_key
    flash('API key saved for this session!', 'success')
    
    # If topic and tone are provided, generate captions immediately
    if topic and tone:
        try:
            captions = generate_instagram_captions(topic, tone, api_key=api_key)
            flash('API key saved and captions generated successfully!', 'success')
            return render_template('index.html', 
                                 captions=captions, 
                                 topic=topic, 
                                 tone=tone,
                                 has_session_key=True)
        except Exception as e:
            logging.error(f"Failed to generate captions: {e}")
            error_message = str(e)
            
            if "authentication" in error_message.lower() or "invalid" in error_message.lower():
                flash('Invalid API key. Please check your OpenAI API key and try again.', 'error')
                session.pop('api_key', None)  # Remove invalid key
                return render_template('index.html', 
                                     api_key_required=True,
                                     topic=topic,
                                     tone=tone,
                                     has_session_key=False)
            elif "quota" in error_message.lower():
                flash('The provided API key has exceeded its quota. Please try a different key or use demo mode.', 'error')
                return render_template('index.html', 
                                     quota_exceeded=True,
                                     topic=topic,
                                     tone=tone)
            else:
                flash('Failed to generate captions. Please try again.', 'error')
    
    # Redirect to main page with session key active
    return redirect(url_for('index'))

@app.route('/update-api-key', methods=['POST'])
def update_api_key():
    """Handle API key update from quota exceeded modal"""
    
    # Get form data
    new_api_key = request.form.get('new_api_key', '').strip()
    topic = request.form.get('topic', '').strip()
    tone = request.form.get('tone', '').strip()
    
    if not new_api_key:
        flash('Please enter a valid OpenAI API key.', 'error')
        return render_template('index.html', 
                             quota_exceeded=True,
                             topic=topic,
                             tone=tone)
    
    # Save the new API key to session first
    session['api_key'] = new_api_key
    
    # Try to generate captions with the new key
    try:
        captions = generate_instagram_captions(topic, tone, api_key=new_api_key)
        flash('API key saved and captions generated successfully!', 'success')
        
        return render_template('index.html', 
                             captions=captions, 
                             topic=topic, 
                             tone=tone,
                             has_session_key=True)
        
    except Exception as e:
        logging.error(f"Failed to generate captions with provided API key: {e}")
        error_message = str(e)
        
        # Check for specific error types
        if "authentication" in error_message.lower() or "invalid" in error_message.lower():
            flash('Invalid API key. Please check your OpenAI API key and try again.', 'error')
        elif "quota" in error_message.lower():
            flash('The provided API key has exceeded its quota. Please try a different key or use demo mode.', 'error')
        else:
            flash('Failed to generate captions. Please check your API key and try again.', 'error')
        
        return render_template('index.html', 
                             api_key_required=True,
                             topic=topic,
                             tone=tone)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route that handles both GET and POST requests"""
    
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic', '').strip()
        tone = request.form.get('tone', '').strip()
        use_mock = request.form.get('use_mock', '').strip() == 'true'
        trigger_api_setup = request.form.get('trigger_api_setup', '').strip() == 'true'
        
        # Handle API key setup trigger
        if trigger_api_setup:
            return render_template('index.html', 
                                 api_key_required=True,
                                 topic=topic,
                                 tone=tone,
                                 has_session_key=False)
        
        # Validate inputs
        if not topic:
            flash('Please enter a topic for your Instagram caption.', 'error')
            return redirect(url_for('index'))
        
        if not tone:
            flash('Please select a tone for your Instagram caption.', 'error')
            return redirect(url_for('index'))
        
        # Handle mock generation request
        if use_mock:
            captions = mock_generate_instagram_captions(topic, tone)
            flash('Demo captions generated successfully! (Mock mode)', 'success')
            return render_template('index.html', 
                                 captions=captions, 
                                 topic=topic, 
                                 tone=tone,
                                 is_mock=True)
        
        # Get API key from session only
        api_key = session.get('api_key', '')
        
        if not api_key:
            flash('Please provide your OpenAI API key to generate captions.', 'error')
            return render_template('index.html', 
                                 api_key_required=True,
                                 topic=topic,
                                 tone=tone,
                                 has_session_key=False)
        
        try:
            # Generate captions with session API key
            captions = generate_instagram_captions(topic, tone, api_key=api_key)
            flash('Captions generated successfully!', 'success')
            
            return render_template('index.html', 
                                 captions=captions, 
                                 topic=topic, 
                                 tone=tone,
                                 has_session_key=bool(session.get('api_key')))
            
        except Exception as e:
            logging.error(f"Error generating captions: {e}")
            error_message = str(e)
            
            # Check for specific error types
            if "quota exceeded" in error_message.lower() or "rate" in error_message.lower():
                return render_template('index.html', 
                                     quota_exceeded=True,
                                     topic=topic,
                                     tone=tone,
                                     api_key=api_key)
            elif "API key required" in error_message:
                flash('Please provide your OpenAI API key to generate captions.', 'error')
                return render_template('index.html', 
                                     api_key_required=True,
                                     topic=topic,
                                     tone=tone)
            elif "authentication" in error_message.lower() or "invalid" in error_message.lower():
                flash('Invalid API key. Please check your OpenAI API key and try again.', 'error')
                return render_template('index.html', 
                                     api_key_required=True,
                                     topic=topic,
                                     tone=tone)
            else:
                flash('An error occurred while generating captions. Please try again.', 'error')
                return render_template('index.html', 
                                     api_key_required=True,
                                     topic=topic,
                                     tone=tone)
    
    # GET request - show the form
    return render_template('index.html', has_session_key=bool(session.get('api_key')))

@app.route('/clear-session', methods=['POST'])
def clear_session():
    """Clear the stored API key from session"""
    session.pop('api_key', None)
    flash('Session API key cleared successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
