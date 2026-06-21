from einstein_ai.einstein_bot import get_einstein_bot
from einstein_ai.utils import logger, sync_dependencies, log_interaction
from einstein_ai.ingest import ingest_docs
import sys
import os
import subprocess

def main():
    # Attempt auto-update on launch
    sync_dependencies()

    # Self-learning: re-index on launch to incorporate new history/sources
    print("Einstein AI is refreshing its memory...")
    try:
        ingest_docs()
    except Exception as e:
        logger.warning(f"Memory refresh failed: {e}")

    # Check if we should launch GUI or CLI
    # If on Windows and no arguments, prefer GUI
    if os.name == 'nt' and len(sys.argv) == 1:
        # Check if the PowerShell script exists
        ps_script = os.path.join(os.getcwd(), "EinsteinAI.ps1")
        if os.path.exists(ps_script):
            print("Launching Einstein AI GUI...")
            subprocess.Popen(["powershell.exe", "-WindowStyle", "Hidden", "-File", ps_script])
            sys.exit(0)

    print("========================================")
    print("      Einstein AI Initializing...      ")
    print("========================================")

    try:
        bot = get_einstein_bot()
    except Exception as e:
        logger.error(f"Error initializing Einstein AI: {e}")
        sys.exit(1)

    print("\nEinstein AI is ready. You can ask me anything.")
    print("To end the session, type 'exit', 'quit', 'bye', or 'stop'.\n")

    while True:
        try:
            user_input = input("You: ")

            # Check for multiple exit commands
            if user_input.lower().strip() in ['exit', 'quit', 'bye', 'goodbye', 'stop']:
                print("\nEinstein: Farewell, my friend. Keep wondering.")
                break

            if not user_input.strip():
                continue

            print("\nEinstein is thinking...", end="\r")
            result = bot.invoke({"query": user_input})
            bot_response = result['result']

            # Log the interaction for future learning
            log_interaction(user_input, bot_response)

            print(" " * 30, end="\r") # Clear thinking message
            print(f"Einstein: {bot_response}\n")

        except KeyboardInterrupt:
            print("\n\nEinstein: Farewell, my friend. Keep wondering.")
            break
        except Exception as e:
            logger.error(f"Einstein encountered an error: {e}")
            print(f"\nEinstein: I am sorry, I encountered an error: {e}\n")

if __name__ == "__main__":
    main()
