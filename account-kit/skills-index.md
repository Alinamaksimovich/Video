# Индекс навыков

Все навыки лежат в `.claude/skills/` репозитория (папка = навык, внутри `SKILL.md`). Claude Code подхватывает их автоматически, если открыть репозиторий.

## Откуда взяты и как переустановить

| Навыки | Источник | Переустановка |
|---|---|---|
| hyperframes* , media-use, general-video, motion-graphics, music-to-video, talking-head-recut, embedded-captions, faceless-explainer, product-launch-video, pr-to-video, slideshow, figma, remotion-to-hyperframes | HeyGen HyperFrames | `npx hyperframes skills update` |
| impeccable | репозиторий-источник не зафиксирован | копия из репозитория |
| emil-design-eng, animate, review-animations, improve-animations и др. из набора Эмиля Ковальски | emilkowalski/skills (названо пользователем) | копия из репозитория |
| playwright-* | microsoft/playwright | копия из репозитория |
| brag, brag-slim | latent-spaces/brag | копия из репозитория |
| gsap-* | greensock/gsap-skills | копия из репозитория |
| remotion-* | официальные навыки Remotion (адрес не зафиксирован) | копия из репозитория |
| recordly, recordly-screen-recorder | webadderall/Recordly | копия из репозитория |

Самое надёжное: **копия в самом репозитории** (там уже лежат все 64). Источники выше нужны только если захочется обновить версии.

## Навыки аккаунта claude.ai (не в `.claude/skills`)

Лежат в `account-kit/account-skills/` и в ZIP-архивах рядом:
- **design-taste**: библиотека дизайн-вкуса. Разбирает присланные референсы, копит правила, применяет в любом визуале. Это самое «личное»: храни обязательно.
- **instagram-posts-premium**: посты, карусели, сторис для Instagram (+ логотипы PROMPTICA, форматы, хуки, режимы art/expert).
Стандартные навыки Anthropic (docx, pdf, pptx, xlsx, docs, deep-research, skill-creator, google-workspace, morning, setup-writing-style и т.д.) есть у любого аккаунта, переносить их не нужно. Список в `account-skills/manifest-anthropic-skills.json`.

## Видео и монтаж (основное, HyperFrames)

| Навык | Что делает |
|---|---|
| `hyperframes` | Mandatory entry point: read this first for any request to make, create, edit, animate, or render a video, animation, or motion graphic, including a promo, explainer, capt |
| `hyperframes-core` | The HyperFrames composition contract — build one renderable project. Use for composition structure, the `data-*` timing attributes, `class="clip"`, tracks, sub-compositio |
| `hyperframes-creative` | Non-animation creative direction for HyperFrames videos. Use for design spec (frame.md / design.md) handling, palettes, typography, narration, beat planning, audio-reacti |
| `hyperframes-animation` | All animation knowledge for HyperFrames — atomic motion rules, multi-phase scene blueprints, scene transitions, broader motion-design techniques, AND the seven runtime ad |
| `hyperframes-keyframes` | Use when a HyperFrames composition needs a punch-in, punch-out, zoom, reframe, Ken Burns treatment, camera move, visual match/whip handoff, or other seek-safe 2D/3D keyfr |
| `hyperframes-audio` | Use when audio already placed in a HyperFrames composition needs to be mixed: fade-in/fade-out, crossfade, track gain or volume, volume automation, ducking, a music bed t |
| `hyperframes-cli` | Use the HyperFrames CLI development loop: init, add, catalog, capture, lint, check, snapshot, compare, grade-compare, preview, play, present, beats, keyframes, single or  |
| `hyperframes-registry` | Search, install, and wire registry blocks and components into HyperFrames compositions. Use BEFORE hand-building any named visual — whenever a brief, a user, or a storybo |
| `hyperframes-studio` | Use when working with a person on a HyperFrames project in Studio: first, whether their message asks for a change at all (questions, loose ideas and "don't change anythin |
| `media-use` | Agent Media OS, the single skill for every media need in a HyperFrames project. Resolve BGM, SFX, image, icon, brand logo, voice, color grade, or LUT into a frozen local  |
| `general-video` | Author or edit a custom HyperFrames composition when no specialized workflow fits, or when BRIEF.md sets flow: companion. Use for longer or multi-scene pieces, brand and  |
| `motion-graphics` | A short, design-led motion graphic where motion is the message — kinetic typography, stat count-up, chart/data-viz hit, logo sting / brand lockup, lower-third / callout / |
| `music-to-video` | Turn a music track (an audio file, a video to pull audio from, or a track generated from a mood brief) into a beat-synced video — lyric video, slideshow, or kinetic promo |
| `talking-head-recut` | Package an existing talking-head / interview / podcast video with timed, designed GRAPHIC OVERLAY cards — kinetic titles, lower-thirds, data callouts, quotes, side panels |
| `embedded-captions` | Add captions or subtitles to an existing single-subject talking-head video without editing the footage. Use for plain verbatim captions, cinematic captions embedded behin |
| `faceless-explainer` | Turn arbitrary text — an article, notes, a topic, a brief — into a faceless explainer video: there is no site or footage to capture, so the visuals are invented per scene |
| `product-launch-video` | Turn a product or marketing URL, pasted script, or brief into a product launch / promo video — SaaS promos, feature reveals, product demos, app and company launches. Use  |
| `pr-to-video` | Turn a GitHub pull request (a PR URL, owner/repo#N, or 'this PR' in a checked-out repo) into a code-change explainer video — changelog, feature reveal, fix, or refactor w |
| `slideshow` | Author a HyperFrames slideshow — a presentation, pitch deck, or interactive deck with discrete slides, fragment reveals, branching, hotspot navigation, and built-in prese |
| `figma` | Import Figma content into a HyperFrames composition — rendered assets, brand tokens, components, storyboard sections → reconstructed motion (frames read as states, not sl |
| `remotion-to-hyperframes` | 'Port an existing Remotion (React) composition''s source to HyperFrames HTML. Use ONLY on an explicit ask to port/convert/migrate/translate a Remotion source — one-way, R |
| `brag` | Turn the current project website into a short, polished, shareable launch video using Hyperframes. Use when someone says "/brag", "let's brag about this", "make a launch  |
| `brag-slim` | Turn a project directory or a website URL into a short, shareable launch video with music, motion, and share copy. One file, no bundled assets — built entirely by the mod |
| `recordly` | Polish screen recordings with Recordly (open-source Screen Studio alternative) — auto-zooms, cursor animations, webcam overlays, styled backgrounds, timeline editing. Als |
| `recordly-screen-recorder` | Expertise in using and extending Recordly, an open-source Electron screen recorder and editor with auto-zoom, cursor animations, and cross-platform capture. |

## Анимация и моушн

| Навык | Что делает |
|---|---|
| `gsap-core` | Official GSAP skill for the core API — gsap.to(), from(), fromTo(), easing, duration, stagger, defaults, gsap.matchMedia() (responsive, prefers-reduced-motion). Use when  |
| `gsap-timeline` | Official GSAP skill for timelines — gsap.timeline(), position parameter, nesting, playback. Use when sequencing animations, choreographing keyframes, or when the user ask |
| `gsap-plugins` | Official GSAP skill for GSAP plugins — registration, ScrollToPlugin, ScrollSmoother, Flip, Draggable, Inertia, Observer, SplitText, ScrambleText, SVG and physics plugins, |
| `gsap-scrolltrigger` | Official GSAP skill for ScrollTrigger — scroll-linked animations, pinning, scrub, triggers. Use when building or recommending scroll-based animation, parallax, pinned sec |
| `gsap-react` | Official GSAP skill for React — useGSAP hook, refs, gsap.context(), cleanup. Use when the user wants animation in React or Next.js, or asks about GSAP with React, useGSAP |
| `gsap-frameworks` | Official GSAP skill for Vue, Svelte, and other non-React frameworks — lifecycle, scoping selectors, cleanup on unmount. Use when the user wants animation in Vue, Nuxt, Sv |
| `gsap-performance` | Official GSAP skill for performance — prefer transforms, avoid layout thrashing, will-change, batching. Use when optimizing GSAP animations, reducing jank, or when the us |
| `gsap-utils` | Official GSAP skill for gsap.utils — clamp, mapRange, normalize, interpolate, random, snap, toArray, wrap, pipe. Use when the user asks about gsap.utils, clamp, mapRange, |
| `motion-design` | Applies motion design principles to create emotionally-driven, technically sound animations and transitions. Provides timing, easing, choreography, and Disney animation p |
| `animate` | Build an animation from scratch, making the decisions in the order that determines whether it feels right — should it animate at all, what purpose, which tool, which prop |
| `animate-expo` | Build animations in React Native and Expo, making the decisions in the order that determines whether they feel right — should it animate, which thread it runs on, which p |
| `animation-vocabulary` | Reverse-lookup glossary that turns a vague description of a web animation or motion effect into its exact term ("the bouncy thing when a popover opens" → Pop in; "the iOS |
| `find-animation-opportunities` | Search a codebase or UI for places that don't animate but should, and reject everything that shouldn't. Read-only; it proposes motion with exact values, it does not imple |
| `improve-animations` | Survey a codebase's animation and motion code as a senior motion advisor, then produce a prioritized audit and self-contained implementation plans for other agents (or ch |
| `review-animations` | Reviews animation and motion code against a high craft bar derived from Emil Kowalski's design engineering philosophy. Default to flagging; approval is earned. |
| `emil-design-eng` | This skill encodes Emil Kowalski's philosophy on UI polish, component design, animation decisions, and the invisible details that make software feel great. |
| `apple-design` | Apple's approach to interface design and fluid, physical motion, translated for the web. Use when building or reviewing gesture-driven UI, spring animations, drag/swipe/s |

## Дизайн интерфейсов

| Навык | Что делает |
|---|---|
| `impeccable` | Use when the user wants to design, redesign, shape, critique, audit, polish, clarify, distill, harden, optimize, adapt, animate, colorize, extract, or otherwise improve a |
| `break-ui` | Try to break a piece of UI by feeding it worst-case data — long names, unbreakable emails, one-letter names, missing fields, huge counts, zero items, long labels, non-Lat |
| `prototype` | Build multiple genuinely different versions of a UI piece you describe, rendered behind a visual picker so you can flip through them live and promote the one that feels r |
| `pick-ui-library` | Pick the right library for a given frontend task from a curated, opinionated list — numbers, OTP inputs, charts, command menus, virtualization, drag and drop, toasts, sta |
| `mobile-native` | Make a web app feel native on a phone — the small CSS and meta-tag fixes that separate "a website in a browser" from something that feels installed. Covers sticky hover s |
| `ask-sonner` | Guide to Sonner, the React toast library — install and wire up the Toaster, pick the right toast() call, promise and loading toasts, updating, dismissing and persisting t |

## Remotion (запасной видеодвижок)

| Навык | Что делает |
|---|---|
| `remotion-best-practices` | Router for all Remotion skills |
| `remotion-create` | Create a new Remotion video |
| `remotion-docs` | Search Remotion documentation |
| `remotion-render` | Export a Remotion video |
| `remotion-studio` | Preview a Remotion video |
| `remotion-captions` | Transcribing, displaying and animating captions |
| `remotion-markup` | Content, animation and effects best practices |
| `remotion-interactivity` | Structure Remotion markup for interactivity |
| `remotion-maps` | Remotion Map animation knowledge |
| `remotion-multimedia` | Interacting with Mediabunny |
| `remotion-saas` | Build an app with Remotion |
| `remotion-upgrade` | Upgrade Remotion, and related packages |

## Браузер и тесты

| Навык | Что делает |
|---|---|
| `playwright-cli` | Automate browser interactions, test web pages and work with Playwright tests. |
| `playwright-component-testing` | Set up component testing with Playwright using a story gallery — scaffold stories and a gallery dev page driven by the built-in mount fixture, no dedicated component-test |
| `playwright-trace` | Inspect Playwright trace files from the command line — list actions, view requests, console, errors, snapshots and screenshots. |

## Прочее

| Навык | Что делает |
|---|---|
| `write-swift` | How to write modern Swift well — modeling with value types, Swift 6 data-race safety and approachable concurrency (@concurrent, main-actor-by-default, actors, task groups |

