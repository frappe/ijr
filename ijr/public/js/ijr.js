window.addEventListener('DOMContentLoaded', () => {
    link_with_query_params();

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
