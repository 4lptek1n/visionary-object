# -*- coding: utf-8 -*-
CSS = r"""
@layer reset, tokens, base, chrome, blocks, motion, utils;

@layer reset{
  *,*::before,*::after{box-sizing:border-box}
  *{margin:0}
  html{-webkit-text-size-adjust:100%}
  body{-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
  img,svg,video{display:block;max-inline-size:100%}
  img{block-size:auto}
  button,input,select,textarea{font:inherit;color:inherit}
  button{background:none;border:0;cursor:pointer}
  ul,ol{list-style:none;padding:0}
  a{color:inherit;text-decoration:none}
  fieldset{border:0;padding:0}
  legend{padding:0}
}

@layer tokens{
  :root{
    /* ---------- renk: 1stDibs marka değerleri + türetilmiş nötrler ---------- */
    --ecru:#F4F2E3;        /* zemin */
    --band:#EDEBDB;        /* dönüşümlü bölüm tonu, aynı aile */
    --paper:#FFFFFF;       /* kart yüzeyi */
    --ink:#222222;         /* metin ve birincil eylem */
    --ink-2:#5C5A50;       /* ikincil metin      6,15:1 */
    --ink-3:#6E6B5E;       /* künye ve meta      4,75:1 */
    --line:#E0DDCC;        /* dekoratif saç çizgisi */
    --line-ui:#8A8779;     /* etkileşimli kenar  3,20:1 */
    --on-ink:#F4F2E3;      /* koyu dolgu üstü    14,13:1 */

    /* ---------- tipografi ---------- */
    --f-serif:'Crimson',Georgia,'Times New Roman',serif;
    --f-sans:'Instrument',system-ui,-apple-system,sans-serif;
    --f-mono:'Geist',ui-monospace,'SF Mono',monospace;

    --t-hero:clamp(2.35rem,3.7vw + .45rem,4.1rem);
    --t-h2:clamp(1.7rem,2.1vw + .6rem,2.9rem);
    --t-h3:clamp(1.22rem,.8vw + .8rem,1.62rem);
    --t-h4:clamp(1.05rem,.35vw + .88rem,1.22rem);
    --t-body:1rem;
    --t-sm:.875rem;
    --t-xs:.8125rem;
    --t-label:.6875rem;
    --track-label:.14em;

    /* ---------- boşluk: 4px taban ---------- */
    --s1:.25rem;--s2:.5rem;--s3:.75rem;--s4:1rem;--s5:1.25rem;--s6:1.5rem;
    --s8:2rem;--s10:2.5rem;--s12:3rem;--s16:4rem;
    --gap-xs:clamp(.5rem,.8vw,.75rem);
    --gap-s:clamp(.75rem,1.2vw,1.25rem);
    --gap-m:clamp(1.25rem,2vw,2rem);
    --gap-l:clamp(2rem,4vw,4rem);
    --band-s:clamp(2.5rem,4.5vw,4rem);
    --band-m:clamp(6rem,7vw,9rem);
    --band-l:clamp(5.5rem,10vw,9rem);

    --pad:clamp(1.15rem,4vw,4rem);
    --shell:min(1400px, 100% - var(--pad) * 2);
    --shell-narrow:min(920px, 100% - var(--pad) * 2);

    --r:2px;              /* tek köşe sistemi: neredeyse keskin */
    --r-pill:999px;

    --dur-1:.16s; --dur-2:.28s; --dur-3:.45s; --dur-4:.8s; --dur-5:1.15s;
    --ease:cubic-bezier(.16,1,.3,1);
    --ease-io:cubic-bezier(.76,0,.24,1);
    --ease-mask:cubic-bezier(.83,0,.17,1);

    --z-rail:1;--z-grain:4;--z-bar:60;--z-menu:70;--z-dialog:90;--z-skip:100;
  }
}

@layer base{
  html{scroll-behavior:smooth}
  body{
    background:var(--ecru);color:var(--ink);
    font-family:var(--f-sans);font-size:var(--t-body);line-height:1.6;
    font-synthesis-weight:none;overflow-x:clip;
  }
  h1,h2,h3,h4{font-family:var(--f-serif);font-weight:400;line-height:1.12;
              letter-spacing:-.012em;text-wrap:balance}
  p{text-wrap:pretty}
  strong,b{font-weight:700}
  :focus-visible{outline:2px solid var(--ink);outline-offset:2px}
  ::selection{background:var(--ink);color:var(--on-ink)}

  .shell{inline-size:var(--shell);margin-inline:auto}
  .narrow{inline-size:var(--shell-narrow);margin-inline:auto}

  .skip{position:fixed;inset-block-start:-120px;inset-inline-start:1rem;z-index:var(--z-skip);
        background:var(--ink);color:var(--on-ink);padding:.8rem 1.2rem;font-weight:700;
        transition:inset-block-start var(--dur-2) var(--ease)}
  .skip:focus{inset-block-start:1rem}

  .grain{position:fixed;inset:0;z-index:var(--z-grain);pointer-events:none;opacity:.032;
         mix-blend-mode:multiply;background-image:var(--grain-src);background-size:180px 180px}
  @media (prefers-reduced-transparency:reduce){.grain{display:none}}

  /* sol marj boyunca inç skalası: sayfanın kendi ölçüm dili */
  .rail{position:fixed;inset-block:0;inset-inline-start:0;inline-size:var(--pad);
        z-index:var(--z-rail);pointer-events:none;display:none}
  @media (min-width:1460px){.rail{display:block}}
  .rail i{position:absolute;inset-inline-end:6px;inline-size:7px;block-size:1px;background:var(--line-ui);opacity:.42}
  .rail i:nth-of-type(5n+1){inline-size:14px;opacity:.7}
  .rail b{position:absolute;inset-block-end:1.4rem;inset-inline-start:50%;
          transform:translateX(-50%) rotate(180deg);writing-mode:vertical-rl;
          font-family:var(--f-mono);font-size:.6rem;letter-spacing:.24em;
          color:var(--ink-3);font-weight:400}
}

@layer chrome{
  /* ---- duyuru şeridi ---- */
  .promo{background:var(--ink);color:var(--on-ink);text-align:center;
         font-family:var(--f-mono);font-size:.7rem;letter-spacing:.1em;
         text-transform:uppercase;padding-block:.55rem}
  .promo span{opacity:.75}

  /* ---- üst çubuk ---- */
  .masthead{position:sticky;inset-block-start:0;z-index:var(--z-bar);
            background:color-mix(in oklab,var(--ecru) 88%,transparent);
            -webkit-backdrop-filter:blur(14px) saturate(150%);
            backdrop-filter:blur(14px) saturate(150%);
            border-block-end:1px solid var(--line)}
  .mh-top{display:grid;grid-template-columns:auto 1fr auto;gap:var(--gap-m);
          align-items:center;padding-block:var(--s4)}
  /* marka kilidi: goz amblemi + yazi. Amblem musterinin logosundan kesildi. */
  .brand{display:flex;align-items:center;gap:.62rem;min-block-size:44px}
  .brand-mark{inline-size:38px;block-size:38px;object-fit:contain;flex:0 0 auto}
  .brand-type{display:flex;flex-direction:column;line-height:.98;gap:3px;
              justify-content:center}
  .brand b{font-family:var(--f-serif);font-weight:400;font-size:1.5rem;letter-spacing:-.02em}
  .brand i{font-style:normal;font-family:var(--f-mono);font-size:.56rem;
           letter-spacing:.34em;color:var(--ink-3)}
  /* altbilgide logonun tamami */
  .brand--full{display:block;min-block-size:0;inline-size:min(240px,72%)}
  .brand--full img{inline-size:100%;block-size:auto;display:block}
  @media (max-width:640px){ .brand--full{inline-size:min(200px,60%)} }

  .search{position:relative;display:flex;align-items:center;gap:.6rem;
          border:1px solid var(--line-ui);border-radius:var(--r);
          background:var(--paper);padding-inline:.9rem;min-block-size:44px;
          max-inline-size:520px;inline-size:100%;justify-self:center;
          transition:border-color var(--dur-1) ease,box-shadow var(--dur-1) ease}
  .search:focus-within{border-color:var(--ink)}
  .search svg{inline-size:16px;block-size:16px;flex:0 0 auto;color:var(--ink-3)}
  .search input{border:0;background:none;inline-size:100%;font-size:.94rem;
                align-self:stretch;min-block-size:44px}
  .search input:focus{outline:0}
  .search input:focus-visible{outline:2px solid var(--ink);outline-offset:-2px;border-radius:var(--r)}
  .search input::placeholder{color:var(--ink-3)}

  .mh-act{display:flex;align-items:center;gap:.15rem}
  .ico{min-inline-size:44px;min-block-size:44px;display:grid;place-items:center;
       border-radius:var(--r);color:var(--ink);
       transition:background-color var(--dur-1) ease}
  .ico:hover{background:color-mix(in oklab,var(--ink) 7%,transparent)}
  .ico svg{inline-size:19px;block-size:19px}
  .ico span{position:absolute;inline-size:1px;block-size:1px;overflow:hidden;clip-path:inset(50%)}

  /* ---- kategori satırı + mega menü ---- */
  .catnav{border-block-start:1px solid var(--line)}
  .catnav ul{display:flex;gap:clamp(1rem,2.4vw,2.4rem);align-items:stretch;
             overflow-x:auto;scrollbar-width:none}
  .catnav ul::-webkit-scrollbar{display:none}
  .catnav a,.catnav button{display:flex;align-items:center;justify-content:center;
    min-block-size:48px;min-inline-size:44px;padding-inline:.15rem;
    font-size:.86rem;letter-spacing:.02em;color:var(--ink);white-space:nowrap;
    position:relative;background:none}
  .catnav a::after,.catnav button::after{content:"";position:absolute;inset-block-end:0;
    inset-inline:0;block-size:1px;background:var(--ink);transform:scaleX(0);
    transform-origin:right;transition:transform var(--dur-2) var(--ease)}
  .catnav a:hover::after,.catnav button:hover::after,
  .catnav [aria-expanded="true"]::after{transform:scaleX(1);transform-origin:left}
  /* muze sitenin kendi fikri: navigasyonda isaretli */
  .catnav .museum-link{position:relative;padding-inline-start:1.05rem}
  .catnav .museum-link::before{content:"";position:absolute;inset-inline-start:0;
    inset-block-start:50%;inline-size:6px;block-size:6px;border-radius:50%;
    background:var(--ink);translate:0 -50%}
  .catnav .accent{font-family:var(--f-mono);font-size:.72rem;letter-spacing:.1em;
                  text-transform:uppercase;color:var(--ink-3)}

  .mega{position:absolute;inset-inline:0;inset-block-start:100%;z-index:var(--z-menu);
        background:var(--paper);border-block-end:1px solid var(--line);
        box-shadow:0 24px 48px -32px rgb(34 34 34 / .3);
        display:none}
  .mega[data-open]{display:block}
  .mega-in{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--gap-l);
           padding-block:var(--band-s)}
  .mega h3{font-family:var(--f-mono);font-weight:400;font-size:var(--t-label);
           letter-spacing:var(--track-label);text-transform:uppercase;
           color:var(--ink-3);margin-block-end:var(--s4)}
  .mega li a{display:inline-flex;align-items:center;min-block-size:38px;font-size:.92rem;
             border-block-end:1px solid transparent}
  .mega li a:hover{border-block-end-color:var(--ink)}
  .mega-feat{grid-column:span 1}
  .mega-feat figure{position:relative;overflow:hidden;border-radius:var(--r);aspect-ratio:4/3}
  .mega-feat img{inline-size:100%;block-size:100%;object-fit:cover;
                 transition:transform .6s var(--ease)}
  .mega-feat:hover img{transform:scale(1.04)}
  .mega-feat figcaption{margin-block-start:.7rem;font-size:.86rem;color:var(--ink-2)}
  @media (max-width:1023px){.mega{display:none !important}}
}

@layer blocks{
  /* ---------- ortak ---------- */
  .eyebrow{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
           text-transform:uppercase;color:var(--ink-3);display:flex;align-items:center;gap:.6rem}
  .eyebrow::before{content:"";inline-size:22px;block-size:1px;background:var(--line-ui);flex:0 0 auto}
  .mono{font-family:var(--f-mono);font-variant-numeric:tabular-nums;letter-spacing:-.01em}
  .lede{font-size:clamp(1.02rem,.5vw + .9rem,1.2rem);color:var(--ink-2);max-inline-size:56ch;line-height:1.62}

  .sec{padding-block:var(--band-m)}
  .sec--tight{padding-block:var(--band-s)}
  .sec--wide{padding-block:var(--band-l)}
  .sec--band{background:var(--band)}
  .sec--paper{background:var(--paper)}

  .sec-head{display:flex;flex-wrap:wrap;gap:var(--gap-s) var(--gap-m);
            align-items:flex-end;justify-content:space-between;margin-block-end:var(--gap-l)}
  .sec-head h2{font-size:var(--t-h2);max-inline-size:22ch}
  .sec-head .eyebrow{margin-block-end:var(--s3)}

  .lnk{display:inline-flex;align-items:center;gap:.5rem;font-size:.9rem;min-block-size:44px}
  .lnk > span:first-child{border-block-end:1px solid var(--ink);padding-block-end:2px}
  .lnk .arw{transition:transform var(--dur-2) var(--ease)}
  .lnk:hover .arw{transform:translateX(4px)}

  .btn{display:inline-flex;align-items:center;justify-content:center;gap:.7rem;
       min-block-size:48px;padding-inline:1.6rem;border-radius:var(--r);
       font-size:.95rem;font-weight:700;letter-spacing:.01em;border:1px solid transparent;
       transition:background-color var(--dur-2) ease,color var(--dur-2) ease,
                  border-color var(--dur-2) ease,transform var(--dur-1) ease}
  .btn--fill{background:var(--ink);color:var(--on-ink)}
  .btn--fill:hover{background:#000}
  .btn--line{border-color:var(--ink);color:var(--ink)}
  .btn--line:hover{background:var(--ink);color:var(--on-ink)}
  .btn:active{transform:translateY(1px)}
  .btn .arw{transition:transform var(--dur-2) var(--ease)}
  .btn:hover .arw{transform:translateX(4px)}

  /* ---------- 1. HERO: editoryal, tam kanama ---------- */
  .hero{position:relative;background:var(--paper)}
  .hero-in{display:grid;grid-template-columns:1fr;gap:0}
  @media (min-width:960px){.hero-in{grid-template-columns:minmax(0,7fr) minmax(0,5fr);align-items:stretch}}
  /* eser bir duvara asilmis gibi butunuyle gorunur: kirpma yok */
  .hero-media{position:relative;overflow:hidden;block-size:clamp(340px,50vw,640px);
              background:var(--band);
              display:grid;grid-template:minmax(0,1fr) / minmax(0,1fr);
              place-items:center;padding:clamp(1.4rem,4vw,3.4rem)}
  .hero-media::after{content:"";position:absolute;inset-block-end:0;inset-inline:0;
                     block-size:1px;background:var(--line)}
  /* on a phone the hero stacks: the image must not push the action below the fold */
  @media (max-width:959px){.hero-media{block-size:min(42dvh,330px)}
    .hero-copy{padding-block:var(--band-s) var(--band-s)}}
  /* one action in the phone hero, as on the sites this follows */
  @media (max-width:560px){.hero-cta .btn--line{display:none}}
  .hero-media img{position:static;inline-size:auto;block-size:auto;
                  max-inline-size:100%;max-block-size:100%;object-fit:contain;
                  filter:drop-shadow(0 26px 40px rgb(34 34 34 / .16))}
  .hero-copy{display:flex;flex-direction:column;justify-content:center;
             padding:var(--band-s) var(--pad);gap:var(--s5);background:var(--paper)}
  @media (min-width:960px){.hero-copy{padding-inline:clamp(2rem,3.4vw,4rem)}}
  .hero-copy h1{font-size:var(--t-hero);line-height:1.02;letter-spacing:-.022em}
  .hero-copy h1 em{font-style:italic}
  .hero-meta{display:flex;flex-wrap:wrap;gap:.5rem 1.2rem;font-family:var(--f-mono);
             font-size:var(--t-xs);color:var(--ink-3);
             padding-block-start:var(--s4);border-block-start:1px solid var(--line)}
  .hero-cta{display:flex;flex-wrap:wrap;gap:var(--gap-xs)}

  /* ---------- 2. kategori döşemeleri ---------- */
  .tiles{display:grid;gap:var(--gap-s);grid-template-columns:1fr}
  @media (min-width:660px){.tiles{grid-template-columns:repeat(2,1fr)}}
  /* uc kategori + bir "yakinda" paneli tek satiri tam dolduruyor */
  @media (min-width:1000px){.tiles{grid-template-columns:repeat(4,1fr)}
    .tile-soon{grid-column:span 1}}
  .tile-soon{border:1px solid var(--line-ui);padding:var(--gap-s);
             display:flex;flex-direction:column;justify-content:space-between;gap:var(--gap-s);
             background:var(--band)}
  .tile-soon h3{font-size:var(--t-h4);line-height:1.2}
  .tile-soon p{color:var(--ink-2);font-size:.88rem;line-height:1.55;
               max-inline-size:40ch;margin-block-start:.5rem}
  @media (min-width:1000px) and (max-width:1240px){.tile-soon p{display:none}}
  .soon-rows{display:grid;gap:.1rem}
  .soon-rows div{display:flex;justify-content:space-between;align-items:baseline;gap:var(--s3);
                 padding-block:.7rem;border-block-start:1px solid var(--line-ui)}
  .soon-rows span:first-child{font-family:var(--f-serif);font-size:var(--t-h4)}
  .soon-rows span:last-child{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3)}
  .tile{display:block;position:relative}
  .tile figure{position:relative;overflow:hidden;aspect-ratio:3/4;background:var(--band)}
  .tile img{inline-size:100%;block-size:100%;object-fit:cover;transition:transform .7s var(--ease)}
  .tile:hover img{transform:scale(1.045)}
  .tile figcaption{display:flex;align-items:baseline;justify-content:space-between;
                   gap:var(--s3);margin-block-start:.8rem;
                   padding-block-end:.55rem;border-block-end:1px solid var(--line-ui)}
  .tile .name{font-family:var(--f-serif);font-size:var(--t-h4)}
  .tile .cnt{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3);
             font-variant-numeric:tabular-nums}

  /* ---------- ürün kartı: müze künyesi çerçevenin altında ---------- */
  .work{display:grid;grid-row:span 5;grid-template-rows:subgrid;gap:.55rem;
        align-content:start;position:relative}
  @supports not (grid-template-rows:subgrid){.work{grid-row:auto;grid-template-rows:auto}}
  .work-fig{position:relative;overflow:hidden;background:var(--paper);
            border:1px solid var(--line);aspect-ratio:4/5;
            transition:border-color var(--dur-2) ease}
  .work-fig img{inline-size:100%;block-size:100%;object-fit:contain;padding:clamp(10px,1.6vw,22px);
                transition:transform .65s var(--ease)}
  .work:hover .work-fig{border-color:var(--line-ui)}
  /* esere yaklasma hissi: yalnizca transform, hareket azaltma tercihine saygili */
  @media (hover:hover){.work:hover .work-fig img{transform:scale(1.035)}}
  @media (prefers-reduced-motion:reduce){.work-fig img{transition:none}
    .work:hover .work-fig img{transform:none}}
  .work .ttl{font-family:var(--f-serif);font-size:var(--t-h4);line-height:1.24;
             margin-block-start:.35rem}
  .work .by{font-size:var(--t-xs);color:var(--ink-2);line-height:1.45;
            display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
            line-clamp:2;overflow:hidden}
  /* olcu satiri: kucuk cizgi metinle ayni satirda kalir, metin serbestce sarar */
  .work .spec{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3);
              font-variant-numeric:tabular-nums;line-height:1.45;overflow-wrap:break-word}
  .work .spec::before{content:"";display:inline-block;inline-size:12px;block-size:1px;
                      background:var(--line-ui);vertical-align:middle;
                      margin-inline-end:.55rem;margin-block-end:.15em}
  .work .price{font-family:var(--f-mono);font-size:.86rem;font-variant-numeric:tabular-nums;
               padding-block-start:.5rem;border-block-start:1px solid var(--line);
               display:flex;justify-content:space-between;align-items:baseline;gap:.6rem}
  .work .price em{font-style:normal;font-size:var(--t-label);letter-spacing:var(--track-label);
                  text-transform:uppercase;color:var(--ink-3);white-space:nowrap}
  .work a::after{content:"";position:absolute;inset:0}
  .fav{position:absolute;inset-block-start:6px;inset-inline-end:6px;z-index:2;
       inline-size:44px;block-size:44px;display:grid;place-items:center;border-radius:var(--r-pill);
       background:color-mix(in oklab,var(--paper) 82%,transparent);color:var(--ink-2);
       opacity:0;transition:opacity var(--dur-2) ease,color var(--dur-1) ease}
  .work:hover .fav,.fav:focus-visible{opacity:1}
  .fav:hover{color:var(--ink)}
  @media (hover:none){.fav{opacity:1}}

  .grid-works{display:grid;gap:var(--gap-m) var(--gap-s);grid-template-columns:repeat(2,1fr)}
  @media (min-width:760px){.grid-works{grid-template-columns:repeat(3,1fr)}}
  @media (min-width:1180px){.grid-works{grid-template-columns:repeat(4,1fr)}}

  /* ---------- yatay ray ---------- */
  .rail-scroll{display:grid;grid-auto-flow:column;
               grid-auto-columns:minmax(210px,26vw);gap:var(--gap-s);
               overflow-x:auto;scroll-snap-type:x mandatory;
               padding-block-end:var(--s4);scrollbar-width:thin}
  @media (min-width:900px){.rail-scroll{grid-auto-columns:minmax(240px,18vw)}}
  .rail-scroll > *{scroll-snap-align:start;min-inline-size:0}
  .rail-nav{display:none;gap:.4rem}
  @media (min-width:900px){.rail-nav{display:flex}}
  .rail-nav button{inline-size:44px;block-size:44px;display:grid;place-items:center;
    border:1px solid var(--line-ui);border-radius:var(--r);color:var(--ink);
    transition:background-color var(--dur-1) ease,border-color var(--dur-1) ease}
  .rail-nav button:hover{background:var(--ink);color:var(--on-ink);border-color:var(--ink)}
  .rail-nav button[disabled]{opacity:.35;pointer-events:none}
  .rail-scroll .work{grid-row:auto;grid-template-rows:auto}

  /* ---------- öne çıkan eser: yapışkan ---------- */
  .feat{background:var(--band)}
  .feat-in{display:grid;gap:var(--gap-l);grid-template-columns:1fr;align-items:start}
  @media (min-width:980px){.feat-in{grid-template-columns:minmax(0,6fr) minmax(0,5fr)}}
  .feat-media{position:relative;background:var(--paper);border:1px solid var(--line);
              padding:clamp(1.2rem,3vw,3rem)}
  .feat-media img{inline-size:100%;block-size:auto;object-fit:contain;
                  max-block-size:min(74vh,720px);margin-inline:auto}
  @media (min-width:980px){.feat-side{position:sticky;inset-block-start:calc(64px + var(--s8))}}
  .feat h2{font-size:var(--t-h2);margin-block:.6rem var(--s4)}
  .plaque{border-block-start:1px solid var(--line-ui);margin-block:var(--s6)}
  .plaque div{display:flex;gap:var(--gap-s);justify-content:space-between;align-items:baseline;
              padding-block:.7rem;border-block-end:1px solid var(--line)}
  .plaque dt{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
             text-transform:uppercase;color:var(--ink-3)}
  .plaque dd{text-align:end;font-size:.94rem}
  .plaque dd.n{font-family:var(--f-mono);font-variant-numeric:tabular-nums;font-size:.9rem}
  .feat-price{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;
              gap:var(--s3);margin-block-end:var(--s6)}
  .feat-price b{font-family:var(--f-mono);font-weight:400;font-variant-numeric:tabular-nums;
                font-size:clamp(1.5rem,2.4vw,2rem);letter-spacing:-.02em}
  .feat-price span{font-family:var(--f-mono);font-size:var(--t-label);
                   letter-spacing:var(--track-label);text-transform:uppercase;color:var(--ink-3)}

  /* ---------- kademe sistemi ---------- */
  .tiers{display:grid;gap:0;border-block-start:1px solid var(--line-ui)}
  .tier{display:grid;gap:var(--gap-s) var(--gap-m);grid-template-columns:1fr;
        padding-block:var(--s8);border-block-end:1px solid var(--line);align-items:start}
  @media (min-width:820px){.tier{grid-template-columns:3.5rem minmax(11rem,16rem) 1fr;align-items:baseline}}
  .tier .no{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3);
            font-variant-numeric:tabular-nums;letter-spacing:.08em}
  .tier h3{font-size:var(--t-h3)}
  .tier p{color:var(--ink-2);font-size:.96rem;max-inline-size:60ch}
  .tier .band-range{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3);
                    margin-block-start:.5rem;font-variant-numeric:tabular-nums}

  /* ---------- müze modülü ---------- */

  /* ---------- dergi ---------- */
  .posts{display:grid;gap:var(--gap-m);grid-template-columns:1fr}
  @media (min-width:760px){.posts{grid-template-columns:repeat(3,1fr)}}
  .post{display:grid;grid-row:span 4;grid-template-rows:subgrid;gap:.6rem;align-content:start;position:relative}
  @supports not (grid-template-rows:subgrid){.post{grid-row:auto;grid-template-rows:auto}}
  .post figure{overflow:hidden;aspect-ratio:16/10;background:var(--band)}
  .post img{inline-size:100%;block-size:100%;object-fit:cover;transition:transform .7s var(--ease)}
  .post:hover img{transform:scale(1.04)}
  .post .kind{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
              text-transform:uppercase;color:var(--ink-3)}
  .post h3{font-size:var(--t-h4);line-height:1.28}
  .post p{font-size:var(--t-sm);color:var(--ink-2)}
  .post a::after{content:"";position:absolute;inset:0}

  /* ---------- güvence ---------- */
  .promise{display:grid;gap:var(--gap-m);grid-template-columns:1fr}
  @media (min-width:640px){.promise{grid-template-columns:repeat(2,1fr)}}
  @media (min-width:1240px){.promise{grid-template-columns:repeat(6,minmax(0,1fr))}}
  .promise li{padding-block-start:var(--s4);border-block-start:1px solid var(--line-ui)}
  .promise h3{font-family:var(--f-sans);font-weight:700;font-size:.98rem;
              letter-spacing:0;margin-block-end:.4rem}
  .promise p{font-size:var(--t-sm);color:var(--ink-2)}

  /* ---------- bülten ---------- */
  .news{display:grid;gap:var(--gap-m);grid-template-columns:1fr;align-items:end}
  @media (min-width:860px){.news{grid-template-columns:1.1fr 1fr}}
  .news h2{font-size:var(--t-h3)}
  .news p{color:var(--ink-2);font-size:.96rem;max-inline-size:46ch;margin-block-start:.6rem}
  .news form{display:flex;gap:.5rem;flex-wrap:wrap}
  .news label{position:absolute;inline-size:1px;block-size:1px;overflow:hidden;clip-path:inset(50%)}
  .news input{flex:1 1 240px;min-block-size:48px;padding-inline:1rem;
              border:1px solid var(--line-ui);border-radius:var(--r);background:var(--paper)}
  .news input:focus{outline:2px solid var(--ink);outline-offset:1px}
  .news small{display:block;margin-block-start:.7rem;font-size:var(--t-xs);color:var(--ink-3)}

  /* ---------- footer ---------- */
  .foot{background:var(--band);border-block-start:1px solid var(--line-ui)}
  .foot-grid{display:grid;gap:var(--gap-l) var(--gap-m);grid-template-columns:repeat(2,minmax(0,1fr));
             padding-block:var(--band-m)}
  @media (min-width:900px){.foot-grid{grid-template-columns:1.4fr repeat(4,minmax(0,1fr))}}
  .foot h3{font-family:var(--f-mono);font-weight:400;font-size:var(--t-label);
           letter-spacing:var(--track-label);text-transform:uppercase;color:var(--ink-3);
           margin-block-end:var(--s4)}
  .foot li a{display:inline-flex;align-items:center;min-block-size:44px;
             font-size:.9rem;color:var(--ink-2);
             border-block-end:1px solid transparent}
  .foot li a:hover{color:var(--ink);border-block-end-color:var(--ink)}
  .foot-base{display:flex;flex-wrap:wrap;gap:var(--s3) var(--gap-m);justify-content:space-between;
             padding-block:var(--s6);border-block-start:1px solid var(--line-ui);
             font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-2)}
  .foot-note{font-size:var(--t-sm);color:var(--ink-2);max-inline-size:34ch;margin-block-start:var(--s4)}
}

@layer motion{
  .rv{display:block;overflow:hidden}
  .rv > *{display:block;transform:translateY(105%);
          transition:transform var(--dur-4) var(--ease-io) calc(var(--i,0) * .08s)}
  .in .rv > *,.in.rv > *{transform:none}

  .up{opacity:0;transform:translateY(22px);
      transition:opacity var(--dur-3) var(--ease) calc(var(--i,0) * .06s),
                 transform var(--dur-3) var(--ease) calc(var(--i,0) * .06s)}
  .in .up,.in.up{opacity:1;transform:none}
  /* a product card reveals through its mask alone: one move per card,
     so a full row entering stays well under the 30 concurrent animation cap */
  .grid-works .work.up,.rail-scroll .work.up{opacity:1;transform:none;transition:none}


  /* eser açılışı: maske + karşı ölçek */
  .msk{position:relative}
  .msk::after{content:"";position:absolute;inset:0;background:var(--paper);z-index:1;
              transform-origin:top;transform:scaleY(1);
              transition:transform var(--dur-5) var(--ease-mask) calc(var(--i,0) * .07s)}
  .in .msk::after,.in.msk::after{transform:scaleY(0);transform-origin:bottom}
  .work.in .msk::after{transform:scaleY(0)}
  .work.in .msk img{transform:none}
  .msk img{transform:scale(1.18);transition:transform 1.4s var(--ease) calc(var(--i,0) * .07s)}
  .in .msk img,.in.msk img,.in .msk .msk img{transform:none}
  @media (hover:hover) and (pointer:fine){
    .in .tile:hover .msk img,
    .in .post:hover .msk img{transform:scale(1.045);transition-duration:.7s;transition-delay:0s}
  }

  @media (prefers-reduced-motion:reduce){
    html{scroll-behavior:auto}
    *,*::before,*::after{animation-duration:.01ms !important;animation-iteration-count:1 !important;
      transition-duration:.01ms !important;transition-delay:0s !important;scroll-behavior:auto !important}
    .rv > *{transform:none}
    .up{opacity:1;transform:none}
    .msk::after{display:none}
    .msk img{transform:none}
  }
}

@layer utils{
  .sr{position:absolute;inline-size:1px;block-size:1px;padding:0;margin:-1px;
      overflow:hidden;clip-path:inset(50%);white-space:nowrap}
  @media (max-width:959px){
    .hide-s{display:none !important}
    .mh-top{grid-template-columns:auto auto;grid-template-areas:"brand act" "search search";
            row-gap:var(--s3)}
    .brand{grid-area:brand}.mh-act{grid-area:act;justify-self:end}
    .search{grid-area:search;max-inline-size:none}
  }
  @media (min-width:960px){.only-s{display:none !important}}
}
"""
