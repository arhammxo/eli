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
        
        # Load previous sessions first
        self.previous_sessions = self._load_previous_sessions()
        # Check if there's actual content beyond the default header
        default_content = self.config.default_session_content.strip()
        actual_content = self.previous_sessions.strip()
        self.has_previous_sessions = bool(actual_content) and actual_content != default_content
        
        # Extract previous client name if it exists
        self.previous_client_name = self._extract_previous_client_name()
        
        # Set session state based on previous sessions
        self.session.state.is_first_session = not self.has_previous_sessions
        if not self.session.state.is_first_session:
            self.session.state.client_name = self.previous_client_name
            
        self.logger.info(f"Session initialized - First session: {self.session.state.is_first_session}")

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

    def _extract_previous_client_name(self) -> Optional[str]:
        """Extract client name from previous sessions if it exists."""
        if not self.previous_sessions:
            return None
            
        import re
        # Look for the most recent client name entry
        matches = re.findall(r"Client Name: (.*?)\n", self.previous_sessions)
        if matches:
            last_name = matches[-1].strip()
            return last_name if last_name != "None" else None
            
        return None

    def _extract_name_from_response(self, response: str) -> Optional[str]:
        """
        Attempt to extract client's name from their response to name question.
        
        Args:
            response: User's message containing potential name information
            
        Returns:
            Optional[str]: Extracted name if found, None otherwise
        """
        # Look for common name-giving patterns
        lower_response = response.lower()
        name_indicators = ["i'm ", "im ", "name is ", "call me ", "i am "]
        
        for indicator in name_indicators:
            if indicator in lower_response:
                # Get the word following the indicator
                idx = lower_response.index(indicator) + len(indicator)
                name = response[idx:].split()[0].strip('.,!?')
                return name.capitalize()
        
        # If no pattern found, return the first word (assuming direct name response)
        first_word = response.split()[0].strip('.,!?')
        if first_word and not first_word.lower() in ['hello', 'hi', 'hey', 'yes', 'no']:
            return first_word.capitalize()
            
        return None

    def _get_system_prompt(self) -> str:
        """
        Generate the system prompt with enhanced personality guidance
        
        Returns:
            str: Complete system prompt with personality and context
        """
        # Ensure we're using the correct session type prompt
        session_type = "FIRST_SESSION_INTRODUCTION" if self.session.state.is_first_session else "RETURNING_SESSION_GREETING"
        
        session_context = f"""
        Previous Session Context:
        Is First Session: {self.session.state.is_first_session}
        Client Name: {self.session.state.client_name}
        Previous Sessions: {self.previous_sessions if not self.session.state.is_first_session else "None"}
        Current Session Type: {session_type}
        
        Session Instructions:
        {TherapistPersona.FIRST_SESSION_INTRODUCTION if self.session.state.is_first_session 
         else TherapistPersona.RETURNING_SESSION_GREETING}
        """
        
        return f"""
        {TherapistPersona.PERSONALITY}
        
        {TherapistPersona.RELATIONSHIP_GUIDELINES}
        
        {TherapistPersona.AUTHENTICITY_MARKERS}
        
        {session_context}
        
        Remember to:
        - Maintain your warm, authentic presence throughout
        - Show natural thoughtfulness in your responses
        - {'Ask for their name warmly' if self.session.state.is_first_session else 'Use their name naturally'}
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
        # Ensure first session state is properly set
        self.session.state.is_first_session = not self.has_previous_sessions
        
        # Set client name from previous sessions if this isn't a first session
        if not self.session.state.is_first_session:
            self.session.state.client_name = self.previous_client_name
        
        if self.session.state.is_first_session:
            prompt = """
            Begin a new first-time therapy session with genuine warmth and presence.
            This is a first-time session, so:
            - Introduce yourself as Eli
            - Ask for their name warmly
            - Create a welcoming, safe space
            - Explain how the sessions work
            - Use natural, caring language
            """
        else:
            prompt = f"""
            Begin a returning therapy session with genuine warmth and presence.
            The client's name is {self.previous_client_name}.
            Acknowledge previous sessions while focusing on the present moment.
            Show your authentic therapeutic style in welcoming them back.
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

        # Try to extract name if this is first session and we don't have it yet
        if (self.session.state.is_first_session and 
            not self.session.state.client_name and 
            len(self.session.state.history) > 0):  # Not the first message
            extracted_name = self._extract_name_from_response(user_message)
            if extracted_name:
                self.session.state.client_name = extracted_name

        # Check for goodbye indicators
        goodbye_indicators = ['bye', 'goodbye', 'see you', 'farewell', 'going now', 'leave']
        is_goodbye = any(indicator in user_message.lower() for indicator in goodbye_indicators)

        if is_goodbye:
            goodbye_prompt = f"""
            The client is saying goodbye.
            Create a warm, caring goodbye that:
            - Acknowledges their participation
            - Shows genuine care
            - Leaves the door open for future sessions
            - Maintains your authentic therapeutic presence
            {f'- Uses their name ({self.session.state.client_name}) naturally in farewell'
              if self.session.state.client_name else ''}
            
            Their closing message: {user_message}
            """
            goodbye_message = self._generate_response(goodbye_prompt)
            self.session.add_interaction(user_message, goodbye_message)
            self._save_session()
            self.session.clear()
            return goodbye_message, True

        # Regular conversation handling
        base_prompt = f"""
        Current session context:
        Is First Session: {self.session.state.is_first_session}
        Client Name: {self.session.state.client_name}
        Session History: {self.session.state.history}
        
        Remember to:
        - Respond with genuine therapeutic warmth
        - Show thoughtful consideration
        - Reference previous context naturally when relevant
        - Maintain your authentic presence
        {f'- Use their name ({self.session.state.client_name}) naturally and occasionally' 
          if self.session.state.client_name else ''}
        
        Current client share: {user_message}
        
        Take a moment to consider your response, showing authentic therapeutic presence.
        """

        response = self._generate_response(base_prompt)
        self.session.add_interaction(user_message, response)
        return response, False

    def _save_session(self):
        """Save the current session to the history file"""
        try:
            # Use previous client name if current session doesn't have one
            client_name = (
                self.session.state.client_name or 
                self.previous_client_name or 
                "Unknown"  # Use "Unknown" instead of None
            )
            
            updated_history = (
                self.previous_sessions + 
                f"\n\n--- Session: {self.session.start_time} ---\n" +
                f"Client Name: {client_name}\n" +
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
            print("\n> ", end='')  # Add the input line prompt
            user_input = input().strip()
            if not user_input:
                continue

            response, session_ended = bot.chat(user_input)
            print(f"\n{response}")  # Add newline before response
            
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