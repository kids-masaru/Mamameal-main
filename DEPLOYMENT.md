# Streamlit Cloudデプロイガイド

## 準備

### 1. GitHubリポジトリにプッシュ

```bash
git add .
git commit -m "Fix: Streamlit Cloud deployment configuration"
git push origin main
```

### 2. 必要なファイルの確認

以下のファイルが正しく配置されているか確認:

- ✅ `streamlit_app.py` - メインアプリケーション
- ✅ `requirements.txt` - Python依存関係
- ✅ `packages.txt` - システムレベル依存関係 (poppler-utils)
- ✅ `.streamlit/config.toml` - Streamlit設定
- ✅ `api/` フォルダ - バックエンドロジック
- ✅ `api/assets/` フォルダ - マスタデータとテンプレート

## Streamlit Cloudでのデプロイ手順

### 1. Streamlit Cloudにアクセス

1. [https://share.streamlit.io/](https://share.streamlit.io/) にアクセス
2. GitHubアカウントでログイン

### 2. 新しいアプリをデプロイ

1. 「New app」ボタンをクリック
2. 以下の情報を入力:
   - **Repository**: `mamameal-next` を選択
   - **Branch**: `main` (またはデプロイしたいブランチ)
   - **Main file path**: `streamlit_app.py`
   - **App URL**: 任意のURL (例: `mamameal-app`)

### 3. Secrets（機密情報）の設定

⚠️ **重要**: API Keyを設定しないとアプリは動作しません

1. デプロイ画面またはアプリ管理画面で「Settings」→「Secrets」に移動
2. 以下のTOML形式でAPI Keyを入力:

```toml
GOOGLE_API_KEY = "YOUR_ACTUAL_GOOGLE_API_KEY_HERE"
```

3. 「Save」をクリック

### 4. デプロイ

1. 「Deploy!」ボタンをクリック
2. ビルドログを確認（数分かかります）
3. デプロイが完了したら、アプリのURLにアクセス

## トラブルシューティング

### エラー: `ModuleNotFoundError: google.generativeai`

**原因**: `requirements.txt`が正しく設定されていない

**解決策**:
1. `requirements.txt`に以下が含まれているか確認:
   ```
   streamlit==1.40.0
   google-generativeai==0.8.3
   openpyxl==3.1.2
   pandas==2.2.0
   python-dotenv==1.0.0
   pdfplumber==0.10.3
   pdfminer.six==20221105
   ```
2. GitHubにプッシュ後、Streamlit Cloudで「Reboot app」

### エラー: `API Key: 未設定`

**原因**: Secretsが設定されていない

**解決策**:
1. Streamlit Cloud管理画面で「Settings」→「Secrets」を開く
2. `GOOGLE_API_KEY = "your_key"` を追加
3. アプリを再起動

### ファイルアップロードエラー

**原因**: ファイルサイズ制限（デフォルト200MB）

**現在の設定**: `.streamlit/config.toml`で200MBに設定済み

**さらに増やす場合**:
```toml
[server]
maxUploadSize = 500
```

### PDFの処理が遅い/タイムアウト

**原因**: Gemini APIの応答時間が長い、または無料プランの制限

**解決策**:
1. より高速なモデルを使用: `gemini-2.5-flash` (サイドバーで選択可能)
2. Gemini APIの課金プランを確認
3. Streamlit Cloudのタイムアウト設定を確認

## マスタデータの管理

### 初回デプロイ時

1. アプリにアクセス
2. 「マスタ管理」タブを開く
3. 以下のCSVファイルをアップロード:
   - 商品マスタ一覧.csv
   - 得意先マスタ一覧.csv

### 注意事項

- ⚠️ Streamlit Cloudでは、アプリを再起動すると**アップロードしたマスタデータは消えます**
- 📌 マスタデータは毎回アップロードするか、GitHubリポジトリの`api/assets/`に含める必要があります

### マスタデータをGitHubに含める方法

1. ローカルの`api/assets/`フォルダに以下を配置:
   - `商品マスタ一覧_YYYYMMDD.csv`
   - `得意先マスタ一覧_YYYYMMDD.csv`
   - `template.xlsm`
   - `nouhinsyo.xlsx`
   - `seal.xlsx`

2. GitHubにプッシュ:
   ```bash
   git add api/assets/
   git commit -m "Add master data files"
   git push origin main
   ```

3. Streamlit Cloudで自動的に再デプロイ

## アプリの更新

コードを変更した後:

```bash
git add .
git commit -m "Update: 変更内容の説明"
git push origin main
```

Streamlit Cloudが自動的に変更を検知して再デプロイします。

## リソース

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
