from fastapi import FastAPI, Depends

app = FastAPI(title='Invites Service',
              version='0.1.0',
              docs_url='/invites-service/docs',
              redoc_url=None,
              openapi_url="/invites-service/openapi.json")
