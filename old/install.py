from models import db, Label, AppUser
from api import app

if __name__ == "__main__":
	db.init_app(app)

	with app.app_context():
		print("Dropping all tables...")
		db.drop_all()
		print("Creating new tables...")
		db.create_all()

		print("Adding default labels...")
		db.session.add(Label(name="testlabel1"))
		db.session.add(Label(name="testlabel2"))
		db.session.add(Label(name="testlabel3"))
		
		AppUser("manolo", "manolo123").save()
		
		print("Commiting changes...")
		db.session.commit()
		print("Done.")
