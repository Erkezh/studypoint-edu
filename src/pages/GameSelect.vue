<template>
  <div class="game-select-page">
    <Header />

    <main class="game-select-shell">
      <GamificationBar class="game-select-progress" />

      <header class="game-select-hero">
        <span class="hero-decoration hero-decoration--trophy"><GameSelectIcon name="trophy" /></span>
        <span class="hero-decoration hero-decoration--controller"><GameSelectIcon name="gamepad" /></span>
        <p>STUDYPOINT ОЙЫНДАРЫ</p>
        <h1>Өз <span>ойыныңды</span> таңда</h1>
        <div class="hero-copy">
          Жинаған сыйлықтарыңды қалай пайдаланатыныңды және профиліңді қалай безендіретініңді таңда.<br />
          Ойынды кейін ауыстырсаң да, барлық заттарың сақталады.
        </div>
      </header>

      <div v-if="gameSettings.error" role="alert" class="game-error">
        Ойынды таңдау мүмкін болмады. Қайтадан байқап көр.
      </div>

      <section class="game-grid" aria-label="Ойын түрлері">
        <article class="game-card game-card--car" role="button" tabindex="0" aria-label="Көлік гаражын алдын ала көру" @click="openPreview('car')" @keydown.enter="openPreview('car')">
          <div class="game-card__simple-action">
            <button type="button" @click.stop="openPreview('car')">
              <GameSelectIcon name="car" />
              <strong>Көлік гаражы</strong>
              <span>→</span>
            </button>
          </div>
        </article>

        <article class="game-card game-card--character" role="button" tabindex="0" aria-label="Кейіпкер әлемін алдын ала көру" @click="openPreview('character')" @keydown.enter="openPreview('character')">
          <div class="game-card__simple-action">
            <button type="button" @click.stop="openPreview('character')">
              <GameSelectIcon name="person" />
              <strong>Кейіпкер әлемі</strong>
              <span>→</span>
            </button>
          </div>
        </article>
      </section>

    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import Header from '@/components/layout/Header.vue'
import GameSelectIcon from '@/components/game/GameSelectIcon.vue'
import GamificationBar from '@/components/gamification/GamificationBar.vue'
import { useGameSettingsStore } from '@/stores/gameSettings'
import type { GameType } from '@/types/api'

const router = useRouter()
const gameSettings = useGameSettingsStore()

function openPreview(game: GameType) {
  void router.push({
    name: game === 'car' ? 'garage' : 'avatar-demo',
    query: { trial: '1' },
  })
}
</script>

<style scoped>
.game-select-page { min-height: 100vh; background: radial-gradient(circle at 8% 50%, rgba(113, 210, 153, .18), transparent 27%), radial-gradient(circle at 92% 55%, rgba(142, 106, 220, .14), transparent 28%), #f8fcfa; color: #111827; }
.game-select-shell { width: min(1280px, calc(100% - 32px)); margin: 0 auto; padding: 38px 0 30px; }
.game-select-hero { position: relative; text-align: center; }
.game-select-hero > p { color: #008b4a; font-size: 13px; font-weight: 900; letter-spacing: .32em; }
.game-select-hero h1 { margin: 7px 0 8px; font-size: clamp(38px, 4.4vw, 60px); line-height: 1.05; font-weight: 950; letter-spacing: -.04em; }
.game-select-hero h1 span { color: #079348; }
.hero-copy { color: #45546b; font-size: 17px; line-height: 1.55; }
.hero-decoration { position: absolute; top: 18px; font-size: 78px; opacity: .1; filter: grayscale(1); }
.hero-decoration--trophy { left: 4%; transform: rotate(-12deg); }
.hero-decoration--controller { right: 4%; transform: rotate(12deg); }
.game-error { max-width: 680px; margin: 18px auto 0; padding: 12px 18px; border: 1px solid #fecaca; border-radius: 16px; background: #fff1f2; color: #be123c; text-align: center; font-weight: 800; }
.game-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 28px; margin-top: 28px; }
.game-card { overflow: hidden; border: 1px solid rgba(255,255,255,.9); border-radius: 28px; background: white; box-shadow: 0 18px 45px rgba(20, 50, 43, .13); transition: transform .2s ease, box-shadow .2s ease; }
.game-card:hover { transform: translateY(-4px); box-shadow: 0 24px 55px rgba(20, 50, 43, .18); }
.game-card:focus-visible { outline: 4px solid rgba(34, 197, 94, .32); outline-offset: 4px; }
.game-card__visual { position: relative; height: 285px; overflow: hidden; }
.game-card--car .game-card__visual { background: linear-gradient(150deg, #0b2c27 0%, #164c3a 54%, #071c1b 100%); }
.game-card--character .game-card__visual { background: linear-gradient(145deg, #e9defc, #c8adf0 52%, #8a5dd1); }
.game-card__badge { position: absolute; z-index: 3; top: 18px; left: 20px; display: flex; align-items: center; gap: 9px; padding: 10px 17px; border-radius: 999px; color: white; font-size: 13px; font-weight: 900; box-shadow: 0 8px 20px rgba(0,0,0,.16); }
.game-card--car .game-card__badge { background: #07934c; }
.game-card--character .game-card__badge { background: #7646d5; }
.garage-scene { position: absolute; inset: 0; background: repeating-linear-gradient(90deg, transparent 0 116px, rgba(94,255,172,.09) 117px 119px), linear-gradient(to top, rgba(1,14,14,.78), transparent 55%); }
.garage-scene::after { content: ''; position: absolute; left: 12%; right: 12%; bottom: 23px; height: 26px; border-radius: 50%; background: rgba(43,255,136,.2); filter: blur(16px); }
.garage-scene img { position: absolute; z-index: 1; width: 76%; left: 12%; bottom: -25px; filter: sepia(.3) saturate(2.4) hue-rotate(76deg) brightness(.88) drop-shadow(0 16px 12px rgba(0,0,0,.45)); }
.garage-light { position: absolute; top: 38px; width: 34%; height: 5px; background: #63ffa7; box-shadow: 0 0 14px #38f789; transform: rotate(-3deg); }
.garage-light--one { left: 8%; }.garage-light--two { right: 8%; }
.character-scene { height: 100%; display: flex; align-items: flex-end; justify-content: center; gap: 2px; padding: 44px 30px 0; background: radial-gradient(circle at 50% 110%, rgba(255,255,255,.9), transparent 56%); }
.character-scene img { width: 29%; max-width: 164px; border-radius: 50% 50% 20% 20%; opacity: .82; filter: drop-shadow(0 14px 14px rgba(62,31,108,.25)); transform: translateY(18px) scale(.92); }
.character-scene .character-scene__main { z-index: 1; width: 37%; max-width: 195px; opacity: 1; transform: translateY(8px) scale(1.08); }
.game-card__content { padding: 22px 30px 26px; }
.game-card__heading { display: flex; gap: 16px; align-items: flex-start; }
.game-card__round-icon { display: grid; flex: 0 0 58px; height: 58px; place-items: center; border-radius: 50%; background: #e4f8ec; font-size: 27px; }
.game-card--character .game-card__round-icon { background: #efe7ff; }
.game-card h2 { margin: 0; font-size: 27px; line-height: 1.15; font-weight: 950; letter-spacing: -.025em; }
.game-card__heading p { min-height: 52px; margin: 6px 0 0; color: #536176; font-size: 14px; line-height: 1.5; }
.feature-list { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 8px; margin: 19px 0; padding: 0; list-style: none; color: #303b4d; font-size: 11px; font-weight: 700; }
.feature-list li { display: flex; align-items: center; gap: 5px; white-space: nowrap; }.feature-list svg { flex: 0 0 18px; font-size: 18px; }
.game-card button { display: flex; width: 100%; align-items: center; justify-content: center; gap: 16px; border: 0; border-radius: 13px; padding: 14px 18px; background: linear-gradient(90deg, #028a45, #04a654); color: white; font-size: 17px; font-weight: 900; cursor: pointer; transition: filter .2s ease, transform .2s ease; }
.game-card--character button { background: linear-gradient(90deg, #7040d3, #8c50df); }.game-card button:hover { filter: brightness(1.08); transform: translateY(-1px); }.game-card button:disabled { opacity: .6; cursor: wait; }.game-card button span { font-size: 24px; line-height: 1; }
.progress-strip { display: grid; grid-template-columns: 2.3fr repeat(4, 1fr); align-items: center; gap: 0; margin-top: 24px; padding: 14px 24px; border: 1px solid #dbe8e0; border-radius: 20px; background: rgba(255,255,255,.9); box-shadow: 0 12px 32px rgba(20,50,43,.09); }
.progress-strip__message { display: flex; align-items: center; gap: 14px; padding-right: 20px; }.progress-strip__message strong { display: block; color: #078b47; font-size: 13px; }.progress-strip__message small { display: block; margin-top: 3px; color: #566476; font-size: 11px; line-height: 1.45; }.shield { display: grid; flex: 0 0 48px; height: 52px; place-items: center; border-radius: 48% 48% 55% 55%; background: #098d4a; color: white; font-size: 24px; font-weight: 900; }
.progress-stat { display: grid; grid-template-columns: 34px 1fr; grid-template-rows: auto auto; padding: 0 14px; border-left: 1px solid #dce5e1; }.progress-stat > span,.progress-stat > img { grid-row: 1 / 3; align-self: center; width: 25px; height: 25px; object-fit: contain; font-size: 25px; }.progress-stat small { color: #607083; font-size: 10px; }.progress-stat strong { color: #111827; font-size: 14px; }
.preview-backdrop { position: fixed; z-index: 1000; inset: 0; display: grid; place-items: center; padding: 24px; background: rgba(5, 18, 28, .72); backdrop-filter: blur(10px); }
.preview-dialog { position: relative; display: grid; grid-template-columns: 1.08fr .92fr; width: min(1040px, 100%); max-height: min(760px, calc(100vh - 48px)); overflow: auto; border: 1px solid rgba(255,255,255,.55); border-radius: 30px; background: white; box-shadow: 0 35px 90px rgba(0,0,0,.38); }
.preview-dialog__close { position: absolute; z-index: 5; top: 16px; right: 16px; display: grid; width: 42px; height: 42px; place-items: center; border: 1px solid rgba(255,255,255,.6); border-radius: 50%; background: rgba(13,29,40,.62); color: white; font-size: 28px; line-height: 1; cursor: pointer; }
.preview-dialog__visual { position: relative; display: grid; min-height: 500px; place-items: center; overflow: hidden; }
.preview-dialog__visual--car { background: repeating-linear-gradient(90deg, transparent 0 110px, rgba(92,255,168,.08) 112px 114px), radial-gradient(circle at 50% 80%, #196f4b, #0a2825 60%, #061817); }
.preview-dialog__visual--character { background: radial-gradient(circle at 50% 90%, #fff, transparent 52%), linear-gradient(145deg, #eee6ff, #9c72dd); }
.preview-dialog__visual > img { z-index: 1; width: 82%; filter: sepia(.25) saturate(2.3) hue-rotate(76deg) drop-shadow(0 28px 22px rgba(0,0,0,.42)); }
.preview-dialog__label { position: absolute; z-index: 3; top: 22px; left: 24px; padding: 10px 16px; border-radius: 999px; background: rgba(0,126,66,.88); color: white; font-size: 12px; font-weight: 900; letter-spacing: .06em; }
.preview-dialog__visual--character .preview-dialog__label { background: rgba(111,63,205,.9); }
.preview-characters { display: flex; align-items: flex-end; justify-content: center; padding: 80px 22px 0; }.preview-characters img { width: 31%; border-radius: 45% 45% 20% 20%; filter: drop-shadow(0 20px 18px rgba(49,20,87,.28)); }.preview-characters img:nth-child(2) { z-index: 1; width: 39%; transform: scale(1.12); }
.preview-dialog__content { display: flex; flex-direction: column; justify-content: center; padding: 52px 42px 38px; }
.preview-dialog__eyebrow { margin: 0 0 8px; color: #079348 !important; font-size: 12px !important; font-weight: 900; letter-spacing: .2em; }
.preview-dialog__content h2 { margin: 0; font-size: clamp(31px, 3vw, 44px); line-height: 1.08; font-weight: 950; letter-spacing: -.04em; }
.preview-dialog__content > p { margin: 16px 0 0; color: #536176; font-size: 16px; line-height: 1.65; }
.preview-dialog__steps { display: grid; gap: 11px; margin: 24px 0; }.preview-dialog__steps span { display: flex; align-items: center; gap: 11px; color: #273548; font-size: 14px; font-weight: 800; }.preview-dialog__steps b { display: grid; width: 28px; height: 28px; place-items: center; border-radius: 50%; background: #e1f8e9; color: #078b47; }
.preview-dialog__go { display: flex; align-items: center; justify-content: center; gap: 16px; border: 0; border-radius: 15px; padding: 15px 20px; background: linear-gradient(90deg, #078b47, #08aa58); color: white; font-size: 19px; font-weight: 950; cursor: pointer; }.preview-dialog__go span { font-size: 25px; }.preview-dialog__go:disabled { opacity: .6; cursor: wait; }
.preview-dialog__back { margin-top: 10px; border: 0; padding: 10px; background: transparent; color: #627083; font-size: 13px; font-weight: 800; cursor: pointer; }
@media (max-width: 960px) { .feature-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }.progress-strip { grid-template-columns: repeat(4, 1fr); }.progress-strip__message { grid-column: 1 / -1; margin-bottom: 14px; padding: 0 0 14px; border-bottom: 1px solid #dce5e1; }.progress-stat:first-of-type { border-left: 0; } }
@media (max-width: 720px) { .game-select-shell { width: min(100% - 22px, 560px); padding-top: 26px; }.game-select-hero h1 { font-size: 38px; }.hero-copy { font-size: 14px; }.hero-decoration { display: none; }.game-grid { grid-template-columns: 1fr; gap: 20px; }.game-card__visual { height: 235px; }.game-card__content { padding: 20px; }.progress-strip { grid-template-columns: repeat(2, 1fr); padding: 15px; }.progress-stat { margin-top: 10px; padding: 8px; }.progress-stat:nth-of-type(odd) { border-left: 0; }.preview-backdrop { padding: 12px; }.preview-dialog { grid-template-columns: 1fr; max-height: calc(100vh - 24px); border-radius: 22px; }.preview-dialog__visual { min-height: 250px; }.preview-dialog__content { padding: 28px 24px 22px; }.preview-dialog__content h2 { font-size: 31px; }.preview-dialog__visual > img { width: 64%; }.preview-characters { padding-top: 55px; }.preview-dialog__steps { margin: 18px 0; } }

/* Retro arcade mood for the game-selection welcome screen. */
.game-select-page {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% -12%, rgb(255 205 93 / 28%), transparent 22rem),
    radial-gradient(circle at 8% 34%, rgb(53 202 255 / 14%), transparent 24rem),
    radial-gradient(circle at 92% 26%, rgb(255 116 168 / 15%), transparent 25rem),
    linear-gradient(180deg, #5d364b 0%, #442a46 46%, #241b39 100%);
  color: #fff8e9;
}

.game-select-page::before {
  position: absolute;
  z-index: -1;
  right: -12%;
  bottom: -14rem;
  left: -12%;
  height: 48rem;
  content: '';
  opacity: 0.62;
  background-image:
    linear-gradient(rgb(242 76 204 / 38%) 1px, transparent 1px),
    linear-gradient(90deg, rgb(242 76 204 / 38%) 1px, transparent 1px);
  background-size: 58px 42px;
  transform: perspective(440px) rotateX(61deg);
  transform-origin: center bottom;
  mask-image: linear-gradient(to bottom, transparent, #000 38%);
}

.game-select-shell {
  position: relative;
  width: min(1320px, calc(100% - 32px));
  padding-top: 30px;
}

.game-select-shell::before,
.game-select-shell::after {
  position: absolute;
  top: 19px;
  color: #ffe064;
  font-size: clamp(30px, 4vw, 58px);
  text-shadow: 5px 5px 0 rgb(31 20 50 / 55%);
  content: '✦';
}

.game-select-shell::before { left: 0; }
.game-select-shell::after { right: 0; color: #62d9ff; content: '◆'; }

.game-select-hero {
  width: min(920px, 100%);
  margin: 0 auto;
  padding: 24px 26px 27px;
  border: 3px solid #fff8e9;
  border-radius: 28px;
  background: rgb(67 38 60 / 64%);
  box-shadow: 0 10px 0 #291b37, inset 0 0 0 4px rgb(255 255 255 / 6%);
}

.game-select-hero > p {
  color: #ffe064;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  letter-spacing: 0.2em;
  text-shadow: 3px 3px 0 #2b1c38;
}

.game-select-hero h1 {
  margin: 7px 0 11px;
  color: #fff8e9;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: clamp(38px, 5vw, 68px);
  letter-spacing: 0.03em;
  text-transform: uppercase;
  text-shadow: 5px 5px 0 #24182f;
}

.game-select-hero h1 span { color: #ffe064; }
.hero-copy { color: #f5dfe7; font-size: 15px; }
.hero-decoration { top: -8px; opacity: 0.78; filter: none; image-rendering: pixelated; }
.hero-decoration--trophy { left: -8%; }
.hero-decoration--controller { right: -8%; }

.game-grid { gap: 24px; margin-top: 30px; }
.game-card {
  border: 3px solid #fff8e9;
  border-radius: 24px;
  background: #38283f;
  color: #fff8e9;
  box-shadow: 0 10px 0 #21172e, 0 22px 38px rgb(14 8 27 / 36%);
}
.game-card:hover { transform: translateY(-5px); box-shadow: 0 15px 0 #21172e, 0 28px 46px rgb(14 8 27 / 44%); }
.game-card:focus-visible { outline-color: #ffe064; }
.game-card__visual { height: 268px; border-bottom: 3px solid #fff8e9; }
.game-card--car .game-card__visual { background: linear-gradient(150deg, #102f34, #155a52 54%, #081c28); }
.game-card--character .game-card__visual { background: linear-gradient(145deg, #5c416f, #815690 52%, #352847); }
.game-card__badge {
  border: 2px solid #fff8e9;
  border-radius: 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  box-shadow: 4px 4px 0 #251a31;
}
.game-card--car .game-card__badge { background: #f1b936; color: #2b2035; }
.game-card--character .game-card__badge { background: #71a7e8; color: #202540; }
.garage-scene img { filter: saturate(1.25) brightness(.96) drop-shadow(0 16px 12px rgba(0,0,0,.45)); }
.character-scene { background: radial-gradient(circle at 50% 110%, rgb(255 229 157 / 72%), transparent 56%); }
.game-card__content { padding: 21px 26px 24px; }
.game-card__round-icon { border: 2px solid #fff8e9; border-radius: 12px; background: #f1b936; box-shadow: 4px 4px 0 #22172e; }
.game-card__round-icon svg { width: 31px; height: 31px; }
.game-card--character .game-card__round-icon { background: #71a7e8; }
.game-card h2 { color: #fff8e9; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
.game-card__heading p { color: #dbcbd7; }
.feature-list { color: #f7e8e1; }
.game-card button {
  border: 2px solid #fff8e9;
  border-radius: 12px;
  background: #f1b936;
  color: #2d2135;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  box-shadow: 0 6px 0 #a66c24;
  text-transform: uppercase;
}
.game-card--character button { background: #71a7e8; box-shadow: 0 6px 0 #3f639d; }
.game-card button:hover { filter: brightness(1.07); transform: translateY(-2px); }
.game-card button:active { transform: translateY(4px); box-shadow: 0 2px 0 #714b22; }

.progress-strip {
  border: 3px solid #fff8e9;
  border-radius: 18px;
  background: rgb(47 33 57 / 90%);
  color: #fff8e9;
  box-shadow: 0 8px 0 #21172e;
}
.progress-strip__message strong { color: #ffe064; }
.progress-strip__message small,
.progress-stat small { color: #ccbcca; }
.progress-stat { border-left-color: rgb(255 248 233 / 20%); }
.progress-stat strong { color: #fff8e9; }
.shield { border: 2px solid #fff8e9; border-radius: 10px; background: #e95084; box-shadow: 3px 3px 0 #271b32; }
.shield svg { width: 28px; height: 28px; }
.progress-stat__icon { display: grid; place-items: center; color: #ffe064; }
.progress-stat__icon svg { width: 25px; height: 25px; }

@media (max-width: 720px) {
  .game-select-hero { padding: 20px 16px 22px; border-radius: 20px; }
  .game-select-hero h1 { font-size: 32px; }
  .game-select-shell::before,
  .game-select-shell::after { display: none; }
  .game-card { border-radius: 19px; }
}

/* StudyPoint dashboard design, matching the main learning page. */
.game-select-page {
  overflow: visible;
  background:
    radial-gradient(circle at 18% 26%, rgb(48 203 190 / 9%), transparent 27rem),
    radial-gradient(circle at 85% 60%, rgb(255 191 62 / 10%), transparent 28rem),
    #f7f9fc;
  color: #101828;
}

.game-select-page::before,
.game-select-shell::before,
.game-select-shell::after {
  display: none;
}

.game-select-shell {
  width: min(1280px, calc(100% - 32px));
  padding: 34px 0 48px;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.game-select-progress {
  margin-bottom: 30px;
}

.progress-strip {
  grid-template-columns: 2.2fr repeat(4, minmax(120px, 0.75fr));
  margin: 0 0 30px;
  padding: 14px 18px;
  border: 0;
  border-radius: 20px;
  background: linear-gradient(90deg, #4b43e7, #5548e7);
  color: #fff;
  box-shadow: 0 18px 36px rgb(63 55 205 / 18%);
}

.progress-strip__message {
  padding-right: 18px;
}

.progress-strip__message strong {
  color: #fff;
  font-size: 14px;
}

.progress-strip__message small,
.progress-stat small {
  color: #d9d8ff;
}

.progress-stat {
  min-height: 52px;
  border-left-color: rgb(255 255 255 / 20%);
}

.progress-stat strong {
  color: #fff;
  font-size: 15px;
}

.shield {
  flex-basis: 48px;
  height: 48px;
  border: 0;
  border-radius: 14px;
  background: #25275d;
  box-shadow: none;
}

.progress-stat__icon {
  color: #ffe16b;
}

.game-select-hero {
  width: min(920px, 100%);
  margin: 0 auto;
  padding: 5px 20px 16px;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none !important;
}

.hero-decoration {
  display: none;
}

.game-select-hero > p {
  color: #0895a4;
  font-family: inherit;
  font-size: 13px;
  letter-spacing: 0.24em;
  text-shadow: none;
}

.game-select-hero h1 {
  margin: 7px 0 9px;
  color: #111827;
  font-family: inherit;
  font-size: clamp(38px, 4.4vw, 60px);
  letter-spacing: -0.04em;
  text-transform: none;
  text-shadow: none;
}

.game-select-hero h1 span {
  color: #4e46e5;
}

.hero-copy {
  color: #667085;
  font-size: 16px;
}

.game-grid {
  width: min(1040px, 100%);
  gap: 28px;
  margin: 22px auto 0;
}

.game-card {
  overflow: hidden;
  border: 0;
  border-radius: 30px;
  color: #101828;
  box-shadow: 0 22px 48px rgb(24 38 70 / 14%);
}

.game-card--car {
  background: #30cbbb;
}

.game-card--character {
  background: #ffd34f;
}

.game-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 28px 58px rgb(24 38 70 / 19%);
}

.game-card__visual {
  height: 220px;
  border-bottom: 0;
}

.game-card--car .game-card__visual {
  background: linear-gradient(145deg, #183e49, #176e68 58%, #112d3d);
}

.game-card--character .game-card__visual {
  background: linear-gradient(145deg, #fff0b1, #f7bf40 60%, #ef9c26);
}

.game-card__badge {
  border: 0;
  border-radius: 999px;
  font-family: inherit;
  box-shadow: 0 8px 18px rgb(18 35 60 / 16%);
}

.game-card--car .game-card__badge {
  background: #20b9aa;
  color: #fff;
}

.game-card--character .game-card__badge {
  background: #4e46e5;
  color: #fff;
}

.garage-scene img {
  filter: saturate(1.12) brightness(1.02) drop-shadow(0 18px 13px rgb(0 0 0 / 37%));
}

.garage-scene .garage-scene__static {
  inset: 0;
  width: 100%;
  height: 100%;
  max-width: none;
  object-fit: cover;
  object-position: center 56%;
  left: 0;
  bottom: 0;
  filter: saturate(1.04) contrast(1.03);
}

.garage-scene .garage-light {
  display: none;
}

.character-scene {
  background: radial-gradient(circle at 50% 110%, rgb(255 255 255 / 74%), transparent 58%);
}

.character-scene .character-scene__full-body {
  width: 100%;
  height: 100%;
  max-width: none;
  border-radius: 0;
  object-fit: cover;
  object-position: center 46%;
  opacity: 1;
  filter: saturate(1.04) contrast(1.02);
  transform: none;
}

.game-card__content {
  padding: 20px 24px 23px;
}

.game-card__round-icon {
  border: 0;
  border-radius: 17px;
  background: rgb(255 255 255 / 76%);
  color: #087e77;
  box-shadow: none;
}

.game-card--character .game-card__round-icon {
  background: rgb(255 255 255 / 78%);
  color: #4e46e5;
}

.game-card h2 {
  color: #101828;
  font-family: inherit;
  font-size: 25px;
}

.game-card__heading p {
  color: #344054;
  font-size: 14px;
}

.feature-list {
  color: #243249;
  margin-block: 15px;
}

.game-card button,
.game-card--character button {
  border: 0;
  border-radius: 16px;
  background: #0b827c;
  color: #fff;
  font-family: inherit;
  box-shadow: none;
  text-transform: none;
  padding-block: 12px;
  font-size: 15px;
}

.game-card--character button {
  background: #4e46e5;
}

.game-card button:active {
  transform: translateY(1px);
  box-shadow: none;
}

/* Quiet, image-first game cards. */
.game-grid {
  gap: 24px;
}

.game-card {
  border: 1px solid rgb(16 24 40 / 8%);
  border-radius: 30px;
  background: #fff;
  box-shadow: 0 22px 55px rgb(31 43 67 / 12%);
}

.game-card__visual {
  height: 410px;
  border: 0;
}

.game-card--car .game-card__visual {
  background: #092e2d;
}

.game-card--character .game-card__visual {
  background: #ffc845;
}

.character-scene {
  padding: 0;
  background: #ffc845;
}

.character-scene .character-scene__full-body {
  object-fit: contain;
  object-position: center;
}

.garage-scene .garage-scene__static {
  object-position: center;
}

.game-card__simple-action {
  padding: 18px;
}

.game-card__simple-action button,
.game-card--character .game-card__simple-action button {
  display: grid;
  grid-template-columns: 76px 1fr 54px;
  min-height: 138px;
  align-items: center;
  padding: 20px 24px;
  border-radius: 24px;
  background: linear-gradient(135deg, #e8faf7, #f7fffd);
  color: #101828;
  text-align: left;
}

.game-card--character .game-card__simple-action button {
  background: linear-gradient(135deg, #f1edff, #fcfaff);
}

.game-card__simple-action button > svg {
  width: 48px;
  height: 48px;
  justify-self: center;
  color: #087e77;
}

.game-card--character .game-card__simple-action button > svg {
  color: #4e46e5;
}

.game-card__simple-action strong {
  font-size: clamp(22px, 2.2vw, 30px);
  font-weight: 900;
}

.game-card__simple-action button span {
  justify-self: center;
  color: #087e77;
  font-size: 36px;
}

.game-card--character .game-card__simple-action button span {
  color: #4e46e5;
}

@media (max-width: 960px) {
  .game-select-shell {
    width: min(100% - 28px, 900px);
  }

  .progress-strip {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 720px) {
  .game-select-shell {
    width: min(100% - 20px, 560px);
    padding-top: 18px;
  }

  .progress-strip {
    grid-template-columns: repeat(2, 1fr);
    margin-bottom: 22px;
  }

  .game-select-hero {
    padding-inline: 8px;
  }

  .game-select-hero h1 {
    font-size: 36px;
  }

  .game-card {
    border-radius: 24px;
  }

  .game-card__simple-action button {
    min-height: 112px;
  }
}
</style>
