# DEP CM Factor Simulator

## English

DEP CM Factor Simulator is a Python GUI application for visualizing the frequency dependence of the real part of the Clausius-Mossotti factor, `Re[K]`, in dielectrophoresis (DEP).

The application is designed for educational, simulation, and parameter-comparison purposes. Users can change physical and electrical parameters, compare multiple conditions, save graphs, and reproduce a reference DEP spectrum from the literature.

## 日本語

DEP CM Factor Simulator は、誘電泳動（DEP: Dielectrophoresis）における Clausius-Mossotti 因子の実部 `Re[K]` と周波数の関係を可視化するための Python GUI アプリケーションです。

教育用途、シミュレーション、パラメータ比較を目的としており、物理・電気的パラメータを変更しながら複数条件の比較、グラフ保存、参考文献に掲載されたDEPスペクトルの再現を行うことができます。

---

# Features / 機能

## English

- Calculate the real part of the CM factor, `Re[K]`
- Plot `Re[K]` against frequency `f [Hz]`
- Provide a GUI for parameter input
- Provide a GUI for graph visualization
- Overlay multiple simulation results on the same graph
- Open simulation results in a new graph window
- Clear the displayed graph
- Save graphs as PNG files
- Show error messages for invalid input values
- Manage the Python environment and dependencies using `uv`
- Reproduce the frequency dependence of the CM factor shown in reference Figure 1(a)–(h)
- Run the reference Figure 1(a)–(h) reproduction directly from the GUI
- Save and load parameter conditions as CSV files
- Add custom graph labels for each simulation condition

## 日本語

- CM因子の実部 `Re[K]` を計算
- 周波数 `f [Hz]` に対する `Re[K]` をグラフ表示
- パラメータ入力用GUI
- グラフ表示用GUI
- 複数条件の重ね描き
- 新しいWindowでのグラフ表示
- グラフクリア
- PNG保存
- 不正な入力値に対するエラー表示
- `uv` による環境構築・依存関係管理
- 参考文献 Figure 1(a)〜(h) に対応するCM因子の周波数依存性の再現
- GUIから参考文献 Figure 1(a)〜(h) の再現グラフを直接生成
- パラメータ条件のCSV保存・読み込み
- シミュレーション条件ごとの任意グラフラベル入力

---

# Requirements / 必要環境

## English

- macOS
- Python 3.12
- uv

## 日本語

- macOS
- Python 3.12
- uv

---

# Setup / セットアップ

## English

Install dependencies with `uv`.

    uv sync

## 日本語

`uv` を用いて依存関係を同期します。

    uv sync

---

# Run / 実行方法

## English

Start the GUI application.

    uv run dep-cm-sim

## 日本語

GUIアプリケーションは以下で起動できます。

    uv run dep-cm-sim

---

# Usage / 使い方

## English

1. Start the application.
2. Enter values in the parameter input window.
3. Click `現在のグラフに重ねる` to plot the result on the current graph window.
4. The graph window shows the relationship between `Re[K]` and frequency.
5. Change parameters and click `現在のグラフに重ねる` again to overlay another curve.
6. Click `新しいWindowで表示` to open the result in a new graph window.
7. Click `PNG保存` in the graph window to save the graph as a PNG file.
8. Click `グラフをクリア` to remove the displayed curves.
9. Enter a custom graph label in the `グラフラベル` field if needed.
10. If the graph label is empty, the application automatically uses `sigma_s=... S/m` as the legend label.
11. Click `CSV保存` to save the current parameter condition as a CSV file.
12. Click `CSV読み込み` to restore a saved parameter condition from a CSV file.
13. Click `論文図(a)〜(h)を再現` to generate the reference Figure 1(a)–(h) reproduction graph directly from the GUI.

## 日本語

1. アプリを起動する
2. パラメータ入力画面で値を入力する
3. 「現在のグラフに重ねる」を押す
4. グラフWindowに `Re[K]` と周波数の関係が表示される
5. 条件を変更して再度「現在のグラフに重ねる」を押すと、同じグラフ上に曲線が追加される
6. 「新しいWindowで表示」を押すと、別Windowにグラフが表示される
7. グラフWindowの「PNG保存」で画像を保存できる
8. 「グラフをクリア」で表示中の曲線を削除できる
9. 必要に応じて「グラフラベル」に条件名を入力する
10. 「グラフラベル」が空欄の場合は、従来通り `sigma_s=... S/m` が凡例に表示される
11. 「CSV保存」で現在のパラメータ条件をCSVファイルとして保存できる
12. 「CSV読み込み」で保存済みのCSVからパラメータ条件を復元できる
13. 「論文図(a)〜(h)を再現」を押すと、参考文献 Figure 1(a)〜(h) に対応する8条件のグラフをGUIから直接生成できる

---

# Parameters / パラメータ

| Parameter | Symbol | Unit | Default | Description |
|---|---:|---:|---:|---|
| Graph label / グラフラベル | `label` | - | empty | Custom legend label. If empty, `sigma_s=... S/m` is used automatically. |
| Membrane capacitance / 細胞膜容量 | `C_m` | F/m^2 | 0.015 | Cell membrane capacitance |
| Cell radius / 細胞半径 | `r` | m | 6.7e-6 | Cell radius |
| Cytoplasm relative permittivity / 細胞質の比誘電率 | `epsilon_c / epsilon_0` | - | 60 | Relative permittivity of cytoplasm |
| Solution relative permittivity / 溶液の比誘電率 | `epsilon_s / epsilon_0` | - | 80 | Relative permittivity of solution |
| Cytoplasm conductivity / 細胞質導電率 | `sigma_c` | S/m | 0.5 | Conductivity of cytoplasm |
| Solution conductivity / 溶液導電率 | `sigma_s` | S/m | 2.0e-4 | Conductivity of solution |
| Minimum frequency / 最小周波数 | `f_min` | Hz | 1 | Lower bound of frequency |
| Maximum frequency / 最大周波数 | `f_max` | Hz | 1.0e10 | Upper bound of frequency |
| Number of points / 計算点数 | `N` | points | 1000 | Number of log-spaced frequency points |

---

# Cell Parameter Templates / 細胞パラメータテンプレート

## English

The application provides cell parameter templates for parameters that are relatively cell-specific:

    membrane_capacitance
    radius_m
    eps_c_relative
    sigma_c

A default template, `reference_cell`, is available. Users can also save their own templates from the GUI.

User-defined templates are saved locally to:

    templates/user_cell_templates.json

This file is excluded from Git tracking so that local experimental or user-specific settings are not committed accidentally.

Cell templates do not include solution or simulation settings such as:

    sigma_s
    eps_s_relative
    f_min
    f_max
    num_points
    graph_label

These values are treated as experimental or plotting conditions rather than cell-specific properties.

## 日本語

本アプリケーションでは、細胞ごとに比較的一定になりやすい以下のパラメータを、細胞テンプレートとして管理できます。

    membrane_capacitance
    radius_m
    eps_c_relative
    sigma_c

デフォルトテンプレートとして `reference_cell` が用意されています。また、GUI上からユーザー自身のテンプレートを保存できます。

ユーザー定義テンプレートはローカルに以下のファイルとして保存されます。

    templates/user_cell_templates.json

このファイルはGit管理対象外にしているため、ローカルの実験条件やユーザー固有設定を誤ってコミットしにくくしています。

細胞テンプレートには、以下のような溶液条件・シミュレーション条件は含めません。

    sigma_s
    eps_s_relative
    f_min
    f_max
    num_points
    graph_label

これらは細胞固有値ではなく、実験条件または描画条件として扱います。


---

# CSV Save and Load / CSV保存・読み込み

## English

The application can save the current parameter condition as a CSV file and load it later.

The saved CSV includes both numerical parameters and the custom graph label:

    graph_label
    membrane_capacitance
    radius_m
    eps_c_relative
    eps_s_relative
    sigma_c
    sigma_s
    f_min
    f_max
    num_points

If `graph_label` is empty, the graph legend is automatically generated from `sigma_s`.

Example:

    sigma_s=2.00e-04 S/m

If `graph_label` is provided, the entered label is used directly in the graph legend.

Example:

    condition_A

## 日本語

本アプリケーションでは、現在のパラメータ条件をCSVファイルとして保存し、後から読み込むことができます。

保存されるCSVには、数値パラメータに加えて、任意のグラフラベルも含まれます。

    graph_label
    membrane_capacitance
    radius_m
    eps_c_relative
    eps_s_relative
    sigma_c
    sigma_s
    f_min
    f_max
    num_points

`graph_label` が空欄の場合は、従来通り `sigma_s` から凡例が自動生成されます。

例:

    sigma_s=2.00e-04 S/m

`graph_label` が入力されている場合は、その文字列がグラフ凡例にそのまま使用されます。

例:

    condition_A

---

# Optimal Frequency Display / 最適周波数表示

## English

When exactly two curves are displayed in the graph window, the application can calculate and display the frequency where the two curves differ the most.

The optimal frequency is defined as the frequency that maximizes:

    |Re[K]_1 - Re[K]_2|

The result is shown on the graph as:

- a vertical dashed line at the optimal frequency
- an annotation showing `f_opt` and `|ΔRe[K]|`

This feature is intended to support visual comparison of two DEP response curves.

## 日本語

グラフWindow上に曲線が2本だけ表示されている場合、2曲線の差が最大となる周波数を計算し、グラフ上に表示できます。

本アプリケーションでは、最適周波数を以下が最大となる周波数として定義しています。

    |Re[K]_1 - Re[K]_2|

結果はグラフ上に以下の形で表示されます。

- 最適周波数位置の破線
- `f_opt` と `|ΔRe[K]|` を示す注釈

この機能は、2つのDEP応答曲線を比較するための補助機能です。


---

# Model / 計算モデル

## English

The application calculates the real part of the Clausius-Mossotti factor, `Re[K]`, using the frequency-dependent model implemented in `src/dep_cm_sim/equations.py`.

The angular frequency is defined as:

    omega = 2 pi f

The time constants are defined as:

    tau_ms = C_m r / sigma_s
    tau_mc = C_m r / sigma_c
    tau_s = epsilon_s / sigma_s
    tau_c = epsilon_c / sigma_c

The permittivities are calculated as:

    epsilon_s = epsilon_s_relative * epsilon_0
    epsilon_c = epsilon_c_relative * epsilon_0

The application plots the real part of the CM factor:

    Re[K]

## 日本語

本アプリケーションでは、`src/dep_cm_sim/equations.py` に実装された周波数依存モデルを用いて、Clausius-Mossotti 因子の実部 `Re[K]` を計算します。

角周波数は以下で定義します。

    omega = 2 pi f

各時定数は以下で定義します。

    tau_ms = C_m r / sigma_s
    tau_mc = C_m r / sigma_c
    tau_s = epsilon_s / sigma_s
    tau_c = epsilon_c / sigma_c

誘電率は以下で計算します。

    epsilon_s = epsilon_s_relative * epsilon_0
    epsilon_c = epsilon_c_relative * epsilon_0

本アプリケーションでは、CM因子の実部をグラフ化します。

    Re[K]

---

# Reproducing Reference Figure 1(a)–(h) / 参考文献 Figure 1(a)〜(h) の再現

## English

This application includes a reproduction mode for the frequency dependence of the real part of the CM factor shown in Figure 1 of the reference article.

The reproduction can be executed in two ways:

1. From the GUI by clicking `論文図(a)〜(h)を再現`
2. From the command line using the reproduction script

When executed from the GUI, the eight conductivity conditions are plotted in a new graph window. The existing PNG save and graph clear functions can also be used.

The following solution conductivity values are used:

| Label | Solution conductivity `sigma_s` |
|---|---:|
| (a) | 2.0e-4 S/m |
| (b) | 1.0e-3 S/m |
| (c) | 1.0e-2 S/m |
| (d) | 1.0e-1 S/m |
| (e) | 2.0e-1 S/m |
| (f) | 4.0e-1 S/m |
| (g) | 5.0e-1 S/m |
| (h) | 1.0e0 S/m |

Run the script with:

    PYTHONPATH=src uv run python src/dep_cm_sim/reproduce_paper_figure.py

The output image is saved as:

    outputs/paper_figure_reproduction.png

## 日本語

本アプリケーションには、参考文献 Figure 1 に示されているCM因子の実部の周波数依存性を再現する機能があります。

この再現機能は、以下の2通りで実行できます。

1. GUI上の「論文図(a)〜(h)を再現」ボタンから実行
2. コマンドラインで再現スクリプトを実行

GUIから実行した場合、8つの溶液導電率条件の曲線が新しいグラフWindowに重ね描きされます。既存のPNG保存機能やグラフクリア機能もそのまま使用できます。

使用している溶液導電率は以下です。

| Label | 溶液導電率 `sigma_s` |
|---|---:|
| (a) | 2.0e-4 S/m |
| (b) | 1.0e-3 S/m |
| (c) | 1.0e-2 S/m |
| (d) | 1.0e-1 S/m |
| (e) | 2.0e-1 S/m |
| (f) | 4.0e-1 S/m |
| (g) | 5.0e-1 S/m |
| (h) | 1.0e0 S/m |

以下のコマンドで実行できます。

    PYTHONPATH=src uv run python src/dep_cm_sim/reproduce_paper_figure.py

出力画像は以下に保存されます。

    outputs/paper_figure_reproduction.png

---

# Reference / 参考文献

This simulator refers to Figure 1, "Frequency dependence of the real part of the CM factor acting on cells," in the following article.

本シミュレータは、以下の文献に掲載されている Figure 1「細胞に作用するCM因子の実部の周波数依存性」を参考にしています。

- Tomoyuki Yasukawa and Fumio Mizutani, "Rapid Detection Technique for Surface Antigen-Expressing Cells Using Dielectrophoresis," Electrochemistry, Vol. 82, No. 11, pp. 993–999, 2014.

---

# Development / 開発

## English

Run lint:

    uv run ruff check .

Run tests:

    uv run pytest

Run the demo plot script:

    PYTHONPATH=src uv run python src/dep_cm_sim/demo_plot.py

## 日本語

lintを実行します。

    uv run ruff check .

テストを実行します。

    uv run pytest

デモ用グラフスクリプトを実行します。

    PYTHONPATH=src uv run python src/dep_cm_sim/demo_plot.py

---

# Project Structure / プロジェクト構成

    dep-cm-factor-simulator/
    - src/dep_cm_sim/equations.py
    - src/dep_cm_sim/cell_templates.py
    - src/dep_cm_sim/plotter.py
    - src/dep_cm_sim/demo_plot.py
    - src/dep_cm_sim/reproduce_paper_figure.py
    - src/dep_cm_sim/parameter_io.py
    - src/dep_cm_sim/optimization.py
    - src/dep_cm_sim/paper_conditions.py
    - src/dep_cm_sim/gui/parameter_window.py
    - src/dep_cm_sim/gui/graph_window.py
    - tests/test_equations.py
    - tests/test_cell_templates.py
    - tests/test_optimization.py
    - tests/test_parameter_io.py
    - pyproject.toml
    - uv.lock
    - README.md

---

# Notes / 注意事項

## English

This software is intended for educational, simulation, and parameter-comparison purposes.

Before using simulation results for formal academic or engineering conclusions, confirm the model assumptions, parameter units, and equation definitions with the original literature and appropriate domain experts.

## 日本語

本ソフトウェアは、教育用途、シミュレーション、およびパラメータ比較を目的としたものです。

シミュレーション結果を正式な学術的・工学的結論に用いる前に、モデルの仮定、パラメータ単位、式の定義を原著論文および専門分野の知見に基づいて確認することを推奨します。
