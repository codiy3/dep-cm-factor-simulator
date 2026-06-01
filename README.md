# DEP CM Factor Simulator

DEP CM Factor Simulator は、誘電泳動（DEP）における Clausius-Mossotti 因子の実部 Re[K] と周波数の関係を可視化するための Python GUI アプリケーションです。

修士研究における細胞・微粒子の DEP 応答確認を目的として、パラメータを変更しながら周波数依存性を比較できるようにしています。

## Features

- CM因子の実部 Re[K] を計算
- 周波数 f [Hz] に対する Re[K] をグラフ表示
- パラメータ入力用GUI
- グラフ表示用GUI
- 複数条件の重ね描き
- 新しいWindowでのグラフ表示
- グラフクリア
- PNG保存
- 不正な入力値に対するエラー表示
- uv による環境構築・依存関係管理

## Requirements

- macOS
- Python 3.12
- uv

## Setup

uv sync

## Run

uv run dep-cm-sim

## Usage

1. アプリを起動する
2. パラメータ入力画面で値を入力する
3. 「現在のグラフに重ねる」を押す
4. グラフWindowに Re[K] と周波数の関係が表示される
5. 条件を変更して再度「現在のグラフに重ねる」を押すと、同じグラフ上に曲線が追加される
6. 「新しいWindowで表示」を押すと、別Windowにグラフが表示される
7. グラフWindowの「PNG保存」で画像を保存できる
8. 「グラフをクリア」で表示中の曲線を削除できる

## Parameters

| Parameter | Symbol | Unit | Default | Description |
|---|---:|---:|---:|---|
| Membrane capacitance | C_m | F/m^2 | 0.015 | Cell membrane capacitance |
| Cell radius | r | m | 6.7e-6 | Cell radius |
| Cytoplasm relative permittivity | epsilon_c / epsilon_0 | - | 60 | Relative permittivity of cytoplasm |
| Solution relative permittivity | epsilon_s / epsilon_0 | - | 80 | Relative permittivity of solution |
| Cytoplasm conductivity | sigma_c | S/m | 0.5 | Conductivity of cytoplasm |
| Solution conductivity | sigma_s | S/m | 2.0e-4 | Conductivity of solution |
| Minimum frequency | f_min | Hz | 1 | Lower bound of frequency |
| Maximum frequency | f_max | Hz | 1.0e10 | Upper bound of frequency |
| Number of points | N | points | 1000 | Number of log-spaced frequency points |

## Model

omega = 2 pi f

tau_ms = C_m r / sigma_s

tau_mc = C_m r / sigma_c

tau_s = epsilon_s / sigma_s

tau_c = epsilon_c / sigma_c

epsilon_s = epsilon_s_relative * epsilon_0

epsilon_c = epsilon_c_relative * epsilon_0

The application plots the real part of the CM factor: Re[K].

## Development

Run lint:

uv run ruff check .

Run tests:

uv run pytest

Run the demo plot script:

PYTHONPATH=src uv run python src/dep_cm_sim/demo_plot.py

## Project Structure

dep-cm-factor-simulator/
- src/dep_cm_sim/equations.py
- src/dep_cm_sim/plotter.py
- src/dep_cm_sim/demo_plot.py
- src/dep_cm_sim/gui/parameter_window.py
- src/dep_cm_sim/gui/graph_window.py
- tests/test_equations.py
- pyproject.toml
- uv.lock
- README.md

## Notes

This software is intended for research support and parameter comparison.

Before using simulation results for formal academic conclusions, confirm the model assumptions, parameter units, and equation definitions with the original literature and a specialist.
