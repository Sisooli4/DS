from fastapi import FastAPI, Depends

app = FastAPI(title='Invite Service',
              version='0.1.0',
              docs_url='/invite-service/docs',
              redoc_url=None,
              openapi_url="/invite-service/openapi.json")
