from fastapi import FastAPI, Depends

app = FastAPI(title='Client Service',
              version='0.1.0',
              docs_url='/client-service/docs',
              redoc_url=None,
              openapi_url="/client-service/openapi.json")
