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

def mock_generate_instagram_captions(topic, tone):
    """Mock fallback function for generating Instagram captions with multi-tone support"""
    
    # Handle multiple tones
    tones = [t.strip() for t in tone.split(',') if t.strip()]
    
    mock_captions = []
    
    for current_tone in tones:
        tone_section = f"**{current_tone.title()} Tone:**\n"
        
        # Generate tone-specific mock captions
        if current_tone.lower() in ['funny', 'humorous', 'comedy']:
            tone_section += f"""1. When {topic} hits different and you can't stop laughing 😂 #FunnyMoments #{topic.replace(' ', '')}Life #Comedy
2. Me trying to be serious about {topic} but failing miserably 🤪 #CannotBeSerious #{topic.replace(' ', '')}Humor #LOL
3. {topic}: Because normal is overrated anyway! 🎭 #WeirdAndProud #{topic.replace(' ', '')}Fun #Hilarious"""
        
        elif current_tone.lower() in ['romantic', 'love', 'dreamy']:
            tone_section += f"""1. Lost in the magic of {topic} with you by my side 💕 #RomanticMoments #{topic.replace(' ', '')}Love #TogetherForever
2. Every moment with {topic} feels like a fairytale come true ✨ #LoveStory #{topic.replace(' ', '')}Dreams #Soulmate
3. You, me, and {topic} - the perfect recipe for forever 💖 #EndlessLove #{topic.replace(' ', '')}Romance #MyHeart"""
        
        elif current_tone.lower() in ['adventurous', 'adventure', 'thrill']:
            tone_section += f"""1. Life begins at the end of your comfort zone! {topic} adventure mode: ON 🏔️ #AdventureTime #{topic.replace(' ', '')}Adventure #ExploreMore
2. Chasing thrills and making memories with {topic} 🌟 #LiveBoldly #{topic.replace(' ', '')}Explorer #AdventureSeeker
3. Not all who wander are lost - sometimes they're just finding {topic}! 🗺️ #Wanderlust #{topic.replace(' ', '')}Journey #BoldChoices"""
        
        elif current_tone.lower() in ['chill', 'relaxed', 'calm']:
            tone_section += f"""1. Just vibing with {topic} and loving every peaceful moment 🌅 #ChillVibes #{topic.replace(' ', '')}Life #RelaxMode
2. Sometimes the best therapy is {topic} and good vibes ☮️ #CalmMoments #{topic.replace(' ', '')}Peace #Mindful
3. Finding zen in {topic} - no rush, just pure bliss 🧘‍♀️ #SlowLiving #{topic.replace(' ', '')}Zen #Peaceful"""
        
        elif current_tone.lower() in ['professional', 'business', 'corporate']:
            tone_section += f"""1. Elevating standards with {topic} - excellence is not negotiable 💼 #ProfessionalGrowth #{topic.replace(' ', '')}Excellence #Leadership
2. Strategic focus on {topic} drives sustainable success 📈 #BusinessMindset #{topic.replace(' ', '')}Strategy #Innovation
3. Investing in {topic} today for tomorrow's breakthrough results 🎯 #ProfessionalDevelopment #{topic.replace(' ', '')}Success #Growth"""
        
        else:
            # Generic captions for any other tone
            tone_section += f"""1. Embracing {topic} with a {current_tone} attitude! 🌟 #{current_tone.title()}Vibes #{topic.replace(' ', '')}Life #Authentic
2. When {topic} meets {current_tone} energy - magic happens ✨ #{current_tone.title()}Mood #{topic.replace(' ', '')}Journey #RealTalk
3. Living my {current_tone} truth through {topic} every single day 💫 #{current_tone.title()}Life #{topic.replace(' ', '')}Story #BeYou"""
        
        mock_captions.append(tone_section)
    
    return '\n\n'.join(mock_captions)

def generate_instagram_captions(topic, tone):
    """Generate Instagram captions using OpenAI GPT-4o API with multi-tone support"""
    
    # Handle multiple tones
    tones = [t.strip() for t in tone.split(',') if t.strip()]
    
    if not openai_client:
        # If no OpenAI client available, show error message
        raise Exception("OpenAI API is not available. Please check your API key configuration.")
    
    try:
        # Build tone description for multiple tones
        if len(tones) == 1:
            tone_description = tones[0]
        elif len(tones) == 2:
            tone_description = f"{tones[0]} and {tones[1]}"
        else:
            tone_description = f"{', '.join(tones[:-1])}, and {tones[-1]}"
        
        # Create comprehensive prompt for multi-tone caption generation
        base_prompt = f"""Generate Instagram captions for the topic "{topic}" with a {tone_description} tone.

Requirements:
- Create 3 unique, engaging captions for each tone mentioned
- Include relevant hashtags that match the tone and topic
- Add appropriate emojis that enhance the message
- Make each caption Instagram-ready (engaging, shareable, authentic)
- Keep captions concise but impactful

Tones to address: {', '.join(tones)}

Format your response as:
**{tones[0].title()} Tone:**
1. [caption with emojis and hashtags]
2. [caption with emojis and hashtags]
3. [caption with emojis and hashtags]
"""
        
        # Add additional tone sections if more than one tone
        if len(tones) > 1:
            for tone in tones[1:]:
                base_prompt += f"""
**{tone.title()} Tone:**
1. [caption with emojis and hashtags]
2. [caption with emojis and hashtags]
3. [caption with emojis and hashtags]
"""
        
        prompt = base_prompt
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert social media content creator specializing in Instagram captions. You create engaging, authentic captions that drive engagement and match specific tones perfectly."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        # Check for quota exceeded or other specific errors
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            raise Exception("OpenAI API quota exceeded. Please check your usage limits and try again later.")
        elif "authentication" in str(e).lower():
            raise Exception("OpenAI API authentication failed. Please check your API key.")
        else:
            raise Exception(f"OpenAI API error: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route that handles both GET and POST requests"""
    
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic', '').strip()
        tone = request.form.get('tone', '').strip()
        use_mock = request.form.get('use_mock', '').strip() == 'true'
        
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
            error_message = str(e)
            
            # Check if it's a quota exceeded error
            if "quota exceeded" in error_message.lower() or "rate" in error_message.lower():
                # Show quota exceeded page with option to use mock
                return render_template('index.html', 
                                     quota_exceeded=True,
                                     topic=topic,
                                     tone=tone)
            elif "OpenAI API is not available" in error_message:
                flash('OpenAI API is not configured. Please check your API key setup.', 'error')
            elif "authentication failed" in error_message.lower():
                flash('OpenAI API authentication failed. Please check your API key.', 'error')
            else:
                flash('An error occurred while generating captions. Please try again.', 'error')
            
            return redirect(url_for('index'))
    
    # GET request - show the form
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
