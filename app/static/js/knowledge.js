document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('faq-search');
    
    // The FAQ cards are inside a flex column with a h2 title "Frequently Asked Questions"
    // Let's select all industrial-card elements inside the FAQ section.
    // They are siblings of the h2.
    const faqCards = Array.from(document.querySelectorAll('.industrial-card')).filter(card => {
        // Exclude the Quick Start Video card and the Support Ticket Form card
        return card.querySelector('button') && card.querySelector('.accordion-content');
    });

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            
            faqCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(term)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});
