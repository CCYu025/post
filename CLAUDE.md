# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

**知識刊** — 部署於 GitHub Pages 的單頁雜誌式首頁，聚合兩個定期更新的內容主題：
- `news/` — 每日 AI 情報日刊
- `summary/` — 長篇主題深度摘要

## 常用指令

```bash
# 重新生成 manifest.json（新增內容後必須執行）
python scripts/build_manifest.py

# 本機預覽（必須用伺服器，直接開 file:// 會因 fetch 跨域失敗）
python -m http.server 8765
# 開啟 http://localhost:8765
```

## 架構說明

### 自動更新流程

```
新增 news/ 或 summary/ 資料夾
  → git push
    → GitHub Actions (.github/workflows/update-manifest.yml)
      → python scripts/build_manifest.py
        → manifest.json 更新並 commit 回 main [skip ci]
          → GitHub Pages 重新部署
```

### manifest.json 結構

```json
{
  "news": [
    { "date": "YYYY-MM-DD", "path": "news/.../xxx.html", "title": "..." }
  ],
  "summary": [
    { "date": "YYYY-MM-DD", "path": "summary/.../xxx.html", "title": "...", "hero": "summary/.../xxx_hero_editorial.png" }
  ]
}
```

`index.html` 在執行期用 `fetch('manifest.json')` 讀取此檔案渲染頁面，**不做靜態生成**。

### 內容資料夾命名規則

| 類型 | 資料夾格式 | 主 HTML 檔命名 |
|---|---|---|
| news | `news/YYYY-MM-DD/` | `YYYY-MM-DD.html` |
| summary | `summary/YYYYMMDD_作者_主題_magazine_brief/` | `*_magazine_brief.html` |

`build_manifest.py` 依資料夾名稱倒序排列（最新在前），從 `<title>` tag 擷取標題，並尋找名稱含 `hero` 的 `.png` 作為封面圖。

### index.html 設計系統

- **字型三層架構**：`Playfair Display`（大標題）、`Libre Bodoni`（卡片標題）、`JetBrains Mono`（所有標籤/日期/按鈕）
- **色彩系統**：左欄 news 暗色 `--n-*` token；右欄 summary 暖色 `--s-*` token
- **動畫 easing**：`cubic-bezier(.16,1,.3,1)`（Expo Out）貫穿全站
- **閱讀器**：點擊卡片觸發 `.reader` overlay，以 `<iframe>` 嵌入 HTML 全螢幕顯示

## 新增內容的正確步驟

1. 依命名規則建立資料夾並放入 HTML（及 hero 圖）
2. 執行 `python scripts/build_manifest.py` 確認輸出正確
3. `git add` → `git commit` → `git push`
4. GitHub Actions 自動更新 `manifest.json` 並觸發 Pages 重新部署

## GitHub Actions 設定需求

Repo 需開啟：**Settings → Actions → General → Workflow permissions → Read and write permissions**，Actions 才能寫回 `manifest.json`。
