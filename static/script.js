// script.js - Latte Lounge Café Modern UI & Floating Chatbot Controller
document.addEventListener('DOMContentLoaded', function() {
    // -------------------------------------------------------------
    // CHATBOT WIDGET ELEMENTS
    // -------------------------------------------------------------
    const chatWidget = document.getElementById('chat-widget');
    const chatFabToggle = document.getElementById('chat-fab-toggle');
    const chatWidgetClose = document.getElementById('chat-widget-close');
    const chatCartShortcut = document.getElementById('chat-cart-shortcut');
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const fabBadge = document.getElementById('fab-badge');
    
    // Notification elements
    const notificationPopup = document.getElementById('notification-popup');
    const notificationContent = document.querySelector('.notification-content');

    // -------------------------------------------------------------
    // LANDING & MENU ELEMENTS
    // -------------------------------------------------------------
    const cartCounter = document.getElementById('cart-counter');
    const menuBasketCount = document.getElementById('menu-basket-count');
    const openCartBtn = document.getElementById('open-cart-btn');
    const basketViewBtn = document.getElementById('basket-view-btn');
    const heroOrderBtn = document.getElementById('hero-order-btn');
    const siteSearch = document.getElementById('site-search');
    const navMenu = document.getElementById('nav-menu');
    const navRewards = document.getElementById('nav-rewards');
    const navDelivery = document.getElementById('nav-delivery');
    
    // Menu filter pills and cards
    const filterPills = document.querySelectorAll('.filter-pill');
    const menuCards = document.querySelectorAll('.drink-card');
    const menuCardsGrid = document.getElementById('menu-cards-grid');
    const menuPrevBtn = document.getElementById('menu-prev-btn');
    const menuNextBtn = document.getElementById('menu-next-btn');
    const menuMoreBtn = document.getElementById('menu-more-btn');

    // Featured carousel
    const carouselPrev = document.getElementById('carousel-prev');
    const carouselNext = document.getElementById('carousel-next');
    const dockCarousel = document.getElementById('dock-carousel');

    let isChatOpen = false;

    // Initial greeting in chat box
    addBotMessage("👋 Welcome to Latte Lounge Café! I'm your digital barista. Ask me anything about our drinks, reserve a table, or build your custom order!");
    
    // Fetch initial cart state from Flask session
    syncCartState();

    // =============================================================
    // FLOATING CHATBOT WIDGET TOGGLE
    // =============================================================
    function toggleChatWidget(forceOpen = null) {
        if (forceOpen === true) {
            isChatOpen = true;
        } else if (forceOpen === false) {
            isChatOpen = false;
        } else {
            isChatOpen = !isChatOpen;
        }

        if (isChatOpen) {
            chatWidget.classList.remove('chat-widget-hidden');
            chatFabToggle.classList.add('fab-active');
            if (fabBadge) fabBadge.style.display = 'none';
            setTimeout(() => userInput.focus(), 250);
        } else {
            chatWidget.classList.add('chat-widget-hidden');
            chatFabToggle.classList.remove('fab-active');
        }
    }

    if (chatFabToggle) {
        chatFabToggle.addEventListener('click', () => toggleChatWidget());
    }

    if (chatWidgetClose) {
        chatWidgetClose.addEventListener('click', () => toggleChatWidget(false));
    }

    if (chatCartShortcut) {
        chatCartShortcut.addEventListener('click', () => {
            triggerBotQuery("checkout");
        });
    }

    // =============================================================
    // CART & BASKET MANAGEMENT (SYNC WITH FLASK SESSION)
    // =============================================================
    function syncCartState() {
        fetch('/api/cart')
            .then(res => res.json())
            .then(data => {
                updateCartBadges(data.count || 0);
            })
            .catch(() => {
                // If API not active yet, keep graceful defaults
            });
    }

    function updateCartBadges(count) {
        if (cartCounter) cartCounter.textContent = count;
        if (menuBasketCount) menuBasketCount.textContent = count;
        
        // Bounce animation on cart counters
        [cartCounter, menuBasketCount].forEach(badge => {
            if (badge) {
                badge.style.transform = 'scale(1.35)';
                setTimeout(() => { badge.style.transform = 'scale(1)'; }, 200);
            }
        });
    }

    function addToBasket(name, price) {
        fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name, price: price })
        })
        .then(res => res.json())
        .then(data => {
            updateCartBadges(data.count);
            showNotification(`☕ Added "${name}" (LKR ${parseFloat(price).toFixed(2)}) to your basket!`);
        })
        .catch(err => {
            console.error("Cart error:", err);
            showNotification(`Added "${name}" to basket!`);
        });
    }

    // Attach click listeners to all "to cart" and "Add to order +" action buttons
    document.querySelectorAll('.add-to-cart-action').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const name = this.getAttribute('data-name') || 'Artisan Coffee';
            const price = parseFloat(this.getAttribute('data-price') || 450.00);
            addToBasket(name, price);
        });
    });

    // "my basket" and Cart Navbar buttons open chat with Checkout prompt
    function openBasketInChat() {
        toggleChatWidget(true);
        fetch('/api/cart')
            .then(res => res.json())
            .then(data => {
                if (data.items && data.items.length > 0) {
                    const list = data.items.map(it => `• ${it.name} (LKR ${parseFloat(it.price).toFixed(2)})`).join('\n');
                    addBotMessage(`🛍️ **Your Current Basket** (${data.count} items):\n${list}\n\n**Total: LKR ${parseFloat(data.total).toFixed(2)}**\n\nWould you like this order for **pickup** or **delivery**?`);
                } else {
                    addBotMessage("🛍️ Your basket is currently empty. Explore our coffee menu above or tell me what drink you're craving!");
                }
            })
            .catch(() => {
                triggerBotQuery("checkout");
            });
    }

    if (basketViewBtn) {
        basketViewBtn.addEventListener('click', openBasketInChat);
    }
    if (openCartBtn) {
        openCartBtn.addEventListener('click', openBasketInChat);
    }

    // =============================================================
    // MENU CATEGORY FILTERING (DRINKO REFERENCE BEHAVIOR)
    // =============================================================
    filterPills.forEach(pill => {
        pill.addEventListener('click', function() {
            filterPills.forEach(p => p.classList.remove('active'));
            this.classList.add('active');

            const selectedCategory = this.getAttribute('data-category');

            menuCards.forEach(card => {
                const cardCategories = (card.getAttribute('data-category') || '').split(' ');
                if (selectedCategory === 'all' || cardCategories.includes(selectedCategory)) {
                    card.style.display = 'flex';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(10px)';
                    setTimeout(() => {
                        card.style.transition = 'all 0.35s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 50);
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Menu Grid Arrow Navigation
    if (menuPrevBtn && menuCardsGrid) {
        menuPrevBtn.addEventListener('click', () => {
            menuCardsGrid.scrollBy({ left: -260, behavior: 'smooth' });
        });
    }

    if (menuNextBtn && menuCardsGrid) {
        menuNextBtn.addEventListener('click', () => {
            menuCardsGrid.scrollBy({ left: 260, behavior: 'smooth' });
        });
    }

    // Menu "More" Button
    if (menuMoreBtn) {
        menuMoreBtn.addEventListener('click', () => {
            toggleChatWidget(true);
            triggerBotQuery("View Menu");
        });
    }

    // =============================================================
    // SEARCH BAR DYNAMIC FILTERING
    // =============================================================
    if (siteSearch) {
        siteSearch.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            if (!query) {
                menuCards.forEach(c => c.style.display = 'flex');
                return;
            }

            menuCards.forEach(card => {
                const drinkName = (card.getAttribute('data-drink') || '').toLowerCase();
                const ingredients = card.querySelector('.drink-ingredients')?.textContent.toLowerCase() || '';
                if (drinkName.includes(query) || ingredients.includes(query)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });

        siteSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const query = this.value.trim();
                if (query) {
                    toggleChatWidget(true);
                    triggerBotQuery(query);
                }
            }
        });
    }

    // =============================================================
    // DOCK & HERO ACTIONS
    // =============================================================
    if (heroOrderBtn) {
        heroOrderBtn.addEventListener('click', function() {
            const name = this.getAttribute('data-drink') || 'Skinny Latte';
            const price = parseFloat(this.getAttribute('data-price') || 340.00);
            addToBasket(name, price);
            toggleChatWidget(true);
            triggerBotQuery("I'd like to place an order for a latte");
        });
    }

    if (carouselPrev && dockCarousel) {
        carouselPrev.addEventListener('click', () => {
            dockCarousel.scrollBy({ left: -220, behavior: 'smooth' });
        });
    }

    if (carouselNext && dockCarousel) {
        carouselNext.addEventListener('click', () => {
            dockCarousel.scrollBy({ left: 220, behavior: 'smooth' });
        });
    }

    // Navbar Nav links
    if (navRewards) {
        navRewards.addEventListener('click', (e) => {
            e.preventDefault();
            toggleChatWidget(true);
            triggerBotQuery("My Loyalty Points");
        });
    }

    if (navDelivery) {
        navDelivery.addEventListener('click', (e) => {
            e.preventDefault();
            toggleChatWidget(true);
            triggerBotQuery("delivery");
        });
    }

    // =============================================================
    // CHATBOT MESSAGING ENGINE
    // =============================================================
    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Quick Reply suggestion chips click handler
    const quickReplyChips = document.querySelectorAll('.chip');
    quickReplyChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const query = this.getAttribute('data-query') || this.textContent.trim();
            triggerBotQuery(query);
        });
    });

    function triggerBotQuery(queryText) {
        userInput.value = queryText;
        sendMessage();
    }

    function showNotification(message, duration = 3500) {
        if (!notificationPopup || !notificationContent) return;
        notificationContent.textContent = message;
        notificationPopup.classList.remove('notification-hidden');

        setTimeout(() => {
            if (notificationPopup) {
                notificationPopup.classList.add('notification-hidden');
            }
        }, duration);
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        // Add user message to chat
        addUserMessage(message);
        userInput.value = '';

        // Show typing indicator
        showTypingIndicator();

        // Send message to Flask server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `user_input=${encodeURIComponent(message)}`
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator();

            // Add bot response
            addBotMessage(data.response);

            // Update shopping cart badge if items exist
            if (data.items) {
                updateCartBadges(data.items.length);
            }

            // Notification for completed orders
            if (data.order_complete) {
                updateCartBadges(0);
                showNotification("🎉 Order confirmed! Thank you for ordering from Latte Lounge.", 4000);
            }
        })
        .catch(error => {
            removeTypingIndicator();
            addBotMessage("Sorry, there was an issue processing your request. Please try again.");
            console.error('Error:', error);
        });
    }

    function addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', 'user-message');
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addBotMessage(text) {
        const formattedText = text.replace(/\n/g, '<br>');
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', 'bot-message');
        messageDiv.innerHTML = formattedText;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function showTypingIndicator() {
        if (document.getElementById('typing-indicator')) return;

        const typingDiv = document.createElement('div');
        typingDiv.classList.add('chat-message', 'bot-message');
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = '<em>Barista is typing...</em>';

        chatBox.appendChild(typingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
});