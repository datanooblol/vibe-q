# Architecture Documentation

## Current Stack Components

### Lambda Functions
1. **VibeLambda** (Python 3.11)
   - Handler: `vibe_handler.lambda_handler`
   - Returns: `{"message": "Vibe with Q"}`

2. **EchoLambda** (Python 3.11)
   - Handler: `echo_handler.lambda_handler`
   - Input: `{"echo_name": "string"}`
   - Returns: `{"vibe_echo": "string"}`

### API Gateway
- **REST API**: `/vibe` endpoint (GET method)
- Integrates with VibeLambda function

### Step Functions
- **Standard Workflow**: Processes echo arrays
- **Map State**: Iterates over input array
- **Input Schema**: `{"echo_arrays": [{"echo_name": "string"}]}`
- **Output Schema**: `{"echoed": ["string1", "string2"]}`

## Architecture Flow

```
Client Request → API Gateway → VibeLambda → Response

Step Function Input → Map State → EchoLambda (parallel) → Collect Results → Output
```

## Data Flow Example

**Step Function:**
- Input: `{"echo_arrays": [{"echo_name": "mock echo 1"}, {"echo_name": "mock echo 2"}]}`
- Output: `{"echoed": ["mock echo 1", "mock echo 2"]}`