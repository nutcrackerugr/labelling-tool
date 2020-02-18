from application import create_app

try:
	import mod_wsgi
	process_group = mod_wsgi.process_group
except:
	process_group = ""

application = create_app(config=process_group + "config")

if __name__ == "__main__":
	application.run(host="0.0.0.0")
