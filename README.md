# CC Order Page

#### Video Demo: [https://youtu.be/D2gC3sgP8rA]

#### Description: An intuitive Card Ordering Website application that allows clients to register an account, log in/out and place inventory orders.

## Table of Contents

- [About](#about)
- [Deployment](#deployment)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Deployment](#deployment)

## About

This application is an intuitive card ordering website for Convenient Cards that allows bank clients to register accounts, log in/out and place inventory orders. CC admin users can log in to review card orders, mark orders as shipped, create new users, edit users, delete users, create new banks, edit banks, delete banks and much more.

It’s deployed on Vercel (https://cc-order-page.vercel.app/) and uses a Neon Postgres database.

## Deployment

🔗 **Live Demo:** https://cc-order-page.vercel.app/

## Features

- Simple order UI
- Form for submitting orders
- Validation and feedback on form fields
- Interactive cart

## Tech Stack

- Framework: Flask
- Database: SQLAlchemy
- Languages used: Python, Jinja, Javascript, SQL
- Hosting: Vercel & Neon
- Styling: HTML + CSS

### Prerequisites

Requirements are found in requirements.txt:

- Python
- psycopg2-binary
- Postgres

## Installation

For local use:

```bash
# Clone the repo
git clone https://github.com/username/cc-order-page.git

# Move into project directory
cd cc-order-page

# Install dependencies
pip install requirements.txt

# Run sql file to create tables & seed database:
card-orders.sql

# Run flask.
python3 -m flask run
```
