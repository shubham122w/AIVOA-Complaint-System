# AIVOA AI Complaint Management System

An AI-powered Customer Complaint Management System designed for pharmaceutical manufacturing.

## Features

- AI complaint data extraction
- PDF complaint analysis
- AI severity and priority classification
- AI risk assessment
- Natural-language complaint correction
- Complaint completeness checker
- Root cause recommendation
- Duplicate complaint detection
- CAPA recommendation
- Complaint summary generation
- QMS complaint ledger

## Tech Stack

- React
- Redux Toolkit
- FastAPI
- Python
- LangGraph
- Groq
- MySQL / PostgreSQL
- PyPDF
- Axios
- Vite

## AI Workflow

Customer Complaint  
↓  
Text / PDF Input  
↓  
FastAPI Backend  
↓  
LangGraph AI Workflow  
↓  
Complaint Data Extraction  
↓  
Risk Assessment  
↓  
Severity & Priority Classification  
↓  
React + Redux Frontend  
↓  
AI Copilot  
↓  
Quality Review / Correction  
↓  
QMS Complaint Ledger

## AI Capabilities

### Complaint Data Extraction

The AI extracts:

- Customer name
- Product name
- Product strength
- Batch / Lot number
- Manufacturing date
- Expiry date
- Affected quantity
- Complaint category
- Complaint description
- Severity
- Priority
- Suggested next action
- Initial risk assessment

### PDF Complaint Analysis

Users can upload a customer complaint PDF and the AI extracts relevant complaint information automatically.

### AI-Powered Correction

Users can correct extracted information using natural language.

Example:

> Change the batch number to BMX240602 and affected quantity to 48 capsules.

### Complaint Completeness Checker

Checks whether important complaint information is available before committing the complaint.

### Root Cause Recommendation

Generates possible root causes and recommended investigation steps.

### Duplicate Complaint Detection

Compares the current complaint with existing QMS complaints and identifies possible duplicates.

### CAPA Recommendation

Generates corrective actions, preventive actions, and QA verification recommendations.

### Complaint Summary

Generates a concise QA-ready summary of the complaint.

### AI Risk Classification

Provides:

- Risk level
- Severity
- Priority
- Risk factors
- Classification rationale
- QA attention recommendation

## Screenshots

### 1. Initial Complaint Interface

![Initial Complaint Interface](screenshots/01-home.png)

### 2. AI Complaint Analysis

![AI Complaint Analysis](screenshots/02-ai-analysis.png)

### 3. AI-Powered Correction

![AI Correction](screenshots/03-ai-correction.png)

### 4. QMS Ledger Commit

![QMS Commit](screenshots/04-qms-commit.png)

### 5. QMS Complaint Ledger

![QMS Complaint Ledger](screenshots/05-qms-ledger.png)

## Project Structure

```text
AIVOA-Complaint-System/
├── backend/
├── frontend/
├── screenshots/
├── .gitignore
├── package.json
├── package-lock.json
└── README.md