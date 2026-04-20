import os

from dotenv import load_dotenv
import anthropic


def main() -> None:
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    if not api_key:
        print("Missing ANTHROPIC_API_KEY in .env")
        return

    client = anthropic.Anthropic(
        api_key=api_key,
        timeout=30.0,
    )

    print("Sending test request...")

    response = client.messages.create(
        model=model,
        max_tokens=120,
        system="You are a helpful assistant for TT&R Elite content operations.",
        messages=[
            {
                "role": "user",
                "content": "Say hello and confirm the API connection is working."
            }
        ],
    )

    text_blocks = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text_blocks.append(block.text)

    print("\nResponse:")
    print("\n".join(text_blocks) if text_blocks else "No text returned.")


if __name__ == "__main__":
    main()