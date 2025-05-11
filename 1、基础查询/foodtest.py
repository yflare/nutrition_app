import mysql.connector

# 连接到MySQL数据库
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Blc080100',
    database='ruangong_fooddb'
)

# 使用 buffered=True 的 cursor
cursor = connection.cursor(buffered=True)

def query_food_features(food_name):
    cursor.execute("SELECT f.name, ff.feature FROM food f JOIN food_feature ff ON f.id = ff.food_id WHERE f.name = %s", (food_name,))
    results = cursor.fetchall()
    for result in results:
        print(f"Food: {result[0]}, Feature: {result[1]}")

query_food_features('燕麦')

