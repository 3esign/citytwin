/* Kompozitor — Muzička akademija Svemira.  Kanonski primjerak: skills/svemir-muzika/scripts/kompozitor.js
   Bez ijedne zavisnosti: čist WebAudio. Radi u pregledniku i kopira se u projekat koji ga koristi.

   Zašto postoji: svaki Svemirov film, lice i alat koji treba zvuk dosad je improvizovao svoj oscilator.
   Ovdje stoji jedan instrument sa imenovanim glasovima, zajedničkim prostorom (odjek) i rasporedom
   koji se oslanja na audio sat, ne na setTimeout (lookahead — „A tale of two clocks", web.dev).

   Glasovi:  udar (ping) · zvono (bell) · trzaj (pluck) · dah (noise) · ploha (pad) · pogon (drone)
   Pravila:  nikad rampa na nulu (eksponencijalna rampa ide na .0001) — nula pravi klik;
             svaki glas ima svoj kraj (stop) — niko ne ostaje da visi;
             zvuk počinje tek na ljudski pokret (politika automatskog puštanja).            */
(function (root) {
'use strict';

function Kompozitor(opt){
  opt = opt || {};
  const AC = opt.ctx || new (window.AudioContext || window.webkitAudioContext)();

  /* ---------- magistrala: glas → (prostor) → ograničavač → izlaz ---------- */
  const out = AC.createGain(); out.gain.value = 0;              // tiho dok se ne pozove uključi()
  const lim = AC.createDynamicsCompressor();
  lim.threshold.value = -14; lim.knee.value = 12; lim.ratio.value = 8;
  lim.attack.value = .005; lim.release.value = .25;
  out.connect(lim); lim.connect(opt.dest || AC.destination);

  /* prostor: povratni odjek kroz prigušen filtar — „echo" bez ijednog uzorka.
     Dvije grane različitih vremena i strana daju širinu; filtar u petlji guta visine,
     pa odjek odlazi, a ne zvoni zauvijek. */
  const space = AC.createGain(); space.gain.value = 1;
  const mk = (time, pan, fbAmt) => {
    const d = AC.createDelay(3), fb = AC.createGain(), lp = AC.createBiquadFilter(), p = AC.createStereoPanner();
    d.delayTime.value = time; fb.gain.value = fbAmt;
    lp.type = 'lowpass'; lp.frequency.value = 2200;
    space.connect(d); d.connect(lp); lp.connect(fb); fb.connect(d); lp.connect(p); p.connect(out);
    p.pan.value = pan;
    return { d, fb, lp };
  };
  const echoL = mk(.273, -.35, .40), echoR = mk(.411, .32, .34);

  const live = [];                                             // sve što još svira, da se može ućutati
  const keep = n => { live.push(n); if (live.length > 220) live.splice(0, 80); return n; };
  const EPS = .0001;

  function env(g, at, atk, dec, peak){
    g.gain.cancelScheduledValues(at);
    g.gain.setValueAtTime(EPS, at);
    g.gain.exponentialRampToValueAtTime(Math.max(peak, .0005), at + Math.max(atk, .003));
    g.gain.exponentialRampToValueAtTime(EPS, at + Math.max(atk, .003) + dec);
  }
  function tap(node, send){                                    // koliko glasa ide u prostor
    if (send <= 0) return;
    const s = AC.createGain(); s.gain.value = send; node.connect(s); s.connect(space);
  }

  /* ---------- glasovi ---------- */
  // udar: čist ton sa kratkim repom — osnovni „beep" koji prati događaj na ekranu
  function udar(f, at, o){
    o = o || {};
    const osc = AC.createOscillator(), g = AC.createGain(), p = AC.createStereoPanner();
    const dur = o.dur == null ? .5 : o.dur, atk = o.atk == null ? .006 : o.atk;
    osc.type = o.type || 'sine';
    osc.frequency.setValueAtTime(f, at);
    if (o.to) osc.frequency.exponentialRampToValueAtTime(Math.max(o.to, 20), at + dur * .9);
    p.pan.value = o.pan || 0;
    osc.connect(g); g.connect(p); p.connect(out); tap(p, o.send == null ? .45 : o.send);
    env(g, at, atk, dur, o.gain == null ? .22 : o.gain);
    osc.start(at); osc.stop(at + atk + dur + .06);
    return keep(osc);
  }
  // zvono: osnovni ton + neharmonični prizvuk (2,76×) — metal, ne sinus
  function zvono(f, at, o){
    o = o || {};
    const dur = o.dur == null ? 2.2 : o.dur, gn = o.gain == null ? .17 : o.gain;
    udar(f, at, { dur: dur, gain: gn, send: o.send == null ? .6 : o.send, pan: o.pan || 0, type: 'sine' });
    udar(f * 2.76, at, { dur: dur * .45, gain: gn * .33, send: .5, pan: (o.pan || 0) * -1, type: 'sine' });
    udar(f * 5.4, at, { dur: dur * .2, gain: gn * .12, send: .4, pan: 0, type: 'sine' });
  }
  // trzaj: kratak, drven — za nabrajanje (stavka, prijedlog, zgrada)
  function trzaj(f, at, o){
    o = o || {};
    const osc = AC.createOscillator(), g = AC.createGain(), lp = AC.createBiquadFilter(), p = AC.createStereoPanner();
    const dur = o.dur == null ? .42 : o.dur;
    osc.type = 'triangle'; osc.frequency.setValueAtTime(f, at);
    lp.type = 'lowpass';
    lp.frequency.setValueAtTime(Math.min(f * 7, 7000), at);
    lp.frequency.exponentialRampToValueAtTime(Math.max(f * 1.4, 160), at + dur);
    p.pan.value = o.pan || 0;
    osc.connect(lp); lp.connect(g); g.connect(p); p.connect(out); tap(p, o.send == null ? .4 : o.send);
    env(g, at, .004, dur, o.gain == null ? .2 : o.gain);
    osc.start(at); osc.stop(at + dur + .06);
    return keep(osc);
  }
  // dah: filtriran šum — vrelina, vjetar, nalet; nikad kao ritam
  function dah(at, dur, o){
    o = o || {};
    const n = Math.floor(AC.sampleRate * dur), buf = AC.createBuffer(1, Math.max(n, 128), AC.sampleRate);
    const ch = buf.getChannelData(0);
    let v = 0;
    for (let i = 0; i < ch.length; i++){ v = (v * .96 + (Math.random() * 2 - 1) * .04); ch[i] = v * 3; }
    const src = AC.createBufferSource(), bp = AC.createBiquadFilter(), g = AC.createGain(), p = AC.createStereoPanner();
    src.buffer = buf; bp.type = 'bandpass'; bp.Q.value = o.q == null ? 1.1 : o.q;
    bp.frequency.setValueAtTime(o.f0 == null ? 320 : o.f0, at);
    bp.frequency.exponentialRampToValueAtTime(Math.max(o.f1 == null ? 900 : o.f1, 40), at + dur);
    p.pan.value = o.pan || 0;
    src.connect(bp); bp.connect(g); g.connect(p); p.connect(out); tap(p, o.send == null ? .35 : o.send);
    g.gain.setValueAtTime(EPS, at);
    g.gain.exponentialRampToValueAtTime(Math.max(o.gain == null ? .12 : o.gain, .0005), at + dur * .4);
    g.gain.exponentialRampToValueAtTime(EPS, at + dur);
    src.start(at); src.stop(at + dur + .05);
    return keep(src);
  }
  // ploha: akord koji se otvori i zatvori — kraj stava, kartica, špica
  function ploha(freqs, at, dur, o){
    o = o || {};
    freqs.forEach((f, i) => {
      const osc = AC.createOscillator(), g = AC.createGain(), p = AC.createStereoPanner();
      osc.type = o.type || 'sine';
      osc.frequency.setValueAtTime(f, at);
      osc.detune.setValueAtTime((i % 2 ? 4 : -4), at);
      p.pan.value = ((i / Math.max(freqs.length - 1, 1)) - .5) * (o.width == null ? .6 : o.width);
      osc.connect(g); g.connect(p); p.connect(out); tap(p, o.send == null ? .45 : o.send);
      const peak = (o.gain == null ? .12 : o.gain) / Math.sqrt(freqs.length);
      g.gain.setValueAtTime(EPS, at);
      g.gain.exponentialRampToValueAtTime(Math.max(peak, .0005), at + (o.atk == null ? .9 : o.atk));
      g.gain.setValueAtTime(Math.max(peak, .0005), at + dur * .62);
      g.gain.exponentialRampToValueAtTime(EPS, at + dur);
      osc.start(at); osc.stop(at + dur + .1);
      keep(osc);
    });
  }

  /* ---------- pogon: stalni sloj koji nosi stav ---------- */
  function Pogon(){
    const g = AC.createGain(), lp = AC.createBiquadFilter(), p = AC.createStereoPanner();
    g.gain.value = EPS; lp.type = 'lowpass'; lp.frequency.value = 500; lp.Q.value = .7;
    const oscs = [];
    [[1, -6, 'sawtooth', -.25], [1, 7, 'sawtooth', .25], [2, 0, 'sine', 0], [1.5, 3, 'sine', .1]].forEach(d => {
      const o2 = AC.createOscillator(), gg = AC.createGain(), pp = AC.createStereoPanner();
      o2.type = d[2]; o2.frequency.value = 73.42 * d[0]; o2.detune.value = d[1];
      gg.gain.value = d[2] === 'sine' ? .22 : .5; pp.pan.value = d[3];
      o2.connect(gg); gg.connect(pp); pp.connect(lp);
      o2.start(); oscs.push({ o: o2, mul: d[0] });
    });
    lp.connect(g); g.connect(p); p.connect(out); tap(p, .3);
    // spor talas na filtru: sloj diše, ne stoji
    const lfo = AC.createOscillator(), lg = AC.createGain();
    lfo.frequency.value = .06; lg.gain.value = 60; lfo.connect(lg); lg.connect(lp.frequency); lfo.start();
    return {
      koren(f, at, glide){ oscs.forEach(x => x.o.frequency.setTargetAtTime(f * x.mul, at, (glide == null ? 1.2 : glide) / 3)); },
      boja(hz, at, glide){ lp.frequency.setTargetAtTime(hz, at, (glide == null ? 1.5 : glide) / 3); },
      jacina(v, at, glide){ g.gain.setTargetAtTime(Math.max(v, EPS), at, (glide == null ? 1.5 : glide) / 3); },
      odmah(f, hz, v, at){ oscs.forEach(x => x.o.frequency.setValueAtTime(f * x.mul, at));
                           lp.frequency.setValueAtTime(hz, at); g.gain.setValueAtTime(Math.max(v, EPS), at); }
    };
  }

  /* ---------- raspored: audio sat vodi, JS sat samo budi (lookahead) ---------- */
  // Film ima svoje vrijeme (pauza, skok). Mi ga prevodimo: audioVrijeme = sada + (notaT - filmT).
  function Raspored(note){
    const sorted = note.slice().sort((a, b) => a.t - b.t);
    let i = 0, lastT = -1;
    return {
      reset(filmT){ i = 0; while (i < sorted.length && sorted[i].t < filmT) i++; lastT = filmT; },
      // pozovi jednom po kadru; vrati broj zakazanih nota
      kadar(filmT, look){
        look = look == null ? .15 : look;
        if (filmT < lastT - .05 || filmT > lastT + 1.5) this.reset(filmT);   // skok ili pauza
        lastT = filmT;
        let n = 0;
        const now = AC.currentTime;
        while (i < sorted.length && sorted[i].t <= filmT + look){
          const e = sorted[i++];
          const at = Math.max(now + .01, now + (e.t - filmT));
          try { e.f(at); n++; } catch (err) { /* jedna nota ne obara film */ }
        }
        return n;
      }
    };
  }

  return {
    ctx: AC, out: out, prostor: space, echo: { L: echoL, R: echoR },
    udar, zvono, trzaj, dah, ploha, Pogon, Raspored,
    uključi(v, s){ AC.resume && AC.resume();
      out.gain.cancelScheduledValues(AC.currentTime);
      out.gain.setValueAtTime(Math.max(out.gain.value, EPS), AC.currentTime);
      out.gain.linearRampToValueAtTime(v, AC.currentTime + (s == null ? 1.2 : s)); },
    isključi(s){ out.gain.cancelScheduledValues(AC.currentTime);
      out.gain.setValueAtTime(Math.max(out.gain.value, EPS), AC.currentTime);
      out.gain.linearRampToValueAtTime(0, AC.currentTime + (s == null ? .8 : s)); },
    tišina(){ const t = AC.currentTime;                     // skok u filmu: sve što visi se prekida
      live.forEach(n => { try { n.stop(t + .02); } catch (e) {} }); live.length = 0; }
  };
}

/* ---------- štim: ravnomjerno temperovano, imena nota ---------- */
Kompozitor.nota = function (ime){
  const m = /^([A-Ga-g])(#|b)?(-?\d)$/.exec(String(ime).trim());
  if (!m) return NaN;
  const base = { c: 0, d: 2, e: 4, f: 5, g: 7, a: 9, b: 11 }[m[1].toLowerCase()];
  const acc = m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0;
  const midi = (parseInt(m[3], 10) + 1) * 12 + base + acc;
  return 440 * Math.pow(2, (midi - 69) / 12);
};
// ljestvica kao niz poluton-pomaka od korijena (dorski je naš podrazumijevani ton filma)
Kompozitor.lestvice = {
  dur: [0, 2, 4, 5, 7, 9, 11],
  mol: [0, 2, 3, 5, 7, 8, 10],
  dorski: [0, 2, 3, 5, 7, 9, 10],
  pentatonika: [0, 2, 5, 7, 9],
  pentamol: [0, 3, 5, 7, 10]
};
// stepenik ljestvice → frekvencija (stepenik smije biti negativan i preko oktave)
Kompozitor.stepen = function (koren, lestvica, i){
  const sc = Kompozitor.lestvice[lestvica] || Kompozitor.lestvice.dorski;
  const okt = Math.floor(i / sc.length), st = ((i % sc.length) + sc.length) % sc.length;
  return koren * Math.pow(2, (sc[st] + okt * 12) / 12);
};
/* Preslikavanje podatka u visinu (parameter mapping sonification, Hermann/Hunt/Neuhoff, pogl. 15):
   veličina ide u STEPENIK ljestvice, nikad u sirovu frekvenciju — tako svaka nota ostaje u tonalitetu,
   a odnos veliko/malo ostaje čujan. Glasnoća se ne koristi kao nosilac podatka (percepcija nije linearna). */
Kompozitor.uStepen = function (v, min, max, odStepena, doStepena){
  if (!(max > min)) return odStepena;
  const k = Math.max(0, Math.min(1, (Math.log(Math.max(v, 1e-9)) - Math.log(Math.max(min, 1e-9)))
                                   / (Math.log(max) - Math.log(Math.max(min, 1e-9)))));
  return Math.round(odStepena + k * (doStepena - odStepena));
};

if (typeof module !== 'undefined' && module.exports) module.exports = Kompozitor;
root.Kompozitor = Kompozitor;
})(typeof window !== 'undefined' ? window : globalThis);
