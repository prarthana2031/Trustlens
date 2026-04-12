import requests
resp = requests.post(
    "https://preeee-276-ml-service-api.hf.space/bias/detect",
    json={
        "scores": [85,72,88,65,90,78,82,70],
        "candidates_data": [{"gender":"Female"}]*4 + [{"gender":"Male"}]*4
    }
)
print(resp.status_code, resp.json())