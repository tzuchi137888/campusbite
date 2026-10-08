# CampusBite 第一次執行指南

## 1. 準備檔案

解壓縮 `campusbite.zip`。用 VS Code 的 File → Open Folder，開啟內層 `campusbite` 資料夾，確認左側看得到 `server.py`、`engine.py`、`static` 和 `data`。

## 2. 確認 Python

VS Code → Terminal → New Terminal，輸入：

```powershell
py --version
```

需要 Python 3.10 以上。若找不到 `py`，試 `python --version`；若兩者都沒有，從 https://www.python.org/downloads/ 安裝 Python，完成後重新開啟 VS Code。本專案不需要 Jupyter、pip install 或虛擬環境。

## 3. 啟動

在看得到 `server.py` 的資料夾執行：

```powershell
py server.py
```

瀏覽器開啟 http://127.0.0.1:8000 。終端機必須保持開啟，按 Ctrl+C 才會停止。若 `py` 不可用而 `python` 可用，就改用 `python server.py`。

常見錯誤：找不到 server.py 代表終端機位置錯誤；8000 已被占用，通常代表另一個終端機已啟動本程式，先關掉前一次執行。不要直接雙擊 index.html，因為它需要 Python API。

## 4. 試操作

1. 保留 Departure time = 12:00、Next class = 13:00。
2. 按 Find my lunch，查看三間餐廳的返校時間。
3. 展開 Table estimates & queue，查看每桌預估還要多久。
4. 在 Restaurant controls 選餐廳與桌號，將 Seated people 改成 0，按 Update table。
5. 在排隊輸入框輸入 `2, 1, 4`，代表前方三組客人分別有 2、1、4 人。
6. 把課程時間改成 12:45、改走路或騎車，再計算一次。
7. Reset demo 可恢復初始桌位與排隊狀態。

介面為英文，方便錄製英文 demo。所有餐廳、路程與用餐紀錄都是示範資料；時間固定為情境快照，不會自動隨真實時間推進。

## 5. 上傳 GitHub

1. 登入 GitHub，新增 repository，名稱可用 `campusbite`。
2. 在 repository 使用 Add file → Upload files（新空 repository 也會有 uploading an existing file 入口）。
3. 將解壓縮資料夾內的檔案與子資料夾拖入，保留 `static`、`data`、`tests` 結構。不是只把 ZIP 上傳。
4. 輸入 commit 訊息，例如 `Add CampusBite local prototype`，完成提交。
5. 確認 repository 首頁直接有 README.md 和 server.py；點進 static 能看到三個前端檔案。
6. 將 repository 網址留待放在簡報最後一頁。

請勿上傳 __pycache__、.pyc、個資或 API 金鑰。這個程式沒有需要金鑰的功能。GitHub 是程式碼儲存空間；上傳後不會自動變成能執行的網站，GitHub Pages 也不能執行此 Python 後端。

## 6. 你需要理解的重點

總時間 = 去餐廳交通 + 抵達後排隊 + 用餐流程 + 回教室交通。

排隊時間不是直接加上現在的等候時間：你在移動時，餐廳原有客人也在用餐。程式會排程桌位釋出時間，再扣除你的抵達時間。排隊採先到先服務，每組一桌且桌子必須夠大。

各桌剩餘時間是從同餐點類型、同組人數、而且總用餐時間長於目前已坐時間的歷史樣本估計。這是一個小型統計預測模型，不是攝影機 AI；樣本不足時會標示 fallback。

Typical 是中位數情境；Cautious 是各組使用第 80 百分位用餐時間的情境，並不代表有 80% 機率準時。安全緩衝會用於最後的趕課判斷。

## 7. 此後要完成的工作

理解及修改程式 → 蒐集或設計合理的驗證資料 → 錄英文展示影片 → 做正文不超過 20 頁的英文簡報 → 完成競賽繳交 → 每位組員另交課程作業。

簡報最後一頁放 GitHub 與 demo 影片連結；簡報內列出組員姓名與學號；課程檔名為 `{學號}_CN_league.pdf`。依老師提供說明，期限是 2026/10/14，不接受遲交。精確截止時間及競賽細節須以正式活動頁公告確認。

目前還沒接攝影機或 UGen300，不能在報告寫成已完成。後續可讓餐廳端設備執行辨識，只傳桌位與等待估計，不上傳原始影像。本機程式只是先驗證完整使用流程。
