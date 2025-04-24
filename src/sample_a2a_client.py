import asyncio
from a2a_min import A2aMinClient


async def client():
    """Run the example client"""
    client = A2aMinClient.connect("http://localhost:8000")
    task = await client.send_message("Hello, Echo Agent!")
    # Print the response
    for artifact in task.artifacts:
        for part in artifact.parts:
            if hasattr(part, "text"):
                print(f"Response: {part.text}")


if __name__ == "__main__":
    # Run the client
    #asyncio.run(client())
    string = """
    {
    "riddles": [
        "I wear red and white with pride on the field, in London I stand as my foes yield. With goals and hopes my team moves ahead, which club am I, by many widely led?",
        "In Premier and Champions League fights, I make lineup decisions and monitor rights—A leader's voice amid hopes and strife, who am I managing this football life?",
        "A warrior in red, whose contract's in doubt, pondering his stay, fans buzz and shout. Whose future at Emirates might shift and sway, who is this player contemplating away?"
    ],
    "answers": [
        "Arsenal Football Club",
        "Mikel Arteta",
        "An Arsenal star player"
    ],
    "hints": [
        "This club is famous for its red and white kit and London base.",
        "He leads the team and makes strategic choices on and off the pitch.",
        "This figure is vital to the team's success and currently has uncertain contract status."
    ]
}"""
    import json
    print(json.loads(string))
