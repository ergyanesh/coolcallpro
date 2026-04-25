// Sticky header + CTA fade (consolidated scroll listener)
const header = document.getElementById('header');
const headerNavCta = document.getElementById('headerNavCta');

window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;

    // Sticky header shadow
    if (scrollY > 60) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }

    // CTA fade in after hero
    if (headerNavCta) {
        const isPastHero = scrollY > 500;
        headerNavCta.style.opacity = isPastHero ? '1' : '0';
        headerNavCta.style.pointerEvents = isPastHero ? 'auto' : 'none';
        headerNavCta.setAttribute('aria-hidden', isPastHero ? 'false' : 'true');
        headerNavCta.setAttribute('tabindex', isPastHero ? '0' : '-1');
    }
}, { passive: true });

// Mobile menu
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');
if (hamburger) {
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('open');
    });
}

// Contact form
async function handleContactSubmit(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    btn.textContent = 'Sending…';
    btn.disabled = true;

    const data = {
        firstName: document.getElementById('firstName').value.trim(),
        lastName:  document.getElementById('lastName').value.trim(),
        zip:       document.getElementById('zip').value.trim(),
        subject:   document.getElementById('subject').value,
        message:   document.getElementById('message').value.trim()
    };

    try {
        await fetch('https://script.google.com/macros/s/AKfycbz76gpDMfqJ6fDIxcS8lSCyhmnxMBAVikDMpIuC4qRRfeoOrsZlEeNxN8h1ADiKbZGL5w/exec', {
            method: 'POST',
            mode: 'no-cors',
            headers: { 'Content-Type': 'text/plain' },
            body: JSON.stringify(data)
        });
    } catch (err) {
        // no-cors fetch always resolves; true network failures land here
    }

    btn.textContent = '✅ Message Sent!';
    btn.style.background = '#38a169';
    const formStatus = document.getElementById('form-status');
    if (formStatus) formStatus.textContent = 'Message sent successfully!';
    e.target.reset();

    setTimeout(() => {
        btn.textContent = 'Send Message';
        btn.style.background = '';
        btn.disabled = false;
        const formStatusReset = document.getElementById('form-status');
        if (formStatusReset) formStatusReset.textContent = '';
    }, 5000);
}

// FAQ accordion — one-open-at-a-time pattern. Opening a FAQ closes any
// other open FAQ on the page. Clicking an already-open FAQ still collapses
// it (users need an escape). Industry-standard for long FAQ lists (NYT,
// Amazon Help, Apple Support). aria-expanded stays in sync for screen
// readers on every affected button.
document.querySelectorAll('.faq-q').forEach(btn => {
    btn.addEventListener('click', () => {
        const item = btn.closest('.faq-item');
        if (!item) return;
        const wasOpen = item.classList.contains('open');

        // Close every other open FAQ on the page
        document.querySelectorAll('.faq-item.open').forEach(openItem => {
            if (openItem === item) return;
            openItem.classList.remove('open');
            const openBtn = openItem.querySelector('.faq-q');
            if (openBtn) openBtn.setAttribute('aria-expanded', 'false');
        });

        // Toggle the clicked one (expand if closed, collapse if open)
        if (wasOpen) {
            item.classList.remove('open');
            btn.setAttribute('aria-expanded', 'false');
        } else {
            item.classList.add('open');
            btn.setAttribute('aria-expanded', 'true');
        }
    });
});

// Back to top button
(function initBackToTop() {
    const btn = document.createElement('button');
    btn.className = 'back-to-top';
    btn.setAttribute('aria-label', 'Back to top');
    btn.innerHTML = '&#9650;';
    document.body.appendChild(btn);

    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            btn.classList.add('is-visible');
        } else {
            btn.classList.remove('is-visible');
        }
    }, { passive: true });

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
})();

// Animate on scroll (simple) — respects prefers-reduced-motion
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const animateItems = document.querySelectorAll('.article-card, .step-card, .precaution-card, .testimonial-card, .safety-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    animateItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(28px)';
        item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(item);
    });
}

// City chips expand/collapse (homepage)
(function initCityChipsToggle() {
    const toggleBtn = document.getElementById('cityChipsToggle');
    const chips = document.querySelector('.city-chips');
    if (!toggleBtn || !chips) return;

    toggleBtn.addEventListener('click', () => {
        const isExpanded = chips.classList.toggle('city-chips--expanded');
        toggleBtn.textContent = isExpanded ? 'Show Less' : 'View All 20 Cities';
    });
})();

// Filter buttons (articles page)
const filterBtns = document.querySelectorAll('.filter-btn');
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const category = btn.dataset.filter;
        const cards = document.querySelectorAll('.article-card[data-category]');
        cards.forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    });
});

// Article pages: show a bottom CTA only when the sidebar is fully out of view
(function initArticleBottomCta() {
    const articleSidebar = document.querySelector('.article-sidebar');
    if (!articleSidebar) {
        return;
    }

    const sourceLink = articleSidebar.querySelector('.sidebar-cta a[href^="tel:"]');
    if (!sourceLink) {
        return;
    }

    const bottomCta = document.createElement('div');
    bottomCta.className = 'article-bottom-cta';

    const ctaLink = document.createElement('a');
    ctaLink.className = 'article-bottom-cta-link btn-vibrate';
    ctaLink.href = sourceLink.getAttribute('href');
    ctaLink.textContent = 'Request Service';
    ctaLink.setAttribute('aria-label', 'Request Service');

    bottomCta.appendChild(ctaLink);
    document.body.appendChild(bottomCta);

    const setBottomCtaVisible = (shouldShow) => {
        bottomCta.classList.toggle('is-visible', shouldShow);
    };

    if ('IntersectionObserver' in window) {
        const sidebarObserver = new IntersectionObserver((entries) => {
            const sidebarEntry = entries[0];
            setBottomCtaVisible(!sidebarEntry.isIntersecting);
        }, { threshold: 0 });

        sidebarObserver.observe(articleSidebar);
        return;
    }

    const updateBottomCta = () => {
        const rect = articleSidebar.getBoundingClientRect();
        const isSidebarVisible = rect.bottom > 0 && rect.top < window.innerHeight;
        setBottomCtaVisible(!isSidebarVisible);
    };

    window.addEventListener('scroll', updateBottomCta, { passive: true });
    window.addEventListener('resize', updateBottomCta);
    updateBottomCta();
})();

/* Mobile sticky-bar auto-hide (since 2026-04-25):
   Hide .mobile-call-bar while any in-page .btn-primary.btn-lg is on screen,
   fade it back in once they all leave the viewport. Mobile-only — desktop
   has no .mobile-call-bar (display:none unless <=768px). */
(function () {
    if (!window.matchMedia || !window.matchMedia('(max-width: 768px)').matches) return;
    if (!('IntersectionObserver' in window)) return;
    var bar = document.querySelector('.mobile-call-bar');
    var ctas = document.querySelectorAll('.btn-primary.btn-lg');
    if (!bar || !ctas.length) return;
    var visible = new Set();
    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
            if (e.isIntersecting) visible.add(e.target);
            else visible.delete(e.target);
        });
        bar.classList.toggle('sticky-hidden', visible.size > 0);
    }, { threshold: 0.5 });
    ctas.forEach(function (c) { io.observe(c); });
})();
