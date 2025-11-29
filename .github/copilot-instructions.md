# PDAA Agent Project

## Project Overview
A multi-agent system for analyzing patient data with memory management, specialized tools, and coordinated agent workflows.

## Project Structure
- `data/` - Patient data storage (JSON)
- `src/` - Source code
  - `memory.py` - Memory management classes
  - `tools.py` - 6 specialized tools
  - `agents.py` - 3 agent implementations
  - `orchestrator.py` - Main coordination loop
- `notebooks/` - Jupyter notebooks for analysis
- `.env` - API keys (not committed)

## Setup Complete
✅ All dependencies installed
✅ Project structure created
✅ README.md documentation available
✅ Example patient data included

## Running the Project

### Interactive Mode
```powershell
$env:PYTHONPATH="."; python src/orchestrator.py
```

### Python Script
```python
from src.orchestrator import Orchestrator
orchestrator = Orchestrator()
response = orchestrator.run("Your query here")
```

### Jupyter Notebook
Open `notebooks/main.ipynb` and run cells interactively.
