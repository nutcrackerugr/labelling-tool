from locust import HttpUser, task, between
import json

class NormalUser(HttpUser):
    wait_time = between(5, 9)

    def on_start(self):
        post_data = json.dumps({"username": "testuser", "password": "%&testuser123"})
        headers = {"content-type": "application/json"}

        with self.client.post("/api/auth/login", data=post_data, headers=headers, catch_response=True) as response:
            # print(response.cookies)
            # print(response.text)
            self.access_token = json.loads(response.text)["access_token"]
            self.refresh_token = json.loads(response.text)["refresh_token"]

    @task
    def index_page(self):
        headers = {"Authentication": f"Bearer {self.access_token}"}
        
        self.client.get("/annotate", headers=headers)
        self.client.get("/api/labels", headers=headers)
        self.client.get("/api/tweet/nextinrank", headers=headers)
        self.client.get("/api/tweet/82608/suggestions", headers=headers)
        self.client.get("/api/user/22084/tweets/5", headers=headers)
        self.client.get("/api/tweet/1200/annotation", headers=headers)
