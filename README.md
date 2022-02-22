<!-- ABOUT THE PROJECT -->
## About The Project
Small service that allows users to upload up to 99 files on their account and download them

<!-- GETTING STARTED -->
## Getting Started
***
You can use docker and/or Makefile to run the project.
### Prerequisites
In order to run the project you will need the following:
* [docker](https://docs.docker.com/engine/install/)
* [docker-compose](https://docs.docker.com/compose/)
* [GNU Make](https://www.gnu.org/software/make/)

## How to run the project
***
1. Rewrite **.env.example** to your own **.env**
2. Execute make up to bring all the project up to life:
```bash
make up
```
3. Navigate [local-docs](http://localhost:8000/docs#) to check docs
and try the API


## Run test suite
***
Execute ```make test``` to run all the tests

## Additional tools
Execute ```make psql``` to have psql terminal to postgres
Execute ```make bash``` to have shell into app service.
