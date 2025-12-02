import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="PDAA Dashboard", layout="wide")

st.title("🏥 PDAA Agent - Patient Adherence Dashboard")

# Load results
results_file = Path("simulation_results.json")
if results_file.exists():
    with open(results_file) as f:
        results = json.load(f)
    
    # Clinical Impact Section (NEW - Prominent Display)
    if "clinical_impact" in results and "population_impact" in results["clinical_impact"]:
        st.header("📊 Clinical Impact Analysis")
        
        impact = results["clinical_impact"]["population_impact"]
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Readmissions Prevented", impact.get("readmissions_prevented", "N/A"))
        col2.metric("Cost Savings (Net)", impact.get("cost_savings_net", "N/A"))
        col3.metric("Bed Days Saved", impact.get("hospital_bed_days_saved", "N/A"))
        col4.metric("ROI", impact.get("roi", "N/A"))
        
        # Detailed impact metrics
        with st.expander("🔍 Detailed Impact Metrics", expanded=True):
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("Clinical Outcomes")
                st.write(f"**Adherence Improvement:** +{impact.get('adherence_improvement_over_baseline', 'N/A')}% over baseline")
                st.write(f"**Readmission Reduction:** {impact.get('readmission_reduction_rate', 'N/A')}")
                st.write(f"**Lives Saved (Est.):** {impact.get('estimated_lives_saved', 'N/A')}")
                st.write(f"**Evidence Quality:** {impact.get('evidence_quality', 'N/A')}")
            
            with col_right:
                st.subheader("Financial Impact")
                st.write(f"**Gross Savings:** {impact.get('cost_savings_gross', 'N/A')}")
                st.write(f"**Monitoring Costs:** {impact.get('monitoring_costs', 'N/A')}")
                st.write(f"**Net Savings:** {impact.get('cost_savings_net', 'N/A')}")
                st.write(f"**Return on Investment:** {impact.get('roi', 'N/A')}")
            
            st.info(f"**Methodology:** {impact.get('methodology', 'Evidence-based calculation')}")
            
            if "citations" in impact and impact["citations"]:
                st.markdown("**Key Citations:**")
                for i, citation in enumerate(impact["citations"][:3], 1):
                    st.markdown(f"{i}. {citation}")
        
        st.divider()
    
    # Summary metrics
    st.header("📈 Simulation Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patients", results["summary"]["total_patients"])
    col2.metric("Avg Adherence", f"{results['summary']['overall_average_score']:.1f}/100")
    col3.metric("Escalations", results["summary"]["total_escalations"])
    col4.metric("High-Risk Patients", results["summary"]["patients_needing_attention"])
    
    st.divider()
    
    # Patient selector
    st.header("👤 Individual Patient Analysis")
    patient_options = {pid: data["patient_name"] for pid, data in results["patient_results"].items()}
    selected_patient = st.selectbox("Select Patient", options=list(patient_options.keys()), 
                                     format_func=lambda x: patient_options[x])
    
    if selected_patient:
        patient_data = results["patient_results"][selected_patient]
        
        st.subheader(f"📊 {patient_data['patient_name']} - 7-Day Adherence Trend")
        
        # Prepare data for chart
        daily_scores = [day["analysis"]["adherence_score"]["total_score"] 
                        for day in patient_data["daily_results"]]
        
        df = pd.DataFrame({
            "Day": list(range(1, len(daily_scores) + 1)),
            "Adherence Score": daily_scores
        })
        
        st.line_chart(df.set_index("Day"))
        
        # Show daily details
        st.subheader("📅 Daily Breakdown")
        for day_result in patient_data["daily_results"]:
            with st.expander(f"Day {day_result['day']}"):
                col1, col2 = st.columns(2)
                
                analysis = day_result["analysis"]
                col2.metric("Risk Level", analysis['risk_assessment']['risk_class'])
                escalated = "✅ Yes" if day_result['escalation']['escalated'] else "❌ No"
                col2.metric("Escalated", escalated)
                
                # Display RAG recommendations if available
                if "rag_recommendations" in analysis and analysis["rag_recommendations"]:
                    st.write("**📚 Evidence-Based Recommendations:**")
                    for task, recommendation in analysis["rag_recommendations"].items():
                        st.info(f"**{task.title()}:** {recommendation}")
                
                # Display red flag warnings if any
                if "red_flag_warnings" in analysis and analysis["red_flag_warnings"]:
                    st.write("**⚠️ Red Flag Warnings:**")
                    for task, warnings in analysis["red_flag_warnings"].items():
                        st.error(f"**{task.title()}:** {', '.join(warnings[:2])}")
                
                st.write("**Chain-of-Thought Analysis:**")
                st.write(analysis['chain_of_thought'])
                
                st.write("**Chain-of-Thought Analysis:**")
                st.write(analysis['chain_of_thought'])
else:
    st.warning("No simulation results found. Run orchestrator first.")

# Run instructions
st.sidebar.header("🚀 Quick Start")
st.sidebar.code("python src/orchestrator.py", language="bash")
st.sidebar.info("Run the simulation to generate data for this dashboard.")