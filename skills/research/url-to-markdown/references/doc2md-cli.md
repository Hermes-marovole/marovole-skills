## Document Conversion Tool (doc2md)

Located at: `/Users/marovole/Workspace/doc2md/`

CLI tool for converting PDF/EPUB/DOCX/HTML documents to KB-ready Markdown.

### Quick Start for Claude Code Users (Recommended)

**Best Practice: Use Gemini Free Tier**

For Claude Code users, we recommend using Gemini CLI's free tier (1500 requests/day) for document OCR:

```bash
# 1. Ensure Gemini CLI is installed
which gemini || npm install -g @google/gemini-cli

# 2. Run directly (auto-detects Gemini)
cd /Users/marovole/Workspace/doc2md
node bin/doc2md extract document.pdf -o ./output
# → Auto-detects Gemini CLI → Uses Flash model (free tier)
```

### Provider Priority (Auto-Detection)

1. **Gemini Flash** (Recommended) - 1500 requests/day free ✅
2. **OpenAI** - Requires OPENAI_API_KEY
3. **Custom Provider** - Requires configuration
4. **Agent CLI** - Uses Claude's own vision (fallback)

### Common Commands

```bash
# Basic extraction (auto-selects best provider)
node bin/doc2md extract file.pdf -o ./output

# Use specific provider and model
node bin/doc2md extract file.pdf --provider gemini --model gemini-2.5-flash-lite

# Check remaining quota
node bin/doc2md quota

# Quick setup for Gemini
node bin/doc2md setup --gemini

# When quota runs low, switch to Agent
node bin/doc2md extract file.pdf --provider agent
```

### Gemini Model Options

- `gemini-2.5-flash` (default) - Balanced quality and speed
- `gemini-2.5-flash-lite` - Faster processing

### Quota Warnings

The tool automatically tracks Gemini usage locally:
- Shows usage after each extraction
- Warns at 70% (1500 requests/day)
- Critical warning at 90%
- Use `node bin/doc2md quota` to check anytime

### Quick Start (Legacy)

```bash
# Build (if not already built)
cd /Users/marovole/Workspace/doc2md && pnpm build

# Extract any document
node /Users/marovole/Workspace/doc2md/bin/doc2md extract <input> -o <output_dir>
```

### Supported Formats

- **PDF**: Uses vision AI (OpenAI/Gemini/Agent) to transcribe pages to images then OCR
- **EPUB**: Direct text extraction via epub2 parser
- **DOCX**: Direct text extraction via mammoth
- **HTML/URL**: Direct conversion via turndown
- **Old DOC**: Uses vision AI same as PDF

### Usage Examples

```bash
# Basic extraction (auto-detect provider)
node bin/doc2md extract document.pdf -o ./output

# With specific provider
node bin/doc2md extract document.pdf -o ./output --provider openai

# From URL
node bin/doc2md extract https://example.com/page.html -o ./output

# Different output modes
node bin/doc2md extract doc.pdf --mode full      # Full content only
node bin/doc2md extract doc.pdf --mode brief     # Summary only
node bin/doc2md extract doc.pdf --mode both      # Both (default)

# Configuration
node bin/doc2md config                           # Show current config
node bin/doc2md init -o ./doc2md.config.json     # Generate sample config
```

### Vision Providers

Choose based on available credentials:

1. **OpenAI** (best quality): `export OPENAI_API_KEY="sk-..."` then `--provider openai`
2. **Gemini**: `export GEMINI_API_KEY="..."` then `--provider gemini`
3. **Agent CLI** (no API key): `--provider agent` (uses local opencode/codex)

### Output Files

Each extraction produces three files:

- `{name}.full.md` - Complete document with frontmatter
- `{name}.brief.md` - First 24 paragraphs summary
- `{name}.qa-checklist.md` - Quality assurance checklist

### When to Use

Use this tool when you need to:
- Convert PDF research papers to readable Markdown
- Process documentation for knowledge base ingestion
- Extract content from EPUB e-books
- Convert Word documents to Markdown format
- Archive web pages as Markdown

### Agent Workflow Integration

```bash
# Convert PDF for easier reading/editing
node /Users/marovole/Workspace/doc2md/bin/doc2md extract ./docs/spec.pdf -o ./docs --provider agent

# Read the markdown version
cat ./docs/spec.full.md
```

### Detailed Documentation

(Full CLI documentation consolidated in this file.)
