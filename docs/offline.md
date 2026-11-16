# 離線欣賞與操作

本頁說明如何在**沒有網路**的環境中「看」與「玩」SCW。發行版（GitHub Releases）
的說明也附有同樣內容。

## 0. 準備環境（一次性）

需要 [`uv`](https://docs.astral.sh/uv/)。連網時：

```bash
uv sync --all-extras --frozen      # 安裝全部依賴（含繪圖 / notebook / 互動）
```

完全離線時，先在可連網的機器執行 `uv sync --all-extras`，取得 uv 快取
（`uv cache dir`），再把整個 `.venv/`（或 uv 快取）複製到離線機器。

## 1. 純文字：跑範例、看數值

```bash
uv run python examples/09_manifolds.py        # 0.6 流形：切空間、metric、flat/sharp
uv run python examples/08_visualization.py    # 繪圖範例，輸出 PNG 到 scw_plots/
uv run python examples/06_decompositions.py   # 0.4 分解：LU / QR / SVD / Cholesky / eigh
```

## 2. 看文件網站（離線）

```bash
uv run mkdocs serve -a 127.0.0.1:8000     # 瀏覽器開 http://127.0.0.1:8000
```

只想產生靜態站（可直接用瀏覽器開檔）：

```bash
uv run mkdocs build --strict              # 產出 site/，開 site/index.html
```

重點頁面：**Gallery**、Mathematics → Manifolds / Visualization / Numerical methods。

## 3. 動手操作（Jupyter）

```bash
uv run jupyter lab
```

- `notebooks/01_scw_quickstart.ipynb` — 基礎導覽。
- `notebooks/02_manifolds.ipynb` — 0.6 靜態教學（已內嵌圖，讀即可）。
- `notebooks/03_manifolds_interactive.ipynb` — 3D 圖**可拖曳旋轉**，附滑桿
  （需 `interactive` extra）。

互動版操作：3D 圖上**左鍵拖曳可旋轉、滾輪縮放、右鍵拖曳可平移**；拖動
`theta` / `phi` 滑桿可即時移動球面上的點，標題顯示 `|e_theta|`、`|e_phi|`，
可觀察 `|e_phi| = r sinθ` 在赤道最大、越靠兩極越小。

## 4. 離線欣賞圖片（不開 notebook）

```bash
uv sync --extra visualization
uv run python scripts/build_gallery.py     # 產生 docs/assets/gallery/*.png
```

再用系統的圖片檢視器開啟 `docs/assets/gallery/` 內的 PNG。
