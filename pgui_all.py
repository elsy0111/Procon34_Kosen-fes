import streamlit as st
from copy import deepcopy as dc
from datetime import datetime
from PIL import Image
import vis
import lib
import threading
import time
# import simple_shortest
# import simple_make_around
import match_
# import clear_
import requests as rq
import json
# from random import randint

p = 0

# url = "http://172.28.0.1:8080/"
url = "http://127.0.0.1:3000/"
# api_token = "ariakee5d5af0c7ad9401b6449eda7ee0e8730f24f77d5b6da2ac615aca3c1f4"
api_token = "A"
# header = {"procon-token" : api_token}
is_accepted = [False for _ in range(201)]

header = {"Content-Type" : "application/json",
        "procon-token" : api_token}

def get_matches():
    """
    試合一覧取得API
    参加する試合の一覧を取得するAPIです

    Require : token
    Response { [
               int    id,                 試合ID                  (0 <= id)
               int    turns,              試合の総ターン数        (30 <= turns <= 200)
               int    turnSeconds,        １ターン当たりの秒数    (3 <= turnSeconds <= 15)

               bonus  {                   得点の係数
               int    wall: 10,           城壁係数        (const 10)
               int    territory : 30,     陣地係数        (const 30)
               int    castle : 100        城係数          (const 100)
                      }

               board  { 
               int    width,              横              (11 <= width <= 25)
               int    height,             縦              (11 <= height <= 25)
               int    mason,              職人の数        (2 <= mason <= 6)
               Arrint structures,         構造物          (0 : なし, 1 : 池, 2 : 城)
               Arrint masons              職人            (0 < masons: 自チーム, 0 > masons: 相手チーム)
                      }

               string opponent,           相手のチーム名
               bool   first               自チームが先手かどうか
               ] }
    """
    r = rq.get(url + "matches", headers = header)
    response = r.json()
    status_code = r.status_code
    print("get_match status_code :", r.status_code)
    return response["matches"], status_code

def get_matching(id : int):
    """
     res = get_matches()
     ID = res['id']
     cout(res)
     print(ID)

     N = res['board']['mason']
     print(N)

     試合状態取得API
     試合の状態を取得するAPIです

     Require : token, id
     Response { 
                int    id,                 試合ID                  (0 <= id)
                int    turn,               どのターンのボードか    (0 <= turn <= turns)

                board  {
                Arrint walls,              城壁の情報      (0 : なし, 1 : 自チーム, 2 : 相手チーム の城壁)
                Arrint territories,        陣地の情報      (0 : 中立, 1 : 自チーム, 2 : 相手チーム, 3 : 両チーム の陣地)
                int    width,              横              (11 <= width <= 25)
                int    height,             縦              (11 <= height <= 25)
                int    mason,              職人の数        (2 <= mason <= 6)
                Arrint structures,         構造物          (0 : なし, 1 : 池, 2 : 城)
                Arrint masons              職人            (0 < masons: 自チーム, 0 > masons: 相手チーム)
                       }

                logs { [
                int    turn,               実施ターン          (1 <= turn <= turn)
                       actions { [
                       bool    succeeded,  行動が成功したか    (true : 成功, false : 失敗)
                       int     type,       行動タイプ          (0 : 滞在,  1 : 移動　, 2 : 建築, 3 : 解体)
                       int     dir         方向(左上を(1, 1))  (1 : 左上,  2 : 上　　, 3 : 右上, 
                               ] }                              8 : 左　,  0 : 無方向, 4 : 右　, 
                       ] }                                      7 : 左下,  6 : 下　　, 5 : 右下)

               }
    """
    r = rq.get(url + "matches/" + str(id), headers = header)
    response = r.json()
    status_code = r.status_code
    # print("get_matching   status_code :", r.status_code)

    r_ = get_matches_id(id)
    response["first"] = r_["first"]
    response["opponent"] = r_["opponent"]
    response["turns"] = r_["turns"]
    response["turnSeconds"] = r_["turnSeconds"]

    return response, status_code

def post_actions(id : int, turn : int, actions_arr : list):

    """
    行動計画更新API
    現在のターンに対する行動計画を更新するAPIです

    Require : token, id
    Response  { 
               int    turn,        行動を計画するターン    (0 <= turn(次のターンのみ) <= 200)
               actions { [
               int     type,       行動タイプ          (0 : 滞在,  1 : 移動　, 2 : 建築, 3 : 解体)
               int     dir         方向(左上を(1, 1))  (1 : 左上,  2 : 上　　, 3 : 右上, 
                      ] }                               8 : 左　,  0 : 無方向, 4 : 右　, 
              }                                         7 : 左下,  6 : 下　　, 5 : 右下)
    """

    try:
        actions_arr = eval(actions_arr)

        actions = {
                'turn' : turn, 
                'actions' : 
                    list2json(actions_arr)
            }

    except:
        raise()

    r = rq.post(url + "matches/" + str(id), headers = header, data = json.dumps(actions))
    try:
        response = r.json()
        print(response)
    except:
        raise()
    status_code = r.status_code
    
    return actions, response, status_code

def list2json(actions : list):
    j = []
    for action in actions:
        j.append({
                'type' : action[0], 
                'dir'  : action[1]
                })
    return j

def get_matches_id(id : int):
    r = rq.get(url + "matches", headers = header)
    response = r.json()
    for match in response["matches"]:
        if match.get("id") == int(id):
            # status_code = r.status_code
            # print("get_matches_id status_code :", status_code)
            return match
    return -1

def simple_get_matches(res : json):
    Res = dc(res)

    structures_arr = Res["board"]["structures"]
    masons_arr = Res["board"]["masons"]

    Res["board"]["structures"] = []
    Res["board"]["masons"] = []
    for i in structures_arr:
        Res["board"]["structures"].append(str(i))
    for i in masons_arr:
        Res["board"]["masons"].append(str(i))

    return Res

def simple_get_matching(res : json):
    Res = dc(res)
    del Res["logs"]

    structures_arr = Res["board"]["structures"]
    masons_arr = Res["board"]["masons"]
    walls_arr = Res["board"]["walls"]
    territories_arr = Res["board"]["territories"]

    Res["board"]["structures"] = []
    Res["board"]["masons"] = []
    Res["board"]["walls"] = []
    Res["board"]["territories"] = []
    for i in structures_arr:
        Res["board"]["structures"].append(str(i))
    for i in masons_arr:
        Res["board"]["masons"].append(str(i))
    for i in walls_arr:
        Res["board"]["walls"].append(str(i))
    for i in territories_arr:
        Res["board"]["territories"].append(str(i))

    return Res

#=====================================================
    st.session_state.Autoreload_4 = False
    match_.refresh_game()
    # sleep(5)
    is_accepted = [0 for _ in range(201)]
    print("\n// Get_Matches ==================")
    st.session_state.dt_now1 = datetime.now()
    st.session_state.res1, st.session_state.status_code1 = get_matches()

    st.session_state.is_first = st.session_state.res1[p]["first"]
    st.session_state.size = st.session_state.res1[p]["board"]["width"]
    st.session_state.mason = st.session_state.res1[p]["board"]["mason"]
    st.session_state.turnSeconds = st.session_state.res1[p]["turnSeconds"]
    st.session_state.opponent = st.session_state.res1[p]["opponent"]
    st.session_state.turns = st.session_state.res1[p]["turns"]
    st.session_state.ID = st.session_state.res1[p]["id"]

    lib.convert_before_match(st.session_state.res1[p]["board"]["masons"], st.session_state.res1[p]["board"]["structures"])
    vis.main()
    print("\n   Get_Matches ==================//")
    st.session_state.Autoreload_4 = True
# except:
#     None

    # st.markdown(f"""
    #             ## ID : {st.session_state.ID}
    # """)

    # Init ==================================================================

    class Worker(threading.Thread):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.res4 = None
            self.status_code4 = None
            self.turn4 = None
            self.dt_now4 = None
            self.ID = 10
            self.vis_struct_mason = Image.open("./img/None.png")
            self.vis_wall_territories = Image.open("./img/None.png")
            self.should_stop = threading.Event()
            self.scoreA = -1
            self.scoreB = -1
            
        def run(self):
            while not self.should_stop.wait(0):
                time.sleep(0.3)
                print("\n// Visualizer ==================")
                self.c = False
                try:
                    print("trying...")
                    print(self.ID)
                    self.res4, self.status_code4 = get_matching(self.ID)
                    self.c = True
                    print("success")
                except:
                    print("get_fault")
                    self.status_code4 = "400 get fault"
                    self.turn4 = None
                if self.c:
                    if 1:
                        self.turn4 = self.res4["turn"]
                        lib.convert(self.res4["board"]["masons"], self.res4["board"]["structures"],self.res4["board"]["walls"],self.res4["board"]["territories"],self.res4["first"])
                        vis.main()
                        self.scoreA, self.scoreB = lib.calculate()

                        self.vis_struct_mason = Image.open("./Field_Data/visualized_struct_masons.png")
                        self.vis_wall_territories = Image.open("./Field_Data/visualized_wall_territories.png")

                        self.dt_now4 = datetime.now()
                    # except:
                    #     time.sleep(.1)
                
    Switch_Auto_Reload = st.button("Auto Reload")
    if Switch_Auto_Reload:
        print("Auto Reload", st.session_state.Autoreload_4,"->",not st.session_state.Autoreload_4)
        st.session_state.Autoreload_4 = not st.session_state.Autoreload_4
        if st.session_state.Autoreload_4:
            worker = st.session_state.worker = Worker(daemon=True)
            worker.start()
            st.rerun()
        else:
            try:
                worker.should_stop.set()
                # 終了まで待つ
                worker.join()
                worker = st.session_state.worker = None
                st.rerun()
            except:
                None



    # Input / Output ========================================================

    st.markdown(f"""
                ## ID : {st.session_state.ID}
                """)

    # worker の状態を表示する部分
    if worker is None:
        st.markdown('No worker running.')
    else:
        st.markdown('worker running.')
        placeholder1 = st.empty()
        placeholder4 = st.empty()
        placeholder5 = st.empty()
        while worker.is_alive():
            st.session_state.turn_now = worker.turn4
            placeholder4.image(worker.vis_struct_mason, caption='Struct and Masons')
            placeholder5.image(worker.vis_wall_territories, caption='Walls and Territories')
            placeholder1.markdown(f"""
                        ## Status Code : {worker.status_code4}
                        ## Received Time : {worker.dt_now4}
                        ## Turn : {st.session_state.turn_now} / {st.session_state.turns}
                        ## Score : {worker.scoreA} vs {worker.scoreB}
            """)
            time.sleep(.1)


id2action =  [[1,1],
              [1,2],
              [1,3],
              [1,4],
              [1,5],
              [1,6],
              [1,7],
              [1,8],

              [2,2],
              [2,4],
              [2,6],
              [2,8],

              [3,2],
              [3,4],
              [3,6],
              [3,8], 
              [0,0]]


pages = dict(
    page1="Get_Matches",
    # page4="Visualizer",
)

# 選択肢を縦に表示
page_id = st.sidebar.radio(
    "Change",
    [
        "page1",
        # "page4",
    ],
    format_func=lambda page_id: pages[page_id],
)

# 選択に応じてページを表示
if page_id == "page1":
    page1()
# elif page_id == "page4":
#     page4()
