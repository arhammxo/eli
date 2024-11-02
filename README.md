# 🤖 Eli - The Therapeutic Companion Bot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Eli is a sophisticated therapeutic companion bot designed to provide empathetic, thoughtful, and authentic conversational support. Built with the Claude API, Eli maintains the warmth and presence of a human therapist while adhering to professional therapeutic boundaries.

## 🌟 Features

- **Authentic Therapeutic Presence**: Engages with genuine warmth and empathy
- **Session Continuity**: Remembers previous conversations and references them naturally
- **Natural Language**: Uses conversational language while maintaining professional boundaries
- **Secure Session Management**: Automatically saves and manages session histories
- **Robust Error Handling**: Gracefully handles interruptions and edge cases
- **Configurable Personality**: Easily adjustable therapeutic style and response patterns

## 📋 Requirements

```
python >= 3.8
anthropic
```

## 🚀 Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/eli-therapybot.git
cd eli-therapybot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure your API key**
Update `config.py` with your Anthropic API key:
```python
api_key = "your-api-key-here"
```

4. **Run Eli**
```bash
python main.py
```

## 💬 Sample Interaction

```
=== Starting New Therapy Session ===

Eli: Hello! I'm Eli. I create a safe space for you to share whatever's on your mind. 
    How are you feeling today?

User: I've been feeling overwhelmed lately.

Eli: I hear how challenging things have been... Let's take a moment to explore what's 
    been contributing to that feeling of being overwhelmed. What would you like to 
    share about it?
```

## 🛠️ Configuration

The bot can be customized through the `ChatConfig` class in `config.py`:

```python
@dataclass
class ChatConfig:
    model_name: str = "claude-3-5-sonnet-20240620"
    max_tokens: int = 4096
    temperature: float = 0.9
    session_file: str = 'ps.txt'
    # ... more configuration options
```

## 📁 Project Structure

```
eli-therapybot/
├── main.py           # Main bot implementation
├── config.py         # Configuration and persona settings
├── file_manager.py   # Session history management
├── requirements.txt  # Project dependencies
└── README.md        # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🔑 Key Components

### TherapyBot
The main class that handles the conversation flow and API integration:
```python
class TherapyBot:
    def __init__(self, config: Optional[ChatConfig] = None):
        self.config = config or ChatConfig()
        self.session = TherapySession()
        # ... initialization
```

### TherapistPersona
Defines Eli's personality and therapeutic approach:
```python
class TherapistPersona:
    PERSONALITY = """
    You are Eli, a deeply empathetic and insightful therapist 
    with a warm, gentle presence...
    """
```

### FileManager
Handles session storage and retrieval with robust error handling:
```python
class FileManager:
    def __init__(self, logger: Optional[logging.Logger] = None,
                 auto_create: bool = True,
                 default_content: str = ""):
        # ... initialization
```

## ⚠️ Important Notes

- This is a companion bot, not a replacement for professional therapy
- All conversations are saved locally for continuity
- The bot requires a valid Anthropic API key to function
- Configure logging levels in `config.py` for different debugging needs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Anthropic's Claude API](https://www.anthropic.com/)
- Inspired by best practices in therapeutic conversation
- Thanks to all contributors and testers

---

Made with ❤️ by [Your Name]

*Remember: While Eli is designed to provide support, it is not a replacement for professional mental health services. If you're experiencing serious mental health issues, please seek help from a qualified mental health professional.*
