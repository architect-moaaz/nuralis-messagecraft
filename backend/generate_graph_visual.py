#!/usr/bin/env python3
"""
Generate Visual Graph from LangGraph Workflow
This script creates a visual representation of the MessageCraft LangGraph workflow
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # Import the workflow system
    from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection
    
    # Create the agent system
    print("🚀 Initializing MessageCraft LangGraph system...")
    agent_system = MessageCraftAgentsWithReflection(
        quality_threshold=9.0,
        max_reflection_cycles=2
    )
    
    print("📊 Generating workflow visualization...")
    
    # Generate the graph visualization using LangGraph's built-in method
    try:
        # Try to get the Mermaid representation
        mermaid_graph = agent_system.app.get_graph().draw_mermaid()
        
        # Save Mermaid diagram
        mermaid_file = "messagecraft_workflow.mmd"
        with open(mermaid_file, "w") as f:
            f.write(mermaid_graph)
        print(f"✅ Mermaid diagram saved to: {mermaid_file}")
        
    except Exception as e:
        print(f"⚠️ Could not generate Mermaid: {e}")
    
    try:
        # Try to get PNG visualization (requires graphviz)
        png_data = agent_system.app.get_graph().draw_mermaid_png()
        
        # Save PNG file
        png_file = "messagecraft_workflow.png"
        with open(png_file, "wb") as f:
            f.write(png_data)
        print(f"✅ PNG diagram saved to: {png_file}")
        
    except Exception as e:
        print(f"⚠️ Could not generate PNG (install graphviz): {e}")
    
    # Print ASCII representation
    try:
        print("\n" + "="*80)
        print("📋 MESSAGECRAFT LANGGRAPH WORKFLOW STRUCTURE")
        print("="*80)
        
        graph = agent_system.app.get_graph()
        
        print("\n🔹 NODES (Agents):")
        for node_id in graph.nodes:
            print(f"  • {node_id}")
        
        print("\n🔹 EDGES (Flow):")
        for edge in graph.edges:
            print(f"  • {edge.source} → {edge.target}")
        
        print("\n🔹 CONDITIONAL EDGES:")
        for node_id, conditions in graph.branches.items():
            print(f"  • {node_id}:")
            for condition, target in conditions.items():
                print(f"    - {condition} → {target}")
        
        print("\n🔹 ENTRY POINT:")
        print(f"  • {', '.join(graph.nodes) if not hasattr(graph, 'entry_point') else 'business_discovery'}")
        
        print("\n🔹 WORKFLOW DESCRIPTION:")
        print("""
  1. business_discovery → Extract business requirements
  2. competitor_research → Analyze competitive landscape  
  3. positioning_analysis → Develop strategic positioning
  4. trust_building → Build industry-specific trust factors
  5. emotional_intelligence → Analyze emotional triggers
  6. social_proof_generator → Create social proof elements
  7. messaging_generator → Generate core messaging
  8. content_creator → Create marketing content
  9. quality_reviewer → Review and score quality
  10. reflection_orchestrator → Decide on refinement
  11. critique_agent → Provide detailed critique (if needed)
  12. refinement_agent → Apply improvements (if needed)
  13. meta_reviewer → Review reflection process (if needed)
  14. final_assembly → Compile final output
        """)
        
        print("\n🔄 REFLECTION LOOP:")
        print("""
  The workflow includes an intelligent reflection system:
  - After quality_reviewer, reflection_orchestrator checks quality score
  - If quality < threshold, enters reflection loop:
    quality_reviewer → reflection_orchestrator → critique_agent → 
    refinement_agent → meta_reviewer → reflection_orchestrator
  - Loop continues until quality threshold met or max cycles reached
  - Then proceeds to final_assembly
        """)
        
        print("\n✨ ADAPTIVE AI FEATURES:")
        print("""
  All agents use adaptive AI with NO hardcoded industry patterns:
  - Business discovery with multi-pass extraction
  - Competitive intelligence with specific competitor data
  - Multi-audience detection for two-sided markets
  - Adaptive trust building for any industry
  - Emotional intelligence without hardcoded triggers
  - Social proof generation without industry templates
  - Premium quality scoring targeting 9.5+/10
        """)
        
    except Exception as e:
        print(f"⚠️ Error displaying graph structure: {e}")
    
    print("\n" + "="*80)
    print("🎯 GRAPH GENERATION COMPLETE")
    print("="*80)
    
except ImportError as e:
    print(f"❌ Error importing workflow: {e}")
    print("Make sure langgraph_agents_with_reflection.py is available")
except Exception as e:
    print(f"❌ Error generating graph: {e}")
    import traceback
    traceback.print_exc()