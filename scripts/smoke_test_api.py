"""Quick end-to-end API smoke test."""
import json
import urllib.request
from pathlib import Path

base = "http://127.0.0.1:8000"

print("HEALTH", urllib.request.urlopen(base + "/api/health").read().decode())

resume = Path(__file__).resolve().parent.parent / "uploads" / "Sample_Resume_Demo.docx"
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="{resume.name}"\r\n'
    "Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n"
).encode() + resume.read_bytes() + f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    base + "/api/upload",
    data=body,
    method="POST",
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
)
upload = json.loads(urllib.request.urlopen(req).read().decode())
print("UPLOAD", upload)

payload = json.dumps(
    {
        "file_id": upload["file_id"],
        "job_description": (
            "We need a Python FastAPI React engineer with Machine Learning, Docker, AWS, and NLP experience."
        ),
    }
).encode()
req2 = urllib.request.Request(
    base + "/api/analyze",
    data=payload,
    method="POST",
    headers={"Content-Type": "application/json"},
)
analysis = json.loads(urllib.request.urlopen(req2).read().decode())
print(
    "ANALYZE",
    analysis["ats_score"],
    analysis["job_match"]["job_match_percentage"],
    analysis["analysis_id"][:8],
    len(analysis["recommendations"]),
)

req3 = urllib.request.Request(base + f"/api/report/{analysis['analysis_id']}")
pdf = urllib.request.urlopen(req3).read()
print("REPORT_BYTES", len(pdf), pdf[:4])
print("API_FLOW_OK")
