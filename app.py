import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import random
import time
from st_supabase_connection import SupabaseConnection

# --- 1. 初期設定 ---
st.set_page_config(page_title="レッツルーレッツ", layout="centered", page_icon="🎲")
JST = timezone(timedelta(hours=+9), 'JST')
STATIONS = ["今治", "松山", "琴平", "大歩危", "宇和島", "窪川", "高松", "高知", "徳島"]

# Supabase接続
conn = st.connection("supabase", type=SupabaseConnection)

# --- 2. スタイル定義 ---
st.markdown("""
    <style>
    .big-dice { font-size: 100px; text-align: center; margin-bottom: -20px; }
    .big-num { font-size: 50px; font-weight: bold; text-align: center; color: white; }
    .station-font { font-size: 45px !important; color: #FFEB3B; font-weight: bold; text-align: center; border: 2px solid #FFEB3B; border-radius: 15px; padding: 10px; }
    .system-msg { background-color: #262730; color: #00FF00; padding: 10px; border-radius: 15px; font-size: 0.85em; border: 1px dotted #555; text-align: center; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

st.title("澤村拓一の宇宙開発 🚀")

# セッション状態
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 3. ログイン処理 ---
if not st.session_state.user_name:
    st.info("班名と現在の駅を登録してください")
    with st.form("login_form"):
        name_input = st.text_input("名前（例：二戸班_高松駅)")
        submit = st.form_submit_button("開発センターへ入場")
        if submit:
            if name_input:
                st.session_state.user_name = name_input
                st.rerun()
            else:
                st.warning("名前を入力してください")

else:
    # サイドバー
    st.sidebar.write(f"👤 ログイン中: **{st.session_state.user_name}**")
    if st.sidebar.button("ログアウト"):
        st.session_state.user_name = ""
        st.rerun()

    tab1, tab2 = st.tabs(["🚀 開発センター", "💬 掲示板"])

    # --- 共通保存関数 ---
    def save_to_supabase(action_type, result_val):
        now = datetime.now(JST)
        # 1. ログテーブル
        conn.table("roulette_logs").insert({
            "developer": st.session_state.user_name,
            "item": action_type,
            "result": str(result_val)
        }).execute()
        # 2. システムメッセージとしてチャットへ
        icon = "🎲" if action_type == "サイコロ" else "📍"
        chat_html = f"""
        <div style="display: flex; justify-content: center; margin: 5px 0;">
            <div class="system-msg">
                📢 {now.strftime("%H:%M")} | {st.session_state.user_name} が {action_type}：<b>{icon} {result_val}</b>
            </div>
        </div>
        """
        conn.table("chat_logs").insert({"name": "SYSTEM", "message": chat_html}).execute()

    # --- Tab 1: 開発センター ---
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            try: st.image("sawamura.jpeg", use_container_width=True, caption="担当:澤村拓一")
            except: st.error("画像(sawamura.jpeg)が見つかりません")

        btn_col1, btn_col2 = st.columns(2)
        
        # --- サイコロ機能 ---
        with btn_col1:
            if st.button("🎲 サイコロを振る", use_container_width=True, type="primary"):
                cut_in = st.empty()
                try:
                    cut_in.image("sawamura.gif", use_container_width=True)
                    time.sleep(1.2)
                    cut_in.empty()
                except: pass
                
                res = random.randint(1, 6)
                dice_icons = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
                save_to_supabase("サイコロ", res)
                
                # サイコロ表示
                st.markdown(f"""
                    <div style="background-color: #262730; padding: 20px; border-radius: 20px; border: 2px solid #FF4B4B;">
                        <p class="big-dice">{dice_icons[res]}</p>
                        <p class="big-num">{res}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.toast(f"サイコロ：{res}")

        # --- 目的地機能 ---
        with btn_col2:
            if st.button("📍 目的地決定", use_container_width=True):
                station_res = random.choice(STATIONS)
                save_to_supabase("目的地", station_res)
                st.markdown(f'<p class="station-font">📍 {station_res}</p>', unsafe_allow_html=True)
                st.toast(f"目的地：{station_res}")

        st.divider()
        st.subheader("最新の履歴")
        try:
            logs = conn.table("roulette_logs").select("*").order("created_at", desc=True).limit(20).execute()
            if logs.data:
                df = pd.DataFrame(logs.data)
                df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Tokyo').dt.strftime('%H:%M:%S')
                st.dataframe(df[["created_at", "developer", "item", "result"]], use_container_width=True)
        except: st.warning("履歴の取得に失敗しました")

    # --- Tab 2: 掲示板 ---
    with tab2:
        with st.form("chat_form", clear_on_submit=True):
            c_msg = st.text_area("メッセージを入力")
            submitted = st.form_submit_button("送信")
            if submitted and c_msg:
                conn.table("chat_logs").insert({
                    "name": st.session_state.user_name,
                    "message": c_msg.replace('\n', ' ')
                }).execute()
                st.rerun()

        st.divider()
        chat_box = st.container(height=500)
        with chat_box:
            chats = conn.table("chat_logs").select("*").order("created_at", desc=True).limit(50).execute()
            if chats.data:
                for row in chats.data:
                    if "SYSTEM" in row['name']:
                        st.markdown(row['message'], unsafe_allow_html=True)
                    else:
                        ts = pd.to_datetime(row['created_at']).tz_convert('Asia/Tokyo').strftime('%m/%d %H:%M')
                        st.markdown(f"**{row['name']}** <small style='color:gray'>{ts}</small>", unsafe_allow_html=True)
                        st.info(row['message'])