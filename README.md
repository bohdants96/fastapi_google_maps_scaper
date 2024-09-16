
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
 27. `DOCKER_IMAGE_BACKEND`
 28. `DOCKER_IMAGE_FRONTEND`
 29. `EMAILS_FROM_ENAIL`
 30. `SUPPORT_EMAIL`
 31. `USERS_OPEN_REGISTRATION` 
  
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

By using endpoint http://127.0.0.1:8000/api/v1/login/access-token you can get login token and use all endpoints after that [POST].

Endpoint http://127.0.0.1:8000/api/v1/users/me return all information about login user [GET], delete login user [DELETE] and update user [PATCH].

Endpoint http://127.0.0.1:8000/api/v1/users/me/password updates password for login user [PATCH].

Endpoint http://127.0.0.1:8000/api/v1/users/signup create a new user [POST].

Endpoint http://127.0.0.1:8000/api/v1//users/me/search-history return all search histories for login user [GET].

Endpoint http://127.0.0.1:8000/api/v1/users/me/search-history/{search_history_id} return search history from database with id search_history_id [GET].

Endpoint http://127.0.0.1:8000/api/v1/business-leads/ will receive list of business types,  
list of cities or states to filter and limit to return a certain number of records [GET].   
  
Endpoint http://127.0.0.1:8000/api/v1/commands/download-csv will receive list of business types,  
list of cities or states to filter and limit to return a certain number of records in csv-file [GET].  
  
Endpoint http://127.0.0.1:8000/api/v1/stripe/create-payment-intent will receive an amount and credits   
to top up your balance. And update payment status by webhook http://127.0.0.1:8000/api/v1/stripe/webhook [POST].  
  
Endpoint http://127.0.0.1:8000/api/v1/commands/start-scraper will receive list of business types,  
list of cities or states to filter and limit to return a certain number of records from scraper with parameter source=business.   
This endpoint sends a request to ScraperLight and starts it [POST]. If you want to change source, then set source to people with parameters: items, limit and email.
Items include list of streets, list of cities and list of states.
  
After the scraper has finished its work, it sends a request back to http://127.0.0.1:8000/api/v1/commands/finish-notification/{tas_id},  
where we reduce the credits for user[POST].  
  
By endpoint http://127.0.0.1:8000/api/v1/commands/get-scraper-status you can   
see status of scraper work [GET].

Endpoint http://127.0.0.1:8000/api/v1/business-types/ will receive name, limit and offset to return a certain number of business types from database [GET].   

Endpoint http://127.0.0.1:8000/api/v1/address/ will receive city, limit and offset to return a certain number of addresses from database [GET].

Endpoint http://127.0.0.1:8000/api/v1/people-lead/ will receive list of streets,  
list of cities and states to filter and limit to return a certain number of records [POST].