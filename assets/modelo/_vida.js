
        // ══════════════════════════════════════════════════════════════════════
        // VIDA (14/10/2026, Mickael: "aprimorar a animação para ficar em um nível absurdamente profissional… mantendo a
        // estética… bem bem bem animado"). Depois de todas as cenas montadas:
        //  · cada etiqueta balança presa pela fita (o canto da fita é o pivô), devagar, cada uma no seu ritmo;
        //  · a câmera respira: aproxima 3,5% bem devagar dentro de cada cena e volta antes do travelling.
        // ══════════════════════════════════════════════════════════════════════
        Array.from(document.querySelectorAll(".cena .tag > span")).forEach((sp, k) => {
          const m = getComputedStyle(sp).transform, base = m && m !== "none" ? (Math.atan2(+m.split(",")[1], +m.split("(")[1].split(",")[0]) * 180) / Math.PI : 0;
          const per = 2.4 + rnd(k * 3.3 + 1) * 1.6, amp = 1.1 + rnd(k * 5.1 + 2) * 1.3, impar = base < 0;
          tl.fromTo(sp, { rotation: base - amp }, { rotation: base + amp, transformOrigin: impar ? "8% 0%" : "92% 0%", duration: per / 2, yoyo: true,
            repeat: Math.ceil(DUR / per) * 2, ease: "sine.inOut", immediateRender: false }, rnd(k * 7.7) * per);
        });
        Object.keys(JAN).forEach((i) => JAN[i].forEach(([a, z]) => {
          const ini = +i === 0 ? a : a + 0.55, fim = z - 0.36;
          if (fim - ini < 1.5) return;
          tl.fromTo("#tremor", { scale: 1 }, { scale: 1.035, transformOrigin: "540px 600px", duration: fim - ini, ease: "sine.inOut", immediateRender: false }, ini);
          if (z < DUR - 0.5) tl.to("#tremor", { scale: 1, duration: 0.42, ease: "power2.inOut" }, fim);
        }));
