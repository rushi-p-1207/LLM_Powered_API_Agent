import requests
import json

class SandboxClient:
    def __init__(self, sandbox_url="http://localhost:9000"):
        self.sandbox_url = sandbox_url

    def execute_code(self, code: str) -> str:
        """
        Executes the given Python code in the sandbox.
        """
        try:
            payload = {"code": code}
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.sandbox_url}/execute", 
                data=json.dumps(payload), 
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if "output" in result:
                return result["output"]
            elif "error" in result:
                return f"Error: {result['error']}"
            else:
                return "No output returned."

        except requests.exceptions.RequestException as e:
            return f"Sandbox execution failed: {str(e)}"
