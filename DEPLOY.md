# 部署成公開網址

目標：讓任何電腦、手機、平板只要打開網址就能使用，不需要安裝 Python。

## 推薦方案：Streamlit Community Cloud

這個專案是 Streamlit app，最短部署路線是 Streamlit Community Cloud。

### 需要準備

- GitHub 帳號
- Streamlit Community Cloud 帳號
- 一個 GitHub repository，內容包含：
  - `app.py`
  - `requirements.txt`
  - `.streamlit/config.toml`
  - `runtime.txt`

### 步驟

1. 把本專案上傳到 GitHub repository。
2. 打開 Streamlit Community Cloud：

```text
https://share.streamlit.io/
```

3. 使用 GitHub 登入。
4. 選 `New app`。
5. Repository 選你的 GitHub repository。
6. Branch 選 `main`。
7. Main file path 填：

```text
app.py
```

8. 按 Deploy。

部署完成後會得到類似下面的網址：

```text
https://你的-app-name.streamlit.app
```

之後任何電腦只要打開這個網址就能使用。

## 備用方案：Render

Render 適合用 Docker 部署，本專案已包含：

- `Dockerfile`
- `render.yaml`

### 步驟

1. 把本專案上傳到 GitHub repository。
2. 打開 Render：

```text
https://render.com/
```

3. 選 `New Web Service`。
4. 連接 GitHub repository。
5. Environment 選 `Docker`。
6. 部署完成後，Render 會提供公開網址。

## 重要注意

- yfinance 需要連線 Yahoo Finance，部署平台必須允許外部網路。
- 免費平台可能會休眠，第一次打開可能需要等幾十秒。
- GitHub Pages 不能直接部署 Streamlit，因為 Streamlit 需要 Python server。

