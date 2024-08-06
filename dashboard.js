window.onload = function() {
    let urls = document.querySelectorAll('a')

    function searchUrls() {
        let search_query = document.getElementById("searchbox").value.toLowerCase();

        for (var i = 0; i < urls.length; i++) {
            if(urls[i].innerText.toLowerCase().includes(search_query)) {
                urls[i].classList.remove("hide");

                /*
                // set open = true for all details ancestors
                parent = urls[i].parentNode;
                while(parent.tagName == 'DETAILS') {
                    console.log("opening details: " + parent.firstChild.innerHTML);
                    parent.setAttribute("open", true);
                    parent = parent.parentNode;
                }
                */
                
            } else {
                urls[i].classList.add("hide");
            }
        }
    }
    
    function hideEmpty() {
        var els = document.body.querySelectorAll("details");
        for (var i = 0; i < els.length; i++) {
            // count number of child elements that...
        }
    }

    function searchAll() {
        // close all "details" elements (then in search functions, open only the matching ones)
        // document.body.querySelectorAll('details').forEach((e) => {e.removeAttribute('open')})

        searchUrls();
        // searchTitles();

        // open all "details" elements (because any that are empty gain "hide")
        document.body.querySelectorAll('details').forEach((e) => {e.setAttribute('open', true)})

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