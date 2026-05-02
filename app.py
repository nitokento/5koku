import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import random
import os
import time  

JST = timezone(timedelta(hours=+9), 'JST')
LOG_FILE = "ルーレッツ.csv"
chat_file = "chatlog.csv"

# 追加：駅名のリスト
STATIONS = ["今治", "松山", "琴平", "大歩危", "宇和島", "窪川", "高松", "高知", "徳島"]

st.set_page_config(page_title="レッツルーレッツ", layout="centered", page_icon="🎲")

st.markdown("""
    <style>
    .big-font { font-size:50px !important; font-weight: bold; color: #ffffff; }
    .station-font { font-size:30px !important; color: #FFEB3B; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("澤村拓一の宇宙開発")

if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

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
    try:
        st.sidebar.image("epstein.jpg", width=100) 
    except:
        st.sidebar.write("👤")
    
    st.sidebar.write(f"ログイン中: **{st.session_state.user_name}**")

    if st.sidebar.button("ログアウト"):
        st.session_state.user_name = ""
        st.rerun()

    tab1, tab2 = st.tabs(["🚀 NASA", "💬 掲示板"])

    with tab1:
        try:
            st.image("sawamura.jpeg", width=200, caption="担当:澤村拓一")
        except:
            st.error("画像ファイル'sawamura.jpeg'が見つかりません。")

        if st.button("🚀宇宙開発(まわす)", use_container_width=True):
            cut_in_container = st.empty() 
            try:
                gif_path = "sawamura.gif"
                cut_in_container.image(gif_path, use_container_width=True)
                time.sleep(1.4) 
                cut_in_container.empty()
            except:
                st.warning("カットイン（GIF）が見つかりません。")

            # 出目と駅をランダムに決定
            result = random.randint(1, 6)
            selected_station = random.choice(STATIONS) # ランダム駅選出
            
            st.session_state.last_result = result 
            now = datetime.now(JST)
            time_stamp = now.strftime("%Y/%m/%d %H:%M:%S") 
            time_stamp_chat_display = now.strftime("%H:%M") 

            # ログに駅名を追加
            new_log = {
                "発生時刻": [time_stamp],
                "開発者": [st.session_state.user_name],
                "出目": [f"🎲 {result}"],
                "目的地": [selected_station]
            }
            pd.DataFrame(new_log).to_csv(LOG_FILE, index=False, header=not os.path.exists(LOG_FILE), mode='a', encoding='utf_8_sig')
            
            # チャット用メッセージ（駅名を追加）
            dice_msg = f"""
            <div style="display: flex; justify-content: center; margin: 10px 0;">
                <div style="background-color: #f0f2f6; color: #555555; padding: 10px 15px; border-radius: 20px; font-size: 0.85em; border: 1px solid #e0e0e0; text-align: center;">
                    📢 {time_stamp_chat_display} | {st.session_state.user_name}<br>
                    <span style="font-size: 1.2em; font-weight: bold;">🎲 {result} ／ 📍 {selected_station}</span>
                </div>
            </div>
            """
            new_chat_post = {
                "時刻": [now.strftime("%Y/%m/%d %H:%M")],
                "名前": ["SYSTEM"], 
                "メッセージ": [dice_msg]
            }
            pd.DataFrame(new_chat_post).to_csv(chat_file, index=False, header=not os.path.exists(chat_file), mode='a', encoding='utf_8_sig')

            # 画面表示
            st.markdown(f'<p class="big-font">出目：{result}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="station-font">目的地：{selected_station}</p>', unsafe_allow_html=True)
            st.success(f"【{time_stamp}】に記録しました")

        st.divider()
        st.subheader("履歴一覧（最新順）")
        if os.path.exists(LOG_FILE):
            try:
                df_log = pd.read_csv(LOG_FILE)
                if not df_log.empty:
                    st.dataframe(df_log.iloc[::-1], use_container_width=True, height=300)
                    csv = df_log.to_csv(index=False).encode('utf_8_sig')
                    st.download_button(
                        label="履歴ファイルを保存 (CSV)",
                        data=csv,
                        file_name=f"dice_history_{datetime.now(JST).strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                    )
            except Exception as e:
                st.error(f"ログの読み込みに失敗しました: {e}")
        else:
            st.write("まだ履歴はありません。")

    with tab2:
        st.subheader("💬 掲示板")
        chat_user = st.text_input("名前", value="", placeholder="風吹けばベーデン・パウエル")
        chat_message = st.text_area("メッセージ", placeholder="書き込み内容を入力してください", height=100)
        
        if st.button("書き込む", use_container_width=True):
            if not chat_user:
                st.error("名前を入力してから送信")
            elif not chat_message:
                st.warning("内容がないよう")
            else:
                now_chat = datetime.now(JST).strftime("%Y/%m/%d %H:%M")
                new_post = {
                    "時刻": [now_chat],
                    "名前": [chat_user],
                    "メッセージ": [chat_message.replace('\n', ' ')] 
                }
                pd.DataFrame(new_post).to_csv(chat_file, index=False, header=not os.path.exists(chat_file), mode='a', encoding='utf_8_sig')
                st.rerun()

        st.divider()
        st.write("▼ 掲示板ログ")
        chat_container = st.container(height=600) 
        with chat_container:
            if os.path.exists(chat_file):
                df_chat_log = pd.read_csv(chat_file)
                for i, row in df_chat_log.iloc[::-1].iterrows():
                    if "<div" in str(row['メッセージ']):
                        st.markdown(row['メッセージ'], unsafe_allow_html=True)
                    else:
                        st.markdown(f"{i+1} ：**{row['名前']}** ：{row['時刻']}")
                        st.write(row['メッセージ'])
                        st.markdown("---")
            else:
                st.write("まだ書き込みはありません。")