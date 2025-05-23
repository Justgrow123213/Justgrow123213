# Real Estate Multi-Agent System

This project implements a multi-agent AI system for real estate that includes:

1. **Data Collection Agent**: Gathers and maintains information about real estate properties
2. **Sales Agent**: Communicates with clients, understands their needs, and matches them with suitable properties

## Project Structure

```
real_estate_agents/
├── data_collector/     # Agent for collecting property data
├── sales_agent/        # Agent for client interaction and property matching
├── database/           # Storage for property information
├── utils/              # Shared utilities
└── api/                # API for system interaction
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   Create a `.env` file with your API keys and configuration

3. Run the application:
   ```
   python main.py
   ```

## Usage

The system provides an API for interacting with the real estate agents. You can:
- Query available properties
- Submit client requirements
- Get property recommendations