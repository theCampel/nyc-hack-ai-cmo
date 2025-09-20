# OnboardingAgent

> **Purpose**: Analyzes product data to define Ideal Customer Profiles (ICPs), marketing angles, and create a knowledge base for downstream agents in the website creation pipeline.

## Overview

The OnboardingAgent is a strategic analysis agent that takes hardcoded product information and transforms it into actionable marketing intelligence. It serves as the first step in an automated website creation workflow by providing foundational customer insights and product knowledge.

## Features

- **ICP Analysis**: Defines 2-3 distinct Ideal Customer Profiles with demographics, psychographics, and behavioral patterns
- **Marketing Strategy**: Generates targeted marketing angles, hooks, and messaging for each ICP
- **Knowledge Base Creation**: Structures product information for use by downstream agents
- **Dual OpenAI Integration**: 
  - First call: Strategic analysis and insights generation
  - Second call: Converts analysis into structured JSON format
- **GPT-5 Integration**: Uses the latest OpenAI model for advanced analysis

## Output Structure

The agent produces a comprehensive JSON output containing:

```json
{
  "product_info": {
    "name": "Product Name",
    "category": "Product Category",
    "price": "$XXX",
    "description": "Product description"
  },
  "ideal_customer_profiles": [
    {
      "profile_name": "Primary Customer Segment",
      "demographics": {...},
      "psychographics": {...},
      "behavioral_patterns": {...}
    }
  ],
  "marketing_angles": {
    "profile_name": {
      "value_propositions": [...],
      "emotional_triggers": [...],
      "messaging_angles": [...],
      "content_hooks": [...]
    }
  },
  "knowledge_base": {
    "key_benefits": [...],
    "competitive_differentiators": [...],
    "use_cases": [...],
    "technical_specs": [...],
    "pricing_positioning": {...}
  }
}
```

## Configuration

### Required Environment Variables

```bash
MODEL_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-5
MODEL_PROVIDER=openai
CORAL_SSE_URL=http://localhost:5555/devmode/exampleApplication/privkey/session1/sse
CORAL_AGENT_ID=onboarding_agent
```

### Optional Configuration

```bash
MODEL_MAX_TOKENS=16000
MODEL_TEMPERATURE=0.3
TIMEOUT_MS=300
```

## Product Data Structure

The agent currently uses hardcoded product data in `main.py`. To modify the product being analyzed, update the `PRODUCT_DATA` dictionary:

```python
PRODUCT_DATA = {
    "name": "Your Product Name",
    "category": "Product Category",
    "price": "$XXX",
    "launch_date": "Launch Date",
    "description": "Product description...",
    "key_features": [
        "Feature 1",
        "Feature 2",
        # ...
    ],
    "target_market_insights": [
        "Market insight 1",
        "Market insight 2",
        # ...
    ],
    "competitive_advantages": [
        "Advantage 1",
        "Advantage 2",
        # ...
    ]
}
```

## Usage

### Running Locally

1. Copy the environment template:
   ```bash
   cp .env_sample .env
   ```

2. Fill in your API keys in `.env`

3. Run the agent:
   ```bash
   ./run_agent.sh
   ```

### Running with Docker

```bash
docker build -t onboarding-agent .
docker run --env-file .env onboarding-agent
```

## Integration with Coral Protocol

The OnboardingAgent follows the standard Coral Protocol agent pattern:

1. **Listens for mentions** from other agents via `wait_for_mentions`
2. **Processes requests** by analyzing product data with OpenAI
3. **Responds with results** via `send_message` back to the requesting agent
4. **Loops continuously** to handle multiple requests

## Agent Workflow

1. **Wait for Mention**: Agent waits for requests from other agents
2. **Product Analysis**: When triggered, analyzes the hardcoded product data using GPT-5
3. **Strategic Insights**: Generates ICPs, marketing angles, and knowledge base elements
4. **JSON Conversion**: Converts the analysis into structured JSON format
5. **Response Delivery**: Sends the structured results back to the requesting agent

## Dependencies

- **LangChain**: Agent framework and model integration
- **OpenAI**: Direct API integration for GPT-5 analysis
- **Coral MCP Adapters**: Integration with Coral Protocol
- **Python 3.13+**: Runtime environment

## Development

### Modifying Product Data

To analyze different products, update the `PRODUCT_DATA` dictionary in `main.py`. The structure is flexible and can accommodate various product types.

### Customizing Analysis

The system prompts in `analyze_product_data()` and `convert_to_json()` can be modified to adjust the analysis focus or output format.

### Adding External Data Sources

Future enhancements could include:
- Loading product data from external files
- API integration for dynamic product information
- Database connectivity for product catalogs

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure your OpenAI API key has access to GPT-5
2. **Timeout Errors**: Increase `TIMEOUT_MS` if analysis takes longer than expected
3. **JSON Parsing**: Check the `convert_to_json()` output for valid JSON format

### Logging

The agent provides detailed logging of:
- Connection status to Coral Server
- Analysis progress and results
- Error messages and stack traces

## Future Enhancements

- Dynamic product data loading
- Multiple product analysis support
- Integration with product databases
- Custom analysis templates
- Result caching and storage
