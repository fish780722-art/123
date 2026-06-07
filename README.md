# 金叉死叉回測 Web App

這是一個 Streamlit 網頁版回測工具，用 yfinance 下載日 K 資料，回測「短均線金叉進場、短均線死叉出場」策略。

## 功能

- 自訂 yfinance 標的代號，例如 `2330.TW`、`0050.TW`、`AAPL`、`MSFT`、`SPY`
- 自訂短均線與長均線天數
- 自訂投入資金
- 快速日期區間：近一月、近三月、近半年、近一年、近三年、近五年、自訂日期
- 輸出日 K、均線、買賣點、資產曲線、回撤曲線
- 輸出勝率、交易次數、獲利因子、報酬金額、總報酬率、最大回撤等分析數據
- 顯示交易明細並可下載 CSV

## 專案檔案

```text
app.py                 # 主程式
requirements.txt       # Python 依賴
runtime.txt            # 雲端平台用 Python 版本
Dockerfile             # Docker 部署用
.dockerignore          # Docker 打包排除清單
render.yaml            # Render 部署設定
.streamlit/config.toml # Streamlit 設定
```

## 方式一：換電腦後在本機執行

新電腦需要先安裝 Python 3.12 或相容版本。

```powershell
cd C:\你的專案位置\PYTHON策略
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

啟動後打開：

```text
http://localhost:8501
```

如果 PowerShell 不允許啟用虛擬環境，先執行：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 方式二：用 Docker 執行

這種方式最適合「換電腦也要一致執行」，因為 Python 版本與套件都包在容器裡。

```powershell
cd C:\你的專案位置\PYTHON策略
docker build -t ma-cross-app .
docker run --rm -p 8501:8501 ma-cross-app
```

啟動後打開：

```text
http://localhost:8501
```

## 方式三：部署成真正的線上網頁

建議流程：

1. 把整個專案上傳到 GitHub repository。
2. 選一個支援 Streamlit 或 Docker 的平台部署，例如 Streamlit Community Cloud、Render、Railway、Fly.io、自己的 VPS。
3. 平台若支援 Streamlit，入口檔填：

```text
app.py
```

4. 平台若使用 Docker，直接使用本專案的 `Dockerfile`。

部署完成後會得到一個公開網址，之後換任何電腦都只要打開該網址即可使用，不需要在每台電腦安裝 Python。

### Render 快速部署

如果使用 Render：

1. GitHub repository 連到 Render。
2. 選 `New Web Service`。
3. Environment 選 `Docker`。
4. Render 會讀取本專案的 `Dockerfile`，也可以用 `render.yaml` 建立服務。
5. 部署完成後，Render 會提供一個公開網址。

## 策略假設

- 只使用日 K。
- 短均線向上穿越長均線時，以收盤價全資買進。
- 短均線向下穿越長均線時，以收盤價全數賣出。
- 不計手續費、交易稅、滑價、融資券、股利。
- 若回測區間結束時仍持倉，會用最後一根日 K 收盤價做結算。

## 注意事項

- yfinance 需要連線到 Yahoo Finance，部署環境必須允許外部網路連線。
- 若平台所在地區或網路政策擋住 Yahoo Finance，APP 會無法下載資料。
- 台股代號通常要加 `.TW` 或 `.TWO`，例如 `2330.TW`、`6488.TWO`。
