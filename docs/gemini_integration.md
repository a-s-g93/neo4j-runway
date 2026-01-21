# Google Gemini Integration for Neo4j Runway

This document explains how to use Google Gemini LLMs with Neo4j Runway for data discovery and modeling.

## Installation

To use Gemini with Neo4j Runway, you need to install the Google GenerativeAI library:

```bash
pip install google-generativeai
```

## Setup

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set your API key as an environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   
   Or pass it directly when creating the LLM instance.

## Usage

### Data Discovery

```python
from neo4j_runway.llm.gemini import GeminiDiscoveryLLM
from neo4j_runway import Discovery, UserInput
import pandas as pd

# Create the discovery LLM
disc_llm = GeminiDiscoveryLLM(
    model_name="gemini-1.5-pro",  # or "gemini-1.5-flash" for faster responses
    model_params={"temperature": 0.5},
    api_key="your-api-key",  # Optional if GEMINI_API_KEY env var is set
    enable_async=False  # Set to True for async operations
)

# Load your data
df = pd.read_csv("your_data.csv")

# Create user input
user_input = UserInput(
    general_description="Description of your data",
    column_descriptions={
        "column1": "Description of column1",
        # ... other columns
    },
    use_cases=["Your use cases"]
)

# Run discovery
disc = Discovery(llm=disc_llm, data=df, user_input=user_input)
disc.run()
```

### Data Modeling

```python
from neo4j_runway.llm.gemini import GeminiDataModelingLLM
from neo4j_runway import GraphDataModeler

# Create the data modeling LLM
dm_llm = GeminiDataModelingLLM(
    model_name="gemini-1.5-pro",  # or "gemini-1.5-flash" for faster responses
    model_params={"temperature": 0.0},
    api_key="your-api-key",  # Optional if GEMINI_API_KEY env var is set
)

# Create the graph data modeler
gdm = GraphDataModeler(discovery=disc, llm=dm_llm)

# Generate the initial model
gdm.create_initial_model(max_retries=2)

# Visualize the model
gdm.current_model.visualize()
```

## Available Models

- `gemini-2.5-pro`: Latest and most advanced model, best for complex reasoning
- `gemini-1.5-pro`: Most capable model, good for complex tasks
- `gemini-1.5-flash`: Faster and more efficient, good for most use cases  
- `gemini-1.0-pro`: Previous generation model

**Note**: The integration uses Gemini's JSON mode for optimal compatibility with complex data schemas.

## Parameters

### Common Parameters

- `model_name`: The Gemini model to use (default: "gemini-1.5-pro")
- `model_params`: Dict of parameters to pass to the model (e.g., {"temperature": 0.5})
- `api_key`: Your Gemini API key (optional if GEMINI_API_KEY env var is set)
- `llm_init_params`: Additional parameters for model initialization

### Discovery-specific Parameters

- `enable_async`: Whether to enable asynchronous operations (default: False)

## Example Notebook

See `examples/llm_providers/gemini.ipynb` for a complete example using the countries dataset.

## Error Handling

The Gemini implementation will raise appropriate errors for:
- Missing API key
- Invalid model names
- Network connectivity issues
- API rate limits

Make sure to handle these exceptions in your code when appropriate.
