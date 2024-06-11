
# Scraper API  
  

## Installation  
  
For cloning repository, use:  
  
`git clone https://github.com/bohdants96/fastapi_google_maps_scaper.git`  
  
For installation, your python's version must be >= 3.10.  
  
You can install all dependencies by pip:  
  
`pip install -r requirements.txt`  
  
or using poetry:  
  
`poetry install`  
  
To use the installed dependencies, activate the virtual environment by running:  
  
`poetry shell`  
  
You can verify that the dependencies have been installed correctly by running:  
  
`poetry show`  
  
or:  
  
`pip list`  
  
### Configure  
  
You can then update configs in the .env files to customize your configurations.  
  
Before deploying it, make sure you set at least the values for:  
  

 1. `DOMAIN`  
 2. `ENVIRONMENT`  
 3. `PROJECT_NAME`  
 4. `STACK_NAME`  
 5. `BACKEND_CORS_ORIGINS`  
 6. `SECRET_KEY`  
 7. `FIRST_SUPERUSER`  
 8. `FIRST_SUPERUSER_PASSWORD`  
 9. `EMAILS_FROM_EMAIL`  
 10. `SMTP_TLS`  
 11. `SMTP_SSL`  
 12. `SMTP_PORT` 
 13. `POSTGRES_SERVER`  
 14. `POSTGRES_PORT`  
 15. `POSTGRES_DB`  
 16. `POSTGRES_USER`  
 17. `POSTGRES_PASSWORD`  
 18. `SENTRY_DSN`  
 19. `STRIPE_SECRET_KEY`  
 20. `STRIPE_WEBHOOK_SECRET`  
 21. `INTERNAL_SCRAPER_API_ADDRESS`  
 22. `REDIS_SERVER`  
 23. `REDIS_PORT`  
 24. `REDIS_USER`  
 25. `REDIS_PASSWORD`  
 26. `REDIS_DB`  
  
## Development  
  
When you're changing the models, create a new version for your db:  
  
`alembic revision --autogenerate -m "My changes"`  
  
And run your migration:  
  
`alembic upgrade heads`
  
If you don't need a specific version, you can simply add the package by its name. For example, to add requests:  
  
`poetry add requests`  
  
and with a specific version of a package:  
  
`poetry add requests@2.25.1`  
  
With using pip, you can do it by next steps:  
  
`pip install requests`  
  
or with a specific version of a package:  
  
`pip install requests==2.25.1`  
  
You should update requirements.txt after installing a new package.  
You can manually add the package to the requirements.txt file,   
or you can use pip to automatically update the file.  
  
`pip freeze > requirements.txt`  
  
## Deployment  
  
After successful installation of all dependencies, you can run a project by command:  
  
`uvicorn main:app --reload --port=8000`  
  
After running the command, you can check all endpoints on the http://127.0.0.1:8000/docs.  
  
Endpoint http://127.0.0.1:8000/api/v1/business-leads/ will receive list of business types,  
list of cities or states to filter and limit to return a certain number of records.   
  
Endpoint http://127.0.0.1:8000/api/v1/business-leads/download-csv will receive list of business types,  
list of cities or states to filter and limit to return a certain number of records in csv-file.  
  
Endpoint http://127.0.0.1:8000/api/v1/stripe/create-payment-intent will receive an amount and credits   
to top up your balance. And update payment status by webhook http://127.0.0.1:8000/api/v1/stripe/webhook.  
  
Endpoint http://127.0.0.1:8000/api/v1/commands/start-scraper will receive list of business types,  
list of cities or states to filter and limit to return a certain number of records from scraper.   
This endpoint sends a request to ScraperLight and starts it.   
  
After the scraper has finished its work, it sends a request back to http://127.0.0.1:8000/api/v1/commands/finish-notification/{tas_id},  
where we reduce the credits for user.  
  
By endpoint http://127.0.0.1:8000/api/v1/commands/get-scraper-status you can   
see status of scraper work.
 