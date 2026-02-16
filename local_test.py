"""Local test script for the trackapp RL environment.

Development workflow:
1. Start the container with hot-reload: hud dev -w tasks -w grading --port 8765
2. Run this script: python local_test.py
3. Edit tasks/*.py or grading/*.py - container auto-reloads
4. Re-run this script to test changes
"""

import asyncio
import os

import hud
from hud import Environment
from hud.agents.claude import ClaudeAgent
from hud.settings import settings
from openai import AsyncOpenAI

# Create a clean Environment for client-side use.
# IMPORTANT: Do NOT import env from env.py here. Importing env.py registers
# @env.tool() bash/editor as LOCAL tools, which makes the router call them
# in-process (where _bash_tool is None) instead of routing to the container.
# With a fresh Environment, all tool calls route to the remote container.
env = Environment("coding")

# Use HUD inference gateway
client = AsyncOpenAI(base_url="https://inference.hud.ai", api_key=settings.api_key)

# Connect to running container
DEV_URL = os.getenv("HUD_DEV_URL", "http://localhost:8765/mcp")
#env.connect_url(DEV_URL)
env.connect_image("trackapp-rl-env:dev")


async def test_tools_standalone():
    """Test environment tools directly (no scenario)."""
    print("=== Test: Standalone Tools ===")
    print(f"Connecting to: {DEV_URL}")

    async with env:
        tools = env.as_tools()
        visible_tools = [t for t in tools if not t.name.startswith("_")]
        print(f"Agent-visible tools: {[t.name for t in visible_tools]}")

        result = await env.call_tool("bash", command="echo 'Hello from trackapp env'")
        print(f"Bash result: {result}")


async def test_scenario():
    """Test the fix-result-crud scenario with an agent."""
    print("\n=== Test: fix-result-crud Scenario ===")

    async with env:
        task = env("fix-result-crud")

        async with hud.eval(task, trace=True) as ctx:
            agent = ClaudeAgent.create(model="claude-sonnet-4-5")
            await agent.run(ctx, max_steps=20)


async def main():
    print("Trackapp RL Environment - Local Test")
    print("=" * 50)
    print(f"Container URL: {DEV_URL}")
    print("Make sure the container is running:")
    print("  hud dev -w tasks -w grading --port 8765")
    print("=" * 50)
    print()

    await test_tools_standalone()

    # Uncomment to run scenario with agent:
    # await test_scenario()


if __name__ == "__main__":
    asyncio.run(main())
