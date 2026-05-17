const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const hasDesktopPointer = window.matchMedia("(hover: hover) and (pointer: fine)");

const revealItems = document.querySelectorAll(".reveal");

if (!prefersReducedMotion.matches) {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      }
    },
    {
      threshold: 0.18,
      rootMargin: "0px 0px -40px 0px",
    },
  );

  for (const item of revealItems) {
    observer.observe(item);
  }
} else {
  for (const item of revealItems) {
    item.classList.add("visible");
  }
}

const topbar = document.querySelector(".topbar");
const parallaxItems = document.querySelectorAll(
  ".hero-media img, .page-hero-media img, .objects-hero-media img, .detail-hero-media img, .dashboard-hero-backdrop img",
);

let scrollFrame = null;

const updateOnScroll = () => {
  scrollFrame = null;
  const y = window.scrollY;

  if (topbar) {
    topbar.classList.toggle("is-condensed", y > 28);
  }

  if (prefersReducedMotion.matches) {
    return;
  }

  for (const item of parallaxItems) {
    const speed = item.closest(".dashboard-hero") ? 0.02 : 0.035;
    item.style.transform = `scale(1.04) translate3d(0, ${y * speed}px, 0)`;
  }
};

const onScroll = () => {
  if (scrollFrame !== null) {
    return;
  }

  scrollFrame = window.requestAnimationFrame(updateOnScroll);
};

window.addEventListener("scroll", onScroll, { passive: true });
updateOnScroll();

const motionSurfaces = document.querySelectorAll(
  ".hero-aside, .hero-facts article, .direction-panel, .page-hero-panel, .investor-note, .property-card, .showcase-panel, .application-panel, .detail-hero-rail, .gallery-note, .detail-card, .dashboard-session, .dashboard-hero-rail, .dashboard-kpis article, .dashboard-panel",
);

for (const surface of motionSurfaces) {
  surface.classList.add("motion-surface");
}

if (hasDesktopPointer.matches && !prefersReducedMotion.matches) {
  for (const surface of motionSurfaces) {
    surface.addEventListener("pointermove", (event) => {
      const rect = surface.getBoundingClientRect();
      const px = ((event.clientX - rect.left) / rect.width) * 100;
      const py = ((event.clientY - rect.top) / rect.height) * 100;
      const rotateY = ((px - 50) / 50) * 3.2;
      const rotateX = ((50 - py) / 50) * 3.2;

      surface.style.setProperty("--mx", `${px}%`);
      surface.style.setProperty("--my", `${py}%`);
      surface.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });

    surface.addEventListener("pointerleave", () => {
      surface.style.removeProperty("--mx");
      surface.style.removeProperty("--my");
      surface.style.removeProperty("transform");
    });
  }
}
