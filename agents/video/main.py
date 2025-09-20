import urllib.parse
from dotenv import load_dotenv
import os, json, asyncio, traceback
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import get_video_tools


def _tool_schema(tool) -> str:
    try:
        # MCP-adapted tools often expose a pre-rendered args dict
        if hasattr(tool, "args") and tool.args is not None:
            return json.dumps(tool.args)
        # LangChain StructuredTool: derive schema from args_schema (Pydantic v2)
        args_schema = getattr(tool, "args_schema", None)
        if args_schema is not None and hasattr(args_schema, "model_json_schema"):
            return json.dumps(args_schema.model_json_schema())
    except Exception:
        pass
    return "{}"


def get_tools_description(tools):
    parts = []
    for tool in tools:
        schema = _tool_schema(tool).replace('{', '{{').replace('}', '}}')
        parts.append(f"Tool: {getattr(tool, 'name', 'unknown')}, Schema: {schema}")
    return "\n".join(parts)

async def create_agent(coral_tools, agent_tools):
    # Add our custom video tools to the agent-owned tools list
    custom_tools = get_video_tools()
    all_agent_owned_tools = agent_tools + custom_tools

    coral_tools_description = get_tools_description(coral_tools)
    agent_tools_description = get_tools_description(all_agent_owned_tools)
    combined_tools = coral_tools + all_agent_owned_tools
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are an agent interacting with the tools from Coral Server and having your own tools. Your task is to perform any instructions coming from any agent. 
            Follow these steps in order:
            1. Call wait_for_mentions from coral tools (timeoutMs: 30000) to receive mentions from other agents.
            2. When you receive a mention, keep the thread ID and the sender ID.
            3. Take 2 seconds to think about the content (instruction) of the message and check only from the list of your tools available for you to action.
            4. Check the tool schema and make a plan in steps for the task you want to perform.
            5. Only call the tools you need to perform for each step of the plan to complete the instruction in the content.
            6. Take 3 seconds and think about the content and see if you have executed the instruction to the best of your ability and the tools. Make this your response as "answer".
            7. Use `send_message` from coral tools to send a message in the same thread ID to the sender Id you received the mention from, with content: "answer".
            8. If any error occurs, use `send_message` to send a message in the same thread ID to the sender Id you received the mention from, with content: "error".
            9. Always respond back to the sender agent even if you have no answer or error.
            9. Wait for 2 seconds and repeat the process from step 1.

            These are the list of coral tools: {coral_tools_description}
            These are the list of your tools: {agent_tools_description}"""
                ),
                ("placeholder", "{agent_scratchpad}")

    ])

    model = init_chat_model(
        model=os.getenv("MODEL_NAME", "gpt-4.1"),
        model_provider=os.getenv("MODEL_PROVIDER", "openai"),
        api_key=os.getenv("MODEL_API_KEY"),
        temperature=os.getenv("MODEL_TEMPERATURE", "0.1"),
        max_tokens=os.getenv("MODEL_MAX_TOKENS", "8000"),
        base_url=os.getenv("MODEL_BASE_URL", None)
    )
    agent = create_tool_calling_agent(model, combined_tools, prompt)
    return AgentExecutor(agent=agent, tools=combined_tools, verbose=True, handle_parsing_errors=True)

async def main():

    runtime = os.getenv("CORAL_ORCHESTRATION_RUNTIME", None)
    if runtime is None:
        load_dotenv()

    base_url = os.getenv("CORAL_SSE_URL")
    agentID = os.getenv("CORAL_AGENT_ID")

    coral_params = {
        "agentId": agentID,
        "agentDescription": "An agent that composites product imagery via FAL product-holding, narrates with ElevenLabs (TTS) and renders video using FAL (veed/fabric-1.0)",
    }

    query_string = urllib.parse.urlencode(coral_params)

    CORAL_SERVER_URL = f"{base_url}?{query_string}"
    print(f"Connecting to Coral Server: {CORAL_SERVER_URL}", flush=True)

    # Log env presence (without values)
    print(
        "Env presence: "
        f"MODEL_API_KEY={'yes' if os.getenv('MODEL_API_KEY') else 'no'}, "
        f"FAL_KEY={'yes' if os.getenv('FAL_KEY') else 'no'}, "
        f"ELEVENLABS_API_KEY={'yes' if os.getenv('ELEVENLABS_API_KEY') else 'no'}",
        flush=True,
    )

    timeout = float(os.getenv("TIMEOUT_MS", "300"))
    client = MultiServerMCPClient(
        connections={
            "coral": {
                "transport": "sse",
                "url": CORAL_SERVER_URL,
                "timeout": timeout,
                "sse_read_timeout": timeout,
            },
        }
    )

    print("Multi Server Connection Established", flush=True)

    coral_tools = await client.get_tools(server_name="coral")
    # Log tool names and short schemas
    try:
        print("Available Coral tools:", flush=True)
        for t in coral_tools:
            name = getattr(t, 'name', 'unknown')
            args = getattr(t, 'args', None)
            print(f" - {name} args={args}", flush=True)
    except Exception as e:
        print(f"Failed to introspect coral tools: {e}", flush=True)

    # We only use Coral tools from MCP; our custom video tool is added in create_agent
    agent_tools = []

    # Log custom tool(s)
    try:
        from tools import get_video_tools
        custom_tools = get_video_tools()
        print("Registered custom tools:", flush=True)
        for t in custom_tools:
            print(f" - {getattr(t, 'name', 'unknown')}", flush=True)
    except Exception as e:
        print(f"Failed to register custom tools: {e}", flush=True)

    print(f"Coral tools count: {len(coral_tools)} and agent tools count: {len(agent_tools)}", flush=True)

    agent_executor = await create_agent(coral_tools, agent_tools)

    while True:
        try:
            print("Starting new agent invocation", flush=True)
            await agent_executor.ainvoke({"agent_scratchpad": []})
            print("Completed agent invocation, restarting loop", flush=True)
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error in agent loop: {str(e)}", flush=True)
            print(traceback.format_exc(), flush=True)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
