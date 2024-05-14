from fastapi import FastAPI, Depends

app = FastAPI(title='Auth Service',
              version='0.1.0',
              docs_url='/docs',
              redoc_url=None,
              openapi_url="/openapi.json")
