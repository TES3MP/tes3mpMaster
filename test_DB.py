from data_base import DataBase

db = DataBase()
db.add('127.0.0.2', 25565, 25566, "another motd", 5, 10, 0)
db.add('127.0.0.1', 25565, 25566, "another motd", 5, 10, 0)
print db.db