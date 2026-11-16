# 離線欣賞與操作

本頁說明如何在**沒有網路**的環境中「看」與「玩」SCW。發行版（GitHub Releases）
的說明也附有同樣內容。

## 0. 取得原始碼並進入專案目錄

`uv` 必須在**有 `pyproject.toml` 的目錄**執行。先確認你是否已經有原始碼：

```bash
ls pyproject.toml        # 有列出檔案 → 你已經在專案目錄內，直接跳到「0.5 安裝依賴」
```

若還沒取得，選下面任一種。**三種來源的前置條件不同**，請照各自的說明做：

**A. 用 git 取得**（需要網路；repo 若為 private 另需存取權）

```bash
git clone https://github.com/twobox77/scientific-computing-workbench.git
cd scientific-computing-workbench        # ← 一定要進來，這裡才有 pyproject.toml
```

- 若 repo 為 **public**：直接 clone 即可，不需登入。
- 若 repo 為 **private**：需 GitHub 帳號權限；未設定好會要你輸入帳密或
  Personal Access Token。要把 private 改成 public，見 §6。
- 若目錄 `scientific-computing-workbench/` **已存在**（例如之前 clone 過），
  **不要再跑 `git clone`**，直接 `cd` 進去就好：

```bash
cd scientific-computing-workbench
git pull                                 # 想更新到最新時
```

**B. 用 Release 的原始碼壓縮包**（必須先下載檔案到**當前目錄**）

先從本頁下方 Assets 下載 `scw-0.6.0.tar.gz` 到當前目錄，再：

```bash
ls scw-0.6.0.tar.gz                      # 確認檔案在，否則下一步會「無法 open」
tar xzf scw-0.6.0.tar.gz                 # 解開後目錄名為 scw-0.6.0/
cd scw-0.6.0                             # ← 一定要進來
```

**C. 只安裝套件**（必須先下載 `.whl`；不跑範例／文件／notebook）

```bash
uv pip install scw-0.6.0-py3-none-any.whl   # 或 uv pip install scw-0.6.0.tar.gz
```

> 只有 A、B 兩種（原始碼）能跑範例、文件站與 notebook；C 只裝套件。

## 0.5 安裝依賴（一次性）

在**上一步 `cd` 進去的專案目錄內**，連網時：

```bash
uv sync --all-extras --frozen      # 安裝全部依賴（含繪圖 / notebook / 互動）
```

完全離線時，先在可連網的機器執行 `uv sync --all-extras`，取得 uv 快取
（`uv cache dir`），再把整個 `.venv/`（或 uv 快取）複製到離線機器。
離線機器上之後的指令都要在**同一個專案目錄**內執行。

### 常見錯誤

- `No pyproject.toml found in current directory or any parent directory`
  → 你**不在專案目錄內**（例如還停在 `~`）。先 `cd` 進去再重跑：

  ```bash
  cd scientific-computing-workbench   # 或 cd scw-0.6.0（依你的來源）
  uv sync --all-extras --frozen
  ```

- `fatal: destination path 'scientific-computing-workbench' already exists and is not an empty directory`
  （中文：目的地路徑已存在，並且不是一個空目錄）
  → 目錄已存在，**不必再 clone**。直接 `cd scientific-computing-workbench`；
  要更新就 `git pull`。想重新 clone 請先把舊目錄改名或刪除。

- `tar (child): scw-0.6.0.tar.gz: Cannot open: No such file or directory`
  （中文：無法 open：沒有此一檔案或目錄）
  → 你還沒把壓縮包**下載到當前目錄**。先從 Release Assets 下載，或改用 git（A）。

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

## 5. 解除安裝

依你要清掉到什麼程度，分三層。**由內而外**做最乾淨。

### 5.1 只移除本專案的虛擬環境（最常見）

專案的 `.venv/` 就在專案目錄內，直接刪除即可（不會動到系統或其他專案）：

```bash
rm -rf .venv/            # 在專案目錄內執行
```

### 5.2 清掉 uv 下載的快取與受管 Python

uv 會把套件快取在 `~/.cache/uv`、下載的 Python 放在 `~/.local/share/uv/python`。
若不再用 uv、想釋放空間：

```bash
uv cache clean                   # 清空 uv 快取
uv cache prune                   # 或只清掉不再使用的項目（較溫和）
uv python uninstall <版本>       # 移除某個 uv 受管 Python，例如 uv python uninstall 3.12
uv python list                   # 先列出已安裝的版本
rm -rf "$(uv python dir)"        # 或一次移除所有 uv 受管 Python
rm -rf "$(uv tool dir)"          # 移除 uv 安裝的 CLI 工具（若沒用可略）
```

> `uv cache dir`、`uv python dir`、`uv tool dir` 可印出實際路徑，先看再刪較安心。

### 5.3 完全移除 uv 本身

uv **沒有** `uv self uninstall` 子命令（`uv self` 只有 `update` / `version`），
需手動刪除執行檔。依[官方安裝文件](https://docs.astral.sh/uv/getting-started/installation/)
的解除安裝步驟：

```bash
# 1)（可選）先清掉 uv 儲存的資料
uv cache clean
rm -rf "$(uv python dir)"
rm -rf "$(uv tool dir)"

# 2) 刪除 uv / uvx 執行檔（路徑依你的安裝方式而定）
rm -f ~/.local/bin/uv ~/.local/bin/uvx          # 官方 standalone 安裝器的預設位置
# 0.5.0 之前裝在：rm -f ~/.cargo/bin/uv ~/.cargo/bin/uvx
# 若用系統套件管理器安裝（例如 apt / Homebrew），請用對應方式移除，例如：
#   sudo apt remove uv        # Debian/Ubuntu（視安裝來源）
#   brew uninstall uv         # macOS（Homebrew）
```

用 `which uv uvx` 可先確認實際路徑，再刪對應檔案。本沙盒環境的 uv 在
`/usr/bin/uv`（系統層級安裝），移除方式與上述 standalone 安裝不同。

### 5.4 移除整個專案

```bash
cd ..
rm -rf scientific-computing-workbench/     # 或 scw-<version>/
```

若只是想解除安裝**套件**（不是原始碼）：`uv pip uninstall scw`。

## 6. 把 repo 改成公開（private → public）

公開後 clone、下載 Release 圖片與壓縮包都不再需要登入，分享與教學更方便。

**在 GitHub 網頁操作（最簡單、必定可行）**：

1. 開 `https://github.com/twobox77/scientific-computing-workbench/settings`
2. 捲到最下方 **Danger Zone** → **Change repository visibility** → **Make public**
3. 依指示輸入 repo 名稱確認

**用 CLI**（需要 token 具備 `administration:write` 權限）：

```bash
gh repo edit twobox77/scientific-computing-workbench \
  --visibility public --accept-visibility-change-consequences
```

> 注意：fine-grained token 若沒有 `administration:write`，上述指令會回
> `403 Resource not accessible`。此時請改用網頁操作，或換一支具該權限的 token。
> 公開前建議先確認 repo 內沒有金鑰、密碼或私密資料。
