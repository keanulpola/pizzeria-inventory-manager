# Pizzeria Inventory Manager

A small Flask + Amazon DynamoDB inventory application built as a **collaborative graduate coursework project**. Supports creating, viewing, updating, and deleting inventory items, filtering by category, and highlighting stock below its configured minimum.

## Contributions

My contributions included category/low-stock filtering, resolving template-rendering issues, AWS configuration troubleshooting, CRUD testing, and documentation. Initial DynamoDB setup, the initial UI and portions of the data schema were collaborative/teammate contributions. **This is a team project, not a solo build.**

- After completing the original project, I independently configured DynamoDB Local using Docker, updated the Flask application's database connection, and tested its inventory functionality.


## Technologies

- Python
- Flask
- Jinja2
- HTML/CSS
- Amazon DynamoDB
- boto3
- Docker
- AWS CLI
- python-dotenv
- Git / GitHub

## Features

- Create inventory items.
- View current inventory.
- Update item information and quantities.
- Delete inventory items.
- Filter inventory by category.
- Identify items below their minimum stock level.
- Store inventory records using DynamoDB.
- Run locally using DynamoDB Local without requiring an AWS account.


## Run Locally

The original application was developed using Amazon DynamoDB hosted on AWS. I adapted the application to support DynamoDB Local through Docker.

I added a configurable DynamoDB endpoint and environment-based configuration, allowing the application to run without an AWSnaccount or cloud charges while preserving compatibility with
AWS-hosted DynamoDB.

The following instructions explain how to set up and run the application locally.

### Prerequisites

Install:

- Python 3
- Docker Desktop
- AWS CLI

### 1. Start DynamoDB Local

Make sure Docker Desktop is running.

Run:

```powershell
docker run -d --name pizzeria-dynamodb `
  -p 127.0.0.1:8000:8000 `
  amazon/dynamodb-local `
  -jar DynamoDBLocal.jar -sharedDb
```

If the container already exists but is stopped, use:

```powershell
docker start pizzeria-dynamodb
```

Verify that DynamoDB Local is running:

```powershell
docker ps
```

DynamoDB Local will be available at:

```text
http://127.0.0.1:8000
```

### 2. Configure Local AWS Credentials

DynamoDB Local requires AWS-style credentials, but they do not need to belong to a real AWS account.

In PowerShell:

```powershell
$env:AWS_ACCESS_KEY_ID = "localtest"
$env:AWS_SECRET_ACCESS_KEY = "localtest"
$env:AWS_DEFAULT_REGION = "us-east-1"
```

These values are only used for the local DynamoDB instance.

### 3. Create the DynamoDB Table

Create the inventory table:

```powershell
aws dynamodb create-table `
  --table-name PizzeriaInventory `
  --attribute-definitions AttributeName=item_id,AttributeType=S `
  --key-schema AttributeName=item_id,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --endpoint-url http://127.0.0.1:8000
```

If the table already exists, this step can be skipped.

Verify the table:

```powershell
aws dynamodb describe-table `
  --table-name PizzeriaInventory `
  --query "Table.TableStatus" `
  --output text `
  --endpoint-url http://127.0.0.1:8000
```

Expected output:

```text
ACTIVE
```

### 4. Configure the Flask Application

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Generate a Flask secret key:

```powershell
py -c "import secrets; print(secrets.token_hex(32))"
```

Configure `.env`:

```dotenv
FLASK_SECRET_KEY=YOUR_GENERATED_SECRET
AWS_REGION_NAME=us-east-1
DYNAMODB_TABLE=PizzeriaInventory
DYNAMODB_ENDPOINT_URL=http://127.0.0.1:8000

AWS_ACCESS_KEY_ID=localtest
AWS_SECRET_ACCESS_KEY=localtest
```

Replace `YOUR_GENERATED_SECRET` with the generated value.

The `.env` file is excluded from Git and should never be committed.

### 5. Create a Python Virtual Environment

```powershell
py -m venv .venv
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 6. Run the Application

```powershell
.\.venv\Scripts\python.exe app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Testing

The portfolio version of the application was manually tested locally using Flask and DynamoDB Local.

The following functionality was verified:

- Creating inventory items.
- Viewing inventory records.
- Updating existing inventory items.
- Updating inventory quantities.
- Filtering items by category.
- Identifying items below their minimum stock level.
- Deleting inventory items.

All listed operations worked successfully during local testing.

## Local Data

The current Docker configuration does not use persistent external storage.

Stopping and restarting the existing `pizzeria-dynamodb` container will normally retain its local data. Deleting and recreating the container may remove the local inventory database.

This is acceptable for the project's intended purpose as a local demonstration environment.

## Scope and Limitations

This project is an instructional and portfolio application rather than a production deployment.

Production-oriented features that would still need to be added include:

- User authentication.
- Authorization and role management.
- CSRF protection.
- Rate limiting.
- More extensive automated testing.
- Production deployment configuration.

DynamoDB scans used by the application may also become inefficient with significantly larger datasets.