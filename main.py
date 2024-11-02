"""
Enhanced therapy bot implementation with authentic therapeutic presence and improved session handling.
"""

import logging
from datetime import datetime
from typing import Optional, Tuple
from anthropic import Anthropic
from config import ChatConfig, SessionState, TherapistPersona
from file_manager import FileManager

class TherapySession:
    """Manages the therapy session state and history"""
    def __init__(self):
        self.state = SessionState()
        self.start_time = datetime.now().isoformat()
        
    def add_interaction(self, user_message: str, bot_response: str):
        """Add a new interaction to the session history"""
        self.state.history += f"\nUser: {user_message}"
        self.state.history += f"\nEli: {bot_response}\n\n"

    def clear(self):
        """Clear the session history and mark as inactive"""
        self.state.history = ""
        self.state.is_active = False

class TherapyBot:
    """Main therapy chatbot class with enhanced authentic presence"""
    def __init__(self, config: Optional[ChatConfig] = None):
        """
        Initialize TherapyBot with configuration
        
        Args:
            config: Optional configuration override
        """
        self.config = config or ChatConfig()
        self.setup_logging()
        
        self.session = TherapySession()
        self.client = Anthropic(api_key=self.config.api_key)
        
        self.file_manager = FileManager(
            logger=self.logger,
            auto_create=self.config.auto_create_files,
            default_content=self.config.default_session_content
        )
        
        self.previous_sessions = self._load_previous_sessions()
        self.has_previous_sessions = bool(self.previous_sessions.strip())

    def setup_logging(self):
        """Set up logging for the therapy bot"""
        self.logger = logging.getLogger('TherapyBot')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(self.config.log_level)

    def _load_previous_sessions(self) -> str:
        """
        Load previous session history from file
        
        Returns:
            str: Previous session history or empty string if none exists
        """
        result = self.file_manager.read_file(self.config.session_file)
        
        if not result.success:
            self.logger.error(f"Failed to load sessions: {result.error}")
            return ""
            
        if result.was_created:
            self.logger.info(f"Created new session file: {self.config.session_file}")
            
        return result.data or ""

    def _get_system_prompt(self) -> str:
        """
        Generate the system prompt with enhanced personality guidance
        
        Returns:
            str: Complete system prompt with personality and context
        """
        return f"""
        {TherapistPersona.PERSONALITY}
        
        {TherapistPersona.RELATIONSHIP_GUIDELINES}
        
        {TherapistPersona.AUTHENTICITY_MARKERS}
        
        Previous Session Context:
        You have access to and should naturally reference these previous sessions when relevant:
        {self.previous_sessions}
        
        Remember to:
        - Maintain your warm, authentic presence throughout
        - Show natural thoughtfulness in your responses
        - Reference past sessions in a natural, caring way
        - Keep your therapeutic wisdom wrapped in genuine warmth
        
        {TherapistPersona.RULES}
        """

    def _generate_response(self, prompt: str) -> str:
        """
        Generate a response using the Claude API
        
        Args:
            prompt: The input prompt for response generation
            
        Returns:
            str: Generated response text
        """
        try:
            response = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                system=self._get_system_prompt(),
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble formulating my response right now. Could we pause for a moment and try again?"

    def start_session(self) -> str:
        """
        Start a new therapy session with authentic warmth
        
        Returns:
            str: Initial session greeting
        """
        self.session = TherapySession()
        
        prompt = """
        Begin a new therapy session with genuine warmth and presence. 
        If there are previous sessions, acknowledge them naturally while focusing on 
        the present moment. Show your authentic therapeutic style in welcoming them 
        to share whatever feels important today.
        
        Remember to:
        - Start with genuine warmth
        - Show thoughtful presence
        - Create a safe, inviting space
        - Use natural, caring language
        """
        
        response = self._generate_response(prompt)
        self.session.add_interaction("New session started", response)
        return response

    def chat(self, user_message: str) -> Tuple[str, bool]:
        """
        Process user message with authentic therapeutic presence
        
        Args:
            user_message: The user's input message
            
        Returns:
            Tuple[str, bool]: (response message, whether session has ended)
        """
        if not self.session.state.is_active:
            return "Session has ended. Please start a new session.", True

        base_prompt = f"""
        Current session context: {self.session.state.history}
        
        Remember to:
        - Respond with genuine therapeutic warmth
        - Show thoughtful consideration
        - Reference previous context naturally when relevant
        - Maintain your authentic presence
        
        Current client share: {user_message}
        
        Take a moment to consider your response, showing authentic therapeutic presence.
        """

        response = self._generate_response(base_prompt)

        if response == "null":
            goodbye_prompt = f"""
            The client has indicated they'd like to end our session.
            Create a warm, caring goodbye that:
            - Acknowledges their participation
            - Shows genuine care
            - Leaves the door open for future sessions
            - Maintains your authentic therapeutic presence
            
            Their closing message: {user_message}
            """
            goodbye_message = self._generate_response(goodbye_prompt)
            self.session.add_interaction(user_message, goodbye_message)
            self._save_session()
            self.session.clear()
            return goodbye_message, True

        self.session.add_interaction(user_message, response)
        return response, False

    def _save_session(self):
        """Save the current session to the history file"""
        try:
            updated_history = (
                self.previous_sessions + 
                f"\n\n--- Session: {self.session.start_time} ---\n" +
                self.session.state.history
            )
            result = self.file_manager.write_file(
                self.config.session_file, 
                updated_history
            )
            
            if not result.success:
                self.logger.error(f"Failed to save session: {result.error}")
                
        except Exception as e:
            self.logger.error(f"Unexpected error saving session: {e}")

def main():
    """Main function to run the therapy chatbot"""
    # Initialize the bot with default configuration
    bot = TherapyBot()
    
    print("\n=== Starting New Therapy Session ===\n")
    
    # Start the session
    initial_response = bot.start_session()
    print(initial_response)

    # Main conversation loop
    while True:
        try:
            user_input = input().strip()
            if not user_input:
                continue

            response, session_ended = bot.chat(user_input)
            print(response)
            
            if session_ended:
                print("\n=== Session Ended ===\n")
                break
                
        except KeyboardInterrupt:
            print("\n\n=== Session Interrupted ===\n")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()