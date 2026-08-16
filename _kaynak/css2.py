# -*- coding: utf-8 -*-
"""Koleksiyon ve ürün sayfası bileşenleri. site_css.CSS'in üzerine eklenir."""
CSS2 = r"""
@layer blocks{
  /* ---------- kırıntı yolu ---------- */
  .crumbs{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;
          font-size:var(--t-xs);color:var(--ink-3);padding-block:var(--s5) 0}
  .crumbs a,.crumbs span[aria-current]{display:inline-flex;align-items:center;min-block-size:26px}
  .crumbs a{border-block-end:1px solid transparent}
  .crumbs a:hover{border-block-end-color:var(--ink-2);color:var(--ink)}
  .crumbs span[aria-current]{color:var(--ink-2)}
  .crumbs i{font-style:normal;opacity:.5}

  /* ---------- koleksiyon başlığı ---------- */
  .coll-top{display:flex;flex-wrap:wrap;gap:var(--gap-s) var(--gap-m);
            align-items:center;padding-block:var(--s6) var(--s8)}
  .coll-top h1{font-size:clamp(1.9rem,2.4vw + .7rem,2.9rem)}
  .btn-save{display:inline-flex;align-items:center;gap:.55rem;min-block-size:44px;
            padding-inline:1.1rem;border:1px solid var(--line-ui);border-radius:var(--r);
            font-size:var(--t-label);letter-spacing:var(--track-label);text-transform:uppercase;
            font-family:var(--f-mono);
            transition:border-color var(--dur-1) ease,background-color var(--dur-1) ease}
  .btn-save:hover{border-color:var(--ink);background:var(--paper)}
  .btn-save svg{inline-size:15px;block-size:15px}

  /* ---------- alt kategori döşemeleri ---------- */
  .subcats{display:grid;gap:var(--gap-s);
           grid-template-columns:repeat(auto-fit,minmax(min(210px,100%),1fr));
           margin-block-end:var(--band-s)}
  @media (max-width:700px){
    .subcats{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;
             margin-inline:calc(var(--pad) * -1);padding-inline:var(--pad);
             margin-block-end:var(--gap-m)}
    .subcats::-webkit-scrollbar{display:none}
    .subcat{flex:0 0 auto;inline-size:min(74vw,260px);scroll-snap-align:start}
  }
  .subcat{display:flex;align-items:center;gap:.9rem;padding:.8rem;
          border:1px solid var(--line);background:var(--paper);
          transition:border-color var(--dur-1) ease,background-color var(--dur-1) ease}
  .subcat:hover{border-color:var(--line-ui);background:var(--band)}
  .subcat figure{inline-size:56px;block-size:64px;flex:0 0 auto;overflow:hidden;background:var(--band)}
  .subcat img{inline-size:100%;block-size:100%;object-fit:contain}
  .subcat b{font-family:var(--f-serif);font-weight:400;font-size:.98rem;line-height:1.2}
  .subcat span{display:block;font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3);
               margin-block-start:.2rem;font-variant-numeric:tabular-nums}

  /* ---------- koleksiyon gövdesi: sol süzgeç + ızgara ---------- */
  .coll-body{display:grid;gap:var(--gap-l);grid-template-columns:1fr;align-items:start}
  @media (min-width:1000px){.coll-body{grid-template-columns:250px minmax(0,1fr)}}
  /* with the filter rail present the grid needs one column fewer */
  @media (min-width:1000px) and (max-width:1179px){.coll-body .grid-works{grid-template-columns:repeat(2,1fr)}}
  @media (min-width:1180px) and (max-width:1419px){.coll-body .grid-works{grid-template-columns:repeat(3,1fr)}}

  .filters{border-block-start:1px solid var(--line-ui)}
  @media (min-width:1000px){.filters{position:sticky;inset-block-start:calc(64px + 1rem);
    max-block-size:calc(100dvh - 6rem);overflow-y:auto;scrollbar-width:thin}}
  .fsearch{display:flex;align-items:center;gap:.5rem;border:1px solid var(--line-ui);
           background:var(--paper);padding-inline:.75rem;min-block-size:44px;margin-block:var(--s5)}
  .fsearch{inline-size:100%}
  .fsearch input{border:0;background:none;inline-size:100%;min-inline-size:0;font-size:.9rem;min-block-size:44px}
  .fsearch input:focus-visible{outline:2px solid var(--ink);outline-offset:-2px}
  .fsearch svg{inline-size:15px;block-size:15px;color:var(--ink-3);flex:0 0 auto}

  .fgroup{border-block-end:1px solid var(--line)}
  .fgroup > summary{display:flex;align-items:center;justify-content:space-between;
    gap:.5rem;min-block-size:52px;cursor:pointer;list-style:none;
    font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
    text-transform:uppercase;color:var(--ink)}
  .fgroup > summary::-webkit-details-marker{display:none}
  .fgroup > summary::after{content:"";inline-size:9px;block-size:9px;flex:0 0 auto;
    border-inline-end:1px solid var(--ink-2);border-block-end:1px solid var(--ink-2);
    transform:rotate(45deg) translate(-2px,-2px);transition:transform var(--dur-2) var(--ease)}
  .fgroup[open] > summary::after{transform:rotate(-135deg) translate(-3px,-3px)}
  .fgroup ul{padding-block-end:var(--s4)}
  .fopt{display:flex;align-items:center;gap:.6rem;min-block-size:44px;
        font-size:.9rem;color:var(--ink-2);cursor:pointer;
        transition:color var(--dur-1) ease}
  .fopt:hover{color:var(--ink)}
  .fopt input{inline-size:15px;block-size:15px;accent-color:var(--ink);flex:0 0 auto;margin:0}
  .fopt .n{margin-inline-start:auto;font-family:var(--f-mono);font-size:var(--t-xs);
           color:var(--ink-3);font-variant-numeric:tabular-nums}

  .sortbar{display:flex;flex-wrap:wrap;gap:var(--gap-s);align-items:center;
           justify-content:space-between;padding-block-end:var(--s5);
           border-block-end:1px solid var(--line)}
  .count,.sortbar .count{font-family:var(--f-serif);font-style:italic;font-size:1.05rem;font-weight:400;letter-spacing:0}
  .count b,.sortbar .count b{font-style:normal;font-family:var(--f-mono);font-variant-numeric:tabular-nums;
                    font-weight:400}
  .selwrap{display:flex;gap:.5rem}
  .sel{position:relative;display:inline-flex;align-items:center}
  .sel select{appearance:none;border:1px solid var(--line-ui);background:var(--paper);
    min-block-size:44px;padding-inline:.9rem 2.2rem;font-size:.9rem;border-radius:var(--r);
    cursor:pointer}
  .sel::after{content:"";position:absolute;inset-inline-end:.85rem;inline-size:7px;block-size:7px;
    border-inline-end:1px solid var(--ink-2);border-block-end:1px solid var(--ink-2);
    transform:rotate(45deg) translateY(-2px);pointer-events:none}

  .chips-active{display:flex;flex-wrap:wrap;gap:.4rem;padding-block:var(--s4)}
  .chip-x{display:inline-flex;align-items:center;gap:.5rem;min-block-size:36px;
    padding-inline:.75rem;border:1px solid var(--line-ui);border-radius:var(--r);
    font-size:var(--t-xs);background:var(--paper)}
  .chip-x b{font-weight:400}
  .chip-x span{font-size:1rem;line-height:1;color:var(--ink-3)}
  .chip-x:hover span{color:var(--ink)}

  /* urun sayfasindan muzeye baglanti */
  .in-room{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3);
           line-height:1.6;margin-block-start:.7rem}
  .in-room svg{display:inline-block;inline-size:15px;block-size:15px;
               vertical-align:-3px;margin-inline-end:.45rem}
  .in-room a{color:var(--ink-2);border-block-end:1px solid var(--line-ui)}
  .in-room a:hover{color:var(--ink);border-block-end-color:var(--ink)}

  .empty{padding-block:var(--band-m);text-align:center;border:1px solid var(--line);
         background:var(--paper)}
  .empty h2,.empty h3{font-size:var(--t-h3);margin-block-end:.6rem}
  .empty p{color:var(--ink-2);max-inline-size:46ch;margin-inline:auto}
  .empty p:last-child{display:flex;flex-wrap:wrap;gap:.6rem;justify-content:center}

  .pager{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;justify-content:center;
         padding-block:var(--band-s)}
  .pager button{min-inline-size:44px;min-block-size:44px;padding-inline:.6rem;
    border:1px solid transparent;border-radius:var(--r);font-family:var(--f-mono);
    font-size:.85rem;font-variant-numeric:tabular-nums;
    transition:border-color var(--dur-1) ease,background-color var(--dur-1) ease}
  .pager button:hover{border-color:var(--line-ui)}
  .pager button[aria-current="page"]{background:var(--ink);color:var(--on-ink);border-color:var(--ink)}
  .pager button[disabled]{opacity:.3;pointer-events:none}

  /* ---------- ürün sayfası ---------- */
  /* minmax(0,1fr): kaydirilabilir sekmeler ve kucuk resim seridi izgara
     sutununu genisletip dar ekranda sayfayi tasitmiyor */
  .pdp{display:grid;gap:var(--gap-l);grid-template-columns:minmax(0,1fr);align-items:start;
       padding-block:var(--s6) var(--band-m)}
  .pdp>*{min-inline-size:0}
  @media (min-width:1000px){.pdp{grid-template-columns:minmax(0,1fr) 400px}
    /* belge blogu galeriyle ayni sutunda: satin alma kutusu kisa kalinca
       altinda bos bir alan olusmuyor */
    .pdp>.gal{grid-column:1;grid-row:1}
    .pdp>.buy{grid-column:2;grid-row:1 / span 2}
    .pdp>.pdp-doc{grid-column:1;grid-row:2;margin-block-start:var(--gap-l)}}
  @media (min-width:1300px){.pdp{grid-template-columns:minmax(0,1fr) 440px}}

  .gal{display:grid;gap:var(--gap-s);grid-template-columns:1fr}
  @media (min-width:700px){.gal{grid-template-columns:72px minmax(0,1fr)}}
  .thumbs{display:flex;gap:.5rem;overflow-x:auto;scrollbar-width:none;order:2}
  .thumbs::-webkit-scrollbar{display:none}
  @media (min-width:700px){.thumbs{order:0;flex-direction:column;overflow-x:visible;
    overflow-y:auto;max-block-size:620px}}
  .thumbs button{flex:0 0 auto;inline-size:64px;block-size:72px;padding:3px;
    border:1px solid var(--line);background:var(--paper);
    transition:border-color var(--dur-1) ease}
  .thumbs button img{inline-size:100%;block-size:100%;object-fit:contain}
  .thumbs button[aria-current="true"]{border-color:var(--ink);border-inline-start-width:2px}
  .thumbs button:hover{border-color:var(--line-ui)}

  .stage{position:relative;background:var(--paper);border:1px solid var(--line);
         display:grid;place-items:center;padding:clamp(1rem,3vw,2.6rem);
         min-block-size:clamp(320px,52vw,660px)}
  .stage img{max-inline-size:100%;max-block-size:min(60vh,600px);inline-size:auto;
             block-size:auto;object-fit:contain}
  .stage .nav{position:absolute;inset-block:0;display:grid;place-items:center;inline-size:56px;
    color:var(--ink);opacity:.55;transition:opacity var(--dur-1) ease}
  .stage .nav:hover{opacity:1}
  .stage .nav svg{inline-size:26px;block-size:26px}
  .stage .prev{inset-inline-start:0}
  .stage .next{inset-inline-end:0}
  .stage .idx{position:absolute;inset-block-end:.9rem;inset-inline-end:1rem;
    font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3);
    font-variant-numeric:tabular-nums}

  .buy{display:grid;gap:var(--s5);align-content:start}
  @media (min-width:1000px){.buy{position:sticky;inset-block-start:calc(64px + 1.5rem)}}
  .buy .kicker svg{inline-size:15px;block-size:15px;flex:0 0 auto}
  .buy .kicker{display:flex;align-items:center;gap:.5rem;font-family:var(--f-mono);
    font-size:var(--t-label);letter-spacing:var(--track-label);text-transform:uppercase;
    color:var(--ink-3)}
  .buy h1{font-size:clamp(1.4rem,1.15vw + .95rem,1.85rem);line-height:1.16;text-wrap:balance}
  .buy .sub{font-family:var(--f-serif);font-style:italic;font-size:1.12rem;
            line-height:1.35;color:var(--ink-2)}
  .buy .askprice{display:flex;flex-wrap:wrap;align-items:baseline;gap:.7rem;
    padding-block:var(--s4);border-block:1px solid var(--line)}
  .buy .askprice b{font-family:var(--f-mono);font-weight:400;font-size:1.3rem;letter-spacing:-.01em}
  .buy .askprice span{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3)}
  .buy .acts{display:grid;gap:.5rem}
  .buy .btn{inline-size:100%}
  .info-card{border:1px solid var(--line);background:var(--paper);padding:var(--s4) var(--s5)}
  .info-card h2,.info-card h3{font-family:var(--f-sans);font-weight:700;font-size:.92rem;letter-spacing:0;
    margin-block-end:.4rem;display:flex;align-items:center;gap:.5rem}
  .info-card h2 svg,.info-card h3 svg{inline-size:16px;block-size:16px;flex:0 0 auto;color:var(--ink-2)}
  .info-card p{font-size:var(--t-sm);color:var(--ink-2);line-height:1.5}
  .info-card p + p{margin-block-start:.3rem}

  .spec{border-block-start:1px solid var(--line-ui)}
  .spec > div{display:grid;grid-template-columns:1fr;gap:.1rem;
    padding-block:.75rem;border-block-end:1px solid var(--line)}
  @media (min-width:520px){.spec > div{grid-template-columns:11rem 1fr;gap:var(--gap-s);
    align-items:baseline}}
  .spec dt{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
    text-transform:uppercase;color:var(--ink-3)}
  .spec dd{font-size:.94rem}
  .spec dd.n{font-family:var(--f-mono);font-variant-numeric:tabular-nums;font-size:.9rem}
  .spec dd .yok{color:var(--ink-3);font-family:var(--f-mono);font-size:var(--t-xs)}

  .acc{border-block-end:1px solid var(--line)}
  .acc summary{display:flex;align-items:center;justify-content:space-between;gap:.5rem;
    min-block-size:60px;cursor:pointer;list-style:none;font-family:var(--f-serif);font-size:1.1rem}
  .acc summary::-webkit-details-marker{display:none}
  .acc summary::after{content:"";inline-size:10px;block-size:10px;flex:0 0 auto;
    border-inline-end:1px solid var(--ink-2);border-block-end:1px solid var(--ink-2);
    transform:rotate(45deg) translate(-3px,-3px);transition:transform var(--dur-2) var(--ease)}
  .acc[open] summary::after{transform:rotate(-135deg) translate(-4px,-4px)}
  .acc .body{padding-block-end:var(--s6);max-inline-size:70ch;color:var(--ink-2);font-size:.95rem}
  .acc .body p + p{margin-block-start:.7rem}

  .seller{display:grid;gap:var(--gap-m);grid-template-columns:1fr;
          border:1px solid var(--line);background:var(--paper);padding:var(--gap-m)}
  @media (min-width:720px){.seller{grid-template-columns:auto 1fr}}
  .seller .mark{inline-size:74px;block-size:74px;border:1px solid var(--line-ui);
    display:grid;place-items:center;font-family:var(--f-serif);font-size:1.5rem}
  .seller h3{font-size:var(--t-h4);margin-block-end:.35rem}
  .seller dl{display:grid;gap:.15rem .9rem;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
    margin-block-start:var(--s4)}
  .seller dl > div{display:flex;justify-content:space-between;gap:.6rem;
    padding-block:.45rem;border-block-end:1px solid var(--line)}
  .seller dt{font-family:var(--f-mono);font-size:var(--t-xs);color:var(--ink-3)}
  .seller dd{font-size:var(--t-sm);text-align:end}

  .pdp-more{padding-block:var(--band-s) var(--band-m)}
  .pdp-more h2{font-size:var(--t-h3);margin-block-end:var(--gap-m)}
}

@layer motion{
  /* paylaşılan öğe geçişi: ızgaradan ürüne */
  @media (prefers-reduced-motion:no-preference){
    ::view-transition-old(pdp-img),::view-transition-new(pdp-img){animation-duration:.42s}
    ::view-transition-old(root),::view-transition-new(root){animation-duration:.3s}
  }
}
"""

CSS2 += r"""
@layer blocks{
  /* reset katmanindaki *{margin:0} tarayicinin dialog icin verdigi margin:auto
     kuralini eziyordu; pencereler sol ust kosede aciliyordu */
  dialog{border:0;padding:0;margin:auto;max-inline-size:min(520px,calc(100vw - 2rem));
    inline-size:100%;max-block-size:min(92dvh,calc(100dvh - 2rem));
    background:var(--paper);color:var(--ink);box-shadow:0 40px 80px -40px rgb(34 34 34 / .45)}
  /* hizli bakis bir urun kartidir, form degil: daha genis */
  #qv{max-inline-size:min(940px,calc(100vw - 2rem))}
  #qv .dbox{padding:clamp(1.2rem,2.6vw,2rem)}
  dialog::backdrop{background:rgb(34 34 34 / .45);backdrop-filter:blur(3px)}
  .dbox{position:relative;padding:clamp(1.5rem,4vw,2.6rem)}
  .dclose{position:absolute;inset-block-start:.5rem;inset-inline-end:.5rem;
    inline-size:44px;block-size:44px;display:grid;place-items:center;font-size:1.4rem;color:var(--ink-2)}
  .dclose:hover{color:var(--ink)}
  .fld{display:grid;gap:.35rem;margin-block-end:var(--s5)}
  .fld label{font-family:var(--f-mono);font-size:var(--t-label);letter-spacing:var(--track-label);
    text-transform:uppercase;color:var(--ink-3)}
  .fld input,.fld textarea{border:1px solid var(--line-ui);background:var(--ecru);
    min-block-size:46px;padding:.6rem .85rem;border-radius:var(--r);font-size:.96rem;
    field-sizing:content}
  .fld textarea{min-block-size:88px;resize:vertical}
  .fld input:focus-visible,.fld textarea:focus-visible{outline:2px solid var(--ink);outline-offset:1px}
  .fld .err{font-size:var(--t-xs);color:#8E2C22;display:none}
  .fld input[aria-invalid="true"],.fld textarea[aria-invalid="true"]{border-color:#8E2C22}
  .fld input[aria-invalid="true"] ~ .err{display:block}
}
"""
