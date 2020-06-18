from application import init_celery

app = init_celery()
app.conf.imports = app.conf.imports + ("application.tasks.tweets",)