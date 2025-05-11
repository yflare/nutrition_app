import pandas as pd
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

# 读取 Excel 文件
feature_data = pd.read_excel('foodfeature.xls', engine='xlrd')
feature_data.rename(columns=lambda x: x.strip(), inplace=True)

# 插入数据到 food_feature 表
for index, row in feature_data.iterrows():
    food_name = row['食品名称']
    feature = row['特征']

    # 查询食品表以获取对应的 food_id
    cursor.execute("SELECT id FROM food WHERE name = %s", (food_name,))
    result = cursor.fetchone()

    if result:  # 找到食品
        food_id = result[0]
    else:  # 未找到，插入新食品
        print(f"未找到食品名称: {food_name}，准备插入新记录")
        cursor.execute("INSERT INTO food (name) VALUES (%s)", (food_name,))
        food_id = cursor.lastrowid  # 获取新插入的食品 ID

    # 检查食品特征是否已存在
    cursor.execute("SELECT * FROM food_feature WHERE food_id = %s AND feature = %s", (food_id, feature))
    if cursor.fetchone():  # 如果已存在
        print(f"已存在食品特征: {food_id} - {feature}，跳过插入")
    else:  # 插入新特征
        cursor.execute("INSERT INTO food_feature (food_id, feature) VALUES (%s, %s)", (food_id, feature))

# 提交插入操作
connection.commit()
cursor.close()
connection.close()

print("特征数据插入完成")
