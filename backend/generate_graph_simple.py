#!/usr/bin/env python3
"""
Generate Visual Graph from LangGraph Workflow
This script creates a visual representation of the MessageCraft LangGraph workflow
"""

import os
import sys
import json

# Set environment variable for demo purposes
os.environ.setdefault("ANTHROPIC_API_KEY", "demo_key")

try:
    # Import required modules
    from typing import Dict, List, Any, Optional, TypedDict, Annotated
    from langchain.schema import HumanMessage, SystemMessage
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    
    print("✅ LangGraph modules imported successfully")
    
    # Import the workflow system
    from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection, MessagingState
    
    # Create the agent system
    print("🚀 Initializing MessageCraft LangGraph system...")
    
    try:
        agent_system = MessageCraftAgentsWithReflection(
            quality_threshold=9.0,
            max_reflection_cycles=2
        )
        print("✅ Agent system initialized successfully")
        
        print("📊 Generating workflow visualization...")
        
        # Get the compiled graph
        compiled_graph = agent_system.app
        graph = compiled_graph.get_graph()
        
        print("\n" + "="*80)
        print("📋 MESSAGECRAFT LANGGRAPH WORKFLOW STRUCTURE")
        print("="*80)
        
        print("\n🔹 NODES (Agents):")
        node_list = []
        for i, node_id in enumerate(graph.nodes, 1):
            print(f"  {i:2d}. {node_id}")
            node_list.append(node_id)
        
        print(f"\n📊 Total Nodes: {len(node_list)}")
        
        print("\n🔹 EDGES (Sequential Flow):")
        edge_count = 0
        for edge in graph.edges:
            edge_count += 1
            print(f"  {edge_count:2d}. {edge.source} → {edge.target}")
        
        print(f"\n🔗 Total Edges: {edge_count}")
        
        print("\n🔹 CONDITIONAL EDGES (Decision Points):")
        conditional_count = 0
        if hasattr(graph, 'branches') and graph.branches:
            for node_id, conditions in graph.branches.items():
                conditional_count += 1
                print(f"  {conditional_count}. {node_id}:")
                for condition, target in conditions.items():
                    print(f"     - IF {condition} → {target}")
        else:
            print("  No conditional edges found")
        
        print("\n🎯 WORKFLOW EXECUTION FLOW:")
        print("""
  Phase 1: Core Analysis (Sequential)
  ════════════════════════════════════
  1. business_discovery      → Extract business requirements & audience
  2. competitor_research     → Analyze competitive landscape  
  3. positioning_analysis    → Develop strategic positioning
  4. trust_building         → Build industry-specific trust factors
  5. emotional_intelligence → Analyze emotional triggers
  6. social_proof_generator → Create social proof elements
  7. messaging_generator    → Generate core messaging framework
  8. content_creator        → Create marketing content assets
  9. quality_reviewer       → Review and score quality (10 dimensions)
  
  Phase 2: Reflection Loop (Conditional)
  ════════════════════════════════════
  10. reflection_orchestrator → Decision: Continue reflection or finalize?
  
      IF quality < 9.5 AND cycles < max:
      ├── 11. critique_agent     → Detailed critique & improvement areas
      ├── 12. refinement_agent   → Apply specific improvements
      ├── 13. meta_reviewer      → Review reflection effectiveness
      └── LOOP BACK to quality_reviewer for re-evaluation
      
      IF quality ≥ 9.5 OR cycles ≥ max:
      └── 14. final_assembly     → Compile final messaging playbook
        """)
        
        print("\n🔄 REFLECTION SYSTEM DETAILS:")
        print(f"""
  Quality Threshold: 9.0+ (targeting 95% quality)
  Max Reflection Cycles: 2
  
  Reflection Trigger Conditions:
  • Overall quality score < threshold
  • Critical gaps identified in messaging
  • Premium quality features insufficient
  
  Reflection Process:
  1. Orchestrator evaluates quality scores
  2. Critique agent provides specific feedback
  3. Refinement agent applies improvements
  4. Meta-reviewer assesses process effectiveness
  5. Loop continues until quality threshold met
        """)
        
        print("\n✨ ADAPTIVE AI FEATURES (No Hardcoded Patterns):")
        print("""
  🤖 All Fallback Mechanisms Use Adaptive AI:
  • Business Discovery: Multi-pass extraction with AI recovery
  • Competitive Intelligence: AI-driven competitor analysis
  • Trust Building: Industry-intelligent without hardcoded patterns
  • Emotional Intelligence: AI-adaptive emotional mapping
  • Social Proof: AI-generated proof without templates
  • Content Creation: AI-driven content for any industry
  • Quality Review: 10-dimension scoring system
        """)
        
        # Try to generate Mermaid diagram
        try:
            print("\n📊 Generating Mermaid Diagram...")
            mermaid_graph = graph.draw_mermaid()
            
            # Save Mermaid diagram
            mermaid_file = "messagecraft_workflow.mmd"
            with open(mermaid_file, "w") as f:
                f.write(mermaid_graph)
            print(f"✅ Mermaid diagram saved to: {mermaid_file}")
            
            # Print first few lines of mermaid for preview
            lines = mermaid_graph.split('\\n')[:10]
            print(f"\n📝 Mermaid Preview (first 10 lines):")
            for line in lines:
                print(f"  {line}")
            print("  ...")
            
        except Exception as e:
            print(f"⚠️ Could not generate Mermaid diagram: {e}")
        
        # Try to generate PNG
        try:
            print("\n🖼️ Generating PNG Image...")
            png_data = graph.draw_mermaid_png()
            
            png_file = "messagecraft_workflow.png"
            with open(png_file, "wb") as f:
                f.write(png_data)
            print(f"✅ PNG image saved to: {png_file}")
            
        except Exception as e:
            print(f"⚠️ Could not generate PNG (may need graphviz): {e}")
        
        print("\n" + "="*80)
        print("🎯 GRAPH VISUALIZATION COMPLETE")
        print("="*80)
        print("\nFiles generated:")
        if os.path.exists("messagecraft_workflow.mmd"):
            print("  • messagecraft_workflow.mmd (Mermaid diagram)")
        if os.path.exists("messagecraft_workflow.png"):
            print("  • messagecraft_workflow.png (PNG image)")
        print("\nUse online Mermaid editor to visualize .mmd file:")
        print("  https://mermaid.live/")
        
    except Exception as e:
        print(f"❌ Error with agent system: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Required modules not available")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()