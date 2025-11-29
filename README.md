# PDAA Agent - Patient Data Analysis Agent

A multi-agent system for analyzing patient data with memory management, specialized tools, and coordinated agent workflows.

## Project Structure

```
pdaa-agent/
├── .env                 # API keys (add to .gitignore!)
├── .gitignore
├── requirements.txt
├── data/
│   └── patients.json    # Patient data storage
├── src/
│   ├── __init__.py
│   ├── memory.py        # Memory management classes
│   ├── tools.py         # 6 specialized tools
│   ├── agents.py        # 3 agent implementations
│   └── orchestrator.py  # Main coordination loop
├── notebooks/
│   └── main.ipynb       # Jupyter notebook for Kaggle submission
└── README.md
```

## Components

### Memory System (`memory.py`)
- **Memory**: Base memory class for storing interactions
- **WorkingMemory**: Short-term memory with size limits
- **LongTermMemory**: Persistent storage for important information

### Tools (`tools.py`)
1. **PatientDataTool**: Load and query patient data
2. **SearchTool**: Search patient records by field or text
3. **AnalysisTool**: Calculate statistics and generate insights
4. **UpdateTool**: Modify and save patient records
5. **ValidationTool**: Validate patient data integrity
6. **ReportTool**: Generate formatted reports

### Agents (`agents.py`)
1. **DataRetrievalAgent**: Specialized in finding and retrieving patient data
2. **AnalysisAgent**: Analyzes data and provides insights
3. **CoordinatorAgent**: Routes requests and synthesizes results

### Orchestrator (`orchestrator.py`)
Main coordination system that:
- Initializes all tools and agents
- Manages the main processing loop
- Coordinates between agents
- Handles user interactions

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   - Copy `.env` and add your API keys
   - Ensure `.env` is in `.gitignore`

3. **Prepare data**:
   - Add your patient data to `data/patients.json`
   - Follow the JSON format in the existing file

## Usage

### Interactive Mode

Run the orchestrator in interactive mode:

```bash
python src/orchestrator.py
```

Commands:
- Type queries to interact with agents
- `report` - Generate summary report
- `stats` - View statistics
- `quit` - Exit

### Programmatic Usage

```python
from src.orchestrator import Orchestrator

# Initialize
orchestrator = Orchestrator()

# Process queries
response = orchestrator.run("Find patient P001")
print(response)

# Generate reports
report = orchestrator.generate_report()
print(report)

# Get statistics
stats = orchestrator.get_statistics()
print(stats)
```

### Jupyter Notebook

Use `notebooks/main.ipynb` for interactive exploration and Kaggle submissions.

## Example Queries

- "Find patient P001"
- "Get all patients"
- "Search for patients with diabetes"
- "Calculate statistics"
- "Analyze patient data"

## Development

The system is modular and extensible:
- Add new tools in `tools.py`
- Implement new agents in `agents.py`
- Extend memory systems in `memory.py`
- Customize orchestration in `orchestrator.py`

## Notes

- API keys should be kept secure in `.env`
- Patient data is stored locally in JSON format
- The system uses a coordinator pattern for agent communication
- Memory management prevents context overflow

## License

MIT License
