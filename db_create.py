from app import app, db  
 
def create_db():
    with app.app_context():
        db.create_all()  # This will create the tables in the database
 
 
if __name__ == "__main__":
    create_db()