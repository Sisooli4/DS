from fastapi import FastAPI, Depends

app = FastAPI(title='Users Service',
              version='0.1.0',
              docs_url='/users-service/docs',
              redoc_url=None,
              openapi_url="/users-service/openapi.json")
