from fastapi import FastAPI, Depends

app = FastAPI(title='Calendar Service',
              version='0.1.0',
              docs_url='/calendar-service/docs',
              redoc_url=None,
              openapi_url="/calendar-service/openapi.json")
