# CareHaven AI

## AI-Powered Humanitarian Aid & Donation Platform

> **Turning Every Contribution Into Smarter Impact**

CareHaven AI is an intelligent humanitarian aid and donation platform designed to make humanitarian assistance **smarter, faster, more transparent, targeted, and data-driven**.

The platform combines **Artificial Intelligence, Machine Learning, Natural Language Processing, Large Language Models, Computer Vision, YOLO, Retrieval-Augmented Generation (RAG), recommendation systems, similarity detection, priority scoring, anomaly detection, and humanitarian analytics** to support donors, volunteers, humanitarian organizations, beneficiaries, and administrators.

The core humanitarian intelligence lifecycle is:

```text
Understand → Verify → Prioritize → Match → Support → Track → Predict
```

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Proposed Solution](#proposed-solution)
- [Project Objectives](#project-objectives)
- [Target Users](#target-users)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Architecture Layers](#architecture-layers)
- [Technology Stack](#technology-stack)
- [End-to-End Workflow](#end-to-end-workflow)
- [AI and ML Components](#ai-and-ml-components)
- [NLP and LLM](#nlp-and-llm)
- [Computer Vision and YOLO](#computer-vision-and-yolo)
- [Priority Scoring](#priority-scoring)
- [Similarity and Duplicate Detection](#similarity-and-duplicate-detection)
- [Anomaly Detection](#anomaly-detection)
- [Recommendation Engine](#recommendation-engine)
- [RAG System](#rag-system)
- [Donation Management](#donation-management)
- [Case Management](#case-management)
- [Human-in-the-Loop](#human-in-the-loop)
- [Explainability](#explainability)
- [Transparency](#transparency)
- [Humanitarian Map](#humanitarian-map)
- [Dashboard and Analytics](#dashboard-and-analytics)
- [Database Architecture](#database-architecture)
- [Database Schema](#database-schema)
- [API Architecture](#api-architecture)
- [API Endpoints](#api-endpoints)
- [Streamlit Application](#streamlit-application)
- [Data Requirements](#data-requirements)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Backend](#running-the-backend)
- [Running the Frontend](#running-the-frontend)
- [Running Ollama](#running-ollama)
- [Docker](#docker)
- [Testing](#testing)
- [GitHub Development Workflow](#github-development-workflow)
- [Team Responsibilities](#team-responsibilities)
- [MVP Scope](#mvp-scope)
- [Development Roadmap](#development-roadmap)
- [Security and Safety](#security-and-safety)
- [Design Principles](#design-principles)
- [End-to-End Demonstration](#end-to-end-demonstration)
- [Future Enhancements](#future-enhancements)
- [Future Production Architecture](#future-production-architecture)
- [Project Status](#project-status)
- [Future Vision](#future-vision)
- [Team](#team)
- [License](#license)

---

# Project Overview

CareHaven AI introduces intelligence into the complete humanitarian assistance lifecycle.

Traditional humanitarian platforms often follow:

```text
Donor
  ↓
Donation
  ↓
Beneficiary
```

CareHaven AI expands this workflow into:

```text
Case Submission
      ↓
AI Understanding
      ↓
Evidence Analysis
      ↓
Verification
      ↓
Priority Scoring
      ↓
Human Review
      ↓
Donor Matching
      ↓
Donation
      ↓
Funding Tracking
      ↓
Analytics
      ↓
Humanitarian Mapping
      ↓
Future Prediction
```

The platform works with multiple types of humanitarian information, including:

- Case descriptions
- Images
- Supporting documents
- Locations
- Number of affected people
- Required assistance
- Required resources
- Required funding
- Current donations
- Case status
- Donor preferences

The AI layer assists with:

- Humanitarian case understanding
- Information extraction
- Assistance classification
- Case summarization
- Image analysis
- Damage detection
- Image similarity
- Duplicate detection
- Suspicious pattern detection
- Priority scoring
- Donor recommendations
- RAG-based question answering
- Funding tracking
- Humanitarian analytics

---

# Problem Statement

Humanitarian organizations and donors may face several challenges.

## 1. Large Amounts of Unstructured Information

Humanitarian cases can contain:

- Text descriptions
- Images
- Documents
- Supporting evidence
- Location information

Manually processing all this information can be time-consuming.

## 2. Difficulty Identifying Urgent Cases

Not every humanitarian case has the same urgency.

Organizations need to understand:

```text
Which cases require immediate assistance?
Which cases have the highest priority?
Which cases affect the largest number of people?
Which cases have significant funding gaps?
```

## 3. Donor-Case Mismatch

Donors may have specific:

- Categories
- Locations
- Budgets
- Humanitarian interests

Finding relevant cases manually can be difficult.

## 4. Verification Challenges

Humanitarian platforms may receive:

- Duplicate images
- Similar case descriptions
- Incomplete evidence
- Unusual submission patterns
- Suspicious activity

These cases may require additional review.

## 5. Limited Transparency

Donors need to understand:

- Where their donation goes
- How much funding a case has received
- How much funding remains
- Current case status
- Funding progress

---

# Proposed Solution

CareHaven AI provides an intelligent decision-support platform connecting:

```text
Humanitarian Cases
        +
Artificial Intelligence
        +
Donors
        +
Humanitarian Organizations
        +
Donation Tracking
        +
Humanitarian Analytics
```

The current MVP architecture is:

```text
Streamlit
    ↓
FastAPI
    ↓
AI / ML Services
    ↓
PostgreSQL
    ↓
ChromaDB
```

FastAPI acts as the central backend communication layer between the frontend, AI services, application logic, and databases.

---

# Project Objectives

The main objectives are:

1. Improve humanitarian case understanding.
2. Automatically extract important information from cases.
3. Classify humanitarian assistance requirements.
4. Analyze uploaded images.
5. Detect visible damage.
6. Detect potentially duplicated evidence.
7. Identify suspicious or unusual patterns.
8. Calculate explainable priority scores.
9. Recommend relevant cases to donors.
10. Track donations and funding gaps.
11. Provide humanitarian analytics.
12. Provide a RAG-based humanitarian AI assistant.
13. Visualize humanitarian cases geographically.
14. Maintain human oversight over critical decisions.
15. Provide a modular architecture for future expansion.

---

# Target Users

CareHaven AI supports five primary user roles.

## Donor

Donors can:

- Browse humanitarian cases
- View recommended cases
- Set donation preferences
- Select preferred categories
- Select geographic preferences
- Specify a budget
- Donate to cases
- Track donations
- Monitor funding progress
- Understand the impact of their contributions

Example:

```text
Category:
Emergency Aid

Location:
Egypt

Budget:
EGP 1,000 - EGP 3,000
```

---

## Volunteer

Volunteers can:

- Submit humanitarian cases
- Document humanitarian situations
- Upload images
- Upload supporting evidence
- Provide information about affected people
- Help organizations collect case information

---

## NGO / Humanitarian Organization

Organizations can:

- Review submitted cases
- Manage humanitarian cases
- Review AI analysis
- Review flagged cases
- Monitor funding progress
- Monitor funding gaps
- View dashboards
- View humanitarian analytics
- Monitor emergency situations

---

## Beneficiary

Beneficiaries can:

- Request assistance
- Submit humanitarian cases
- Describe their needs
- Upload supporting evidence
- Track request status

---

## Administrator

Administrators can:

- Manage users
- Monitor platform activity
- Moderate cases
- Review suspicious cases
- Review anomaly flags
- Monitor system performance
- View analytics

---

# Key Features

## Platform Features

- User authentication
- Role-based access
- Humanitarian case submission
- Case management
- Case status tracking
- Image upload
- Document upload
- Donation management
- Funding tracking
- Donor recommendations
- Humanitarian map
- Dashboard
- Analytics
- Human review queue

## AI Features

- NLP case understanding
- Information extraction
- Case classification
- Case summarization
- LLM integration
- YOLO image analysis
- Damage detection
- Image similarity
- Duplicate detection
- Anomaly detection
- Explainable priority scoring
- Recommendation engine
- Retrieval-Augmented Generation

---

# System Architecture

## High-Level Architecture

```text
                              CAREHAVEN AI
                                   │
                                   ▼
                             USERS LAYER
                                   │
                                   ▼
                         ┌──────────────────┐
                         │    STREAMLIT     │
                         │    FRONTEND      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FASTAPI      │
                         │     BACKEND      │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
        PostgreSQL           AI / ML Layer         ChromaDB
              │                   │                   │
              │          ┌────────┼────────┐          │
              │          │        │        │          │
              │          ▼        ▼        ▼          │
              │         NLP      YOLO   Priority      │
              │          │        │      Engine       │
              │          │        │        │          │
              │          └────────┼────────┘          │
              │                   │                   │
              │                   ▼                   │
              │          Recommendation               │
              │              Engine                   │
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                              RESULTS
                                  │
                                  ▼
                              STREAMLIT
```

---

# Architecture Layers

## 1. Users Layer

The system supports:

```text
Donor
Volunteer
NGO / Humanitarian Organization
Beneficiary
Administrator
```

Each role has different permissions and responsibilities.

---

## 2. Frontend Layer

The current MVP uses:

```text
Streamlit
```

Streamlit provides:

- Dashboard
- Case Submission
- Case Browsing
- Donations
- Recommendations
- Humanitarian Map
- AI Assistant
- Image Analysis
- Review Queue
- Analytics

---

## 3. FastAPI Backend Layer

FastAPI is the central backend.

Responsibilities include:

- REST APIs
- Authentication
- Authorization
- Request validation
- Business logic
- Case management
- Donation management
- AI service communication
- Database communication
- Analytics
- Recommendation services
- CORS
- File handling

---

## 4. AI / ML Layer

The AI layer contains:

```text
NLP / LLM
RAG
Computer Vision
YOLO
Priority Engine
Similarity Detection
Anomaly Detection
Recommendation Engine
```

---

## 5. Data Layer

The data layer contains:

```text
PostgreSQL
Object Storage
ChromaDB
```

### PostgreSQL

Stores structured application data.

### Object Storage

Stores large unstructured files such as:

- Images
- Documents
- Supporting evidence
- Case attachments

### ChromaDB

Stores:

- Document chunks
- Embeddings
- Vector metadata

---

# Technology Stack

## Frontend

- Streamlit

## Backend

- Python
- FastAPI
- REST APIs

## Database

- PostgreSQL

## Vector Database

- ChromaDB

## AI / ML

- Python
- PyTorch
- YOLO
- OpenCV
- Scikit-learn
- NLP Models
- Large Language Models
- Ollama

## Development

- Git
- GitHub
- Docker
- Python Virtual Environment

---

# End-to-End Workflow

The complete humanitarian workflow is:

```text
                    CASE SUBMISSION
                           │
                           ▼
                    FastAPI Validation
                           │
                           ▼
                      Save Case
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        NLP / LLM                Computer Vision
              │                         │
              ▼                         ▼
       Case Understanding        Image Analysis
              │                         │
              └────────────┬────────────┘
                           ▼
                   Similarity Check
                           │
                           ▼
                   Priority Scoring
                           │
                           ▼
                   Anomaly Detection
                           │
                           ▼
                  Human Review Queue
                           │
                           ▼
                     Case Approval
                           │
                           ▼
                Recommendation Engine
                           │
                           ▼
                         Donor
                           │
                           ▼
                       Donation
                           │
                           ▼
                  Funding Tracking
                           │
                           ▼
                       Dashboard
                           │
                           ▼
                  Humanitarian Map
```

---

# AI and ML Components

CareHaven AI uses multiple independent AI components.

```text
                    AI / ML LAYER
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
      NLP              YOLO             Priority
       │                 │              Engine
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
                 Similarity Engine
                         │
                         ▼
                Recommendation Engine
                         │
                         ▼
                        RAG
```

---

# NLP and LLM

## Purpose

NLP is responsible for understanding humanitarian case descriptions.

### Example Input

```text
A family of six was affected by severe flooding.
Their house was damaged and they need food and shelter.
```

### Processing

```text
Text
 ↓
NLP / LLM
 ↓
Information Extraction
 ↓
Classification
 ↓
Severity Analysis
 ↓
Summary Generation
```

### Example Output

```json
{
  "category": "Emergency Aid",
  "assistance": [
    "Food",
    "Shelter"
  ],
  "people_affected": 6,
  "severity": "High",
  "summary": "Family affected by severe flooding and requiring emergency assistance."
}
```

### NLP Responsibilities

- Case understanding
- Information extraction
- Assistance classification
- Severity indicators
- Summary generation

---

# Computer Vision and YOLO

## Purpose

Computer Vision analyzes uploaded humanitarian images.

### Workflow

```text
Upload Image
     ↓
Image Preprocessing
     ↓
YOLO / Computer Vision
     ↓
Object / Damage Detection
     ↓
Confidence Score
     ↓
Results
```

### Example

```text
Damage Detected:
YES

Damage Type:
Building Damage

Confidence:
89%
```

The exact classes depend on the selected and trained Computer Vision model.

---

# Priority Scoring

The MVP uses an explainable weighted priority scoring approach.

The score can consider:

```text
Severity
+
Number of People Affected
+
Emergency Status
+
Funding Gap
+
Urgency
```

### Example

```text
Severity:
High

People Affected:
6

Emergency:
Yes

Funding Gap:
Large

Urgency:
High
```

Result:

```text
Priority Score:
92 / 100

Priority Level:
CRITICAL
```

---

# Priority Explainability

The system should explain why a case received its priority score.

Example:

```text
Priority Score: 92 / 100

Reasons:

✓ Severe damage
✓ High number of affected people
✓ Emergency situation
✓ Large funding gap
```

This allows humanitarian organizations to review the AI output instead of receiving an unexplained score.

---

# Similarity and Duplicate Detection

The system can compare new evidence with previously submitted information.

## Image Similarity

```text
New Image
    ↓
Image Embedding
    ↓
Similarity Search
    ↓
Existing Images
    ↓
Similarity Score
```

Example:

```text
Similarity Score:
94%

Result:
Potential Duplicate

Action:
Human Review Required
```

## Text Similarity

Case descriptions can also be compared:

```text
New Case Description
        ↓
Text Embedding
        ↓
Vector Search
        ↓
Existing Cases
        ↓
Similarity Score
```

This can help identify potentially duplicated or highly similar submissions.

---

# Anomaly Detection

Anomaly detection identifies unusual patterns that may require additional review.

Potential signals include:

- Repeated images
- Highly similar descriptions
- Unusual submission patterns
- Unusual donation patterns
- Inconsistent information
- Unexpected behavior

The output should be:

```text
FLAG
```

rather than automatically:

```text
FRAUD
```

Flagged cases are sent to human reviewers.

---

# Recommendation Engine

The recommendation engine helps donors discover relevant humanitarian cases.

## Donor Preferences

Example:

```text
Category:
Emergency Aid

Location:
Egypt

Budget:
EGP 1,000 - EGP 3,000
```

## Matching Process

```text
Donor Preferences
        ↓
Candidate Cases
        ↓
Category Matching
        ↓
Location Matching
        ↓
Budget Compatibility
        ↓
Priority
        ↓
Funding Gap
        ↓
Match Score
```

## Example

```text
Recommended Cases

1. Flood Emergency
   Match Score: 91%

2. Emergency Shelter
   Match Score: 87%

3. Food Assistance
   Match Score: 82%
```

---

# RAG System

CareHaven AI includes a Retrieval-Augmented Generation system.

RAG allows users to ask questions based on a curated humanitarian knowledge base.

## RAG Architecture

```text
Humanitarian Documents
        ↓
Document Processing
        ↓
Text Extraction
        ↓
Chunking
        ↓
Embeddings
        ↓
ChromaDB
        ↓
User Question
        ↓
Query Embedding
        ↓
Similarity Retrieval
        ↓
Relevant Chunks
        ↓
Ollama / LLM
        ↓
Answer + Sources
```

---

# RAG Knowledge Base

The knowledge base may contain:

- Humanitarian guidelines
- Disaster response procedures
- NGO procedures
- Donation policies
- FAQs
- Humanitarian reports

RAG is used to provide grounded answers based on retrieved information.

---

# Example RAG Query

User:

```text
What assistance is recommended for flood victims?
```

System:

```text
1. Convert the question into an embedding.
2. Search ChromaDB.
3. Retrieve relevant documents.
4. Provide the retrieved context to the LLM.
5. Generate the answer.
6. Display the supporting sources.
```

Example result:

```text
Answer:

Flood-affected families may require emergency shelter,
food, clean water, and medical assistance depending on
their specific circumstances.

Sources:
- Emergency Response Guide
- Humanitarian Assistance Policy
```

---

# Donation Management

Donation management tracks financial support for humanitarian cases.

## Donation Flow

```text
Donor
  ↓
Select Case
  ↓
Enter Amount
  ↓
Create Donation
  ↓
Update Case Funding
  ↓
Update Funding Progress
  ↓
Update Remaining Gap
```

## Funding Progress

```text
Funding Progress =
(Current Donations / Required Amount) × 100
```

Example:

```text
Required Amount:
EGP 100,000

Current Donations:
EGP 40,000

Funding Progress:
40%
```

## Remaining Funding Gap

```text
Remaining Gap =
Required Amount - Current Donations
```

Example:

```text
Required:
EGP 100,000

Current:
EGP 40,000

Remaining:
EGP 60,000
```

---

# Case Management

A humanitarian case may contain:

```text
Case ID
Beneficiary ID
Volunteer ID
NGO ID
Description
Category
Location
Latitude
Longitude
People Affected
Required Assistance
Required Resources
Required Amount
Current Donations
Funding Progress
Remaining Gap
Priority Score
Priority Level
Status
Created Date
Updated Date
```

---

# Case Status Lifecycle

```text
Pending
   ↓
Under Review
   ↓
Approved
   ↓
Active
   ↓
Funded
   ↓
Completed
```

Potential suspicious cases can enter:

```text
Flagged
   ↓
Human Review
   ↓
Decision
```

---

# Human-in-the-Loop

Human oversight is a core principle of CareHaven AI.

The system follows:

```text
AI Analysis
     ↓
Potential Concern
     ↓
Flag
     ↓
Human Review
     ↓
Human Decision
```

The system should not automatically:

- Reject humanitarian cases
- Accuse users of fraud
- Make critical humanitarian eligibility decisions

Instead:

```text
Suspicious Pattern
       ↓
Flagged Case
       ↓
Human Review
       ↓
Final Decision
```

---

# Explainability

AI results should provide understandable information.

Instead of only displaying:

```text
Priority = 92
```

the system should display:

```text
Priority = 92

Reasons:

• Severe damage
• High number of affected people
• Large funding gap
• Emergency situation
```

Explainability makes AI-assisted decisions easier to understand and review.

---

# Transparency

The platform should allow donors to understand:

```text
Where their donation goes
Funding progress
Remaining funding gap
Case status
Donation history
```

Transparency is important for building trust between donors, organizations, and beneficiaries.

---

# Humanitarian Map

The humanitarian map displays cases geographically.

Each case can contain:

```text
Location
Latitude
Longitude
Priority
Category
Funding Status
Emergency Status
```

Example priority visualization:

```text
🔴 Critical
🟠 High
🟡 Moderate
🟢 Supported / Completed
```

Users can filter cases by:

- Priority
- Assistance type
- Funding status
- Geographic area
- Emergency status

The map can help organizations identify:

- Concentrated humanitarian needs
- Underfunded areas
- Emergency situations
- Geographic patterns

---

# Dashboard and Analytics

The dashboard provides a high-level view of humanitarian activity.

## Main Metrics

```text
Total Cases
Active Cases
Critical Cases
Total Donations
Funding Gaps
People Supported
```

## Possible Visualizations

```text
Cases by Category
Cases by Priority
Donation Trends
Funding Progress
Cases by Location
Emergency Cases
```

---

# Database Architecture

PostgreSQL is the primary relational database.

It stores structured application data.

```text
PostgreSQL
│
├── users
├── cases
├── donations
├── ngos
├── volunteers
├── case_images
├── ai_analysis
├── priority_scores
├── flags
├── donor_preferences
└── case_status_history
```

---

# Database Schema

## Users

```text
users
-------------------------
id
name
email
password_hash
role
location
created_at
```

## Cases

```text
cases
-------------------------
id
submitted_by
description
category
location
latitude
longitude
people_affected
required_assistance
required_resources
required_amount
current_donations
funding_progress
remaining_gap
priority_score
priority_level
status
created_at
updated_at
```

## Donations

```text
donations
-------------------------
id
donor_id
case_id
amount
donation_date
```

## NGOs

```text
ngos
-------------------------
id
name
location
specialization
capacity
```

## Volunteers

```text
volunteers
-------------------------
id
name
skills
location
availability
```

## Case Images

```text
case_images
-------------------------
id
case_id
file_path
image_type
similarity_score
quality_score
created_at
```

## AI Analysis

```text
ai_analysis
-------------------------
id
case_id
category
severity
summary
extracted_data
confidence
created_at
```

## Flags

```text
flags
-------------------------
id
case_id
flag_type
risk_score
reason
status
created_at
```

---

# Database Relationships

```text
USER
 │
 └────── submits ──────► CASE
                            │
                ┌───────────┼────────────┐
                │           │            │
                ▼           ▼            ▼
             IMAGES    AI ANALYSIS   PRIORITY
                │
                ▼
          SIMILARITY CHECK

DONOR
 │
 └────── makes ─────────► DONATION
                              │
                              ▼
                             CASE

NGO
 │
 └────── manages ───────► CASE
```

---

# Object Storage

Large files should not be stored directly inside PostgreSQL.

Object storage can be used for:

- Images
- Documents
- Supporting evidence
- Case attachments

PostgreSQL stores metadata and file references.

```text
User Upload
    ↓
Object Storage
    ↓
File Path / URL
    ↓
PostgreSQL Metadata
```

---

# ChromaDB

ChromaDB is used for vector-based retrieval.

It stores:

```text
Document Chunks
Embeddings
Metadata
```

Workflow:

```text
Humanitarian Documents
        ↓
Text Processing
        ↓
Chunking
        ↓
Embeddings
        ↓
ChromaDB
```

---

# API Architecture

FastAPI acts as the central API layer.

```text
Streamlit
    ↕
FastAPI
    ↕
PostgreSQL

FastAPI
    ↕
AI Services

FastAPI
    ↕
ChromaDB
```

This separation keeps the frontend, backend, AI services, and data layer modular.

---

# API Endpoints

## Authentication

```http
POST /auth/register
POST /auth/login
GET  /auth/me
```

## Users

```http
GET /users
GET /users/{user_id}
PUT /users/{user_id}
```

## Cases

```http
POST /cases
GET /cases
GET /cases/{case_id}
PUT /cases/{case_id}
DELETE /cases/{case_id}
```

## Donations

```http
POST /donations
GET /donations
GET /donations/{donation_id}
GET /cases/{case_id}/donations
```

## AI

```http
POST /ai/analyze-case
POST /ai/analyze-image
POST /ai/calculate-priority
POST /ai/check-similarity
```

## Recommendations

```http
GET /recommendations/{donor_id}
```

## RAG

```http
POST /chat
```

## Analytics

```http
GET /analytics
GET /analytics/cases
GET /analytics/donations
GET /analytics/funding
```

---

# Example API Workflow

## Create Case

```http
POST /cases
```

Request:

```json
{
  "description": "Family affected by severe flooding",
  "location": "Cairo",
  "people_affected": 6,
  "required_assistance": [
    "Food",
    "Shelter"
  ],
  "required_amount": 20000
}
```

Example response:

```json
{
  "case_id": 101,
  "category": "Emergency Aid",
  "priority_score": 92,
  "priority_level": "Critical",
  "status": "Pending"
}
```

---

# Streamlit Application

Streamlit is the current frontend for the MVP.

Recommended pages:

```text
Home
Dashboard
Cases
Case Details
Submit Case
Donations
Recommendations
Humanitarian Map
AI Assistant
Image Analysis
Review Queue
Analytics
```

---

# Dashboard

The dashboard provides a high-level view of humanitarian activity.

Example cards:

```text
Total Cases
Active Cases
Critical Cases
Total Donations
Remaining Funding
People Supported
```

---

# Review Queue

The review queue supports Human-in-the-Loop workflows.

Example:

```text
Flagged Case #102

Reason:
Potential duplicate image

Similarity:
94%

Status:
Pending Human Review
```

Possible actions:

```text
Review
Approve
Request More Evidence
Mark as Resolved
```

---

# Data Requirements

Different AI components require different types of data.

## NLP Data

Possible data:

```text
Humanitarian Case Descriptions
Disaster-Related Text
Assistance Categories
```

The final dataset should match the actual classification and information-extraction tasks implemented in the project.

---

## Computer Vision Data

Possible categories include:

```text
No Damage
Minor Damage
Major Damage
Destroyed
```

The exact classes depend on the selected dataset and trained model.

---

## Custom CareHaven Data

Application-specific data may include:

```text
cases.csv
donors.csv
donations.csv
ngos.csv
volunteers.csv
```

Example:

```text
case_id:
1

description:
"We need food after flooding"

category:
Food

people_affected:
5

location:
Cairo

required_amount:
20000

priority:
High
```

---

## RAG Data

RAG requires a humanitarian knowledge base.

Possible sources include:

```text
Humanitarian Guidelines
Disaster Response Procedures
NGO Procedures
Donation Policies
FAQs
Humanitarian Reports
```

---

# Project Structure

Recommended repository structure:

```text
CareHaven-AI/
│
├── backend/
│   │
│   ├── main.py
│   ├── database.py
│   ├── dependencies.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── case.py
│   │   ├── donation.py
│   │   ├── ngo.py
│   │   ├── volunteer.py
│   │   ├── ai_analysis.py
│   │   └── flag.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── case.py
│   │   ├── donation.py
│   │   └── ai.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── cases.py
│   │   ├── donations.py
│   │   ├── ai.py
│   │   ├── recommendations.py
│   │   ├── analytics.py
│   │   └── chat.py
│   │
│   └── services/
│       ├── case_service.py
│       ├── donation_service.py
│       ├── recommendation_service.py
│       └── analytics_service.py
│
├── ai/
│   │
│   ├── nlp/
│   │   ├── analyzer.py
│   │   ├── classifier.py
│   │   └── summarizer.py
│   │
│   ├── vision/
│   │   ├── detector.py
│   │   ├── preprocessing.py
│   │   └── similarity.py
│   │
│   ├── priority/
│   │   └── priority_engine.py
│   │
│   ├── recommendation/
│   │   └── recommender.py
│   │
│   ├── anomaly/
│   │   └── detector.py
│   │
│   └── rag/
│       ├── document_loader.py
│       ├── chunker.py
│       ├── embeddings.py
│       ├── vector_store.py
│       └── rag_pipeline.py
│
├── streamlit/
│   │
│   ├── app.py
│   ├── api_client.py
│   │
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── cases.py
│   │   ├── submit_case.py
│   │   ├── donations.py
│   │   ├── recommendations.py
│   │   ├── map.py
│   │   ├── ai_assistant.py
│   │   ├── image_analysis.py
│   │   ├── review_queue.py
│   │   └── analytics.py
│   │
│   └── components/
│       ├── cards.py
│       ├── charts.py
│       └── forms.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── documents/
│
├── models/
│   ├── nlp/
│   └── vision/
│
├── tests/
│   ├── test_auth.py
│   ├── test_cases.py
│   ├── test_donations.py
│   ├── test_ai.py
│   └── test_recommendations.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

# Installation

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd CareHaven-AI
```

---

# 2. Create a Virtual Environment

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a file named:

```text
.env
```

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/carehaven

SECRET_KEY=your_secret_key

CHROMA_HOST=localhost
CHROMA_PORT=8000

OLLAMA_BASE_URL=http://localhost:11434

MODEL_PATH=./models
```

Never commit the actual `.env` file to GitHub.

Use:

```text
.env.example
```

instead.

---

# Database Setup

Make sure PostgreSQL is installed and running.

Create the database:

```sql
CREATE DATABASE carehaven;
```

Configure the connection:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/carehaven
```

Run migrations or database initialization according to the backend implementation.

---

# Running the Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

---

# Running the Frontend

Open another terminal and activate the virtual environment.

Then run:

```bash
streamlit run streamlit/app.py
```

The application will open in the browser.

---

# Running Ollama

If the RAG implementation uses Ollama:

```bash
ollama serve
```

Then pull the required model:

```bash
ollama pull <MODEL_NAME>
```

The exact model should be configured according to the project's implementation.

---

# Docker

The project can be containerized using Docker.

Run:

```bash
docker compose up --build
```

The intended service architecture can contain:

```text
Streamlit
FastAPI
PostgreSQL
ChromaDB
Ollama
```

---

# API Documentation

FastAPI automatically provides interactive API documentation.

After starting the backend, open:

```text
http://localhost:8000/docs
```

Alternative documentation:

```text
http://localhost:8000/redoc
```

---

# Testing

Run the test suite with:

```bash
pytest
```

---

# Testing Strategy

## Authentication Tests

Test:

```text
Registration
Login
Invalid Password
Invalid Email
Role Authorization
```

## Case Tests

Test:

```text
Create Case
Retrieve Case
Update Case
Case Status
Case Validation
```

## Donation Tests

Test:

```text
Create Donation
Funding Progress
Remaining Gap
Donation History
```

## AI Tests

Test:

```text
NLP Analysis
Image Analysis
Priority Calculation
Similarity Detection
Recommendation
RAG Retrieval
```

---

# GitHub Development Workflow

Because the project is developed by three team members, the `main` branch should remain stable.

Recommended branches:

```text
main
│
├── feature/backend
├── feature/ai
└── feature/streamlit
```

---

# Backend Developer Workflow

Create a branch:

```bash
git checkout -b feature/backend
```

After implementation:

```bash
git add .
git commit -m "feat: implement case management API"
git push origin feature/backend
```

Create a Pull Request into:

```text
main
```

---

# AI Developer Workflow

Create a branch:

```bash
git checkout -b feature/ai
```

Example:

```bash
git add .
git commit -m "feat: implement NLP case analysis"
git push origin feature/ai
```

---

# Streamlit Developer Workflow

Create a branch:

```bash
git checkout -b feature/streamlit
```

Example:

```bash
git add .
git commit -m "feat: implement case submission interface"
git push origin feature/streamlit
```

---

# Before Starting New Work

Always synchronize your local branch:

```bash
git checkout main
git pull origin main
```

Then update your feature branch.

---

# Team Responsibilities

## Developer 1 — Backend and Database

Responsible for:

```text
FastAPI
PostgreSQL
Database Models
Authentication
Authorization
Case APIs
Donation APIs
Analytics APIs
Business Logic
API Integration
```

---

## Developer 2 — AI / ML

Responsible for:

```text
NLP
LLM
YOLO
Computer Vision
Image Similarity
Priority Engine
Anomaly Detection
Recommendation Engine
RAG
ChromaDB
```

---

## Developer 3 — Streamlit and Integration

Responsible for:

```text
Streamlit UI
Dashboard
Case Submission
Case Browsing
Donation UI
Recommendations
Humanitarian Map
AI Assistant
Image Analysis UI
Review Queue
Frontend ↔ FastAPI Integration
```

---

# MVP Scope

The MVP focuses on delivering a complete working end-to-end system rather than implementing every advanced feature.

## MVP Features

```text
✓ Authentication
✓ Role Management
✓ Case Submission
✓ Case Management
✓ Image Upload
✓ NLP Case Analysis
✓ Case Classification
✓ Case Summary
✓ Priority Scoring
✓ Explainable Priority Reasons
✓ YOLO / Image Analysis
✓ Image Similarity
✓ Anomaly Flagging
✓ Human Review
✓ Donor Recommendations
✓ Donation Management
✓ Funding Tracking
✓ RAG Assistant
✓ ChromaDB
✓ PostgreSQL
✓ Streamlit Dashboard
✓ Humanitarian Map
✓ Analytics
```

---

# Development Roadmap

## Phase 1 — Requirements

Define:

- Users
- Roles
- Features
- AI components
- MVP boundaries

---

## Phase 2 — Data Requirements

Determine:

- Required data
- Datasets
- Custom application data
- RAG documents
- AI inputs
- AI outputs

---

## Phase 3 — Database

Implement:

- ERD
- PostgreSQL
- Tables
- Relationships
- Constraints

---

## Phase 4 — Backend Foundation

Implement:

- FastAPI
- Database connection
- Authentication
- Authorization
- CORS
- API routing

---

## Phase 5 — Case Management

Implement:

- Case submission
- Case storage
- Image upload
- Case retrieval
- Case updates
- Case status

---

## Phase 6 — AI Case Analysis

Implement:

- NLP
- Information extraction
- Classification
- Summary generation

---

## Phase 7 — Priority Engine

Start with:

```text
Rule-Based / Weighted Scoring
```

Then later consider:

```text
Machine Learning
```

---

## Phase 8 — Computer Vision

Implement:

- Image preprocessing
- YOLO
- Damage detection
- Image similarity

---

## Phase 9 — Recommendation Engine

Implement:

- Donor preferences
- Case matching
- Case ranking
- Match score

---

## Phase 10 — RAG

Implement:

```text
Documents
↓
Processing
↓
Chunking
↓
Embeddings
↓
ChromaDB
↓
Retrieval
↓
LLM
```

---

## Phase 11 — Frontend Integration

Current MVP:

```text
Streamlit
   ↕
FastAPI
```

Future production version:

```text
Next.js / React
       ↕
    FastAPI
```

---

## Phase 12 — Dashboard and Map

Implement:

- Analytics
- Funding visualization
- Priority visualization
- Humanitarian map
- Filters

---

# Security and Safety

CareHaven AI handles humanitarian information and therefore follows strong safety principles.

## Authentication

Users must authenticate before accessing protected functionality.

## Authorization

Different roles should have different permissions.

Example:

```text
Donor
 ├── Browse Cases
 ├── Donate
 └── View Recommendations

Volunteer
 ├── Submit Cases
 └── Upload Evidence

NGO
 ├── Manage Cases
 ├── Review Cases
 └── View Analytics

Administrator
 ├── Manage Users
 ├── Review Flags
 └── Monitor System
```

---

# Humanitarian Safety

The system must not automatically determine that a person is fraudulent or ineligible for humanitarian assistance.

Instead:

```text
AI
 ↓
Risk Signal
 ↓
Flag
 ↓
Human Review
 ↓
Decision
```

AI outputs are decision-support signals and should not replace appropriate human judgment.

---

# Data Privacy

The system should:

- Avoid exposing sensitive beneficiary information unnecessarily.
- Protect authentication credentials.
- Store passwords using secure hashing.
- Keep secrets in environment variables.
- Avoid committing `.env` files.
- Restrict access to protected case information.
- Apply role-based authorization.

---

# Explainability and Transparency

AI-assisted outputs should be understandable.

For example:

```text
Priority Score: 92 / 100

Main Reasons:
• Severe damage
• High number of affected people
• Emergency situation
• Large funding gap
```

For RAG responses, sources should be displayed when available.

For donations, the platform should show:

```text
Donation Amount
Case
Funding Progress
Remaining Funding Gap
Case Status
```

---

# Design Principles

## 1. Human-in-the-Loop

AI assists humans instead of replacing critical humanitarian decisions.

## 2. Explainability

AI outputs should provide understandable reasons whenever possible.

## 3. Safety

Suspicious patterns should be flagged for review rather than automatically treated as fraud.

## 4. Transparency

Donors should understand how their contributions are being used.

## 5. Modularity

AI components should remain independently manageable.

## 6. Scalability

The architecture should support future models, datasets, APIs, and real-time data.

---

# End-to-End Demonstration

The recommended demonstration uses a humanitarian emergency case.

## Step 1 — Submit Case

Example:

```text
Description:
A family of six has been affected by severe flooding.

Location:
Cairo

People Affected:
6

Required Assistance:
Food + Shelter

Required Amount:
EGP 20,000

Supporting Image:
Uploaded
```

---

## Step 2 — NLP Analysis

Example output:

```text
Category:
Emergency Aid

Assistance:
Food
Shelter

People Affected:
6

Severity:
High
```

---

## Step 3 — Computer Vision

Example:

```text
Damage Detected:
YES

Damage Type:
Building Damage

Confidence:
89%
```

---

## Step 4 — Similarity Check

Example:

```text
Similarity:
12%

Result:
No potential duplicate detected
```

Or:

```text
Similarity:
94%

Result:
Potential duplicate

Action:
Human Review Required
```

---

## Step 5 — Priority Scoring

Example:

```text
Priority Score:
92 / 100

Priority:
CRITICAL
```

Reasons:

```text
✓ Severe damage
✓ 6 people affected
✓ Emergency situation
✓ Large funding gap
```

---

## Step 6 — NGO Review

The NGO reviews:

```text
Case #101

AI Category:
Emergency Aid

Priority:
Critical

AI Analysis:
Available

Evidence:
Available

Flags:
None
```

The organization can approve the case.

---

## Step 7 — Donor Recommendation

A donor enters:

```text
Category:
Emergency Aid

Location:
Egypt

Budget:
EGP 1,000 - EGP 3,000
```

The recommendation engine returns:

```text
Case #101

Match Score:
91%

Priority:
Critical

Funding:
25%
```

---

## Step 8 — Donation

The donor contributes:

```text
EGP 2,000
```

---

## Step 9 — Funding Update

Before:

```text
Required:
EGP 20,000

Current:
EGP 5,000
```

After:

```text
Required:
EGP 20,000

Current:
EGP 7,000

Progress:
35%

Remaining:
EGP 13,000
```

---

## Step 10 — Dashboard Update

The dashboard updates:

```text
Total Donations
Active Cases
Critical Cases
Funding Progress
People Supported
```

---

## Step 11 — Humanitarian Map

The case appears on the map with:

```text
Location
Priority
Category
Funding Status
Emergency Status
```

---

## Step 12 — RAG Assistant

The user asks:

```text
What assistance is recommended for flood victims?
```

The RAG system:

```text
Retrieves relevant humanitarian documents
        ↓
Provides context to the LLM
        ↓
Generates an answer
        ↓
Displays supporting sources
```

---

# Complete Demo Flow

```text
          BENEFICIARY / VOLUNTEER
                    │
                    ▼
              SUBMIT CASE
                    │
                    ▼
             FASTAPI BACKEND
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
         NLP                YOLO
          │                   │
          ▼                   ▼
   CASE UNDERSTANDING    IMAGE ANALYSIS
          │                   │
          └─────────┬─────────┘
                    ▼
             SIMILARITY CHECK
                    │
                    ▼
             PRIORITY SCORE
                    │
                    ▼
             FLAG IF NEEDED
                    │
                    ▼
              HUMAN REVIEW
                    │
                    ▼
                APPROVAL
                    │
                    ▼
          RECOMMENDATION ENGINE
                    │
                    ▼
                  DONOR
                    │
                    ▼
                DONATION
                    │
                    ▼
             FUNDING TRACKING
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      DASHBOARD              MAP
          │
          ▼
      ANALYTICS
```

---

# Future Enhancements

The following features can be introduced after the MVP:

- Advanced ML priority prediction
- Advanced anomaly and fraud-risk detection
- Satellite imagery analysis
- Weather integration
- Real-time disaster data
- Advanced geospatial analytics
- Multilingual AI
- Voice-based case submission
- Government integrations
- Automated resource allocation
- Advanced predictive analytics
- Production React / Next.js frontend
- Mobile application
- Notification system
- Advanced donor impact reporting

---

# Future Predictive Analytics

Once sufficient reliable historical data is available, CareHaven AI can be extended to predict:

```text
Future Humanitarian Demand
        ↓
Required Resources
        ↓
Expected Funding Needs
        ↓
Potential Emergency Areas
```

Predictive analytics should only be introduced after enough high-quality historical data has been collected and validated.

---

# Future Production Architecture

The current MVP uses Streamlit to maximize development speed and simplify deployment.

A future production frontend can use:

```text
Next.js
React
TypeScript
Tailwind CSS
```

while keeping the backend architecture:

```text
Next.js / React
       ↓
    FastAPI
       ↓
 AI / ML Services
       ↓
 PostgreSQL
       ↓
 ChromaDB
```

The AI and backend layers can remain independent from the presentation layer.

---

# Scalability

The modular architecture allows additional components to be added without redesigning the complete system.

Future integrations may include:

```text
Additional AI Models
Additional Datasets
External APIs
Real-Time Emergency Data
Additional Recommendation Models
Additional Vision Models
Predictive Models
Government Data Sources
```

---

# Project Status

```text
Project:
CareHaven AI

Version:
MVP Development

Frontend:
Streamlit

Backend:
FastAPI

Database:
PostgreSQL

Vector Database:
ChromaDB

AI:
NLP + LLM + YOLO + Priority + Recommendation + RAG

Architecture:
Modular API-Based Architecture
```

The README distinguishes between features intended for the MVP and advanced future features so that the repository documentation remains aligned with the actual implementation.

---

# Future Vision

CareHaven AI aims to evolve into a scalable intelligent humanitarian decision-support platform.

The long-term vision is:

```text
Understand
    ↓
Verify
    ↓
Prioritize
    ↓
Match
    ↓
Support
    ↓
Track
    ↓
Predict
```

The goal is to help humanitarian organizations and donors allocate assistance more effectively and transparently.

---

# Core Philosophy

> **Deliver the right help to the right people at the right time.**

CareHaven AI transforms the traditional:

```text
Donate → Deliver
```

model into:

```text
Understand → Verify → Prioritize → Match → Support → Track → Predict
```

---

# Team

## CareHaven AI Development Team

### Developer 1
**Backend & Database**

Responsibilities:

- FastAPI
- PostgreSQL
- Authentication
- Authorization
- Case Management
- Donation Management
- APIs
- Business Logic

### Developer 2
**AI / ML**

Responsibilities:

- NLP
- LLM
- YOLO
- Computer Vision
- Image Similarity
- Priority Engine
- Anomaly Detection
- Recommendation Engine
- RAG
- ChromaDB

### Developer 3
**Streamlit & Integration**

Responsibilities:

- Streamlit
- Dashboard
- Case Submission
- Case Browsing
- Donation Interface
- Recommendations
- Humanitarian Map
- AI Assistant
- Image Analysis UI
- Review Queue
- FastAPI Integration

---

# Contributing

Contributions should follow the team's Git workflow.

1. Create a feature branch.
2. Implement the feature.
3. Test locally.
4. Commit with a descriptive message.
5. Push the branch.
6. Open a Pull Request.
7. Review the changes.
8. Merge into `main` after approval.

Example:

```bash
git checkout main
git pull origin main

git checkout -b feature/example

git add .
git commit -m "feat: add example feature"

git push origin feature/example
```

---

# License

This project is currently developed as an academic / graduation project.

License information can be added if the project is later released under an open-source license.

---

# CareHaven AI

> **Turning Every Contribution Into Smarter Impact.**

```text
Understand → Verify → Prioritize → Match → Support → Track → Predict
```
