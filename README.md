# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/luckyind2020/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/luckyind2020/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A deterministic program that draws a newspaper front page summing up the world news of Wednesday 25 November 2026 — Kyiv confirming the drone strike on a Russian ship in the Gulf of Finland, the Houthi strike on Riyadh's tallest tower, Huawei's conviction in a US trial, the CIA cyber breach, and more — and writes it to `/output/entry.png`.

Pure Python standard library: no network, no fonts on disk, no randomness. The picture is built from an embedded 5×7 bitmap font and simple vector shapes, then encoded as PNG by hand, so running it twice writes the same bytes.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=4ha9jy2z&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
