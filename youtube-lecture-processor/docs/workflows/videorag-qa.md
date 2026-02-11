# VideoRAG Q&A Workflow

Ask questions about video content using AI-powered retrieval and question answering.

## Overview

VideoRAG enables you to:
- Index lecture videos for semantic search
- Ask questions about video content
- Get answers with references to specific video segments
- Interactive Q&A sessions

## Prerequisites

1. **VideoRAG installation** - See [Installation Guide](../installation.md#optional-videorag-for-qa)
2. **LLM API access** - Choose one:
   - OpenAI API key
   - Anthropic API key
   - Google Gemini API key
   - Local Ollama installation

## Quick Start

### 1. Set API Key

```bash
export OPENAI_API_KEY="sk-..."
# Or
export ANTHROPIC_API_KEY="sk-ant-..."
# Or
export GOOGLE_API_KEY="..."
```

### 2. Index a Video

```bash
python scripts/video_qa.py --index lecture.mp4 --working-dir ./qa-index
```

This processes the video and creates a searchable index in `./qa-index/`.

**Indexing time:** Depends on video length and hardware. Expect 2-5x video duration on CPU.

### 3. Ask Questions

**Single question:**

```bash
python scripts/video_qa.py --working-dir ./qa-index --question "What is the main topic discussed?"
```

**Interactive mode:**

```bash
python scripts/video_qa.py --working-dir ./qa-index --interactive
```

Type questions and get instant answers!

## Detailed Usage

### Indexing Videos

#### Index Multiple Videos

```bash
python scripts/video_qa.py \
  --index lecture1.mp4 lecture2.mp4 lecture3.mp4 \
  --working-dir ./course-index
```

All videos are indexed together, enabling cross-video Q&A.

#### Using Different LLM Providers

**Anthropic Claude:**

```bash
python scripts/video_qa.py \
  --index lecture.mp4 \
  --working-dir ./qa-index \
  --llm anthropic
```

**Google Gemini:**

```bash
python scripts/video_qa.py \
  --index lecture.mp4 \
  --working-dir ./qa-index \
  --llm gemini
```

**Local Ollama:**

```bash
# First, start Ollama server with:
# ollama serve

python scripts/video_qa.py \
  --index lecture.mp4 \
  --working-dir ./qa-index \
  --llm ollama
```

#### Specific Models

```bash
python scripts/video_qa.py \
  --index lecture.mp4 \
  --working-dir ./qa-index \
  --llm openai \
  --model gpt-4o
```

### Asking Questions

#### Single Question Mode

```bash
python scripts/video_qa.py \
  --working-dir ./qa-index \
  --question "Summarize the key points about machine learning"
```

**Without video references:**

```bash
python scripts/video_qa.py \
  --working-dir ./qa-index \
  --question "What are the main topics?" \
  --no-references
```

#### Interactive Mode

```bash
python scripts/video_qa.py --working-dir ./qa-index --interactive
```

**Example session:**

```
Question: What is supervised learning?
Generating answer...

Answer: Supervised learning is a type of machine learning where the model is trained on labeled data...
[References: video_1.mp4 at 00:15:30, video_2.mp4 at 00:03:45]

------------------------------------------------------------

Question: Compare supervised and unsupervised learning
Generating answer...

Answer: The main differences are...

------------------------------------------------------------

Question: quit
Exiting...
```

### Advanced Options

#### Re-indexing

To re-index (e.g., after adding more videos):

```bash
# Add new videos to existing index
python scripts/video_qa.py \
  --index new_lecture.mp4 \
  --working-dir ./qa-index
```

VideoRAG handles incremental indexing.

#### Working Directory Structure

```
./qa-index/
├── video_features/      # Extracted video features
├── text_index/          # Text embeddings
├── metadata.json        # Index metadata
└── cache/              # Model cache
```

**Storage:** Expect ~100-500MB per hour of video.

## LLM Provider Comparison

### OpenAI (Default)

**Models:** gpt-4o-mini (default), gpt-4o, gpt-4-turbo

**Pros:**
- Fast responses
- High quality answers
- Good video understanding

**Cons:**
- Requires API key
- Costs per query

**Setup:**
```bash
export OPENAI_API_KEY="sk-..."
```

### Anthropic Claude

**Models:** claude-3-5-sonnet-20241022 (default), claude-3-opus

**Pros:**
- Excellent reasoning
- Long context support
- Detailed answers

**Cons:**
- Requires API key
- Higher cost than OpenAI

**Setup:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Google Gemini

**Models:** gemini-1.5-flash (default), gemini-1.5-pro

**Pros:**
- Multimodal capabilities
- Fast processing
- Competitive pricing

**Cons:**
- Requires API key
- May need Google Cloud setup

**Setup:**
```bash
export GOOGLE_API_KEY="..."
```

### Ollama (Local)

**Models:** llama3.1:8b (default), mistral, phi3

**Pros:**
- Completely free
- No API key needed
- Privacy (runs locally)

**Cons:**
- Requires powerful hardware
- Slower than cloud models
- Lower quality answers

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull llama3.1:8b

# Start server
ollama serve
```

## Configuration

Default LLM provider can be set in `config.yaml`:

```yaml
videorag:
  default_llm: openai
  models:
    openai: gpt-4o-mini
    anthropic: claude-3-5-sonnet-20241022
    gemini: gemini-1.5-flash
    ollama: llama3.1:8b
```

## Use Cases

### Study Sessions

Index course lectures and quiz yourself:

```bash
# Index all lectures
python scripts/video_qa.py --index lecture*.mp4 --working-dir ./course

# Interactive Q&A
python scripts/video_qa.py --working-dir ./course --interactive
```

### Research

Extract specific information from conference talks:

```bash
python scripts/video_qa.py \
  --working-dir ./conference-talks \
  --question "What are the latest advances in transformer architectures?"
```

### Content Creation

Generate summaries and key points:

```bash
python scripts/video_qa.py \
  --working-dir ./videos \
  --question "Create a bullet-point summary of the main topics" \
  --no-references
```

## Tips & Best Practices

### Indexing

- **Batch index:** Index multiple related videos together
- **Storage:** Keep working directory on SSD for faster access
- **GPU:** Use CUDA-enabled GPU for 5-10x faster indexing

### Asking Questions

- **Be specific:** "Explain the backpropagation algorithm" > "Tell me about neural networks"
- **Context:** Reference specific topics mentioned in the videos
- **Follow-ups:** Build on previous questions in interactive mode

### Performance

- **First query:** Slower (model loading), subsequent queries are faster
- **Long videos:** May take longer to search and retrieve
- **Multiple videos:** Cross-video queries may be slower

### Cost Management

**For OpenAI:**
- Use `gpt-4o-mini` (default) for most queries
- Upgrade to `gpt-4o` only for complex questions
- `--no-references` mode uses less tokens

**For Anthropic:**
- `claude-3-5-sonnet` is the standard model
- Use for high-quality, detailed answers

**For Ollama:**
- Free but requires local compute
- `llama3.1:8b` is a good balance of speed and quality

## Troubleshooting

### VideoRAG Not Installed

```
Error: VideoRAG is not installed.
```

**Solution:** Follow [VideoRAG installation guide](../installation.md#optional-videorag-for-qa)

### API Key Errors

```
Error: OpenAI API key required
```

**Solution:** Set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

### Out of Memory

```
CUDA out of memory
```

**Solutions:**
- Use smaller model: `--model gpt-4o-mini`
- Process shorter videos
- Use CPU instead of GPU (slower)

### Slow Performance

**Solutions:**
- Use GPU if available
- Switch to faster model (e.g., gemini-1.5-flash)
- Use local Ollama with smaller model

## Next Steps

- [Document Generation Workflow](document-generation.md) - Create study notes
- [Configuration Reference](../configuration.md) - Customize VideoRAG settings
- [Troubleshooting](../troubleshooting.md) - Common issues
