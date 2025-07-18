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
- **Caption Generation**: Function to create 3 Instagram captions per request
- **Tone Variety**: Supports 15 different tone options for diverse caption styles

### Template System
- **Professional UI**: Custom generator card with centered header, minimalist form design, and gradient buttons
- **Form Handling**: POST method with loading animations and smooth transitions
- **Flash Messages**: User feedback system with custom styling
- **Interactive Elements**: Hover effects, copy-to-clipboard functionality, professional feature cards
- **Statistics Display**: Centered feature cards with gradient icons and professional typography
- **Loading States**: Spinner animations and smooth form submission feedback
- **Section Separators**: Clean typography-based separators with gradient accent lines

## Data Flow

1. **User Input**: User provides topic and tone through web form
2. **Request Processing**: Flask handles POST request and extracts form data
3. **API Call**: Application calls OpenAI API with structured prompt
4. **Response Generation**: GPT-4o generates 3 numbered captions with emojis
5. **Result Display**: Generated captions are displayed to user with success message
6. **Error Handling**: Fallback to mock responses if API fails

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