# Ministry of Finance Budget Analysis System

A full-stack application for analyzing financial data and generating comprehensive budget reports using a multi-agent AI system.

## Project Structure

```
ministry-finance-system/
├── backend/           # Existing Python multi-agent backend
│   ├── agents/        # Agent implementations
│   ├── skills/        # Tools and utilities
│   ├── main.py        # Main entry point
│   └── ...
├── frontend/          # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── ...
│   └── package.json
└── api/               # FastAPI wrapper
    ├── server.py      # API endpoints
    └── requirements.txt
```

## Setup Instructions

### 1. Backend Setup

The backend should already be set up as per your existing codebase. Make sure your environment variables are configured properly in a `.env` file:

```
OPENAI_API_KEY=your_openai_api_key
MODEL=gpt-4o-2024-08-06  # or your preferred model
```

### 2. API Setup

1. Navigate to the `api` directory:
   ```
   cd api
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:
   ```
   python server.py
   ```

   The API will be available at http://localhost:8000

### 3. Frontend Setup

1. Navigate to the `frontend` directory:
   ```
   cd frontend
   ```

2. Install the required dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

   The frontend will be available at http://localhost:3000

## Usage

1. Open your browser and navigate to http://localhost:3000
2. Upload a JSON file with the required structure (including revenue, expenditure, inflation, and gdp_growth data)
3. The system will process the data and generate a comprehensive budget analysis report
4. Once processing is complete, you can download the generated PDF report

## JSON File Format

The uploaded JSON file should have the following structure:

```json
{
  "revenue": [
    { "name": "Tax Revenue", "amount": 5000000 },
    { "name": "Non-tax Revenue", "amount": 2000000 },
    ...
  ],
  "expenditure": [
    { "name": "Education", "amount": 3000000 },
    { "name": "Healthcare", "amount": 2500000 },
    ...
  ],
  "inflation": [
    { "year": "2020", "rate": 3.4 },
    { "year": "2021", "rate": 3.5 },
    ...
  ],
  "gdp_growth": [
    { "year": "2020", "rate": 1.5 },
    { "year": "2021", "rate": 2.5 },
    ...
  ]
}
```

## System Workflow

1. The user uploads a JSON file through the frontend
2. The API validates the file structure and starts the multi-agent processing pipeline
3. The Data Manager Agent validates the data and creates visual plots
4. The Budget Agent generates projections and performs risk analysis
5. The Tax Policy Agent recommends tax slabs based on the projections
6. The Report Agent compiles all information into a comprehensive PDF report
7. The user can download the generated report through the frontend