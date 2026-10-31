# Онбординг WeArt (8 экранов, прототип в Claude Design)

Живой холст: https://claude.ai/artifact/VbjDdK4PFcdNN7tZsmqjcN (если аккаунт недоступен, исходник в `onboarding-trends/prototype/`).

## Экраны
1. **Трендовая стена:** три автоскроллящиеся колонки фото, плашка «New trends every week», «Any trend. One photo.», чипы моделей (Nano Banana 2, GPT Image 2, Kling 3.0, Seedance 2.5, Veo 3.1, ElevenLabs v3), кнопка «Get started». Акцент синий.
2. **Before/After:** карточки «селфи → тренд» с кроссфейдом, скан-линия, «Easier than copying it.» Акцент пурпурный.
3. **Квиз 1:** что создаёшь (одиночный выбор). Бирюзовый.
4. **Квиз 2:** 2×4 карточки трендов, до 3 штук. Жёлтый.
5. **Результат:** два примера «селфи → тренд» с wipe-эффектом. Фиолетовый.
6. **Пейволл:** «Try WeArt for 7 days», $6.99 / 7-day trial / includes 100 tokens, ниже мелко «Then $16.99/month after the trial. Cancel anytime.», футер «Terms · Privacy».
7. **Спасибо:** конфетти, «You are in!», «+100 tokens».
8. **Регистрация:** Google / email, плавающие миниатюры, «Save your trends.»

## Техника
- Файлы `*.dc.html` + `canvas.json` (v3). Каждая страница 390×844, `<x-dc>`, переходы ссылками между артбордами (интерактивный прототип).
- Шрифт: SF Pro Display через `-apple-system` / `'SF Pro Display'` с запасным Inter (лицензия SF запрещает встраивание в веб).
- Загрузка ассетов: WebP ≤150 KB + быстрые анимации (CSS keyframes), цвет меняется по экранам.
- Фото трендов: `onboarding-trends/photos/` (9 штук). Фото с оружием (trend-04) в UI не используется: риск отказа App Store / Meta.
- Холст редактируется пользователем вручную: перед публикацией перечитывать изменённые файлы и накатывать правки поверх.
