from locust import HttpUser, task, between
import json

class NormalUser(HttpUser):
    wait_time = between(5, 9)

    def on_start(self):
        response = self.client.post("/api/auth/login", data=json.dumps({"username": "testuser", "password": "%&testuser123"}))
        print(response)

    @task
    def index_page(self):
        self.client.get("/annotate")