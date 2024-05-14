from fastapi import FastAPI, Depends

app = FastAPI(title='Event Service',
              version='0.1.0',
              docs_url='/events-service/docs',
              redoc_url=None,
              openapi_url="/events-service/openapi.json")
