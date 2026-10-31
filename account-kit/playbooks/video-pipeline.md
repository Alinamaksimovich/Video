# Как собирается видео (общий конвейер)

1. **Бриф и сценарий.** Формат, длительность, язык, материалы, текст. Сценарий таблицей «время / кадр / титр», согласовать.
2. **Проект.** Новая папка `videos/<имя>/`: скопировать `hyperframes.json`, `package.json`, `CLAUDE.md`, `AGENTS.md`, `assets/vendor/gsap.min.js` и шрифты из соседнего проекта. `meta.json` с id.
3. **Медиа.** Исходники пользователя в `assets/video|img|audio` (видео в H.264, `-g 12`, без звука, если звук отдельным треком; фото ≤ 1400 px).
4. **Вёрстка (`index.html`).** Одна корневая композиция `data-composition-id="main"`, GSAP-таймлайн `paused`, зарегистрирован в `window.__timelines["main"]`,
   в `defaults` стоит `immediateRender:false`. Видео: `<video muted playsinline data-start data-duration data-media-start>`. Звук отдельными `<audio>`.
5. **Звук.** Музыка и SFX генерируются/раскладываются скриптами в `tools/`, результат в `assets/audio/music.wav` и `sfx.wav`. Голос кладётся как есть.
6. **Проверка.** `npm run check`, затем рендер `npx --yes hyperframes@0.8.138 render --workers 1 -o renders/<имя>.mp4`.
7. **Кадры.** Достать 8–12 кадров (`select` + `tile`) и посмотреть: границы текста, перекрытия, пустые кадры.
8. **Громкость.** Измерить `ebur128`, затем один проход `volume=…dB` или `loudnorm=I=-14:TP=-1.5`, видео копировать. Цель −14 LUFS, пик ≤ −1 dBFS.
9. **Коммит и отправка.** `git add videos/<имя>`, commit, push на ветку; mp4 отправить в чат.

## Типовые ловушки
- Текст шире кадра: у `Roboto Flex` с `font-stretch:140%` кириллица очень широкая; считать ширину через PIL (`ImageFont.getbbox`) до вёрстки.
- Первый кадр пустой: появление элементов делать от 0.3 с, не от 0.
- Видео короче фразы: ping-pong цикл (`reverse` + `concat` + `loop`).
- Рендер упирается в память: `--workers 1`.
- Warnings про `nested_structure_needs_subcomposition` и «много элементов на треке» для титров можно игнорировать.
- Предупреждение `gsap_repeated_fromto_without_baseline`: добавить `immediateRender:false` ко всем `fromTo`, кроме самого раннего.
