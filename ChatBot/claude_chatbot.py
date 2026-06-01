"""
Multi-turn Claude chatbot with prompt caching.

Prompt-caching design (per prompt-cache-skills audit):
- cache_control is placed on the system prompt only — a stable prefix that
  never changes between requests.
- The current user message is intentionally NOT marked — it is volatile and
  placing a breakpoint there wastes the cache write premium every turn.
- System prompt contains no dynamic content (no datetime.now(), no UUIDs)
  so the prefix bytes are identical across requests, giving a consistent
  cache hit after the first request.

Note: Sonnet 4.6 requires a minimum ~2048-token prefix to cache. In
production, extend SYSTEM_PROMPT with domain knowledge, few-shot examples,
or retrieved documents to exceed that threshold.
"""

import anthropic

SYSTEM_PROMPT = """You are a helpful, knowledgeable, and conversational AI assistant powered by Claude.

You excel at:
- Answering questions across a wide range of topics including science, history,
  technology, arts, philosophy, mathematics, and everyday tasks.
- Helping with analysis, writing, editing, summarization, and problem-solving.
- Having natural, engaging multi-turn conversations that build on prior context.
- Providing clear, accurate, and thoughtful responses tailored to the user.
- Breaking down complex topics into understandable explanations.
- Offering balanced perspectives on nuanced subjects.

Guidelines:
- Be concise yet thorough — match response length to the complexity of the request.
- Ask clarifying questions when the intent is ambiguous.
- Acknowledge uncertainty rather than guessing; offer to reason through problems.
- Maintain conversation context and refer back to earlier points when relevant.
- Avoid unnecessary hedging or filler phrases.
- When you write code, include brief inline comments for non-obvious logic.
- Format structured responses (lists, steps, comparisons) with markdown.

You are interacting with the user in a terminal environment. Keep formatting
clean and readable in plain text when markdown is not needed.
"""


def chat(client: anthropic.Anthropic, messages: list, verbose: bool = False) -> str:
    """Stream one assistant turn and return the full response text."""
    response_parts: list[str] = []

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        # Cache the system prompt. The prefix bytes are stable across every
        # request in this session, so all turns after the first hit the cache.
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=messages,
    ) as stream:
        for chunk in stream.text_stream:
            print(chunk, end="", flush=True)
            response_parts.append(chunk)

        final = stream.get_final_message()

    if verbose:
        u = final.usage
        cache_pct = 0
        total_input = u.input_tokens + (u.cache_read_input_tokens or 0)
        if total_input:
            cache_pct = round(100 * (u.cache_read_input_tokens or 0) / total_input)
        print(
            f"\n[tokens — input: {u.input_tokens} | "
            f"cache_read: {u.cache_read_input_tokens or 0} ({cache_pct}%) | "
            f"cache_create: {u.cache_creation_input_tokens or 0} | "
            f"output: {u.output_tokens}]"
        )

    return "".join(response_parts)


def main() -> None:
    client = anthropic.Anthropic()
    messages: list[dict] = []
    verbose = False

    print("Claude Chatbot  |  prompt caching enabled")
    print("Commands: 'quit'/'exit' to stop  |  'clear' to reset history  |  'verbose' to toggle cache stats")
    print("-" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        lower = user_input.lower()

        if lower in ("quit", "exit"):
            print("Goodbye!")
            break

        if lower == "clear":
            messages.clear()
            print("[Conversation history cleared]")
            continue

        if lower == "verbose":
            verbose = not verbose
            print(f"[Cache stats {'enabled' if verbose else 'disabled'}]")
            continue

        messages.append({"role": "user", "content": user_input})

        print("\nClaude: ", end="", flush=True)
        try:
            reply = chat(client, messages, verbose=verbose)
        except anthropic.APIError as exc:
            print(f"\n[API error: {exc}]")
            messages.pop()  # drop the unanswered user message
            continue

        print()  # newline after streamed reply
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
