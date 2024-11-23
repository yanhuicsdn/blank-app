import streamlit as st
import requests

# 设置页面标题
st.title("AMA 讨论生成器及观点收集")

# Step 1: 用户输入讨论议题
st.header("输入AMA讨论议题")
topic = st.text_input("请输入讨论议题，例如：AI对投资的影响")

# Step 2: 通过API生成讨论内容
if st.button("生成讨论内容"):
    if topic:
        with st.spinner("正在生成讨论内容..."):
            api_url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer xai-YcNS98aOC1ozn5HAaaHoYFsBg6PZhQFcuYyEjSEneY9W81wZVQE7r1lhRQyLNU8ebsUl7kZYmqfXjN7D"
            }
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant specialized in generating AMA topics."},
                    {"role": "user", "content": f"Generate detailed talking points for the AMA topic: {topic}"}
                ],
                "model": "grok-beta",
                "stream": False,
                "temperature": 0.7
            }
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 200:
                discussion_points = response.json().get("choices")[0].get("message", {}).get("content", "No response")
                st.success("生成成功！以下是讨论点：")
                st.markdown(discussion_points)
            else:
                st.error(f"API调用失败，错误代码：{response.status_code}")
    else:
        st.warning("请输入讨论议题！")

# Step 3: 集成Twitter X，获取相关观点
st.header("Twitter X观点收集")
if st.button("收集大V观点"):
    with st.spinner("正在收集相关讨论..."):
        # 模拟从Twitter API获取数据
        tweets = [
            {"user": "BigThinker1", "content": "AI is reshaping finance!", "likes": 120, "retweets": 30},
            {"user": "InvestGuru", "content": "AI investments are growing rapidly, but risks remain.", "likes": 95, "retweets": 25},
            {"user": "TechTrends", "content": "What will AI's role in portfolio management look like?", "likes": 80, "retweets": 20},
        ]
        for tweet in tweets:
            st.subheader(f"{tweet['user']}的观点")
            st.write(tweet["content"])
            st.write(f"👍 {tweet['likes']} ❤️ {tweet['retweets']}")

# Step 4: 数据筛选功能
st.header("筛选观点")
filter_keyword = st.text_input("输入关键词进行筛选，例如：投资")
if st.button("筛选"):
    filtered_tweets = [tweet for tweet in tweets if filter_keyword.lower() in tweet["content"].lower()]
    if filtered_tweets:
        for tweet in filtered_tweets:
            st.subheader(f"{tweet['user']}的观点")
            st.write(tweet["content"])
            st.write(f"👍 {tweet['likes']} ❤️ {tweet['retweets']}")
    else:
        st.warning("未找到包含该关键词的观点。")
