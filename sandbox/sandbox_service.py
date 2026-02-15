import subprocess
import sys
import tempfile
import os
import resource

MAX_OUTPUT = 10000
TIME_LIMIT = 5


def limit_resources():
    # CPU limit only (memory limit removed for macOS stability)
    resource.setrlimit(resource.RLIMIT_CPU, (TIME_LIMIT, TIME_LIMIT))


class SandboxService:
    def execute(self, code: str) -> dict:
        cleaned_code = code.strip()
        if not cleaned_code:
            return {"error": "No code provided."}

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, "code.py")

                with open(file_path, "w") as f:
                    f.write(cleaned_code)

                result = subprocess.run(
                    [sys.executable, file_path],
                    capture_output=True,
                    text=True,
                    timeout=TIME_LIMIT,
                    preexec_fn=limit_resources
                )

                stdout = result.stdout[:MAX_OUTPUT] if result.stdout else ""
                stderr = result.stderr[:MAX_OUTPUT] if result.stderr else ""

                if stderr:
                    return {"error": stderr.strip()}

                if stdout.strip():
                    return {"output": stdout.strip()}

                return {"output": "Code executed successfully (no output)."}

        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out."}
        except Exception as e:
            return {"error": str(e)}
