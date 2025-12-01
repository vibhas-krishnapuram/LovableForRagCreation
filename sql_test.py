import sqlalchemy as sa 

engine = sa.create_engine("sqlite:///test.db")
connection = engine.connect()
metadata = sa.MetaData()

user_table = sa.Table(
    "users", 
    metadata,
    sa.Column("user_id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("username", sa.String, unique=True, nullable=False),
    sa.Column("password", sa.String, nullable=False)
)

def insert_user(username: str, password: str):
    query = user_table.insert().values(username=username, password=password)
    connection.execute(query)
    connection.commit()


def select_user(username: str):
    query = user_table.select().where(user_table.c.username == username)
    result = connection.execute(query)
    return result.fetchone()

metadata.create_all(engine)
insert_user("vibhask08", "password")

print(select_user("vibhask08"))

connection.close()



