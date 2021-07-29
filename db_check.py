from flask_sqlalchemy import SQLAlchemy
from basic import UserData


query = UserData.query.filter(UserData.username=='inoueaus')
rows = query.statement.execute()

print(rows)
