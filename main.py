from einstein_ai.einstein_bot import get_einstein_bot
from einstein_ai.utils import logger, sync_dependencies
import sys
import os

def main():
    # Attempt auto-update on launch
    sync_dependencies()

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

            print(" " * 30, end="\r") # Clear thinking message
            print(f"Einstein: {result['result']}\n")

        except KeyboardInterrupt:
            print("\n\nEinstein: Farewell, my friend. Keep wondering.")
            break
        except Exception as e:
            logger.error(f"Einstein encountered an error: {e}")
            print(f"\nEinstein: I am sorry, I encountered an error: {e}\n")

if __name__ == "__main__":
    main()
