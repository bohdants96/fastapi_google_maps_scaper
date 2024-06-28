# Introduction

## Protocol

The ScraperRus API uses HTTP and JSON formats, following a RESTful architecture wherever possible.

### Security
All communication is encrypted using TLS/SSL, and plain HTTP access is not allowed.

#### JWT Authentication
JWT authentication is the recommended method for using the API. To obtain an access token, send a `POST` request to `/api/v1/login/access-token` with `username` and `password` in the body. The API will return both `access` and `refresh` tokens. The `access` token expires 8 days after it is issued.

For authenticated requests, include the `Authorization` header with `Bearer <access>`. 

### Versioning
The API strives to maintain backward compatibility. However, when incompatible changes are necessary, the version number will be incremented. Older versions will have a compatibility layer for six months before it is removed.

## Use Cases
An example use case for starting a scraper is illustrated in the following diagram:


![Diagram depicting API calls required to start a scraper](/static/docs/start-scraper.png)