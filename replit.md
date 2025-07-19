# Instagram Caption Generator

## Overview

This is a Flask-based web application that generates Instagram captions using OpenAI's GPT-4o model. The application provides a simple web interface where users can input a topic and tone to generate creative, engaging Instagram captions with emojis.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology**: HTML templates with Bootstrap for styling and custom CSS
- **Framework**: Flask's Jinja2 templating engine
- **UI Components**: Bootstrap-based responsive design with Font Awesome icons
- **Styling**: Uses Replit's Bootstrap dark theme with custom aesthetic enhancements
- **Visual Design**: Custom gradient backgrounds, glass morphism effects, animations
- **Typography**: Inter font family for modern, clean appearance
- **Interactive Elements**: Hover effects, loading animations, smooth transitions

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Single-file application (main.py) with template rendering
- **Session Management**: Flask's built-in session handling with secret key
- **Error Handling**: Comprehensive logging and graceful fallbacks

### API Integration
- **External Service**: OpenAI GPT-4o API for caption generation
- **Fallback Strategy**: Mock responses when OpenAI API is unavailable
- **Model**: Uses "gpt-4o" model specifically (latest as of May 2024)

## Key Components

### Main Application (main.py)
- **Flask App**: Core web application with secret key management
- **OpenAI Integration**: Conditional initialization based on API key availability
- **Logging**: Debug-level logging for troubleshooting
- **Caption Generation**: Function to create 3 Instagram captions per request with tone blending
- **Tone Blending**: Multiple selected tones are seamlessly combined into unified captions
- **Tone Variety**: Supports 27 different tone options for diverse caption styles
- **Tone Memory**: LocalStorage-based system to remember previously used tones
- **Quota Handling**: User-friendly quota exceeded detection with demo mode fallback
- **Custom API Key Support**: Seamless personal OpenAI API key integration for unlimited access
- **Mock Generation**: Enhanced tone-blending mock caption system with combined tone content
- **Tutorial System**: Animated walkthrough for first-time users with interactive spotlight and progress tracking

### Template System
- **Professional UI**: Custom generator card with centered header, minimalist form design, and gradient buttons
- **Form Handling**: POST method with loading animations and smooth transitions
- **Flash Messages**: User feedback system with custom styling
- **Interactive Elements**: Hover effects, copy-to-clipboard functionality, professional feature cards
- **Features Display**: Four feature cards highlighting tone blending, AI power, unlimited possibilities, and custom API key support
- **Loading States**: Spinner animations and smooth form submission feedback
- **Section Separators**: Clean typography-based separators with gradient accent lines
- **Tutorial Interface**: Animated overlay with spotlight effects, progress indicators, and step-by-step guidance

## Data Flow

1. **User Input**: User provides topic and selects multiple tones through web form
2. **Request Processing**: Flask handles POST request and extracts form data
3. **Tone Blending**: System combines multiple selected tones into unified prompts
4. **API Call**: Application calls OpenAI API with tone-blending structured prompt
5. **Response Generation**: GPT-4o generates 3 captions that blend all selected tones
6. **Result Display**: Generated blended captions are displayed to user with success message
7. **Error Handling**: Graceful quota handling with demo mode option

## User Experience Features

### Quota Management
- **Intelligent Detection**: Automatic detection of API quota exceeded errors
- **User-Friendly Modal**: Beautiful modal interface explaining the situation
- **Custom API Key Input**: Secure form for users to input their personal OpenAI API key
- **Demo Mode Option**: One-click fallback to enhanced mock generation
- **Helpful Tips**: Clear guidance on resolving quota issues
- **Seamless Transition**: Preserves user's topic and tone selections

### Enhanced Tone Blending System
- **Multi-Tone Fusion**: Seamlessly blends multiple tones into unified captions (e.g., "funny + romantic")
- **Intelligent Combinations**: Smart handling of tone pairs like "adventurous + chill" or "professional + funny"
- **Unified Caption Generation**: Each caption reflects ALL selected tones simultaneously
- **Instagram-Ready Format**: Includes relevant hashtags and emojis that capture the blended mood
- **Professional Quality**: High-quality content that authentically combines multiple emotional tones

### Tutorial Walkthrough System
- **First-Time User Detection**: Automatically shows tutorial for new users using localStorage tracking
- **Interactive Spotlight**: Animated spotlight highlighting key interface elements with pulsing border effects
- **6-Step Journey**: Comprehensive tour covering topic input, tone selection, generation, features, and completion
- **Smart Positioning**: Dynamic tooltip positioning with viewport boundary detection and smooth animations
- **Progress Tracking**: Visual progress bar and step counter with forward/backward navigation
- **Accessibility Features**: Skip option, overlay click to close, and keyboard-friendly interface
- **Mobile Optimized**: Responsive design with adjusted tooltip sizes and positioning for mobile devices
- **Persistent Access**: Floating help button for returning users to retake the tour anytime

## External Dependencies

### Required Libraries
- **Flask**: Web framework for handling HTTP requests and rendering templates
- **OpenAI**: Official OpenAI Python client for API integration
- **OS/Logging**: Built-in Python modules for environment and logging

### External Services
- **OpenAI API**: GPT-4o model for caption generation
- **Bootstrap CDN**: Frontend styling framework
- **Font Awesome CDN**: Icon library for UI elements

### Environment Variables
- **OPENAI_API_KEY**: Required for OpenAI API integration
- **SESSION_SECRET**: Flask session security (defaults to dev key)

## Deployment Strategy

### Environment Setup
- **Development**: Uses development secret key as fallback
- **Production**: Requires proper environment variables (OPENAI_API_KEY, SESSION_SECRET)
- **Graceful Degradation**: Application functions with mock responses if OpenAI unavailable

### Error Handling
- **API Failures**: Graceful fallback to mock responses
- **Missing Dependencies**: Warns and continues with reduced functionality
- **User Feedback**: Flash messages for both success and error states

### Security Considerations
- **Session Management**: Proper secret key handling for session security
- **Environment Variables**: API keys managed through environment variables
- **Input Validation**: Form data processed securely through Flask