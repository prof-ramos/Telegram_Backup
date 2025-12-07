// Terminal typing animation
const terminalPhrases = [
    "$ python backup_cli.py menu",
    "🚀 Iniciando Telegram Backup CLI...",
    "✅ Conectado com sucesso!",
    "📋 Configurações carregadas",
    "🔍 Escaneando chats disponíveis...",
    "📊 12 chats encontrados",
    "⚙️  Configurando rotas de backup...",
    "📝 Backup iniciado em tempo real",
    "✨ Sistema operacional!"
];

let terminalIndex = 0;
let charIndex = 0;
let isDeleting = false;

function typeTerminal() {
    const terminalElement = document.getElementById('terminal-text');
    const currentPhrase = terminalPhrases[terminalIndex];
    
    if (isDeleting) {
        terminalElement.textContent = currentPhrase.substring(0, charIndex - 1);
        charIndex--;
    } else {
        terminalElement.textContent = currentPhrase.substring(0, charIndex + 1);
        charIndex++;
    }
    
    let typeSpeed = isDeleting ? 50 : 100;
    
    if (!isDeleting && charIndex === currentPhrase.length) {
        typeSpeed = 2000;
        isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        terminalIndex = (terminalIndex + 1) % terminalPhrases.length;
        typeSpeed = 500;
    }
    
    setTimeout(typeTerminal, typeSpeed);
}

// Initialize terminal typing
typeTerminal();

// Text splitting animation
function initTextSplitting() {
    Splitting();
    
    const splitText = document.querySelectorAll('[data-splitting]');
    splitText.forEach((element, index) => {
        const chars = element.querySelectorAll('.char');
        anime({
            targets: chars,
            opacity: [0, 1],
            translateY: [50, 0],
            delay: (el, i) => (index * 200) + (i * 30),
            duration: 800,
            easing: 'easeOutExpo'
        });
    });
}

// Scroll reveal animation
function initScrollReveal() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.scroll-reveal').forEach(el => {
        observer.observe(el);
    });
}

// Smooth scroll function
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        const offsetTop = element.offsetTop - 80; // Account for fixed nav
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
    }
}

// Feature cards hover animation
function initFeatureCards() {
    const cards = document.querySelectorAll('.feature-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            anime({
                targets: card,
                scale: 1.02,
                duration: 300,
                easing: 'easeOutQuad'
            });
        });
        
        card.addEventListener('mouseleave', () => {
            anime({
                targets: card,
                scale: 1,
                duration: 300,
                easing: 'easeOutQuad'
            });
        });
    });
}

// Navigation scroll effect
function initNavigation() {
    const nav = document.querySelector('nav');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 100) {
            nav.classList.add('bg-white/90');
            nav.classList.remove('bg-white/80');
        } else {
            nav.classList.add('bg-white/80');
            nav.classList.remove('bg-white/90');
        }
        
        lastScrollY = currentScrollY;
    });
}

// Counter animation for stats
function animateCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-counter'));
        const duration = 2000;
        const increment = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.floor(current);
        }, 16);
    });
}

// Particle background effect
function createParticles() {
    const hero = document.querySelector('.hero-gradient');
    if (!hero) return;
    
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'absolute w-2 h-2 bg-sage-400 rounded-full opacity-20';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 5 + 's';
        particle.style.animation = 'float 6s ease-in-out infinite';
        
        hero.appendChild(particle);
    }
    
    // Add CSS for floating animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
        }
    `;
    document.head.appendChild(style);
}

// Terminal command examples
const commandExamples = [
    {
        command: "python backup_cli.py menu",
        description: "Abre interface interativa completa",
        category: "Interface"
    },
    {
        command: "python backup_cli.py add-route",
        description: "Adiciona nova rota de backup",
        category: "Configuração"
    },
    {
        command: "python backup_cli.py run",
        description: "Inicia backup em tempo real",
        category: "Execução"
    },
    {
        command: "python backup_cli.py show-config",
        description: "Visualiza configuração atual",
        category: "Status"
    }
];

// Interactive command showcase
function initCommandShowcase() {
    const showcase = document.getElementById('command-showcase');
    if (!showcase) return;
    
    let currentIndex = 0;
    
    function updateShowcase() {
        const example = commandExamples[currentIndex];
        showcase.innerHTML = `
            <div class="text-center">
                <div class="code-block mb-4">
                    <div class="text-green-400">$ ${example.command}</div>
                </div>
                <p class="text-charcoal-600">${example.description}</p>
                <span class="inline-block bg-sage-100 text-sage-700 px-3 py-1 rounded-full text-sm mt-2">
                    ${example.category}
                </span>
            </div>
        `;
        
        currentIndex = (currentIndex + 1) % commandExamples.length;
    }
    
    updateShowcase();
    setInterval(updateShowcase, 3000);
}

// Initialize all animations and interactions
document.addEventListener('DOMContentLoaded', () => {
    // Initialize core functions
    initTextSplitting();
    initScrollReveal();
    initFeatureCards();
    initNavigation();
    createParticles();
    initCommandShowcase();
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            scrollToSection(targetId);
        });
    });
    
    // Add loading animation
    const loader = document.createElement('div');
    loader.className = 'fixed inset-0 bg-sage-50 flex items-center justify-center z-50 transition-opacity duration-500';
    loader.innerHTML = `
        <div class="text-center">
            <div class="w-16 h-16 border-4 border-sage-200 border-t-sage-600 rounded-full animate-spin mb-4"></div>
            <p class="text-charcoal-600 font-medium">Carregando sistema...</p>
        </div>
    `;
    
    document.body.appendChild(loader);
    
    // Remove loader after page loads
    window.addEventListener('load', () => {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => loader.remove(), 500);
        }, 1000);
    });
});

// Add some interactive easter eggs
let konamiCode = [];
const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.keyCode);
    if (konamiCode.length > konamiSequence.length) {
        konamiCode.shift();
    }
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        // Easter egg: Show developer message
        const message = document.createElement('div');
        message.className = 'fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-sage-600 text-white p-6 rounded-xl shadow-2xl z-50 text-center';
        message.innerHTML = `
            <h3 class="text-xl font-bold mb-2">🎉 Easter Egg Encontrado!</h3>
            <p class="text-sage-200">Você descobriu o código secreto do desenvolvedor!</p>
            <p class="text-sm mt-2 text-sage-300">Telegram Backup CLI v1.0</p>
        `;
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500);
        }, 3000);
        
        konamiCode = [];
    }
});

// Performance optimization: Lazy load heavy animations
const observerOptions = {
    root: null,
    rootMargin: '50px',
    threshold: 0.1
};

const lazyAnimationObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const element = entry.target;
            
            // Trigger specific animations based on element type
            if (element.classList.contains('feature-card')) {
                anime({
                    targets: element,
                    translateY: [30, 0],
                    opacity: [0, 1],
                    duration: 600,
                    easing: 'easeOutQuad',
                    delay: Math.random() * 200
                });
            }
            
            lazyAnimationObserver.unobserve(element);
        }
    });
}, observerOptions);

// Observe elements for lazy animation
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.feature-card').forEach(card => {
        lazyAnimationObserver.observe(card);
    });
});

// Add responsive navigation menu
document.addEventListener('DOMContentLoaded', () => {
    const nav = document.querySelector('nav');
    const navLinks = nav.querySelectorAll('a');
    
    // Add mobile menu toggle (if needed)
    const mobileMenuButton = document.createElement('button');
    mobileMenuButton.className = 'md:hidden p-2 rounded-lg hover:bg-sage-100 transition-colors';
    mobileMenuButton.innerHTML = `
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
    `;
    
    // Add click handlers for navigation
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('text-sage-600'));
            // Add active class to clicked link
            link.classList.add('text-sage-600');
        });
    });
});

// Console welcome message
console.log('%c🚀 Telegram Backup CLI', 'color: #5c7359; font-size: 24px; font-weight: bold;');
console.log('%cSistema profissional de backup para Telegram', 'color: #6d6d6d; font-size: 14px;');
console.log('%cDesenvolvido com Python, Telethon e Rich CLI', 'color: #6d6d6d; font-size: 12px;');
console.log('%c✨ Site criado com animações e design responsivo', 'color: #5c7359; font-size: 12px;');