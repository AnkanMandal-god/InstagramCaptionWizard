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

def mock_generate_instagram_captions(topic, tone, length="medium"):
    """Mock fallback function for generating Instagram captions that blend multiple tones"""
    
    # Handle multiple tones
    tones = [t.strip().lower() for t in tone.split(',') if t.strip()]
    
    # Create tone description for hashtags
    tone_hashtags = ''.join([f"#{t.title()}" for t in tones])
    
    # Generate captions based on length preference
    if length == "short":
        # Short captions (1-2 sentences)
        if 'funny' in tones and 'romantic' in tones:
            captions = f"""1. {topic} = instant love-laugh combo 😂💕 #{topic.replace(' ', '')}Love {tone_hashtags}
2. Found my {topic} comedy-romance match 🤪❤️ #{topic.replace(' ', '')}Magic {tone_hashtags}
3. {topic} + giggles + heart eyes ✨ #{topic.replace(' ', '')}Vibes {tone_hashtags}"""
        else:
            tone_blend = ' and '.join(tones)
            captions = f"""1. {topic} + {tone_blend} energy ✨ #{topic.replace(' ', '')}Magic {tone_hashtags}
2. Perfect {tone_blend} vibes 🌟 #{topic.replace(' ', '')}Mood {tone_hashtags}
3. {topic} through {tone_blend} lens 💫 #{topic.replace(' ', '')}Life {tone_hashtags}"""
    
    elif length == "long":
        # Long captions (5+ sentences)
        if 'funny' in tones and 'romantic' in tones:
            captions = f"""1. So here's the thing about {topic} - it's got me feeling like the main character in a romantic comedy, except I can't tell if I'm falling in love or just falling over my own two feet. Either way, I'm here for this chaotic energy that somehow makes perfect sense. Life's too short not to laugh at your own love story, right? Sometimes the best relationships are built on inside jokes and shared adventures. This is what happens when romance meets comedy in real life. 😂💕 #{topic.replace(' ', '')}Love {tone_hashtags} #RomCom
2. They told me {topic} was serious business, but nobody warned me I'd be over here making heart eyes while simultaneously crafting the world's corniest jokes. Plot twist: apparently you can be swoony AND silly at the same time, and honestly? It's the best combination I never knew I needed. When you find someone who laughs at your terrible puns and still thinks you're attractive, you hold onto that forever. This is what happens when humor meets heart. 🤪❤️ #{topic.replace(' ', '')}Magic {tone_hashtags} #LoveAndLaughs
3. Update from the front lines of {topic}: I've discovered that the secret ingredient to everything is being equal parts dreamy romantic and absolute goofball. Some days you're writing poetry, other days you're making terrible jokes, but every day you're authentically, beautifully, chaotically yourself. And that's the kind of energy I'm bringing to everything now. Because why choose between heart eyes and belly laughs when you can have both? ✨ #{topic.replace(' ', '')}Vibes {tone_hashtags} #AuthenticChaos"""
        else:
            tone_blend = ' and '.join(tones)
            captions = f"""1. There's something magical that happens when you approach {topic} with {tone_blend} energy - suddenly everything feels more intentional, more meaningful, more authentically you. It's like finding the perfect filter for life, except instead of changing how you look, it changes how you feel about everything around you. This is what happens when you stop forcing yourself into boxes and start embracing the beautiful complexity of who you actually are. Why settle for one-dimensional when life is meant to be a full spectrum experience? ✨ #{topic.replace(' ', '')}Magic {tone_hashtags} #Authentic
2. Been thinking a lot about how {topic} hits different when you're channeling that perfect {tone_blend} vibe. It's not about being one thing or another - it's about finding that sweet spot where all parts of your personality can coexist and actually enhance each other. Like a perfectly balanced playlist where every song flows into the next, creating something bigger than the sum of its parts. This is how we're meant to live - not in rigid categories, but in beautiful, flowing authenticity. 🌟 #{topic.replace(' ', '')}Mood {tone_hashtags} #RealTalk
3. Here's what I've learned about seeing {topic} through a {tone_blend} lens: it's not just about changing your perspective, it's about expanding it. When you allow yourself to hold space for seemingly contradictory energies, you create room for growth, for surprise, for the kind of authentic moments that make life feel less like performance and more like art. This is how I choose to see the world now - complex, nuanced, and beautifully contradictory, just like life should be. 💫 #{topic.replace(' ', '')}Life {tone_hashtags} #BeYou"""
    
    else:
        # Medium captions (3-4 sentences) - default
        if 'funny' in tones and 'romantic' in tones:
            captions = f"""1. When {topic} makes you laugh until you fall in love all over again 😂💕 Can't tell if I'm falling for the moment or just falling over my own feet, but either way I'm here for it! This is what happens when romance meets comedy in the best possible way. #{topic.replace(' ', '')}Love {tone_hashtags} #RomCom
2. Found someone who thinks my {topic} jokes are actually romantic... definitely a keeper! 🤪❤️ Plot twist: apparently you can be swoony AND silly at the same time, and honestly? It's the perfect combination I never knew I needed. #{topic.replace(' ', '')}Magic {tone_hashtags} #LoveAndLaughs
3. They say laughter is the best medicine, but {topic} with you is pure magic 😍🎭 Some days you're writing poetry, other days you're making terrible puns, but every day you're authentically, beautifully, chaotically yourself. This is my kind of energy! ✨ #{topic.replace(' ', '')}Vibes {tone_hashtags} #AuthenticChaos"""
        
        elif 'adventurous' in tones and 'chill' in tones:
            captions = f"""1. Finding adventure in {topic} while keeping my zen intact 🏔️☮️ It's called balanced exploration, and I'm absolutely here for it! Sometimes the best adventures happen when you're completely relaxed about the outcome. #{topic.replace(' ', '')}Balance {tone_hashtags} #AdventurousZen
2. Sometimes the best adventures happen when you're completely relaxed about {topic} 🌊✨ Ready for anything but also totally fine doing absolutely nothing - it's the perfect mindset! Both mountain climbing and Netflix marathons count as valid exploration. #{topic.replace(' ', '')}Vibes {tone_hashtags} #ChillAdventure
3. Peaceful exploration of {topic} - because not all adventures need adrenaline 🧘‍♀️🗺️ Found my sweet spot: adventurous enough to try new things, chill enough to actually enjoy them. Perfect balance between pushing boundaries and savoring moments! #{topic.replace(' ', '')}Journey {tone_hashtags} #MindfulAdventure"""
        
        elif 'professional' in tones and 'funny' in tones:
            captions = f"""1. Bringing humor to the workplace: {topic} edition 💼😄 Turns out balancing business acumen with a healthy sense of humor is actually the secret sauce. Who knew professionalism could be this fun? #{topic.replace(' ', '')}Success {tone_hashtags} #ProfessionallyFunny
2. When {topic} meets corporate comedy - productivity through laughter! 📈🎭 Apparently you can close deals AND crack jokes - revolutionary concept, honestly. Serious goals don't always require serious faces. #{topic.replace(' ', '')}Growth {tone_hashtags} #BusinessHumor
3. Serious about success, silly about everything else - especially {topic} 🎯😂 The best boardrooms have the best laughs, and I'm here to prove it. Sometimes the best ideas come from the silliest moments! #{topic.replace(' ', '')}Life {tone_hashtags} #WorkHardLaughHard"""
        
        elif len(tones) > 2:
            # For multiple complex tones
            tone_blend = ', '.join(tones[:-1]) + f', and {tones[-1]}'
            captions = f"""1. {topic} hits different when you blend {tone_blend} energy together ✨ There's something beautiful about embracing all facets of who you are instead of picking just one. Why choose one vibe when you can be authentically multifaceted? #{topic.replace(' ', '')}Fusion {tone_hashtags} #Authentic
2. Why choose one vibe when {topic} can be {tone_blend} all at once? 🌟 It's not about being one thing or another - it's about being completely, authentically you. Complex, nuanced, and beautifully contradictory! #{topic.replace(' ', '')}Multifaceted {tone_hashtags} #RealTalk
3. Embracing every shade of {topic} - {tone_blend} and unapologetically me 💫 When you allow yourself to hold space for seemingly contradictory energies, you create room for authentic growth. This is how I choose to see the world! #{topic.replace(' ', '')}Journey {tone_hashtags} #BeYou"""
        
        else:
            # Default blended approach for any two tones
            tone_blend = ' and '.join(tones)
            captions = f"""1. When {topic} meets {tone_blend} energy - pure magic happens ✨ There's something beautiful about embracing all facets of who you are instead of picking just one. This is what authentic living looks like! #{topic.replace(' ', '')}Magic {tone_hashtags} #Authentic
2. Blending {tone_blend} vibes with {topic} for the perfect mood 🌟 It's not about being one thing or another - it's about being authentically, completely you. Complex and beautifully contradictory! #{topic.replace(' ', '')}Vibes {tone_hashtags} #RealTalk
3. {topic} through a {tone_blend} lens - this is how I see the world 💫 When you stop forcing yourself into boxes and start embracing beautiful complexity, everything feels more meaningful. This is my authentic energy! #{topic.replace(' ', '')}Perspective {tone_hashtags} #BeYou"""
    
    return clean_caption_content(captions)

def generate_instagram_captions(topic, tone, length="medium", api_key=None):
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
        raise Exception(f"Failed to initialize OpenAI client: {str(e)}")
    
    try:
        # Build tone description for multiple tones
        if len(tones) == 1:
            tone_description = tones[0]
        elif len(tones) == 2:
            tone_description = f"{tones[0]} and {tones[1]} combined"
        else:
            tone_description = f"{', '.join(tones[:-1])}, and {tones[-1]} blended together"
        
        # Define length specifications
        length_specs = {
            "short": "1-2 sentences, concise and punchy",
            "medium": "3-4 sentences, balanced detail",
            "long": "5+ sentences, detailed and storytelling"
        }
        
        length_instruction = length_specs.get(length, length_specs["medium"])
        
        # Create comprehensive prompt for blended tone caption generation
        prompt = f"""Generate Instagram captions for the topic "{topic}" that seamlessly blend {tone_description} into each caption.

Requirements:
- Create exactly 3 unique captions where EACH caption embodies ALL selected tones simultaneously
- Each caption should be a fusion of {tone_description}, not separate tones
- Length: {length_instruction}
- Include relevant hashtags that capture the blended mood and topic
- Add appropriate emojis that enhance the combined message
- Make each caption Instagram-ready (engaging, shareable, authentic)

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
        
        content = response.choices[0].message.content
        if content:
            content = content.strip()
        else:
            content = ""
        
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
        length = request.form.get('length', 'medium').strip()
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
            captions = mock_generate_instagram_captions(topic, tone, length)
            flash('Demo captions generated successfully! (Mock mode)', 'success')
            return render_template('index.html', 
                                 captions=captions, 
                                 topic=topic, 
                                 tone=tone,
                                 length=length,
                                 is_mock=True)
        
        # Get API key from form or session (hybrid approach)
        api_key = request.form.get('api_key', '').strip()
        save_for_session = request.form.get('save_for_session') == 'true'
        
        # Use session key if no form key provided
        if not api_key:
            api_key = session.get('api_key', '')
        
        if not api_key:
            flash('Please provide your OpenAI API key to generate captions.', 'error')
            return render_template('index.html', 
                                 api_key_required=True,
                                 topic=topic,
                                 tone=tone,
                                 length=length,
                                 has_session_key=bool(session.get('api_key')))
        
        # Save to session if checkbox is checked
        if save_for_session and api_key:
            session['api_key'] = api_key
            session.permanent = True
        
        try:
            # Generate captions with session API key
            captions = generate_instagram_captions(topic, tone, length, api_key=api_key)
            flash('Captions generated successfully!', 'success')
            
            return render_template('index.html', 
                                 captions=captions, 
                                 topic=topic, 
                                 tone=tone,
                                 length=length,
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
