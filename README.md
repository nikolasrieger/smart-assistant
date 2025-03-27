# 🚀 OmniAssist: Smart Assistant for Computer Interaction

## Overview

Welcome to the **Smart Assistant** GitHub repository! This project is designed to enable users to perform tasks on their computer using **🗣️ speech input** and **👁️ visual analysis** of the computer screen. The assistant combines natural language processing (NLP) and real-time screen analysis to create an intuitive hands-free experience for interacting with your desktop environment.

With this assistant, users can control various applications, automate tasks, and perform everyday actions like opening programs, managing files, and browsing the web, all via simple voice commands. 🖥️🎙️

## 🌟 Features

- **🗣️ Speech Command Recognition**: The assistant listens to your voice and processes natural language commands.
- **👁️ Screen Recognition**: It visually analyzes the screen to understand which windows, applications, and elements are currently displayed.
- **🤖 Task Automation**: Automatically performs tasks like opening apps, sending emails, copying files, and more based on voice commands and screen context.
- **🔄 Cross-Application Support**: Works with multiple software environments, such as browsers, text editors, and productivity tools.
- **🧠 Context Awareness**: Recognizes the current state of your desktop to execute commands in the right context (e.g., switching between applications, interacting with open windows).

## Known Limitations:

Click Timing & Placement – The agent occasionally lacks precision in determining the optimal moment and location to interact.

Error Recovery – If an unexpected step occurs, the agent may not always recognize the need to adjust.

Overactivity – In some cases, the agent might infer additional actions beyond the intended task.

## 🚀 Getting Started

### Prerequisites

To get started, ensure you have the following:
- **🐍 Python 3.x**: Required for running the assistant's core logic.
- **📦 Libraries**: Install the required libraries from `requirements.txt`
- **🔑 Gemini API Key**: For visual and textual understanding, create a `.env` file for that 
    (**Note**: Be aware, that screenshots of your screen will be sent to the Gemini Model and stored on the Google Cloud, but deleted afterwards by the assistant. Do not share any private or secret data. If you do not want that, you can simply plug-in your own model by adapting the `model.py` file.)

### Installation

1. Set up the virtual environment by running `python -m venv .venv`.
2. Activate the virtual environment:
   - On **Windows**: `.\.venv\Scripts\activate`
   - On **Linux**: `source .venv/bin/activate`
3. Run the backend with `python app.py`.

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
