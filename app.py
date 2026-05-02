import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import random
import os
import time  

JST = timezone(timedelta(hours=+9), 'JST')
LOG_FILE = "ルーレッツ.csv"
chat_file = "chatlog.csv"

# 駅名のリスト
STATIONS = ["今治", "松山", "琴平", "大歩危", "宇和島", "窪川", "高松", "高知", "徳島"]

st.set_page_config(page_title="レッツルーレッツ", layout="centered", page_icon="🎲")

st.markdown("""
    <style>
    .big-font { font-size:50px !important; font-weight: bold; color: #ffffff; }
    .station-font { font-size:40px !important; color: #FFEB3B; font-weight: bold; }
    .system-msg { background-color: #f0f2f6; color: #555555; padding: 8px 15px; border-radius: 20px; font-size: 0.8em; border: 1px solid #e0e0e0; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("澤村拓一の宇宙開発")

if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# ログイン処理
if not st.session_state.user_name:
    st.info("最初に班名と現在の駅を登録してください")
    with st.form("login_form"):
        name_input = st.text_input("名前（例：二戸班_高松駅)")
        submit = st.form_submit_button("登録")
        if submit:
            if name_input:
                st.session_state.user_name = name_input
                st.rerun()
            else:
                st.warning("名前を入力しろ")

else:
    # サイドバー
    st.sidebar.write(f"👤 ログイン中: **{st.session_state.user_name}**")
    if st.sidebar.button("ログアウト"):
        st.session_state.user_name = ""
        st.rerun()

    tab1, tab2 = st.tabs(["🚀 開発センター", "💬 掲示板"])

    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                st.image("sawamura.jpeg", use_container_width=True, caption="担当:澤村拓一")
            except:
                st.error("画像なし")

        # --- ボタン共通処理用関数 ---
        def save_log(action_type, result_val):
            now = datetime.now(JST)
            time_stamp = now.strftime("%Y/%m/%d %H:%M:%S")
            # ログ保存
            new_log = {
                "発生時刻": [time_stamp],
                "開発者": [st.session_state.user_name],
                "項目": [action_type],
                "結果": [result_val]
            }
            pd.DataFrame(new_log).to_csv(LOG_FILE, index=False, header=not os.path.exists(LOG_FILE), mode='a', encoding='utf_8_sig')
            
            # チャット掲示板へ流す
            icon = "🎲" if action_type == "サイコロ" else "📍"
            chat_msg = f"""
            <div style="display: flex; justify-content: center; margin: 5px 0;">
                <div class="system-msg">
                    📢 {now.strftime("%H:%M")} | {st.session_state.user_name} が {action_type}を実行： <b>{icon} {result_val}</b>
                </div>
            </div>
            """
            new_chat = {"時刻": [now.strftime("%Y/%m/%d %H:%M")], "名前": ["SYSTEM"], "メッセージ": [chat_msg]}
            pd.DataFrame(new_chat).to_csv(chat_file, index=False, header=not os.path.exists(chat_file), mode='a', encoding='utf_8_sig')
            return time_stamp

        # --- ボタン配置 ---
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("🎲 サイコロを振る", use_container_width=True, type="primary"):
                # カットイン演出
                cut_in = st.empty()
                try:
                    cut_in.image("sawamura.gif", use_container_width=True)
                    time.sleep(1.2)
                    cut_in.empty()
                except: pass
                
                res = random.randint(1, 6)
                ts = save_log("サイコロ", res)
                st.markdown(f'<p class="big-font">🎲 {res}</p>', unsafe_allow_html=True)
                st.toast(f"サイコロを記録しました ({ts})")

        with btn_col2:
            if st.button("📍 目的地を決定", use_container_width=True):
                # 目的地選出
                station_res = random.choice(STATIONS)
                ts = save_log("目的地", station_res)
                st.markdown(f'<p class="station-font">📍 {station_res}</p>', unsafe_allow_html=True)
                st.toast(f"目的地を記録しました ({ts})")

        st.divider()
        st.subheader("履歴一覧")
        if os.path.exists(LOG_FILE):
            df_log = pd.read_csv(LOG_FILE)
            st.dataframe(df_log.iloc[::-1], use_container_width=True, height=250)
        else:
            st.write("履歴なし")

    with tab2:
        st.subheader("💬 掲示板")
        c_user = st.text_input("名前", value=st.session_state.user_name)
        c_msg = st.text_area("メッセージ", height=100)
        
        if st.button("書き込む", use_container_width=True):
            if c_user and c_msg:
                now_chat = datetime.now(JST).strftime("%Y/%m/%d %H:%M")
                new_post = {"時刻": [now_chat], "名前": [c_user], "メッセージ": [c_msg.replace('\n', ' ')]}
                pd.DataFrame(new_post).to_csv(chat_file, index=False, header=not os.path.exists(chat_file), mode='a', encoding='utf_8_sig')
                st.rerun()

        st.divider()
        chat_container = st.container(height=500) 
        with chat_container:
            if os.path.exists(chat_file):
                df_chat_log = pd.read_csv(chat_file)
                for i, row in df_chat_log.iloc[::-1].iterrows():
                    if "<div" in str(row['メッセージ']):
                        st.markdown(row['メッセージ'], unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{row['名前']}** <small style='color:gray'>{row['時刻']}</small>", unsafe_allow_html=True)
                        st.write(row['メッセージ'])
                        st.markdown("---")