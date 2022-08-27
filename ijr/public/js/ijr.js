frappe.ready(() => {
  link_with_query_params();
});

function link_with_query_params() {
  $(document).on("click", "a", (e) => {
    let $a = $(e.target);
    let query = $a.attr("query");
    if (!query) {
      return;
    }
    let [key, value] = query.split("=");
    if (key && value) {
      e.preventDefault();
      set_query_params(key, value);
    }
  });

  $(document).on("sl-change", "sl-select", (e) => {
    let $el = $(e.target);
    let query = $el.attr("query");
    if (!query) {
      return;
    }
    let key = query;
    let value = e.target.value;
    if (key && value) {
      set_query_params(key, value);
    }
  });
}

function set_query_params(key, value, clear_others = false) {
  let searchParams = new URLSearchParams(clear_others ? '' : window.location.search);
  searchParams.set(key, value);
  window.location.search = searchParams.toString();
}

function generate_export_url({
  doctype,
  fields,
  filters = null,
  order_by = null,
}) {
  fields = fields.map((f) => `\`tab${doctype}\`.\`${f}\``);
  let params = new URLSearchParams({
    cmd: "frappe.desk.reportview.export_query",
    doctype,
    fields: JSON.stringify(fields),
    filters: filters ? JSON.stringify(filters) : null,
    order_by,
    file_format_type: "CSV",
  });

  return params.toString();
}

function download_file_from_url(url, filename) {
  let a = document.createElement("a");
  a.href = url;
  a.target = "_blank";
  a.download = filename || "download";
  a.click();
}
