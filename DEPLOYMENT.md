# Deployment Guide

This guide explains how to deploy the Real Estate Multi-Agent System.

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (for AI functionality)

## Deployment Options

### 1. Docker Deployment (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/Justgrow123213/Justgrow123213.git
   cd Justgrow123213
   ```

2. Create a `.env` file with your OpenAI API key:
   ```
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

3. Run the Docker deployment script:
   ```
   ./docker-run.sh
   ```

4. Access the application:
   - Web interface: http://localhost:8000
   - API documentation: http://localhost:8000/docs

5. To stop the application:
   ```
   docker-compose down
   ```

### 2. Manual Deployment

1. Clone the repository:
   ```
   git clone https://github.com/Justgrow123213/Justgrow123213.git
   cd Justgrow123213
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenAI API key:
   ```
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

4. Run the application:
   ```
   ./run.sh both  # Run both the web app and the scraper
   ```

   Alternatively, you can run them separately:
   ```
   ./run.sh app     # Run only the web app
   ./run.sh scraper # Run only the scraper
   ```

5. Access the application:
   - Web interface: http://localhost:8000
   - API documentation: http://localhost:8000/docs

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for AI functionality)

### Data Storage

Property data is stored in `data/properties.json`. This file is created automatically if it doesn't exist.

## Scraping Configuration

To configure the property scrapers:

1. Edit `schedule_scraping.py` to change the scraping schedule or sources
2. Run the scraper manually:
   ```
   python scrape_properties.py --source ddproperty --location bangkok --max-pages 2
   ```

## Troubleshooting

### Mock Mode

If no valid OpenAI API key is provided, the system will run in mock mode with simulated AI responses.

### Logs

- Application logs: Standard output
- Scraper logs: `scraping.log`