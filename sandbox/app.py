from fastapi import FastAPI
from pydantic import BaseModel
from sandbox_service import SandboxService

app = FastAPI()
sandbox = SandboxService()


class CodeRequest(BaseModel):
    code: str


@app.post("/execute")
def execute_code(request: CodeRequest):
    return sandbox.execute(request.code)
