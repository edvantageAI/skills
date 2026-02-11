#!/usr/bin/env python3
"""
Video Q&A using VideoRAG for asking questions about lecture videos.
Requires VideoRAG installation and setup.
"""

import argparse
import sys
import os
import json
import warnings
import logging
import multiprocessing
from pathlib import Path
import yaml

warnings.filterwarnings("ignore")
logging.getLogger("httpx").setLevel(logging.WARNING)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path=None):
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent.parent / 'config.yaml'

    config_path = Path(config_path)
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return {}
    return {}


def check_videorag_installed():
    """Check if VideoRAG is installed."""
    try:
        import videorag
        return True
    except ImportError:
        return False


def setup_videorag(working_dir, llm_provider="openai", api_key=None, model_name=None, config=None):
    """
    Initialize VideoRAG instance with custom LLM configurations.

    Args:
        working_dir: Directory to store VideoRAG index and cache
        llm_provider: LLM provider (openai, anthropic, gemini, ollama)
        api_key: API key for the LLM provider
        model_name: Specific model name to use (optional)
        config: Configuration dict from config.yaml

    Returns:
        VideoRAG instance
    """
    from videorag import VideoRAG

    # Get default models from config
    if config:
        videorag_config = config.get('videorag', {})
        models = videorag_config.get('models', {})
    else:
        models = {}

    # Set API key if provided
    if api_key:
        if llm_provider == "openai":
            os.environ["OPENAI_API_KEY"] = api_key
        elif llm_provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = api_key
        elif llm_provider == "gemini":
            os.environ["GOOGLE_API_KEY"] = api_key

    # Define our own LLM configurations (no internal imports)
    llm_configs = {
        "openai": {
            "model": model_name or models.get('openai', 'gpt-4o-mini'),
            "api_base": "https://api.openai.com/v1",
            "api_key": os.environ.get("OPENAI_API_KEY"),
            "temperature": 0.7,
        },
        "anthropic": {
            "model": model_name or models.get('anthropic', 'claude-3-5-sonnet-20241022'),
            "api_base": "https://api.anthropic.com",
            "api_key": os.environ.get("ANTHROPIC_API_KEY"),
            "temperature": 0.7,
        },
        "gemini": {
            "model": model_name or models.get('gemini', 'gemini-1.5-flash'),
            "api_key": os.environ.get("GOOGLE_API_KEY"),
            "temperature": 0.7,
        },
        "ollama": {
            "model": model_name or models.get('ollama', 'llama3.1:8b'),
            "api_base": "http://localhost:11434",
            "temperature": 0.7,
        }
    }

    if llm_provider not in llm_configs:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    llm_config = llm_configs[llm_provider]

    # Initialize VideoRAG
    try:
        videorag = VideoRAG(llm=llm_config, working_dir=working_dir)
    except Exception as e:
        # Fallback for older VideoRAG versions or if config is incompatible
        logger.warning(f"Failed to initialize with custom config: {e}")
        logger.info("Falling back to VideoRAG defaults...")
        try:
            videorag = VideoRAG(working_dir=working_dir)
        except Exception as e2:
            logger.error(f"Failed to initialize VideoRAG: {e2}", exc_info=True)
            raise

    return videorag


def index_videos(videorag, video_paths):
    """
    Index videos for Q&A.
    
    Args:
        videorag: VideoRAG instance
        video_paths: List of video file paths
    """
    logger.info(f"Indexing {len(video_paths)} video(s)...")
    logger.info("This may take a while depending on video length...")

    videorag.insert_video(video_path_list=video_paths)

    logger.info(f"✅ Successfully indexed {len(video_paths)} video(s)")


def query_video(videorag, question, with_references=True):
    """
    Ask a question about the indexed videos.
    
    Args:
        videorag: VideoRAG instance
        question: Question to ask
        with_references: Whether to include video clip references
    
    Returns:
        Answer string
    """
    from videorag import QueryParam
    
    # Load caption model if not already loaded
    videorag.load_caption_model(debug=False)
    
    # Set query parameters
    param = QueryParam(mode="videorag")
    param.wo_reference = not with_references
    
    # Query
    logger.info(f"Question: {question}")
    logger.info("Generating answer...")

    response = videorag.query(query=question, param=param)

    return response


def interactive_mode(videorag):
    """
    Interactive Q&A mode - ask multiple questions.
    
    Args:
        videorag: VideoRAG instance
    """
    print("\n" + "="*60)
    print("Interactive Q&A Mode")
    print("Type your questions (or 'quit' to exit)")
    print("="*60 + "\n")
    
    while True:
        try:
            question = input("Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Exiting...")
                break
            
            if not question:
                continue
            
            answer = query_video(videorag, question, with_references=True)
            print(f"\nAnswer: {answer}\n")
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


def main():
    # Load configuration
    config = load_config()
    videorag_config = config.get('videorag', {})
    default_llm = videorag_config.get('default_llm', 'openai')

    parser = argparse.ArgumentParser(
        description='Ask questions about lecture videos using VideoRAG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index videos first
  python video_qa.py --index lecture1.mp4 lecture2.mp4 --working-dir ./qa-index

  # Ask a single question
  python video_qa.py --working-dir ./qa-index --question "What is the main topic?"

  # Interactive mode
  python video_qa.py --working-dir ./qa-index --interactive

  # Use Ollama instead of OpenAI
  python video_qa.py --index lecture.mp4 --working-dir ./qa-index --llm ollama

  # Use Anthropic Claude
  python video_qa.py --working-dir ./qa-index --llm anthropic --question "Summarize the lecture"

  # Use Google Gemini with specific model
  python video_qa.py --working-dir ./qa-index --llm gemini --model gemini-1.5-pro --interactive
        """
    )

    parser.add_argument('--index', nargs='+', metavar='VIDEO',
                        help='Video file(s) to index for Q&A')
    parser.add_argument('--working-dir', required=True,
                        help='Directory to store VideoRAG index and cache')
    parser.add_argument('--question', '-q',
                        help='Question to ask about the videos')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Enter interactive Q&A mode')
    parser.add_argument('--llm', choices=['openai', 'anthropic', 'gemini', 'ollama'], default=default_llm,
                        help=f'LLM provider to use (default: {default_llm})')
    parser.add_argument('--model',
                        help='Specific model name (e.g., gpt-4o, claude-3-5-sonnet-20241022, gemini-1.5-pro)')
    parser.add_argument('--api-key',
                        help='API key for LLM provider (or set OPENAI_API_KEY/ANTHROPIC_API_KEY/GOOGLE_API_KEY env var)')
    parser.add_argument('--no-references', action='store_true',
                        help='Do not include video clip references in answers')
    parser.add_argument('--config', help='Path to config file')

    args = parser.parse_args()

    # Reload config if custom path provided
    if args.config:
        config = load_config(args.config)
    
    # Check if VideoRAG is installed
    if not check_videorag_installed():
        logger.error("VideoRAG is not installed")
        logger.error("\nTo install VideoRAG, follow these steps:")
        logger.error("1. Clone the repository:")
        logger.error("   git clone https://github.com/HKUDS/VideoRAG.git")
        logger.error("2. Follow installation instructions in VideoRAG-algorithm/README.md")
        sys.exit(1)
    
    # Validate arguments
    if not args.index and not args.question and not args.interactive:
        parser.error("Must specify --index, --question, or --interactive")
    
    # Check API key for cloud providers
    if args.llm == 'openai' and not args.api_key and not os.environ.get('OPENAI_API_KEY'):
        parser.error("OpenAI API key required. Set via --api-key or OPENAI_API_KEY env var")
    elif args.llm == 'anthropic' and not args.api_key and not os.environ.get('ANTHROPIC_API_KEY'):
        parser.error("Anthropic API key required. Set via --api-key or ANTHROPIC_API_KEY env var")
    elif args.llm == 'gemini' and not args.api_key and not os.environ.get('GOOGLE_API_KEY'):
        parser.error("Google API key required. Set via --api-key or GOOGLE_API_KEY env var")
    
    try:
        # Set multiprocessing start method
        multiprocessing.set_start_method('spawn', force=True)
        
        # Initialize VideoRAG
        logger.info("Initializing VideoRAG...")
        videorag = setup_videorag(
            working_dir=args.working_dir,
            llm_provider=args.llm,
            api_key=args.api_key,
            model_name=args.model,
            config=config
        )
        
        # Index videos if specified
        if args.index:
            # Validate video files exist
            for video_path in args.index:
                if not Path(video_path).exists():
                    logger.error(f"Video file not found: {video_path}")
                    sys.exit(1)

            index_videos(videorag, args.index)
        
        # Answer question if specified
        if args.question:
            answer = query_video(
                videorag,
                args.question,
                with_references=not args.no_references
            )
            print(f"\nAnswer: {answer}\n")
        
        # Enter interactive mode if specified
        if args.interactive:
            interactive_mode(videorag)

        logger.info("✅ Done")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
