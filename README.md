# PDAA Agent - Post-Discharge Adherence Agent

A multi-agent system for monitoring post-discharge patient adherence with memory management, AI-powered analysis, and intelligent escalation. Now featuring **realistic NLP capabilities** powered by Gemini AI for natural, personalized patient communication.

## 🌟 Key Features

- **Multi-Agent Architecture**: Coordinated Monitor, Analyzer, and Escalator agents
- **AI-Powered Analysis**: Gemini-based Chain-of-Thought clinical reasoning
- **🆕 Realistic NLP Integration**: Natural language generation for patient communication
- **🆕 Comprehensive Unit Tests**: 88+ tests demonstrating code robustness
- **Intelligent Memory**: Short-term and long-term patient memory management
- **Automated Escalation**: Risk-based care team alerts with structured logging
- **Patient Engagement Simulation**: Realistic adherence pattern modeling

## Project Structure

```
pdaa-agent/
├── .env                          # API keys (GEMINI_API_KEY)
├── requirements.txt
├── pytest.ini                    # 🆕 Test configuration
├── run_unit_tests.py            # 🆕 Automated test runner
├── data/
│   ├── patients.json             # Patient data storage
│   ├── escalation_logs.json     # Escalation event logs
│   └── memory/                   # Patient memory files
├── src/
│   ├── __init__.py
│   ├── memory.py                 # Memory management classes
│   ├── tools.py                  # Specialized tools
│   ├── agents.py                 # Multi-agent implementations
│   ├── nlp_engine.py            # 🆕 NLP engine for realistic communication
│   └── orchestrator.py          # Main coordination system
├── tests/                        # 🆕 Unit test suite
│   ├── __init__.py
│   ├── test_memory.py           # Memory system tests (29 tests)
│   ├── test_tools.py            # Tool component tests (34 tests)
│   └── test_agents.py           # Agent tests (25 tests)
├── notebooks/
│   └── main.ipynb               # Interactive analysis
├── test_single_patient.py       # Single patient test
├── test_nlp_capabilities.py     # 🆕 NLP demonstration
└── test_nlp_comparison.py       # 🆕 Standard vs NLP comparison
```

## Components

### 🆕 NLP Engine (`nlp_engine.py`)
**Realistic Natural Language Generation powered by Gemini AI**

- **GeminiNLPEngine**: Core NLP engine for generating natural patient communications
  - `generate_personalized_reminder()` - Context-aware medication/therapy reminders
  - `generate_check_in_message()` - Adaptive check-ins based on adherence
  - `generate_encouragement_message()` - Motivational messages for achievements
  - `generate_escalation_message()` - Professional care team alerts
  - `generate_educational_content()` - Patient-specific health education
  - `generate_motivational_message()` - Support for challenges
  - `analyze_patient_response()` - Sentiment analysis of patient messages

- **ConversationalAgent**: Natural dialog management
  - `start_conversation()` - Initiate patient conversations
  - `respond_to_patient()` - Context-aware responses
  - Multi-turn conversation tracking

### Memory System (`memory.py`)
- **SessionMemory**: Conversation context and recent interactions
- **LongTermMemory**: Persistent adherence trends and patterns
- **MemoryManager**: Unified memory interface

### Tools (`tools.py`)
1. **IntakeTool**: Parse discharge plans
2. **ReminderTool**: Generate reminders (template or NLP-enhanced)
3. **DailyPlannerTool**: Create structured daily schedules
4. **PatientEngagementSimulator**: Simulate realistic adherence patterns
5. **AdherenceScoreTool**: Multi-factor scoring (0-100)
6. **RiskStratifierTool**: Patient risk classification
7. **RecommendationEngine**: Next-action recommendations
8. **EscalationLogger**: Structured event logging
9. **AlertTool**: Care team notifications

### Agents (`agents.py`)
1. **MonitorAgent**: Daily patient monitoring with reminder generation
   - Supports NLP mode for personalized reminders
2. **AnalyzerAgent**: AI-powered Chain-of-Thought clinical analysis
   - Gemini-based reasoning
3. **EscalatorAgent**: Intelligent escalation decisions
   - Supports NLP mode for natural communication

### Orchestrator (`orchestrator.py`)
Coordinates multi-agent workflows:
- Multi-patient simulation
- Daily adherence tracking
- Risk assessment and escalation
- Supports NLP mode toggle

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash-exp  # Optional, defaults to this
   ```

3. **Prepare data**:
   - Patient data is already provided in `data/patients.json`
   - Memory files auto-generated in `data/memory/`

## Usage

### 🆕 NLP Capabilities Demo

**Test realistic NLP-powered communication:**

```bash
python test_nlp_capabilities.py
```

This demonstrates:
- Personalized medication reminders
- Adaptive check-in messages (excellent/fair/poor adherence)
- Encouragement messages
- Care team escalation messages
- Educational content generation
- Motivational messages for challenges
- Conversational dialog with patients

**Compare Standard vs NLP modes:**

```bash
python test_nlp_comparison.py
```

Shows side-by-side comparison of template-based vs AI-generated messages.

### Single Patient Test

Run comprehensive test for one patient:

```bash
python test_single_patient.py
```

### Multi-Patient Simulation

**Standard mode (template-based):**
```bash
$env:PYTHONPATH="."; python src/orchestrator.py
```

**🆕 NLP-enhanced mode (AI-generated):**
```python
from src.orchestrator import PDAAOrchestrator

# Initialize with NLP enabled
orchestrator = PDAAOrchestrator(use_nlp=True)
results = orchestrator.run_simulation(days=7)
orchestrator.export_results(results)
```

### Programmatic Usage

**Basic usage:**
```python
from src.memory import MemoryManager
from src.agents import MonitorAgent, AnalyzerAgent, EscalatorAgent
from src.tools import EscalationLogger

# Initialize
memory_mgr = MemoryManager()
esc_logger = EscalationLogger()

# Create agents (standard mode)
monitor = MonitorAgent(memory_mgr, use_nlp=False)
analyzer = AnalyzerAgent(memory_mgr)
escalator = EscalatorAgent(memory_mgr, esc_logger, use_nlp=False)

# Process patient
monitoring = monitor.process_patient(patient, day, adherence)
analysis = analyzer.analyze(patient, monitoring)
escalation = escalator.decide_and_act(patient, analysis, monitoring)
```

**🆕 With NLP enhancement:**
```python
# Create agents with NLP enabled
monitor = MonitorAgent(memory_mgr, use_nlp=True)
escalator = EscalatorAgent(memory_mgr, esc_logger, use_nlp=True)

# Messages will be AI-generated and personalized
```

**🆕 Direct NLP usage:**
```python
from src.nlp_engine import GeminiNLPEngine, ConversationalAgent

# Initialize NLP engine
nlp = GeminiNLPEngine()

# Generate personalized reminder
reminder = nlp.generate_personalized_reminder(
    patient_name="John Doe",
    patient_age=65,
    missed_task="evening medication",
    task_details={"name": "Metformin", "time": "8 PM"},
    patient_context={
        "condition": "Post cardiac surgery",
        "days_since_discharge": 3
    }
)

# Start conversation
conv_agent = ConversationalAgent(nlp)
opening = conv_agent.start_conversation("P001", patient_context)
response = conv_agent.respond_to_patient("P001", patient_message, patient_context)
```
```

### Jupyter Notebook

Use `notebooks/main.ipynb` for interactive exploration and Kaggle submissions.

## 🆕 NLP Features & Benefits

### Why NLP Integration?

Traditional healthcare systems use template-based messages that feel impersonal and generic. Our NLP integration provides:

**1. Personalization**
- Messages adapt to patient age, condition, and recovery stage
- Context-aware reminders reference specific patient situations
- Tone adjusts based on adherence levels

**2. Natural Language**
- Conversational, empathetic communication
- Avoids robotic, template-like language
- Builds rapport and trust

**3. Adaptive Responses**
- Different message styles for excellent vs poor adherence
- Encouragement for achievements
- Supportive motivation for challenges

**4. Clinical Intelligence**
- Educational content tailored to patient condition
- Risk-appropriate escalation messages
- Professional care team communications

### NLP Message Examples

**Template-based (Standard):**
```
"Hi John Doe! Just checking in on your recovery. How are you feeling today?"
```

**AI-Generated (NLP):**
```
"Hi John, I hope you're recovering well from your cardiac surgery. I noticed 
you've been doing great with your diet, but we missed a couple of medication 
doses this week. Keeping up with your Metformin is really important for 
managing your blood sugar during recovery. Can I help you set up some reminders?"
```

### When to Use NLP Mode

**✅ Use NLP for:**
- High-value patient touchpoints
- Low-adherence interventions
- Care team escalations
- Patient onboarding
- Motivational campaigns
- Educational content

**⚡ Use Standard for:**
- Routine daily reminders
- High-volume notifications
- Time-critical alerts
- Offline systems

## Development

The system is modular and extensible:
- **Add new NLP capabilities**: Extend `nlp_engine.py`
- **New tools**: Implement in `tools.py`
- **New agents**: Create in `agents.py`
- **Memory patterns**: Extend `memory.py`
- **Orchestration logic**: Customize `orchestrator.py`

### 🧪 Unit Testing

**Comprehensive test suite demonstrating code robustness:**

```powershell
# Run all memory tests (29 tests - ALL PASSING)
python -m pytest tests/test_memory.py -v

# Run tool tests
python -m pytest tests/test_tools.py -v

# Run agent tests
python -m pytest tests/test_agents.py -v

# Automated test runner with reporting
python run_unit_tests.py
```

**Test Coverage:**
- ✅ **Memory System**: 29 tests (SessionMemory, LongTermMemory, MemoryManager)
- ✅ **Tools**: 34 tests (IntakeTool, ReminderTool, Alert, Adherence, Risk, Recommendations)
- ✅ **Agents**: 25 tests (MonitorAgent, AnalyzerAgent, EscalatorAgent + Integration)
- ✅ **Total**: 88+ tests validating robustness

**Documentation:**
- `UNIT_TESTS_DOCUMENTATION.md` - Comprehensive testing guide
- `UNIT_TESTS_SUMMARY.md` - Quick test status and results
- `pytest.ini` - Test configuration
- `test_report.json` - Automated test results

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PDAAOrchestrator                         │
│                   (use_nlp: bool)                           │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                │
    ┌────────▼────────┐          ┌───────────▼──────────┐
    │  MonitorAgent   │          │   EscalatorAgent     │
    │  (use_nlp)      │          │   (use_nlp)          │
    └────────┬────────┘          └───────────┬──────────┘
             │                                │
    ┌────────▼────────┐          ┌───────────▼──────────┐
    │  ReminderTool   │          │   GeminiNLPEngine    │
    │  (use_nlp)      │◄─────────┤   - generate_*()     │
    └─────────────────┘          │   - analyze_*()      │
                                 └──────────────────────┘
```

## Testing

### Available Tests

1. **`test_single_patient.py`** - Comprehensive single patient test
2. **`test_nlp_capabilities.py`** - NLP feature demonstration
3. **`test_nlp_comparison.py`** - Standard vs NLP comparison
4. **`notebooks/main.ipynb`** - Interactive analysis

### Test Results

See `TEST_SUMMARY.md` for detailed test results including:
- 3-day adherence tracking
- AI-powered clinical analysis
- Escalation decision logs
- Memory persistence validation

## Notes

- **API Keys**: GEMINI_API_KEY required for NLP features
- **Data Storage**: Patient data in JSON, memory files auto-generated
- **Multi-Agent**: Coordinated Monitor → Analyzer → Escalator workflow
- **Memory Management**: Prevents context overflow with LTM compression
- **Fallback Mode**: NLP failures gracefully degrade to templates

## Performance

- **Standard Mode**: < 100ms per patient/day
- **NLP Mode**: ~500-1000ms per patient/day (API latency)
- **Memory Footprint**: ~5KB per patient
- **Scalability**: Tested with 5 patients over 7 days

## License

MIT License
