# -*- coding: utf-8 -*-
"""CSS for the components added to match 1stDibs' page set."""

CSS3 = r"""
@layer chrome{
  /* --- masthead extras --- */
  .mh-auth{display:none;gap:.9rem;align-items:center;font-size:var(--t-xs);
           padding-inline-end:.9rem;margin-inline-end:.2rem;border-inline-end:1px solid var(--line)}
  @media (min-width:900px){.mh-auth{display:flex}}
  .mh-auth button{min-block-size:44px;padding-inline:.2rem;letter-spacing:.02em;
                  border-block-end:1px solid transparent}
  .mh-auth button:hover{border-block-end-color:var(--ink)}
  .search .clr{position:absolute;inset-block-start:50%;translate:0 -50%;inset-inline-end:44px;
               inline-size:32px;block-size:32px;display:none;place-items:center;
               color:var(--ink-3);border-radius:var(--r-pill)}
  .search[data-has] .clr{display:grid}
  .search .clr:hover{color:var(--ink)}
  .search .go{position:absolute;inset-block-start:50%;translate:0 -50%;inset-inline-end:5px;
              inline-size:36px;block-size:36px;display:grid;place-items:center;
              background:var(--ink);color:var(--on-ink);border-radius:var(--r)}
  .search .go svg{inline-size:17px;block-size:17px;color:currentColor}
  .search input{padding-inline-end:88px}
  /* typeahead */
  .sugg{position:absolute;inset-block-start:calc(100% + 4px);inset-inline:0;z-index:70;
        background:var(--paper);border:1px solid var(--line-ui);border-radius:var(--r);
        box-shadow:0 18px 44px -24px rgb(34 34 34/.34);overflow:hidden}
  .sugg[hidden]{display:none}
  .sugg h4{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
           text-transform:uppercase;color:var(--ink-3);padding:.8rem 1rem .3rem}
  .sugg a{display:flex;gap:.8rem;align-items:center;padding:.5rem 1rem;min-block-size:52px}
  .sugg a:hover,.sugg a:focus-visible{background:var(--band)}
  .sugg img{inline-size:40px;block-size:40px;object-fit:contain;background:var(--paper);
            border:1px solid var(--line);flex:0 0 auto}
  .sugg b{font-weight:400;font-family:var(--f-serif);font-size:.98rem;line-height:1.2;
          display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-clamp:2;overflow:hidden}
  .sugg span{font-size:var(--t-xs);color:var(--ink-3)}
  .sugg .all{justify-content:space-between;border-block-start:1px solid var(--line);font-size:.9rem}

  /* --- cart / favorites drawer --- */
  .drawer{position:fixed;inset-block:0;inset-inline-end:0;z-index:90;inline-size:min(400px,92vw);
          background:var(--paper);border-inline-start:1px solid var(--line);
          display:flex;flex-direction:column;translate:100% 0;
          transition:translate var(--dur-3) var(--ease);box-shadow:-30px 0 60px -40px rgb(34 34 34/.4)}
  .drawer[data-open]{translate:0 0}
  /* soldan acilan gezinme cekmecesi (mobil) */
  .drawer--left{inset-inline:0 auto;translate:-102% 0}
  .drawer--left[data-open]{translate:0 0}
  .navlist{list-style:none;margin:0;padding:0}
  .navlist a{display:block;padding-block:.85rem;border-block-end:1px solid var(--line);
             font-family:var(--f-serif);font-size:1.12rem}
  .navlist--s{margin-block-start:1.4rem}
  .navlist--s a{font-family:var(--f-sans);font-size:.94rem;color:var(--ink-2);
                padding-block:.62rem}
  .navlist a:hover{color:var(--ink)}
  .drawer-top{display:flex;justify-content:space-between;align-items:center;
              padding:1.1rem 1.3rem;border-block-end:1px solid var(--line)}
  .drawer-top h2{font-size:1.15rem}
  .drawer-body{flex:1;overflow:auto;padding:1.3rem}
  .drawer-foot{padding:1.1rem 1.3rem;border-block-start:1px solid var(--line)}
  .scrim{position:fixed;inset:0;z-index:89;background:rgb(34 34 34/.44);opacity:0;
         pointer-events:none;transition:opacity var(--dur-2) ease}
  .scrim[data-open]{opacity:1;pointer-events:auto}
  .minirow{display:grid;grid-template-columns:64px 1fr auto;gap:.9rem;align-items:start;
           padding-block:.9rem;border-block-end:1px solid var(--line)}
  .minirow img{inline-size:64px;block-size:64px;object-fit:contain;border:1px solid var(--line);background:var(--paper)}
  .minirow b{font-weight:400;font-family:var(--f-serif);font-size:.95rem;line-height:1.25;display:block}
  .minirow span{display:block;font-size:var(--t-xs);color:var(--ink-3);margin-block-start:.25rem}
  .minirow span:last-of-type{font-family:var(--f-mono);color:var(--ink-2)}
  .minirow button{color:var(--ink-3);font-size:var(--t-xs);min-block-size:44px;
                  border-block-end:1px solid var(--line-ui)}
  .minirow button:hover{color:var(--ink)}
}

@layer blocks{
  /* --- generic info page --- */
  .doc{max-inline-size:74ch;margin-inline:auto;padding-block:var(--band-s) var(--band-l)}
  .doc h1{font-size:clamp(2rem,2.6vw + .8rem,3.1rem);line-height:1.05;margin-block:.5rem 1.4rem}
  .doc h2{font-size:var(--t-h4);margin-block:2.4rem .7rem}
  .doc p{color:var(--ink-2);max-inline-size:70ch;margin-block-end:.9rem;line-height:1.72}
  .doc .lead{font-size:1.1rem;color:var(--ink-2)}
  .doc-nav{display:flex;flex-wrap:wrap;gap:.5rem;margin-block-start:3rem;
           padding-block-start:1.6rem;border-block-start:1px solid var(--line)}
  .doc-nav a{font-size:var(--t-xs);border:1px solid var(--line-ui);border-radius:var(--r-pill);
             padding:.55rem 1rem;min-block-size:44px;display:inline-flex;align-items:center}
  .doc-nav a:hover{background:var(--ink);color:var(--on-ink);border-color:var(--ink)}

  /* --- museum --- */
  .mz-hero{position:relative;min-block-size:min(74dvh,620px);display:grid;
           grid-template-columns:1fr;align-items:end;background:var(--ink);color:var(--on-ink);
           overflow:hidden;isolation:isolate}
  .mz-hero img{position:absolute;inset:0;inline-size:100%;block-size:100%;object-fit:cover;
               opacity:.42;filter:saturate(.85)}
  /* fotografin parlak bolgeleri uzerinde beyaz metnin kontrasti dusuyordu:
     metnin oldugu tarafa dogru koyulasan bir perde */
  .mz-hero::after{content:"";position:absolute;inset:0;z-index:0;pointer-events:none;
    background:
      linear-gradient(102deg, color-mix(in oklab,var(--ink) 90%,transparent) 0%,
                              color-mix(in oklab,var(--ink) 66%,transparent) 40%,
                              transparent 76%),
      linear-gradient(to top, color-mix(in oklab,var(--ink) 78%,transparent) 0%,
                              transparent 58%)}
  .mz-hero .in{position:relative;z-index:1;padding:var(--band-s) var(--pad) var(--band-m);
               max-inline-size:var(--shell);margin-inline:auto;inline-size:100%}
  .mz-hero h1{font-size:clamp(2.3rem,4.4vw + .5rem,4.6rem);line-height:1;letter-spacing:-.02em}
  .mz-hero p{max-inline-size:56ch;color:color-mix(in oklab,var(--on-ink) 82%,transparent);
             margin-block-start:1.1rem;line-height:1.7}
  .mz-hero .eyebrow{color:color-mix(in oklab,var(--on-ink) 70%,transparent)}
  .mz-hero .eyebrow::before{background:color-mix(in oklab,var(--on-ink) 45%,transparent)}
  .rooms{display:grid;gap:var(--gap-l)}
  .room-jump{display:flex;flex-wrap:wrap;gap:.5rem;margin-block-end:var(--gap-l)}
  .room-jump a{font-family:var(--f-mono);font-size:var(--t-xs);letter-spacing:.04em;
               padding:.5rem .85rem;border:1px solid var(--line-ui);border-radius:999px;
               color:var(--ink-2);min-block-size:38px;display:inline-flex;align-items:center}
  .room-jump a:hover{border-color:var(--ink);color:var(--ink)}
  .room-jump a[aria-current="true"]{background:var(--ink);color:var(--on-ink);border-color:var(--ink)}
  .room-no{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
           text-transform:uppercase;color:var(--ink-3);margin-block-end:.35rem}
  /* odanin icindeki eserler: kucuk vitrin */
  .room-strip{display:flex;flex-wrap:wrap;gap:.5rem;margin-block:var(--s5) var(--s5)}
  .room-strip a{inline-size:74px;block-size:74px;display:grid;place-items:center;
                background:var(--paper);border:1px solid var(--line);padding:5px}
  .room-strip a:hover{border-color:var(--ink)}
  .room-strip img{max-inline-size:100%;max-block-size:100%;inline-size:auto;block-size:auto;
                  object-fit:contain}
  /* ana sayfadan bir odaya gelindiginde o oda isaretlenir */
  .room--on{background:var(--band);box-shadow:0 0 0 1px var(--line-ui);
            padding-inline:var(--gap-s);scroll-margin-block-start:140px}
  .room{display:grid;gap:var(--gap-m);align-items:center;
        grid-template-columns:1fr;padding-block:var(--band-s);border-block-end:1px solid var(--line)}
  @media (min-width:900px){
    .room{grid-template-columns:minmax(0,5fr) minmax(0,6fr)}
    .room:nth-child(even) .room-fig{order:2}
  }
  .room-fig{position:relative;overflow:hidden;background:var(--paper);border:1px solid var(--line);
            aspect-ratio:4/3}
  .room-fig img{inline-size:100%;block-size:100%;object-fit:contain;padding:clamp(14px,2vw,34px)}
  .room .no{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
            color:var(--ink-3)}
  .room h2{font-size:var(--t-h2);line-height:1.06;margin-block:.5rem .3rem}
  .room .sub{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
             text-transform:uppercase;color:var(--ink-3)}
  .room p{color:var(--ink-2);margin-block:1rem 1.4rem;max-inline-size:52ch;line-height:1.72}

  /* --- collections --- */
  .colls{display:grid;gap:var(--gap-m);grid-template-columns:1fr}
  @media (min-width:640px){.colls{grid-template-columns:repeat(2,1fr)}}
  @media (min-width:1000px){.colls{grid-template-columns:repeat(4,1fr)}}
  .coll{position:relative;display:block;overflow:hidden;background:var(--paper);
        border:1px solid var(--line)}
  .coll figure{aspect-ratio:1;overflow:hidden}
  .coll img{inline-size:100%;block-size:100%;object-fit:contain;padding:clamp(12px,2vw,26px);
            transition:scale var(--dur-4) var(--ease)}
  .coll:hover img{scale:1.035}
  .coll figcaption{padding:1rem 1.1rem 1.2rem;display:grid;gap:.35rem}
  .coll b{font-weight:400;font-family:var(--f-serif);font-size:1.12rem;line-height:1.2}
  .coll span{font-size:var(--t-xs);color:var(--ink-3)}
  .coll .cta{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
             text-transform:uppercase;margin-block-start:.4rem;display:inline-flex;gap:.4rem;align-items:center}
  .coll .cta::after{content:"→";transition:translate var(--dur-2) var(--ease)}
  .coll:hover .cta::after{translate:4px 0}

  /* --- chips (trending searches) --- */
  .chips{display:flex;flex-wrap:wrap;gap:.55rem}
  .chips a{border:1px solid var(--line-ui);border-radius:var(--r-pill);padding:.6rem 1.05rem;
           font-size:var(--t-xs);min-block-size:44px;display:inline-flex;align-items:center;
           transition:background var(--dur-1) ease,color var(--dur-1) ease,border-color var(--dur-1) ease}
  .chips a:hover{background:var(--ink);color:var(--on-ink);border-color:var(--ink)}

  /* --- editorial band --- */
  .edit{position:relative;overflow:hidden;background:var(--ink);color:var(--on-ink);
        display:grid;grid-template-columns:1fr;align-items:center;min-block-size:min(58dvh,460px)}
  @media (min-width:900px){.edit{grid-template-columns:minmax(0,6fr) minmax(0,5fr)}}
  .edit-fig{position:relative;block-size:100%;min-block-size:260px;overflow:hidden}
  .edit-fig img{position:absolute;inset:0;inline-size:100%;block-size:100%;object-fit:cover}
  .edit-in{padding:var(--band-s) clamp(1.4rem,4vw,4rem)}
  .edit h2{font-size:clamp(1.9rem,2.6vw + .6rem,3rem);line-height:1.04}
  .edit p{color:color-mix(in oklab,var(--on-ink) 80%,transparent);margin-block:1rem 1.6rem;
          max-inline-size:46ch;line-height:1.7}
  .edit .eyebrow{color:color-mix(in oklab,var(--on-ink) 68%,transparent)}
  .edit .eyebrow::before{background:color-mix(in oklab,var(--on-ink) 42%,transparent)}
  .edit .btn--fill{background:var(--on-ink);color:var(--ink);border-color:var(--on-ink)}
  .edit .btn--fill:hover{background:transparent;color:var(--on-ink)}

  /* --- tabs --- */
  .tabs{min-inline-size:0;display:flex;gap:0;border-block-end:1px solid var(--line);
        overflow:auto;scrollbar-width:none}
  .tabs::-webkit-scrollbar{display:none}
  .tabs button{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
               text-transform:uppercase;color:var(--ink-3);padding:.9rem 1.15rem;min-block-size:48px;
               white-space:nowrap;border-block-end:2px solid transparent;margin-block-end:-1px}
  .tabs button[aria-selected="true"]{color:var(--ink);border-block-end-color:var(--ink)}
  .tabs button:hover{color:var(--ink)}

  /* --- quick view --- */
  .qv{position:absolute;inset-block-start:6px;inset-inline-start:6px;z-index:2;
      inline-size:44px;block-size:44px;display:grid;place-items:center;border-radius:var(--r-pill);
      background:color-mix(in oklab,var(--paper) 82%,transparent);color:var(--ink-2);
      opacity:0;transition:opacity var(--dur-2) ease}
  .work:hover .qv,.qv:focus-visible{opacity:1}
  @media (hover:none){.qv{opacity:1}}
  .qv svg{inline-size:17px;block-size:17px}
  .qvbox{display:grid;grid-template-columns:1fr;gap:var(--gap-m)}
  @media (min-width:720px){.qvbox{grid-template-columns:minmax(0,5fr) minmax(0,6fr)}}
  .qvbox figure{background:var(--paper);border:1px solid var(--line);aspect-ratio:4/5;
                display:grid;place-items:center;overflow:hidden}
  .qvbox figure img{inline-size:100%;block-size:100%;object-fit:contain;padding:14px}
  .qvbox dl{display:grid;gap:.4rem;margin-block:1rem;font-size:var(--t-xs)}
  .qvbox dl div{display:flex;gap:.6rem}
  .qvbox dt{color:var(--ink-3);min-inline-size:88px}

  /* --- lightbox --- */
  /* izgara satiri otomatikken img'nin max-block-size:100% degeri cozulmuyor
     ve buyuk kareler ekrandan tasiyordu */
  .lb{position:fixed;inset:0;z-index:95;background:rgb(20 20 20/.94);display:grid;
      grid-template:minmax(0,1fr) / minmax(0,1fr);
      place-items:center;padding:clamp(1rem,4vw,3rem)}
  .lb[hidden]{display:none}
  .lb img{max-inline-size:100%;max-block-size:100%;inline-size:auto;block-size:auto;
          min-inline-size:0;min-block-size:0;object-fit:contain}
  .lb .x,.lb .nav{position:absolute;inline-size:52px;block-size:52px;display:grid;place-items:center;
                  color:#fff;border:1px solid rgb(255 255 255/.3);border-radius:var(--r-pill)}
  .lb .x{inset-block-start:clamp(.8rem,2vw,1.6rem);inset-inline-end:clamp(.8rem,2vw,1.6rem);font-size:1.4rem}
  .lb .nav{inset-block-start:50%;translate:0 -50%}
  .lb .prev{inset-inline-start:clamp(.4rem,2vw,1.6rem)}
  .lb .next{inset-inline-end:clamp(.4rem,2vw,1.6rem)}
  .lb .x:hover,.lb .nav:hover{background:rgb(255 255 255/.14)}
  .lb .cap{position:absolute;inset-block-end:clamp(.8rem,2vw,1.6rem);inset-inline:0;text-align:center;
           color:rgb(255 255 255/.72);font-family:var(--f-mono);font-size:var(--t-xs)}

  /* --- similar strip (pdp top) --- */
  .simbar{background:var(--band);border-block-end:1px solid var(--line);
          padding-block:var(--gap-s)}
  .simbar-in{display:grid;gap:var(--gap-s);grid-template-columns:minmax(0,1fr);align-items:center}
  @media (min-width:820px){.simbar-in{grid-template-columns:230px minmax(0,1fr)}}
  .simbar h2{font-size:.92rem;line-height:1.3;font-family:var(--f-sans);font-weight:400;color:var(--ink-2)}
  .simbar h2 i{display:block;font-family:var(--f-serif);font-style:italic;color:var(--ink);font-size:1rem;
               display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-clamp:2;overflow:hidden}
  .simbar .lnk{font-size:var(--t-xs);margin-block-start:.4rem;display:inline-flex}
  /* izgara ogesinin varsayilan min-width:auto degeri kaydiriciyi buyutup
     dar ekranda sayfayi tasiriyordu */
  .simstrip{min-inline-size:0;display:flex;gap:.6rem;overflow:auto;scroll-snap-type:x mandatory;
            scrollbar-width:none;padding-block:2px}
  .simstrip::-webkit-scrollbar{display:none}
  .simstrip a{flex:0 0 auto;inline-size:96px;block-size:96px;background:var(--paper);
              border:1px solid var(--line);display:grid;place-items:center;scroll-snap-align:start;
              transition:border-color var(--dur-1) ease}
  .simstrip a:hover{border-color:var(--ink)}
  .simstrip img{inline-size:100%;block-size:100%;object-fit:contain;padding:8px}

  /* --- seller badge --- */
  .sellbox{display:flex;gap:.9rem;align-items:center;padding:.9rem 1rem;
           border:1px solid var(--line);border-radius:var(--r);margin-block-start:var(--gap-s)}
  .sellbox .mk{inline-size:40px;block-size:40px;display:grid;place-items:center;flex:0 0 auto;
               background:var(--ink);color:var(--on-ink);font-family:var(--f-serif);font-size:1.1rem}
  .sellbox b{font-weight:400;font-size:.95rem;display:block}
  .sellbox span{font-size:var(--t-xs);color:var(--ink-3);display:flex;gap:.35rem;align-items:center}
  .stars{color:var(--ink);letter-spacing:.1em}

  /* --- empty / state pages --- */
  .statepage{text-align:center;padding-block:var(--band-l);max-inline-size:52ch;margin-inline:auto}
  .statepage h1{font-size:clamp(1.7rem,2.2vw + .7rem,2.5rem);margin-block-end:.9rem}
  .statepage p{color:var(--ink-2);line-height:1.7}
  .statepage .btn{margin-block-start:1.8rem}

  /* --- creators / sitemap lists --- */
  .cols3{columns:1;column-gap:var(--gap-m)}
  @media (min-width:640px){.cols3{columns:2}}
  @media (min-width:1000px){.cols3{columns:3}}
  .cols3 a{display:flex;justify-content:space-between;gap:1rem;break-inside:avoid;
           min-block-size:44px;align-items:center;border-block-end:1px solid var(--line);
           font-size:.96rem}
  .cols3 a:hover{color:var(--ink)}
  .cols3 em{font-style:normal;font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3)}
  .maplist{display:grid;gap:var(--gap-m);grid-template-columns:1fr}
  @media (min-width:700px){.maplist{grid-template-columns:repeat(2,1fr)}}
  @media (min-width:1040px){.maplist{grid-template-columns:repeat(4,1fr)}}
  .maplist h2{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
              text-transform:uppercase;color:var(--ink-3);margin-block-end:.7rem}
  .maplist a{display:block;min-block-size:44px;display:flex;align-items:center;font-size:.95rem;color:var(--ink-2)}
  .maplist a:hover{color:var(--ink)}

  /* --- seo copy at foot of a listing page --- */
  .seo{border-block-start:1px solid var(--line);margin-block-start:var(--band-s);
       padding-block:var(--band-s)}
  .seo h2{font-size:var(--t-h4);margin-block-end:.8rem}
  .seo p{color:var(--ink-2);max-inline-size:74ch;line-height:1.72;margin-block-end:.8rem;font-size:.96rem}
  .qa{margin-block-start:var(--gap-m);max-inline-size:74ch}
  .qa details{border-block-end:1px solid var(--line)}
  .qa summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:1rem;
              padding-block:1rem;min-block-size:56px;align-items:center;font-size:1rem}
  .qa summary::-webkit-details-marker{display:none}
  .qa summary::after{content:"";inline-size:9px;block-size:9px;border-inline-end:1px solid var(--ink-2);
                     border-block-end:1px solid var(--ink-2);rotate:45deg;flex:0 0 auto;
                     transition:rotate var(--dur-2) var(--ease)}
  .qa details[open] summary::after{rotate:225deg}
  .qa p{color:var(--ink-2);padding-block-end:1.1rem;line-height:1.7;font-size:.96rem}

  /* --- colour swatch filter --- */
  .swatches{display:flex;flex-wrap:wrap;gap:.5rem;padding-block:.4rem}
  .swatches label{position:relative;inline-size:44px;block-size:44px;display:grid;place-items:center;cursor:pointer}
  .swatches i{inline-size:26px;block-size:26px;border-radius:var(--r-pill);
              border:1px solid var(--line-ui);display:block}
  .swatches input{position:absolute;opacity:0;inline-size:44px;block-size:44px;margin:0;cursor:pointer}
  .swatches input:checked + i{outline:2px solid var(--ink);outline-offset:3px}
  .swatches input:focus-visible + i{outline:2px solid var(--ink);outline-offset:3px}

  /* --- newsletter / footer extras --- */
  .news-form{display:flex;gap:.5rem;margin-block:.8rem;max-inline-size:340px}
  .news-form input{flex:1 1 0;min-inline-size:0;min-block-size:46px;padding-inline:.9rem;background:var(--paper);
                   border:1px solid var(--line-ui);border-radius:var(--r);font-size:.92rem;color:var(--ink)}
  .news-form button{min-block-size:46px;padding-inline:1.1rem;background:var(--ink);color:var(--on-ink);
                    border-radius:var(--r);font-family:var(--f-mono);font-size:var(--t-label);
                    letter-spacing:var(--track-label);text-transform:uppercase}
  .news-note{font-size:var(--t-xs);color:var(--ink-3);line-height:1.6;max-inline-size:340px}
  .news-note a{border-block-end:1px solid var(--line-ui)}
  .social{display:flex;gap:.6rem;margin-block-start:1.1rem}
  .social a{inline-size:44px;block-size:44px;display:grid;place-items:center;color:var(--ink-2);
            border:1px solid var(--line);border-radius:var(--r-pill)}
  .social a:hover{color:var(--ink);border-color:var(--line-ui)}
  .social svg{inline-size:17px;block-size:17px}
  .disp{display:flex;flex-wrap:wrap;gap:.35rem .9rem;align-items:center;max-inline-size:100%;font-family:var(--f-mono);
        font-size:var(--t-label);letter-spacing:var(--track-label);text-transform:uppercase;
        color:var(--ink-3);padding-block:1rem}
  .disp select{font:inherit;letter-spacing:inherit;text-transform:inherit;color:var(--ink-2);
               background:transparent;border:1px solid var(--line);border-radius:var(--r);
               min-block-size:44px;padding-inline:.6rem;min-inline-size:0;max-inline-size:100%;
               inline-size:auto;flex:0 1 auto}
  .search .go{inline-size:44px;block-size:44px}
  .search input{padding-inline-end:96px}
  .mh-act .ico{flex:0 0 auto;min-inline-size:44px}
  .foot-base a,.foot-base button{display:inline-flex;align-items:center;min-block-size:44px}
  .foot li a{white-space:normal;overflow-wrap:anywhere}
  .work .price{flex-wrap:wrap}
  .work .price span,.work .price em{white-space:nowrap}
  /* dar iki sutunlu izgarada fiyat satiri kirpilmasin */
  @media (max-width:520px){
    .work .price{font-size:.76rem;column-gap:.4rem}
    .work .price span{white-space:normal}
    .work .spec{font-size:.68rem}
  }

  /* --- cookie bar --- */
  .cookie{position:fixed;inset-inline:0;inset-block-end:0;z-index:88;background:var(--paper);
          border-block-start:1px solid var(--line-ui);box-shadow:0 -20px 40px -34px rgb(34 34 34/.4);
          padding:1.1rem var(--pad)}
  .cookie[hidden]{display:none}
  .cookie-in{max-inline-size:var(--shell);margin-inline:auto;display:grid;gap:1rem;
             grid-template-columns:1fr;align-items:center}
  @media (min-width:860px){.cookie-in{grid-template-columns:1fr auto}}
  .cookie p{font-size:.92rem;color:var(--ink-2);max-inline-size:70ch;line-height:1.6}
  .cookie p a{border-block-end:1px solid var(--line-ui);color:var(--ink)}
  .cookie .acts{display:flex;flex-wrap:wrap;gap:.6rem}
  .cookie .btn{padding-inline:1.2rem}
}

@layer motion{
  @media (prefers-reduced-motion:no-preference){
    .room .room-fig{clip-path:inset(0 0 0 0)}
    .drawer[data-open],.scrim[data-open]{will-change:translate,opacity}
  }
}

@layer chrome{
  .ico .cnt-b,.cnt-b{position:absolute;clip-path:none;inset-block-start:2px;inset-inline-end:2px;min-inline-size:17px;
         block-size:17px;padding-inline:4px;display:grid;place-items:center;border-radius:var(--r-pill);
         background:var(--ink);color:var(--on-ink);font-family:var(--f-mono);font-size:.625rem;
         line-height:1;font-variant-numeric:tabular-nums}
  .cnt-b[hidden]{display:none}
  .mh-act .ico{position:relative}
  .mega-tile{display:grid;gap:.7rem;align-content:start}
  .mega-fig{display:block;aspect-ratio:4/3;background:var(--band) center/contain no-repeat;
            border:1px solid var(--line)}
  .mega-cap{display:flex;flex-direction:column;gap:.25rem}
  .mega-cap b{font-weight:400;font-family:var(--f-serif);font-size:1.05rem}
  .mega-cap i{font-style:normal;font-family:var(--f-mono);font-size:var(--t-label);
              letter-spacing:var(--track-label);text-transform:uppercase;color:var(--ink-3)}
  .mega-tile:hover .mega-cap i{color:var(--ink)}
  .foot-base button{font:inherit;letter-spacing:inherit;color:inherit;text-transform:inherit}
  .foot-base button:hover,.foot-base a:hover{color:var(--ink)}
}

@layer blocks{
  .buy-top{display:flex;justify-content:space-between;align-items:flex-start;gap:1rem}
  .buy-save{display:flex;gap:.4rem}
  .buy-save .fav{position:static;opacity:1;inline-size:44px;block-size:44px;background:none;color:var(--ink-2)}
  .buy-save .fav:hover{color:var(--ink);background:var(--band)}
  .buy-save .fav svg{inline-size:20px;block-size:20px}
  .iconb{inline-size:44px;block-size:44px;display:grid;place-items:center;color:var(--ink-2);
         border-radius:var(--r-pill)}
  .iconb:hover{color:var(--ink);background:var(--band)}
  .iconb svg{inline-size:20px;block-size:20px}
  .creatorline{font-family:var(--f-serif);font-size:1.22rem;line-height:1.2;margin-block:.5rem .35rem}
  .creatorline a{border-block-end:1px solid var(--line-ui)}
  .creatorline a:hover{border-block-end-color:var(--ink)}
  .btn--ghost{border:1px solid var(--line);color:var(--ink-2);background:transparent}
  .btn--ghost:hover{border-color:var(--ink);color:var(--ink)}
  .lnk-s{font-size:inherit;color:var(--ink);border-block-end:1px solid var(--line-ui);
         min-block-size:0;padding:0}
  .lnk-s:hover{border-block-end-color:var(--ink)}
  .lnk-in{border-block-end:1px solid var(--line-ui)}
  .lnk-in:hover{border-block-end-color:var(--ink)}
  .zoomb{position:absolute;inset-block-end:10px;inset-inline-start:10px;inline-size:40px;block-size:40px;
         display:grid;place-items:center;background:color-mix(in oklab,var(--paper) 88%,transparent);
         border:1px solid var(--line);border-radius:var(--r);color:var(--ink-2)}
  .zoomb{inline-size:44px;block-size:44px}
  .zoomb:hover{color:var(--ink);border-color:var(--line-ui)}
  .zoomb svg{inline-size:18px;block-size:18px}
  .stage img{cursor:zoom-in}

  /* ---- buyutec ----
     Gercek bir buyutec gibi calisir: imlecin altindaki bolgeyi, fotografin
     kendi cozunurlugunde gosterir. Buyutme orani fotografa gore hesaplanir,
     yani goruntu bulanik buyutulmez; ne kadar detay varsa o kadar gosterilir.
     Dokunmatikte gizli: orada parmak imlecin yerini tutmuyor, tam ekran acilir. */
  .loupe{position:absolute;pointer-events:none;z-index:3;border-radius:var(--r-pill);
         inline-size:var(--loupe,240px);block-size:var(--loupe,240px);
         background-repeat:no-repeat;background-color:var(--paper);
         box-shadow:0 10px 34px rgb(0 0 0/.22),0 0 0 1px var(--line-ui),
                    inset 0 0 0 4px rgb(255 255 255/.92);
         opacity:0;scale:.92;transform-origin:center;
         transition:opacity .13s ease,scale .13s ease}
  .loupe[data-on]{opacity:1;scale:1}
  .stage[data-loupe] img{cursor:none}
  @media (hover:none),(pointer:coarse){ .loupe{display:none} }
  @media (prefers-reduced-motion:reduce){ .loupe{transition:none} }

  /* tam ekranda tikla-yaklas: dokunmatikte de calisir */
  .lb img{cursor:zoom-in;touch-action:none}
  .lb img[data-zoom]{cursor:grab;max-inline-size:none;max-block-size:none}
  .lb img[data-zoom][data-grab]{cursor:grabbing}
  .lb .hint{position:absolute;inset-block-start:clamp(.8rem,2vw,1.6rem);inset-inline-start:0;
            inset-inline-end:0;text-align:center;color:rgb(255 255 255/.62);
            font-family:var(--f-mono);font-size:.62rem;letter-spacing:.16em;
            text-transform:uppercase;pointer-events:none}
  .pdp-doc{max-inline-size:900px;margin-block-start:var(--gap-m)}
  .pdp-h{font-size:var(--t-h3);margin-block:var(--gap-m) var(--s5)}
  .pdp-p{color:var(--ink-2);max-inline-size:70ch;margin-block-end:.9rem;line-height:1.72}
  .dot{display:inline-block;inline-size:11px;block-size:11px;border-radius:var(--r-pill);
       border:1px solid var(--line-ui);margin-inline-end:.35rem;vertical-align:-1px}
  .totop{position:fixed;inset-block-end:calc(clamp(1rem,3vw,2rem) + var(--ck-h,0px));inset-inline-end:clamp(1rem,3vw,2rem);
         z-index:80;inline-size:56px;block-size:56px;border-radius:var(--r-pill);
         background:color-mix(in oklab,var(--ecru) 92%,transparent);border:1px solid var(--line-ui);
         -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
         display:grid;place-items:center;gap:1px;color:var(--ink-2);
         font-family:var(--f-mono);font-size:.58rem;letter-spacing:.14em;
         animation:pop var(--dur-2) var(--ease)}
  .totop[hidden]{display:none}
  .totop:hover{color:var(--ink);border-color:var(--ink)}
  .totop .ar{inline-size:9px;block-size:9px;border-block-start:1px solid currentColor;
             border-inline-start:1px solid currentColor;rotate:45deg;margin-block-start:4px}
  @keyframes pop{from{opacity:0;translate:0 8px}to{opacity:1;translate:0 0}}
  @media (prefers-reduced-motion:reduce){.totop{animation:none}}
  .related{margin-block-start:var(--band-s);padding-block-start:var(--gap-m);
           border-block-start:1px solid var(--line)}
  .related h2{font-size:var(--t-h4);margin-block-end:var(--gap-s)}
  .related-all{margin-block-start:var(--gap-m);text-align:center}
  .related-all a{border-block-end:1px solid var(--line-ui);min-block-size:44px;
                 display:inline-flex;align-items:center;font-size:.95rem;color:var(--ink-2)}
  .related-all a:hover{color:var(--ink)}
  .related-all b{font-weight:400;color:var(--ink)}
  #topSentinel{position:absolute;inset-block-start:0;block-size:1px;inline-size:1px}
  .filter-btn{display:none}
  .filters-top,.filters-foot{display:none}
  @media (max-width:999px){
    .filter-btn{display:inline-flex;align-items:center;gap:.6rem;min-block-size:48px;
                padding-inline:1.1rem;border:1px solid var(--line-ui);border-radius:var(--r);
                background:var(--paper);font-family:var(--f-mono);font-size:var(--t-label);
                letter-spacing:var(--track-label);text-transform:uppercase;
                margin-block-end:var(--gap-s)}
    .filter-btn svg{inline-size:16px;block-size:16px}
    .filter-btn:hover{border-color:var(--ink)}
    .filters{position:fixed;inset:0;z-index:92;background:var(--ecru);
             border:0;overflow-y:auto;padding:0 var(--pad) 0;
             translate:0 100%;transition:translate var(--dur-3) var(--ease);
             visibility:hidden;max-block-size:none}
    .filters[data-open]{translate:0 0;visibility:visible}
    .filters-top{display:flex;justify-content:space-between;align-items:center;
                 position:sticky;inset-block-start:0;background:var(--ecru);z-index:2;
                 padding-block:1rem;border-block-end:1px solid var(--line)}
    .filters-top h2{font-size:1.2rem}
    .filters-foot{display:block;position:sticky;inset-block-end:0;background:var(--ecru);
                  padding-block:1rem;border-block-start:1px solid var(--line)}
  }
  .fback{padding-block:.2rem .5rem}
  .fback a{font-size:var(--t-xs);color:var(--ink-3);min-block-size:36px;display:inline-flex;align-items:center;
           border-block-end:1px solid var(--line-ui)}
  .fback a:hover{color:var(--ink)}
  @media (max-width:620px){.promo span{display:none}}
  .promo a{border-block-end:1px solid color-mix(in oklab,var(--on-ink) 50%,transparent);
           margin-inline-start:.5rem}
  .promo a:hover{border-block-end-color:var(--on-ink)}
  .fsub{padding-block:.4rem .6rem}
  .fsub input{inline-size:100%;min-block-size:44px;padding-inline:.7rem;font-size:.9rem;
              background:var(--paper);border:1px solid var(--line-ui);border-radius:var(--r);color:var(--ink)}
  .sw-l{position:relative;inline-size:44px;block-size:44px;display:grid;place-items:center;cursor:pointer}
  .sw-l input{position:absolute;opacity:0;inline-size:44px;block-size:44px;margin:0;cursor:pointer}
  .sw-l i{inline-size:26px;block-size:26px;border-radius:var(--r-pill);border:1px solid var(--line-ui);display:block}
  .sw-l input:checked + i{outline:2px solid var(--ink);outline-offset:3px}
  .sw-l input:focus-visible + i{outline:2px solid var(--ink);outline-offset:3px}
  .sw-l input:disabled + i{opacity:.3}
  .fgroup li[data-zero] .fopt{opacity:.42}
  .dbox--wide{max-inline-size:820px}
  .dprose p{color:var(--ink-2);font-size:.95rem;line-height:1.7;margin-block-end:.8rem}
  .simbar .lnk{color:var(--ink)}
  /* izgara rayinda kartin genisligini sutun belirler; sabit genislik
     kartlarin birbirinin uzerine tasmasina yol aciyordu */
  .rail2 .work{inline-size:100%;min-inline-size:0}
  .rail-scroll .work{align-self:stretch}
  .rail-scroll .work .ttl{min-block-size:1.25em}
  .rail-scroll .work .by{min-block-size:2.9em}
  /* iki satirlik yer ayrilarak kartlar hizali kaliyor */
  .rail-scroll .work .spec{min-block-size:2.9em}
  .rail-scroll .work .price{margin-block-start:auto}
}

@layer blocks{
  /* intrinsic sizing everywhere: no layout shift while images decode */
  .simstrip a,.thumbs button{aspect-ratio:1}
  .simstrip img,.thumbs img{aspect-ratio:1;object-fit:contain}
  .subcat figure{aspect-ratio:7/8}
  .subcat img{aspect-ratio:7/8;object-fit:contain}
  .sugg img{aspect-ratio:1}
  .minirow img{aspect-ratio:1}
  .lb img{aspect-ratio:auto;contain-intrinsic-size:70vmin 70vmin}
  .hero-media,.edit-fig,.mz-hero{contain-intrinsic-size:auto 480px}
  .stage img{contain-intrinsic-size:auto 520px}
  /* the router fills #app after parse: reserve the viewport so nothing jumps */
  #app{min-block-size:100dvh}
  #app:empty{min-block-size:100dvh}
}
"""


# ---------------------------------------------------------------- fiyat ve kampanya
# Indirim tek renkle degil, ustu cizili eski fiyatla da anlatilir: bilgi
# yalnizca renkle tasinmaz. Rakamlar tabular-nums, satirda sarkma olmaz.
CSS3 += """
@layer blocks{
  .p-now{font-weight:600;font-variant-numeric:tabular-nums}
  .p-was{color:var(--ink-3);text-decoration:line-through;
         text-decoration-thickness:1px;font-variant-numeric:tabular-nums;margin-inline-start:.35rem}
  .p-off{font-style:normal;font-size:.78em;letter-spacing:.06em;text-transform:uppercase;
         color:var(--ink);border:1px solid var(--line-ui);padding:.05em .4em;
         margin-inline-start:.4rem;white-space:nowrap}
  .p-sold,.p-res{font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-size:.86em}
  .p-sold{color:var(--ink-3)}
  .askprice .p-now{font-size:1.06em}
  .askprice s,.askprice em{font-size:.82em}
  .work .price s,.work .price em{font-size:.9em}

  .kmp{display:flex;align-items:center;justify-content:center;gap:.6rem;flex-wrap:wrap;
       background:var(--ink);color:var(--on-ink);padding:.55rem var(--pad);
       font-size:.82rem;letter-spacing:.02em;text-align:center}
  .kmp b{font-weight:500;letter-spacing:.1em;text-transform:uppercase;font-size:.72rem}
  .kmp a{color:inherit;text-underline-offset:3px}
  @media (max-width:640px){ .kmp{font-size:.76rem;padding-inline:1rem} }
}
"""
