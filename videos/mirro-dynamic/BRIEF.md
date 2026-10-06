---
workflow: general-video
flow: automation
storyboard: no
message: "Примерь свою одежду на себе за секунды"
destination: reels
aspect: 1080x1920
language: ru
length: 15s
---

## Intent

Динамичная версия промо MIRRO: быстрый монтаж в ритм музыки, кинетический текст,
звуковые эффекты, озвучка заказчика.

## Assets

- assets/audio/voiceover-src.mp3 — озвучка заказчика (12.9 с), стоит с 0.6 с
- assets/screens/*.png — скриншоты приложения

## Customizations

- Музыка и SFX генерируются tools/soundtrack.py (120 BPM, A-moll, детерминированно).
- Склейки на долях: 3.0 / 6.5 / 9.0–10.0 (смена образов) / 11.0 (логотип).
