from setuptools import setup, find_packages

setup(
    name="youtube-lecture-processor",
    version="1.0.0",
    packages=find_packages(),
    scripts=[
        'scripts/extract_keyframes.py',
        'scripts/align_transcript_keyframes.py',
        'scripts/create_document.py',
        'scripts/video_qa.py',
    ],
    install_requires=[
        'opencv-python>=4.8.0',
        'yt-dlp>=2023.12.0',
        'pyyaml>=6.0',
    ],
    extras_require={
        'docx': ['python-docx>=1.1.0'],
        'gdocs': [
            'google-auth>=2.25.0',
            'google-auth-oauthlib>=1.2.0',
            'google-auth-httplib2>=0.2.0',
            'google-api-python-client>=2.111.0',
        ],
        'dev': ['pytest', 'black', 'flake8', 'mypy'],
    },
    python_requires='>=3.11',
    author='YouTube Lecture Processor Contributors',
    description='Process YouTube videos to extract transcripts, keyframes, and create study notes',
    long_description=open('README.md').read() if __file__ else '',
    long_description_content_type='text/markdown',
    url='https://github.com/edvantageAI/agent-skills',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
