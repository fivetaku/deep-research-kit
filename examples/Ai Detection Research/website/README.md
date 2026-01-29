# AI Detection Research Comparison Website

This website presents a comprehensive comparison of AI detection research outputs from different AI tools based on the same initial prompt.

## Features

- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Tab Navigation**: Easy switching between different tool outputs
- **Expandable Content**: Summary view with option to see full research
- **Comparison Overview**: Side-by-side comparison of all tools
- **Fast Loading**: All content embedded for instant access

## Tools Compared

1. **Claude Code Deep Research**: Most comprehensive with 50,000+ words
2. **Gemini Pro**: Strong academic focus on the "arms race" dynamics
3. **Manus Free**: Well-structured modular approach
4. **OpenAI Pro**: Comprehensive single document with policy focus
5. **Perplexity Pro**: Concise field briefing format

## Usage

Simply open `index.html` in a web browser. No server required - all content is embedded.

## Updating Content

To update the research content:
1. Place new research files in their respective folders
2. Run `python3 compile_research_data.py` to regenerate the data
3. Refresh the website

## Technical Details

- Pure HTML/CSS/JavaScript (no framework dependencies)
- Markdown rendering via marked.js
- Responsive CSS Grid layout
- Tab-based navigation system