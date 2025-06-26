[![codecov](https://codecov.io/github/MG814/mc_api_gateway/graph/badge.svg?token=1087Q2Q1SN)](https://codecov.io/github/MG814/mc_api_gateway)

# API Gateway

The API Gateway microservice serves as the central access point to the Medicare system. It is responsible for routing requests to appropriate microservices and handling user authentication.

## Architecture

API Gateway is the main entry point to the Medicare system, which:
- Routes HTTP requests to appropriate microservices
- Handles user authentication through Auth0
- Manages JWT tokens
- Provides a unified API interface for client applications

## Features

### API Modules
- **api_accounts** - User account management
- **api_medical_records** - Medical documentation management
- **api_visits** - Medical visits handling
- **api_statistics** - Statistics and reports generation (GraphQL)

### Authentication
- **Callback** - View handling Auth0 service responses
- JWT token validation for endpoint security

## Technologies

- **bandit 1.7.9**
- **coverage 7.6.1**
- **django 5.1**
- **django-environ 0.12.0**
- **djangorestframework 3.15.2**
- **python 3.13**
- **requests 2.32.3**
- **responses 0.25.3**
- **ruff 0.6.3**
- **safety 3.5.2**

## Installation

### Requirements
- Python 3.13+
- Poetry (for dependency management)

### Setup

#### 1. Clone the repository

```bash
git clone https://github.com/MG814/mc_api_gateway.git
cd mc_api_gateway
```

#### 2. Running the entire application:

```bash
docker-compose up --build
```
