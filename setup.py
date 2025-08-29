from setuptools import setup, find_packages

setup(
    name="video-to-text",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "click>=8.2.0",
        "yt-dlp>=2025.8.11",
        "faster-whisper>=1.2.0",
        "requests>=2.32.0",
        "python-dotenv>=1.1.0",
        "isodate>=0.7.2",
    ],
    extras_require={
        "dev": [
            "pytest>=8.4.1",
            "pytest-vcr>=1.0.2",
        ]
    },
    entry_points={
        "console_scripts": [
            "video-to-text=video_to_text.entrypoint:main",
        ],
    },
    include_package_data=True,
    description="Download and transcribe YouTube videos from a channel",
    author="Jindu Okoli",
    license="MIT",
)
