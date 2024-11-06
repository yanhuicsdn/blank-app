import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# 设置页面配置
st.set_page_config(page_title="48小时任务 - 只活今天和明天", page_icon="📅", layout="wide")


# 初始化数据库连接和表
def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            date TEXT,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()

# 添加任务到数据库
def add_task(conn, content, date=None):
    conn.execute("INSERT INTO tasks (content, date, completed) VALUES (?, ?, 0)", (content, date))
    conn.commit()

# 获取任务从数据库，自动分类
def get_tasks(conn):
    tasks = {"今日任务": [], "明日任务": [], "备忘录": [], "过期已完成任务": []}
    cur = conn.cursor()
    cur.execute("SELECT id, content, date, completed FROM tasks")
    rows = cur.fetchall()
    today = datetime.now().date()
    for id, content, date, completed in rows:
        if date:
            task_date = datetime.strptime(date, "%Y-%m-%d").date()
            if task_date < today and completed:
                tasks["过期已完成任务"].append((id, content))
            elif task_date == today:
                tasks["今日任务"].append((id, content, completed))
            elif task_date > today:
                tasks["明日任务"].append((id, content, completed))
            else:
                if not completed:
                    tasks["备忘录"].append((id, content, completed))
        else:
            if not completed:
                tasks["备忘录"].append((id, content, completed))
    return tasks

# 更新任务的完成状态
def update_task_completion(conn, task_id, completed):
    conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
    conn.commit()

# 页面标题
st.title("48小时任务 ")

# 访问密码
password = st.text_input("请输入访问密码", type="password")

# 数据库连接
conn = sqlite3.connect("tasks.db")
init_db(conn)

# 验证密码
if password == "12345":
    # 用户输入任务内容
    task_content = st.text_input("任务内容", key="task_content")

    # 用户选择任务日期或备忘录
    task_date_option = st.selectbox("任务日期", ["今日", "明日", "备忘录"], key="date_option")
    if task_date_option in ["今日", "明日"]:
        task_date = (datetime.now() + timedelta(days=("明日" == task_date_option))).strftime("%Y-%m-%d")
    else:
        task_date = None  # 对于备忘录，日期字段为None

    # 当用户点击添加任务按钮时，将任务添加到数据库
    if st.button("添加任务"):
        add_task(conn, task_content, task_date)
        st.success("任务添加成功！")

    # 从数据库获取任务并显示，包括勾选框
    tasks = get_tasks(conn)
    for category, tasks_list in tasks.items():
        if category == "过期已完成任务":
            with st.expander(f"{category}"):
                for task_id, task_content in tasks_list:
                    st.text(f"{task_content}")
        elif category != "备忘录":
            st.write(f"## {category}")
            for task_id, task_content, completed in tasks_list:
                checkbox_label = f"{task_content}"
                if st.checkbox(checkbox_label, completed, key=f"task_{task_id}_{category}"):
                    if not completed:  # 如果任务未完成，用户勾选后更新为完成
                        update_task_completion(conn, task_id, True)
                        st.success(f"任务 '{task_content}' 完成！")
                elif completed:  # 如果任务已完成，用户取消勾选后更新为未完成
                    update_task_completion(conn, task_id, False)
                    st.warning(f"任务 '{task_content}' 标记为未完成。")
        else:
            with st.expander("备忘录"):
                for task_id, task_content, completed in tasks_list:
                    checkbox_label = f"{task_content}"
                    if st.checkbox(checkbox_label, completed, key=f"task_{task_id}_{category}"):
                        if not completed:  # 如果任务未完成，用户勾选后更新为完成
                            update_task_completion(conn, task_id, True)
                            st.success(f"任务 '{task_content}' 完成！")
                    elif completed:  # 如果任务已完成，用户取消勾选后更新为未完成
                        update_task_completion(conn, task_id, False)
                        st.warning(f"任务 '{task_content}' 标记为未完成。")

# 关闭数据库连接
conn.close()
