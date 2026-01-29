#!/usr/bin/env python3
"""
Compile research data from various folders into a JavaScript file for the website
"""

import os
import json
import re

def clean_text(text):
    """Clean text for JavaScript string embedding"""
    # Remove zone identifier lines
    text = re.sub(r'.*:Zone\.Identifier.*\n', '', text)
    # Escape backticks and dollar signs for template literals
    text = text.replace('`', '\\`').replace('$', '\\$')
    return text

def read_file_safely(filepath):
    """Read file content safely, handling encoding issues"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return clean_text(f.read())
    except:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return clean_text(f.read())
        except:
            return "Error reading file"

def get_claude_research():
    """Extract Claude Code Deep Research content"""
    base_path = "../Claude Code Deep Research output"
    
    # Read executive summary
    summary_path = os.path.join(base_path, "00_Executive_Summary.md")
    summary = read_file_safely(summary_path) if os.path.exists(summary_path) else ""
    
    # Compile full research from all parts
    full_parts = [
        "00_Executive_Summary.md",
        "01_Full_Report_Part1_Current_Landscape.md", 
        "02_Full_Report_Part2_End_User_Solutions.md",
        "03_Full_Report_Part3_Technical_Architecture_Ch14.md",
        "03_Full_Report_Part3_Technical_Architecture_Ch15.md",
        "03_Full_Report_Part3_Technical_Architecture_Ch16.md",
        "03_Full_Report_Part3_Technical_Architecture_Ch17.md",
        "03_Full_Report_Part3_Technical_Architecture_Ch18.md",
        "04_Full_Report_Part4_Effectiveness_Ch19.md",
        "04_Full_Report_Part4_Effectiveness_Ch20.md",
        "04_Full_Report_Part4_Effectiveness_Ch21.md",
        "04_Full_Report_Part4_Effectiveness_Ch22.md",
        "04_Full_Report_Part4_Effectiveness_Ch23.md",
        "05_Full_Report_Part5_Standards_Ch24.md",
        "05_Full_Report_Part5_Standards_Ch25.md",
        "05_Full_Report_Part5_Standards_Ch26.md",
        "05_Full_Report_Part5_Standards_Ch27.md",
        "05_Full_Report_Part5_Standards_Ch28.md"
    ]
    
    full_content = []
    for part in full_parts:
        filepath = os.path.join(base_path, part)
        if os.path.exists(filepath):
            content = read_file_safely(filepath)
            if content and content != "Error reading file":
                full_content.append(content)
    
    return {
        "summary": summary[:5000] if summary else "",  # First 5000 chars for summary
        "fullResearch": "\\n\\n---\\n\\n".join(full_content)
    }

def get_gemini_research():
    """Extract Gemini research content"""
    filepath = "../Gemini Output (pro plan)/Gemini output.md"
    content = read_file_safely(filepath) if os.path.exists(filepath) else ""
    
    return {
        "summary": content[:5000] if content else "",
        "fullResearch": content
    }

def get_manus_research():
    """Extract Manus research content"""
    base_path = "../Manus output (free plan)"
    
    # Read field briefing as summary
    summary_path = os.path.join(base_path, "field_briefing.md")
    summary = read_file_safely(summary_path) if os.path.exists(summary_path) else ""
    
    # Compile full research from multiple files
    files = [
        "field_briefing.md",
        "Comprehensive Field Briefing_ Detecting AI-Generated Content.md",
        "ai_text_detection_overview.md",
        "ai_image_detection_overview.md",
        "ai_video_detection_overview.md",
        "ai_voice_detection_overview.md",
        "end_user_toolkit.md",
        "developer_blueprints.md",
        "roadmap_tables.md"
    ]
    
    full_content = []
    for file in files:
        filepath = os.path.join(base_path, file)
        if os.path.exists(filepath):
            content = read_file_safely(filepath)
            if content and content != "Error reading file":
                full_content.append(f"# {file}\\n\\n{content}")
    
    return {
        "summary": summary[:5000] if summary else "",
        "fullResearch": "\\n\\n---\\n\\n".join(full_content)
    }

def get_openai_research():
    """Extract OpenAI research content"""
    filepath = "../Openai Output (pro plan)/Openai Deep Research output.md"
    content = read_file_safely(filepath) if os.path.exists(filepath) else ""
    
    return {
        "summary": content[:5000] if content else "",
        "fullResearch": content
    }

def get_perplexity_research():
    """Extract Perplexity research content"""
    filepath = "../Perpelxity deep research (pro plan)/AI Content Detection Field Briefing_ Methods, Tool.md"
    content = read_file_safely(filepath) if os.path.exists(filepath) else ""
    
    return {
        "summary": content[:5000] if content else "",
        "fullResearch": content
    }

def get_initial_prompt():
    """Extract initial prompt content"""
    filepath = "../Initial Prompt Used.md"
    return read_file_safely(filepath) if os.path.exists(filepath) else ""

def main():
    """Main function to compile all research data"""
    print("Compiling research data...")
    
    # Change to the website directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Compile all research data
    research_data = {
        "claude": get_claude_research(),
        "gemini": get_gemini_research(),
        "manus": get_manus_research(),
        "openai": get_openai_research(),
        "perplexity": get_perplexity_research(),
        "initialPrompt": get_initial_prompt()
    }
    
    # Generate JavaScript file
    js_content = f"""// Research data content (compiled from source files)
const researchData = {{
    claude: {{
        summary: `{research_data['claude']['summary']}`,
        fullResearch: `{research_data['claude']['fullResearch']}`
    }},
    gemini: {{
        summary: `{research_data['gemini']['summary']}`,
        fullResearch: `{research_data['gemini']['fullResearch']}`
    }},
    manus: {{
        summary: `{research_data['manus']['summary']}`,
        fullResearch: `{research_data['manus']['fullResearch']}`
    }},
    openai: {{
        summary: `{research_data['openai']['summary']}`,
        fullResearch: `{research_data['openai']['fullResearch']}`
    }},
    perplexity: {{
        summary: `{research_data['perplexity']['summary']}`,
        fullResearch: `{research_data['perplexity']['fullResearch']}`
    }},
    initialPrompt: `{research_data['initialPrompt']}`
}};

// Export data for use in main script
window.researchData = researchData;"""
    
    # Write to file
    with open('data-loader.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("Research data compiled successfully!")
    print(f"Claude research: {len(research_data['claude']['fullResearch'])} chars")
    print(f"Gemini research: {len(research_data['gemini']['fullResearch'])} chars")
    print(f"Manus research: {len(research_data['manus']['fullResearch'])} chars")
    print(f"OpenAI research: {len(research_data['openai']['fullResearch'])} chars")
    print(f"Perplexity research: {len(research_data['perplexity']['fullResearch'])} chars")

if __name__ == "__main__":
    main()