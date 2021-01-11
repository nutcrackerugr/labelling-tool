from application import create_app, db
from application.models import Task
from rq import get_current_job
from datetime import datetime

def rqjob(func):
    def rqjob_inner(*args, **kwargs):
        from application import create_app
        
        app = create_app()
        with app.app_context():
            job = get_current_job()
            task = Task.query.get(job.get_id())

            try:
                func(*args, **kwargs)
            except:
                task.exception = True
            finally:
                if job:
                    job.meta["progress"] = 100
                    job.save_meta()

                    task.completed = True
                    task.completed_at = datetime.utcnow()

                    db.session.commit()
    
    return rqjob_inner