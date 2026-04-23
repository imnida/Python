"""
Multi-turn conversation chatbot using the Anthropic Claude API.
Usage: python claude_chat.py
Requires: pip install anthropic
Set ANTHROPIC_API_KEY environment variable before running.
"""

import os
import anthropic

SYSTEM_PROMPT = """You are a helpful AI assistant with expertise in Python and data science.
You help the user understand their code, debug issues, and learn new concepts.
Be concise, clear, and provide working code examples when relevant."""

MODEL = "claude-opus-4-7"


def chat():
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    messages = []

    print("Claude Chat — tapez 'quit' ou 'exit' pour quitter, 'reset' pour effacer l'historique.")
    print("-" * 60)

    while True:
        try:
            user_input = input("\nVous: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Au revoir!")
            break

        if user_input.lower() == "reset":
            messages = []
            print("Historique effacé.")
            continue

        messages.append({"role": "user", "content": user_input})

        print("\nClaude: ", end="", flush=True)

        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=messages,
        ) as stream:
            response_text = ""
            for event in stream:
                if event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        print(event.delta.text, end="", flush=True)
                        response_text += event.delta.text

        print()
        messages.append({"role": "assistant", "content": response_text})

        final = stream.get_final_message()
        usage = final.usage
        cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
        if cache_read:
            print(f"  [tokens: in={usage.input_tokens}, out={usage.output_tokens}, cache_hit={cache_read}]")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Erreur: définissez la variable d'environnement ANTHROPIC_API_KEY")
        raise SystemExit(1)
    chat()
