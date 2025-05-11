from flask import Flask, render_template, request
import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# 连接到MySQL数据库
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # 替换为你的MySQL用户名
        password='root',  # 替换为你的MySQL密码
        database='ruangong_fooddb',  # 替换为你的数据库名
        charset='utf8mb4'  # 确保使用UTF-8字符集处理中文
    )
    return connection



# 路由和处理器
@app.route('/', methods=['GET', 'POST'])
def index():
    nutrition_data = None
    if request.method == 'POST':
        # 获取用户输入，并将其转换为小写
        food_name = request.form['food_name'].strip().lower()

        print(f"User input (after stripping and lowering): {food_name}")  # 打印用户输入


        # 查询食物及其特征和营养成分
        connection = get_db_connection()
        cursor = None  # 初始化cursor为None
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT f.name, f.image_url, f.detail_url, f.calories, f.carbs, f.fat, f.protein, f.fiber, f.category, ff.feature 
            FROM food f
            LEFT JOIN food_feature ff ON f.id = ff.food_id
            WHERE LOWER(f.name) = LOWER(%s)
            """
            cursor.execute(query, (food_name,))

            print("Food Name:", food_name)  # 打印用户输入的食物名

            nutrition_data = cursor.fetchall()  # 确保读取所有数据
            print(f"Nutrition data found: {nutrition_data}")

            if not nutrition_data:
                print("No nutrition data found for the food name.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if cursor:  # 确保cursor不为None再关闭
                cursor.close()  # 在所有结果读取后关闭游标
            connection.close()


    return render_template('index.html', nutrition_data=nutrition_data)


if __name__ == '__main__':
    app.run(debug=True)
