window.addEventListener('DOMContentLoaded', () => {
    link_with_query_params();

    if (!window.frappe_bundle_loaded) {
        $(document).on('click', 'button[data-toggle=collapse]', (e) => {
            let $el = $(e.currentTarget);
            let $target = $($el.attr('data-target'));
            $target.toggleClass('show');
        });
        make_view_log();
    }

    // fill remaining hieght available in viewport scroll for featured-table
    if (window.innerWidth > 400) {
        $('.fill-height-scroll, .fill-height').each((i, el) => {
            let top = $(el).offset().top;
            $(el).css('max-height', `calc(100vh - ${top + 5}px)`);
        });
        $(document).on('mouseenter', '.fill-height-scroll', (e) => {
            $(document.body).css('overflow', 'hidden');
        })
        $(document).on('mouseleave', '.fill-height-scroll', (e) => {
            $(document.body).css('overflow', '');
        });
    }

    // horizontal breakout from container for featured-table
    $('.horizontal-breakout').each((i, el) => {
        let right = el.getBoundingClientRect().right;
        let windowWidth = $(window).width();
        $(el).css('margin-right', -1 * (windowWidth - right));
    })
});

function link_with_query_params() {
  [
    {event: 'sl-change', selector: 'sl-select[query]'},
    {event: 'change', selector: 'select[query]'},
    {event: 'click', selector: 'a[query]'},
  ].forEach(({event, selector}) => {
      $(document).on(event, selector, (e) => {
        let $el = $(e.target);
        let is_link = $el.is("a");
        let query = $el.attr("query");
        if (!query) {
          return;
        }
        let key = query;
        let value = e.target.value;
        if (is_link) {
            [key, value] = query.split("=");
        }
        if (key && value) {
            e.preventDefault();
            set_query_params(key, value);
        }
      });
  });

}

function set_query_params(key, value, clear_others = false) {
  let searchParams = new URLSearchParams(clear_others ? '' : window.location.search);
  searchParams.set(key, value);
  window.location.search = searchParams.toString();
}

function get_browser() {
    let ua = navigator.userAgent;
    let tem;
    let M = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];

    if (/trident/i.test(M[1])) {
        tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
        return { name: "IE", version: tem[1] || "" };
    }
    if (M[1] === "Chrome") {
        tem = ua.match(/\bOPR|Edge\/(\d+)/);
        if (tem != null) {
            return { name: "Opera", version: tem[1] };
        }
    }
    M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, "-?"];
    if ((tem = ua.match(/version\/(\d+)/i)) != null) {
        M.splice(1, 1, tem[1]);
    }
    return {
        name: M[0],
        version: M[1],
    };
}

function make_view_log() {
    try {
        if (navigator.doNotTrack != 1) {
            let browser = get_browser();
            fetch('/api/method/frappe.website.doctype.web_page_view.web_page_view.make_view_log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    path: location.pathname,
                    referrer: document.referrer,
                    browser: browser.name,
                    version: browser.version,
                    url: location.origin,
                    user_tz: Intl.DateTimeFormat().resolvedOptions().timeZone
                })
            });
        }
    } catch (error) {
        console.error(error)
        console.log('Could not track page view');
    }
}