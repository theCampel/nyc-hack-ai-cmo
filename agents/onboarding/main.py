# Purpose: OnboardingAgent for analyzing product data to define ICPs, marketing angles, and create knowledge base
import urllib.parse
from dotenv import load_dotenv
import os, json, asyncio, traceback
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool
from openai import AsyncOpenAI

# Product data structure - can be easily modified or made dynamic
PRODUCT_DATA = {
    "name": "EcoClean Pro",
    "category": "Smart Home Cleaning Robot",
    "price": "$899",
    "launch_date": "Q2 2024",
    "description": "EcoClean Pro is an AI-powered robotic vacuum that uses advanced LIDAR mapping and eco-friendly cleaning solutions. It features voice control, smartphone app integration, and can clean for 3 hours on a single charge.",
    "key_features": [
        "LIDAR mapping technology",
        "3-hour battery life",
        "Voice control (Alexa, Google)",
        "Eco-friendly cleaning solutions",
        "Self-emptying base station",
        "Pet hair specialization"
    ],
    "target_market_insights": [
        "Tech-savvy homeowners aged 25-45",
        "Pet owners",
        "Urban and suburban areas"
    ],
    "competitive_advantages": [
        "50% longer battery life than competitors",
        "Only robot vacuum using 100% biodegradable cleaning solutions",
        "Advanced pet hair detection"
    ]
}

def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

async def analyze_product_data(product_data, openai_client):
    """First OpenAI call: Analyze product data and generate ICP insights"""
    system_prompt = """You are a marketing analyst. Analyze the product data and provide:

1. IDEAL CUSTOMER PROFILES (2-3 segments): Demographics, psychographics, pain points
2. MARKETING ANGLES: Value props, emotional triggers, messaging for each ICP  
3. KNOWLEDGE BASE: Key benefits, differentiators, use cases, pricing position

Be concise and actionable. Focus on practical marketing insights."""
    
    user_prompt = f"""Analyze this product data:
    
    Product: {product_data['name']}
    Category: {product_data['category']}
    Price: {product_data['price']}
    Launch Date: {product_data['launch_date']}
    
    Description: {product_data['description']}
    
    Key Features:
    {chr(10).join(f"- {feature}" for feature in product_data['key_features'])}
    
    Target Market Insights:
    {chr(10).join(f"- {insight}" for insight in product_data['target_market_insights'])}
    
    Competitive Advantages:
    {chr(10).join(f"- {advantage}" for advantage in product_data['competitive_advantages'])}
    
    Please provide comprehensive analysis following the structure outlined in the system prompt."""
    
    response = await openai_client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-5"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=1.0,  # Hardcoded to 1.0 (only supported value for this model)
        max_completion_tokens=int(os.getenv("MODEL_MAX_TOKENS", "4000"))
    )
    
    return response.choices[0].message.content

async def convert_to_json(analysis_text, openai_client):
    """Second OpenAI call: Convert analysis into structured JSON"""
    system_prompt = """Convert the marketing analysis to JSON format:
{
  "product_info": {"name": "", "category": "", "price": "", "description": ""},
  "ideal_customer_profiles": [{"profile_name": "", "demographics": {}, "psychographics": {}, "behavioral_patterns": {}}],
  "marketing_angles": {"profile_name": {"value_propositions": [], "emotional_triggers": [], "messaging_angles": []}},
  "knowledge_base": {"key_benefits": [], "competitive_differentiators": [], "use_cases": [], "pricing_positioning": {}}
}
Return only valid JSON."""
    
    user_prompt = f"Convert this analysis into the specified JSON structure:\n\n{analysis_text}"
    
    response = await openai_client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-5"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=1.0,  # Hardcoded to 1.0 (only supported value for this model)
        max_completion_tokens=int(os.getenv("MODEL_MAX_TOKENS", "4000"))
    )
    
    return response.choices[0].message.content

# Global OpenAI client for tools to use
openai_client_global = None

@tool
async def analyze_product_for_marketing() -> str:
    """Analyze the hardcoded product data to generate ICPs, marketing angles, and knowledge base."""
    global openai_client_global
    if not openai_client_global:
        return "Error: OpenAI client not initialized"
    
    try:
        print("Starting product analysis...")
        analysis = await analyze_product_data(PRODUCT_DATA, openai_client_global)
        print("Converting analysis to JSON...")
        json_result = await convert_to_json(analysis, openai_client_global)
        print("Product analysis completed successfully")
        return json_result
    except Exception as e:
        error_msg = f"Error during product analysis: {str(e)}"
        print(error_msg)
        return error_msg

async def create_agent(coral_tools, agent_tools):
    coral_tools_description = get_tools_description(coral_tools)
    
    # Add our custom analysis tool
    custom_tools = [analyze_product_for_marketing]
    agent_tools_description = get_tools_description(custom_tools)
    combined_tools = coral_tools + custom_tools
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are the OnboardingAgent for automatic product analysis. When mentioned by any agent, you immediately analyze the product data and return structured marketing insights.
            
            Follow these steps in order:
            1. Call wait_for_mentions from coral tools (timeoutMs: 30000) to receive mentions from other agents.
            2. When you receive a mention, keep the thread ID and the sender ID.
            3. IMMEDIATELY call the `analyze_product_for_marketing` tool - do not ask for clarification or additional information.
            4. Use `send_message` from coral tools to send the complete analysis results back to the sender in the same thread ID.
            5. Use `coral_close_thread` from coral tools to close the thread after sending the results.
            6. If any error occurs, use `send_message` to send an error message back to the sender, then close the thread.
            7. Wait for 2 seconds and repeat the process from step 1.
            
            IMPORTANT: Never ask the user for input or provide options. Always immediately execute the product analysis when mentioned. Always close the thread after completing the task.

            These are the list of coral tools: {coral_tools_description}
            These are the list of your tools: {agent_tools_description}"""
        ),
        ("placeholder", "{agent_scratchpad}")
    ])

    model = init_chat_model(
        model=os.getenv("MODEL_NAME", "gpt-5"),
        model_provider=os.getenv("MODEL_PROVIDER", "openai"),
        api_key=os.getenv("MODEL_API_KEY"),
        temperature=1.0,  # Hardcoded to 1.0 (only supported value for this model)
        max_tokens=os.getenv("MODEL_MAX_TOKENS", "4000"),  # LangChain may handle the parameter conversion
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
        "agentDescription": "OnboardingAgent that analyzes product data to define ICPs, marketing angles, and create knowledge base for downstream agents"
    }

    query_string = urllib.parse.urlencode(coral_params)
    CORAL_SERVER_URL = f"{base_url}?{query_string}"
    print(f"Connecting to Coral Server: {CORAL_SERVER_URL}")

    # Initialize OpenAI client for custom analysis
    global openai_client_global
    openai_client_global = AsyncOpenAI(api_key=os.getenv("MODEL_API_KEY"))

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

    print("Multi Server Connection Initialized")

    coral_tools = await client.get_tools(server_name="coral")
    agent_tools = []  # We'll add custom tools in create_agent function
    
    print(f"Coral tools count: {len(coral_tools)}, Agent tools count: {len(agent_tools)}")

    agent_executor = await create_agent(coral_tools, agent_tools)

    while True:
        try:
            print("Starting new agent invocation")
            await agent_executor.ainvoke({"agent_scratchpad": []})
            print("Completed agent invocation, restarting loop")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error in agent loop: {e}")
            traceback.print_exc()
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
