import subprocess

def run_in_deno_sandbox(js_code: str, timeout=5):
    process = subprocess.Popen(
        [
            "deno",
            "run",
            "--no-prompt",
            "--deny-read",
            "--deny-write",
            "--deny-net",
            "--deny-env",
            "--deny-run",
            "sandbox/deno_runner.ts",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        stdout, stderr = process.communicate(js_code, timeout=timeout)
        return {
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "returncode": process.returncode
        }
    except subprocess.TimeoutExpired:
        process.kill()
        return {
            "stdout": "",
            "stderr": "Execution timed out",
            "returncode": -1
        }
