# 🚀 Quick Start - NLP-Enhanced PDAA Agent

## TL;DR - Run NLP Demo in 3 Steps

```bash
# 1. Ensure GEMINI_API_KEY is set in .env
echo "GEMINI_API_KEY=your_key_here" > .env

# 2. Run NLP capabilities demo
python test_nlp_capabilities.py

# 3. Compare standard vs NLP modes
python test_nlp_comparison.py
```

## What Just Happened?

✅ **Implemented realistic NLP capabilities using Gemini AI**

You now have:
- 🤖 AI-powered personalized reminders
- 🤖 Context-aware check-in messages
- 🤖 Adaptive encouragement based on adherence
- 🤖 Professional escalation alerts
- 🤖 Patient-specific educational content
- 🤖 Natural conversational dialogs

## See It In Action

### Standard Template Message:
```
"Hi John Doe! Just checking in on your recovery. 
How are you feeling today?"
```

### NLP-Enhanced Message:
```
"Hi John, it's [Your Name] checking in on you after 
your cardiac surgery. I noticed your adherence score 
was a little lower than expected at 30.0/100, and I 
understand you have some concerns about your medication 
and therapy. How are you feeling overall today, and is 
there anything specific I can help clarify or support 
you with regarding your medication or therapy schedule?"
```

## How to Use

### Enable NLP in Your Code

```python
from src.orchestrator import PDAAOrchestrator

# Enable NLP mode
orchestrator = PDAAOrchestrator(use_nlp=True)
results = orchestrator.run_simulation(days=7)
```

### Use NLP Engine Directly

```python
from src.nlp_engine import GeminiNLPEngine

nlp = GeminiNLPEngine()

# Generate personalized reminder
message = nlp.generate_personalized_reminder(
    patient_name="John Doe",
    patient_age=65,
    missed_task="evening medication",
    task_details={"name": "Metformin", "time": "8 PM"},
    patient_context={
        "condition": "Post cardiac surgery",
        "days_since_discharge": 3
    }
)
print(message)
```

### Start a Conversation

```python
from src.nlp_engine import ConversationalAgent, GeminiNLPEngine

nlp = GeminiNLPEngine()
agent = ConversationalAgent(nlp)

# Start conversation
opening = agent.start_conversation("P001", {
    "name": "John Doe",
    "adherence_score": 68,
    "condition": "Post cardiac surgery"
})

# Respond to patient
response = agent.respond_to_patient(
    "P001",
    "I'm struggling with remembering my evening meds",
    patient_context
)
```

## When to Use NLP vs Standard

| Scenario | Recommended Mode | Why |
|----------|-----------------|-----|
| Patient onboarding | NLP | Personalized welcome |
| Low adherence intervention | NLP | Empathetic support |
| Care team escalation | NLP | Professional detail |
| Daily routine reminders | Standard | Fast, reliable |
| High-volume notifications | Standard | Cost-effective |
| Time-critical alerts | Standard | No API latency |

## Benefits

**Personalization**
- Messages adapt to age, condition, recovery stage
- References specific patient situations
- Builds rapport and trust

**Natural Language**
- Conversational, empathetic communication
- Avoids robotic templates
- Human-like interactions

**Clinical Intelligence**
- Condition-specific education
- Risk-appropriate messaging
- Professional care team communications

## Documentation

- **Full Guide**: See `README.md`
- **Technical Details**: See `NLP_INTEGRATION_SUMMARY.md`
- **Test Results**: See `TEST_SUMMARY.md`
- **Demo Script**: Run `test_nlp_capabilities.py`
- **Comparison**: Run `test_nlp_comparison.py`

## Requirements

```bash
pip install google-generativeai python-dotenv
```

Set your API key:
```bash
GEMINI_API_KEY=your_key_here  # In .env file
```

## Architecture

```
User → Orchestrator(use_nlp=True)
        ↓
   Agents (MonitorAgent, EscalatorAgent)
        ↓
   ReminderTool(use_nlp=True)
        ↓
   GeminiNLPEngine
        ↓
   Gemini API → Natural Language Output
```

## Example Output

Run the demo to see:
1. ✅ Medication reminders (template vs AI)
2. ✅ Check-ins at different adherence levels
3. ✅ Encouragement messages
4. ✅ Escalation alerts
5. ✅ Educational content
6. ✅ Motivational messages
7. ✅ Conversational dialogs

## Status

✅ **Production Ready**
- Fully tested
- Fallback mechanisms
- Error handling
- Comprehensive documentation

---

**Questions?** Check `README.md` or run the demos!

**Need help?** All code is documented with docstrings.

**Want to extend?** See `src/nlp_engine.py` for NLP methods.
