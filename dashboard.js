window.onload = function() {
    let urls = document.querySelectorAll('a:not(.quick-bookmark)');

    // Format timestamp in human-readable form
    function formatTimestamp(timestamp) {
        if (!timestamp || timestamp === 0) {
            return 'never';
        }

        const now = Math.floor(Date.now() / 1000);
        const delta = now - timestamp;

        if (delta < 0) {
            return 'in the future';
        }

        if (delta < 60) {
            return `${delta}s ago`;
        } else if (delta < 3600) {
            const minutes = Math.floor(delta / 60);
            const seconds = delta % 60;
            return `${minutes}:${seconds.toString().padStart(2, '0')} ago`;
        } else if (delta < 86400) {
            const hours = Math.floor(delta / 3600);
            const minutes = Math.floor((delta % 3600) / 60);
            const seconds = delta % 60;
            return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')} ago`;
        } else {
            const days = Math.floor(delta / 86400);
            if (days === 1) {
                return '1 day ago';
            } else if (days < 7) {
                const hours = Math.floor((delta % 86400) / 3600);
                if (hours > 0) {
                    const fraction = Math.floor(hours / 24 * 10);
                    return `${days}.${fraction} days ago`;
                } else {
                    return `${days} days ago`;
                }
            } else if (days < 30) {
                const weeks = (days / 7).toFixed(1);
                return `${weeks} weeks ago`;
            } else if (days < 365) {
                const months = (days / 30).toFixed(1);
                return `${months} months ago`;
            } else {
                const years = (days / 365).toFixed(1);
                return `${years} years ago`;
            }
        }
    }

    // Update all timestamps
    function updateTimestamps() {
        document.querySelectorAll('.human-time').forEach(el => {
            const timestamp = parseInt(el.getAttribute('data-timestamp'));
            el.textContent = formatTimestamp(timestamp);
        });
    }

    // Update immediately and then every hour
    updateTimestamps();
    setInterval(updateTimestamps, 3600000); // 1 hour in milliseconds

    // Tab navigation - Main tabs
    const mainTabButtons = document.querySelectorAll('.main-tabs .tab-button');
    mainTabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');

            // Remove active class from all main tabs
            mainTabButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Add active class to clicked tab
            button.classList.add('active');
            const contentId = tabName + '-content';
            document.getElementById(contentId).classList.add('active');
        });
    });

    // Tab navigation - Sub tabs (event delegation for dynamically loaded content)
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-button') && e.target.hasAttribute('data-subtab')) {
            const subtabName = e.target.getAttribute('data-subtab');
            const parentTabContent = e.target.closest('.tab-content');

            // Remove active from sibling subtab buttons
            const siblingButtons = e.target.parentElement.querySelectorAll('.tab-button');
            siblingButtons.forEach(btn => btn.classList.remove('active'));

            // Remove active from sibling subtab contents
            parentTabContent.querySelectorAll('.subtab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Add active to clicked button
            e.target.classList.add('active');

            // Add active to corresponding content
            const contentId = subtabName + '-content';
            const targetContent = document.getElementById(contentId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        }
    });

    // Search functionality
    function searchUrls() {
        let search_query = document.getElementById("searchbox").value.toLowerCase();

        for (var i = 0; i < urls.length; i++) {
            if(urls[i].innerText.toLowerCase().includes(search_query)) {
                urls[i].classList.remove("hide");

                // Set open = true for all details ancestors
                let parent = urls[i].parentNode;
                while(parent && parent.tagName == 'DETAILS') {
                    parent.setAttribute("open", true);
                    parent = parent.parentNode;
                }

            } else {
                urls[i].classList.add("hide");
            }
        }
    }

    function hideEmpty() {
        var els = document.body.querySelectorAll("details");
        for (var i = 0; i < els.length; i++) {
            // count number of child elements that are visible
            let visibleChildren = 0;
            let children = els[i].querySelectorAll('a');
            for (var j = 0; j < children.length; j++) {
                if (!children[j].classList.contains('hide')) {
                    visibleChildren++;
                }
            }

            // Hide the details element if it has no visible children
            if (visibleChildren === 0) {
                els[i].classList.add('hide');
            } else {
                els[i].classList.remove('hide');
            }
        }
    }

    function searchAll() {
        searchUrls();

        // Open all "details" elements (so search results are visible)
        document.body.querySelectorAll('details').forEach((e) => {
            e.setAttribute('open', true);
            e.classList.remove('hide');
        });

        hideEmpty();
    }

    let typingTimer;
    let typeInterval = 50;
    let searchInput = document.getElementById('searchbox');

    searchInput.addEventListener('keyup', () => {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(searchAll, typeInterval);
    });

}