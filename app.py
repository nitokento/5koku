import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import random
import time
from supabase import create_client, Client

# --- Supabase接続設定 ---
# 自身のプロジェクトのURLとキーに書き換えてください
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- 基本設定 ---
JST = timezone(timedelta(hours=+9), 'JST')
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

# --- ログイン処理 ---
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
                st.write("👤 画像なし")

        # --- ボタン共通処理用関数 ---
        def save_and_notify(action_type, result_val):
            # 5.gif の演出
            cut_in = st.empty()
            try:
                cut_in.image("5.gif", use_container_width=True)
                time.sleep(1.3)
                cut_in.empty()
            except: pass

            now = datetime.now(JST)
            
            # Supabaseへログ保存
            try:
                supabase.table("dice_logs").insert({
                    "user_name": st.session_state.user_name,
                    "item": action_type,
                    "result": str(result_val)
                }).execute()

                # チャット掲示板へシステムメッセージを流す
                icon = "🎲" if action_type == "サイコロ" else "📍"
                chat_msg = f"""
                <div style="display: flex; justify-content: center; margin: 5px 0;">
                    <div class="system-msg">
                        📢 {now.strftime("%H:%M")} | {st.session_state.user_name} が {action_type}を実行： <b>{icon} {result_val}</b>
                    </div>
                </div>
                """
                supabase.table("chat_logs").insert({
                    "user_name": "SYSTEM",
                    "message": chat_msg
                }).execute()
            except Exception as e:
                st.error(f"DBエラー: {e}")

            return result_val

        # --- ボタン配置 ---
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("🎲 サイコロを振る", use_container_width=True, type="primary"):
                res = save_and_notify("サイコロ", random.randint(1, 6))
                st.markdown(f'<p class="big-font">🎲 {res}</p>', unsafe_allow_html=True)

        with btn_col2:
            if st.button("📍 目的地を決定", use_container_width=True):
                res = save_and_notify("目的地", random.choice(STATIONS))
                st.markdown(f'<p class="station-font">📍 {res}</p>', unsafe_allow_html=True)

        st.divider()
        st.subheader("履歴一覧（最新50件）")
        try:
            response = supabase.table("dice_logs").select("*").order("created_at", desc=True).limit(50).execute()
            if response.data:
                df = pd.DataFrame(response.data)
                # 表示用に整理
                df_disp = df[['created_at', 'user_name', 'item', 'result']].rename(columns={
                    'created_at': '発生時刻', 'user_name': '開発者', 'item': '項目', 'result': '結果'
                })
                st.dataframe(df_disp, use_container_width=True, height=250)
            else:
                st.write("履歴なし")
        except:
            st.write("履歴の取得に失敗しました")

    with tab2:
        st.subheader("💬 掲示板")
        c_user = st.text_input("名前", value=st.session_state.user_name)
        c_msg = st.text_area("メッセージ", height=100)
        
        if st.button("書き込む", use_container_width=True):
            if c_user and c_msg:
                try:
                    supabase.table("chat_logs").insert({
                        "user_name": c_user,
                        "message": c_msg.replace('\n', ' ')
                    }).execute()
                    st.rerun()
                except Exception as e:
                    st.error(f"送信失敗: {e}")

        st.divider()
        chat_container = st.container(height=500) 
        with chat_container:
            try:
                chat_res = supabase.table("chat_logs").select("*").order("created_at", desc=True).limit(100).execute()
                for row in chat_res.data:
                    # 時刻の変換
                    dt = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')).astimezone(JST)
                    time_str = dt.strftime("%Y/%m/%d %H:%M")

                    if "<div" in str(row['message']):
                        st.markdown(row['message'], unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{row['user_name']}** <small style='color:gray'>{time_str}</small>", unsafe_allow_html=True)
                        st.write(row['message'])
                        st.markdown("---")
            except:
                st.write("まだ書き込みはありません。")