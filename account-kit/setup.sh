#!/usr/bin/env bash
# Устанавливает всё, что нужно для видео-проектов из этого репозитория.
# Запуск: bash account-kit/setup.sh            (пакеты + проверки)
#         bash account-kit/setup.sh --models   (+ скачать модели речи, ~450 МБ)
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ok(){ echo "  ✔ $1"; }; bad(){ echo "  ✘ $1"; FAIL=1; }
FAIL=0

echo "== Системные программы"
for c in python3 node npm ffmpeg git; do command -v $c >/dev/null && ok "$c $($c --version 2>&1 | head -1)" || bad "$c не найден (установи через пакетный менеджер)"; done

echo "== Python-пакеты"
python3 -m pip install -q --disable-pip-version-check numpy scipy soundfile pillow rembg kokoro-onnx sherpa-onnx onnxruntime 2>&1 | tail -2
python3 - <<'PY'
import importlib
for m in ["numpy","scipy","soundfile","PIL","rembg","kokoro_onnx","sherpa_onnx"]:
    try: importlib.import_module(m); print("  ✔",m)
    except Exception as e: print("  ✘",m,e)
PY

echo "== HyperFrames (рендер видео)"
( cd "$ROOT/videos/promptica-cases" && npx --yes hyperframes@0.8.138 --version >/dev/null 2>&1 ) && ok "hyperframes 0.8.138" || bad "hyperframes не запустился (нужен интернет к npm)"
command -v chromium >/dev/null || [ -d "${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}" ] && ok "Chromium для рендера" || bad "Chromium не найден: npx playwright install chromium"

if [ "${1:-}" = "--models" ]; then
  echo "== Модели речи"
  M="$HOME/models"; mkdir -p "$M"
  [ -d "$M/sherpa-onnx-whisper-small" ] || { curl -fL -o "$M/w.tar.bz2" https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2 && tar -xjf "$M/w.tar.bz2" -C "$M" && rm "$M/w.tar.bz2"; } && ok "Whisper small → $M" || bad "Whisper не скачался"
  mkdir -p "$M/kokoro"
  [ -f "$M/kokoro/kokoro-v1.0.onnx" ] || curl -fL -o "$M/kokoro/kokoro-v1.0.onnx" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  [ -f "$M/kokoro/voices-v1.0.bin" ] || curl -fL -o "$M/kokoro/voices-v1.0.bin" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
  [ -f "$M/kokoro/kokoro-v1.0.onnx" ] && ok "Kokoro TTS → $M/kokoro" || bad "Kokoro не скачался"
fi

echo "== Навыки"
n=$(ls -d "$ROOT"/.claude/skills/*/ 2>/dev/null | wc -l); [ "$n" -ge 60 ] && ok "$n навыков в .claude/skills" || bad "навыки не найдены в .claude/skills"
[ -f "$ROOT/account-kit/account-skills/design-taste/SKILL.md" ] && ok "design-taste, instagram-posts-premium лежат в account-kit/account-skills" || bad "нет account-skills"

echo; [ $FAIL = 0 ] && echo "Готово." || echo "Есть пункты ✘, покажи их Claude."
exit 0
