# Pizzeria Inventory Manager

A small Flask + Amazon DynamoDB inventory application built as a **collaborative graduate coursework project**. Supports creating, viewing, updating, and deleting inventory items, filtering by category, and highlighting stock below its configured minimum.

## Contributions

Based on the team's original project report, my contributions included category/low-stock filtering, resolving template-rendering issues, AWS configuration troubleshooting, CRUD testing, and documentation. Initial DynamoDB setup, the initial UI and portions of the data schema were collaborative/teammate contributions. **This is a team project, not a solo build.**

## Stack

- Python, Flask, Jinja2, HTML/CSS
- Amazon DynamoDB through boto3
- Environment-based local configuration using python-dotenv

## Run locally

1. Create and activate a Python virtual environment; install dependencies with `pip install -r requirements.txt`.
2. Create a DynamoDB table with primary partition key **`item_id` (String)** in your AWS account. Use an AWS identity with access only to this demo table. AWS charges may apply.
3. Copy `.env.example` to `.env`, then set a secure `FLASK_SECRET_KEY`, your AWS region and the table name. Configure AWS credentials locally using an AWS profile or role; never commit them.
4. Run `python app.py` and open `http://127.0.0.1:5000`.

## What was tested

The original team report documents successful local create, update, delete, category filter and low-stock operations against DynamoDB. This portfolio-review copy includes small configuration, numeric validation and scan-pagination refinements. Those refinements passed Python syntax validation, **but have not been retested against a live AWS table**. Verify all CRUD operations with your own test table before publishing.

## Scope and limitations

This is an instructional/local demonstration, **not production-ready**. It has no user authentication, authorization, CSRF protection or rate limiting. Don't deploy it publicly without adding these protections. DynamoDB scans also may be inefficient at scale.

## Attribution and publication

This project was completed with classmates. Confirm that team members and the course permit public posting before publishing the shared code or screenshots. Keep the original course report private unless everyone agrees. The environment/configuration fixes in this review copy were made as a later portfolio cleanup, rather than part of the original coursework.
