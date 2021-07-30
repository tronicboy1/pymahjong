from pyjong import app,db
from flask import render_template

#create all db
#with app.app_context is necessary when importing alchemy db
with app.app_context():
    db.create_all()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

    

if __name__ == '__main__':
    app.run(debug=True)
