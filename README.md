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

This application serves as a centralized ordering platform for bank clients working with Convenient Cards. Client users can create an account, authenticate securely, browse available card products, and submit inventory orders using an interactive cart-based workflow. The system is designed to simplify the ordering process while providing administrators with complete control in processing submitted orders. CC admin users can log in to review card orders, mark orders as shipped, create new users, edit users, delete users, create new banks, edit banks, delete banks and much more.

The primary objective of this project was to design a real-world web application that emphasizes clarity, maintainability, and separation of concerns, while also being suitable for deployment in a live production environment. Special attention was paid to error handling, data validation, and scalability so that the application can grow alongside business needs.

It’s deployed on Vercel (https://cc-order-page.vercel.app/) and uses a Neon Postgres database.

Relevent Page Discussion:

- app.py:
  app.py contains all my routes throughout my Flask program. My goal when writing my application was to not handle too much "business logic" into my routes. This was achieved by heavy use of helper functions in my helpers.py file to manage all database queries, handle formatting, and other computations. This ensures that my routes page maintains readability - helping to make debugging simpler by separating concerns.

- helpers.py:
  helpers.py is the largest file contained within my app and manages all database queries. One strict design concept I had in mind when writing every helper function that makes a call to the database is to be sure to handle every exception that could be raised. I decided the best way I can return data to my routes in app.py was through the use of a tuple containing 3 pieces of relevent information (boolean, string, data) this way I can easily manage from app.py whether I should be flashing an error, or proceeding with displaying information on the page. The first element of my response tuple is a BOOLEAN. True means that the query was not only successful, but retrieved valid information. I was able to return False if certain issues occured (like if no data existed) I could then handle this in my app.py file. The second item in my response is a confirmation message. This was used heavily for flash messages when an error has occured and helped with debugging my code. The first item in my response is data retrieved from the DB query.

A big decision change I had to make was to migrate from using CS50's library to implementing sqlalchemy to query my database. I've opted to use plain text queries instead of SQLAlchemy's ORM because I already had all of my valid SQL statements I had to make. So while tedious, the change to the code was relatively minimal to migrate to SQLAlchemy. This migration was necessary to support deployment on Neon, a managed Postgres hosting service. Using SQLAlchemy ensured compatibility with production environments and removed dependencies that were unsuitable for deployment beyond local development.

- card-orders-schema.sql, card-orders-seed.sql, card-orders.sql

Supporting SQL files (card-orders-schema.sql, card-orders-seed.sql, and card-orders.sql) are included to help quickly set up and populate the database in a local environment. Running these scripts creates all required tables and seeds them with initial data, allowing the application to be up and running immediately.

## Deployment

🔗 **Live Demo:** https://cc-order-page.vercel.app/

## Features

- Simple order UI with login and logout functionality
- Ability to register an account
- Form for submitting orders including user feedback or concerns
- Validation and feedback on form fields
- Interactive cart for placing inventory orders
- Order status tracking, including shipment updates
- Admins can create new banks and users to meet growing customer base

## Tech Stack

- Framework: Flask
- Database: PostgreSQL(SQLAlchemy)
- Languages used: Python, Jinja, Javascript, SQL
- Hosting: Vercel (Application) & Neon (database)
- Styling: HTML and CSS

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
