# Scraper API

## Installation

For cloning repository, use:

<code>git clone https://github.com/bohdants96/fastapi_google_maps_scaper.git</code>

For installation, your python's version must be >= 3.10.

You can install all dependencies by pip:

<code>pip install -r requirements.txt</code>

or using poetry:

<code>poetry install</code>

To use the installed dependencies, activate the virtual environment by running:

<code>poetry shell</code>

You can verify that the dependencies have been installed correctly by running:

<code>poetry show</code>

or:

<code>pip list</code>

### Configure

You can then update configs in the .env files to customize your configurations.

Before deploying it, make sure you set at least the values for:

<code>DOMAIN</code>

<code>ENVIRONMENT</code>

<code>PROJECT_NAME</code>

<code>STACK_NAME</code>

<code>BACKEND_CORS_ORIGINS</code>

<code>SECRET_KEY</code>

<code>FIRST_SUPERUSER</code>

<code>FIRST_SUPERUSER_PASSWORD</code>

<code>EMAILS_FROM_EMAIL</code>

<code>SMTP_TLS</code>

<code>SMTP_SSL</code>

<code>SMTP_PORT</code>

<code>POSTGRES_SERVER</code>

<code>POSTGRES_PORT</code>

<code>POSTGRES_DB</code>

<code>POSTGRES_USER</code>

<code>POSTGRES_PASSWORD</code>

<code>SENTRY_DSN</code>

<code>STRIPE_SECRET_KEY</code>

<code>STRIPE_WEBHOOK_SECRET</code>

<code>INTERNAL_SCRAPER_API_ADDRESS</code>

<code>REDIS_SERVER</code>

<code>REDIS_PORT</code>

<code>REDIS_USER</code>

<code>REDIS_PASSWORD</code>

<code>REDIS_DB</code>

## Development

When you're changing the models, create a new version for your db:

<code>$ alembic revision --autogenerate -m "My changes"</code>

And run your migration:

<code>alembic upgrade heads</code>

If you don't need a specific version, you can simply add the package by its name. For example, to add requests:

<code>poetry add requests</code>

and with a specific version of a package:

<code>poetry add requests@2.25.1</code>

With using pip, you can do it by next steps:

<code>pip install requests</code>

or with a specific version of a package:

<code>pip install requests==2.25.1</code>

You should update requirements.txt after installing a new package.
You can manually add the package to the requirements.txt file, 
or you can use pip to automatically update the file.

<code>pip freeze > requirements.txt</code>

## Deployment

After successful installation of all dependencies, you can run a project by command:

<code>uvicorn main:app --reload --port=8000</code>

After running the command, you can check all routs on the http://127.0.0.1:8000/docs.

Rout http://127.0.0.1:8000/api/v1/business-leads/ will receive list of business types,
list of cities or states to filter and limit to return a certain number of records. 

Rout http://127.0.0.1:8000/api/v1/business-leads/download-csv will receive list of business types,
list of cities or states to filter and limit to return a certain number of records in csv-file.

Rout http://127.0.0.1:8000/api/v1/stripe/create-payment-intent will receive an amount and credits 
to top up your balance. And update payment status by webhook http://127.0.0.1:8000/api/v1/stripe/webhook.

Rout http://127.0.0.1:8000/api/v1/commands/start-scraper will receive list of business types,
list of cities or states to filter and limit to return a certain number of records from scraper. 
This rout sends a request to ScraperLight and starts it. 

After the scraper has finished its work, it sends a request back to http://127.0.0.1:8000/api/v1/commands/finish-notification/{tas_id},
where we reduce the credits for user.

By rout http://127.0.0.1:8000/api/v1/commands/get-scraper-status you can 
see status of scraper work.