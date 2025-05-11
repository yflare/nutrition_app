import pandas as pd
import mysql.connector

# 连接到MySQL数据库
connection = mysql.connector.connect(
    host='localhost',
    user='root',  # 替换为你的MySQL用户名
    password='Blc080100',  # 替换为你的MySQL密码
    database='ruangong_fooddb'  # 替换为你的数据库名
)

cursor = connection.cursor()

# 读取第一个Excel文件：food.xls
food_data = pd.read_excel('food.xls', engine='xlrd')

# 打印列名以检查
print(food_data.columns)

# 更新列名，去除可能的空格
food_data.rename(columns=lambda x: x.strip(), inplace=True)

# 检查列是否存在并处理数据
if '纤维素(克)' in food_data.columns:
    # 替换 "一" 为 None 表示数据缺失
    food_data.replace('一', None, inplace=True)
    
    # 清洗数据，将无法转换的值设为NaN
    food_data['纤维素(克)'] = pd.to_numeric(food_data['纤维素(克)'], errors='coerce')
else:
    print("列名 '纤维素(克)' 不存在，请检查 Excel 文件")

# 插入数据到food表
for index, row in food_data.iterrows():
    sql_food = """
    INSERT INTO food (name, image_url, detail_url, calories, carbs, fat, protein, fiber, category)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values_food = (row['食品名称'], row['图片链接'], row['详情页链接'], row['每100克热量(大卡)'],
                   row['每100克碳水化合物(克)'], row['每100克脂肪(克)'], row['每100克蛋白质(克)'],
                   row['纤维素(克)'] if pd.notnull(row['纤维素(克)']) else None,  # 处理NaN
                   row['类别'])
    cursor.execute(sql_food, values_food)

# 提交插入操作
connection.commit()

# 关闭连接
cursor.close()
connection.close()

print("数据插入完成")
