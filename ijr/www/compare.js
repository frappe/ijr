const colors = ["#F1D68F", "#A8D8B4", "#63BDBB", "#8FAAF1", "#F1909E"];
const raw_data = window.raw_data;

let cur_tab = undefined;
let lineOrBar = "line";
let filters = {
	indicator_1: null,
	indicator_2: null,
	indicator_3: null,
	states: [],
	ijrs: [],
};

frappe.ready(() => {
	parse_query_params();
	set_active_tab();
	setup_indicator_select();
	setup_state_select();
	setup_ijr_select();
	render_chart_or_table();
});

function parse_query_params() {
	const url = new URL(window.location.href);
	const params = url.searchParams;
	const tab = params.get("tab");
	const indicators = params.get("indicators");
	const states = params.get("states");
	const ijrs = params.get("ijrs");

	if (tab) {
		cur_tab = tab;
	}
	if (indicators) {
		const _indicators = indicators.split(",");
		filters.indicator_1 = _indicators[0];
		filters.indicator_2 = _indicators[1];
		filters.indicator_3 = _indicators[2];
	}
	if (states) {
		filters.states = states.split(",");
	}
	if (ijrs) {
		filters.ijrs = ijrs.split(",");
	}
}

function toggle_empty_state(show = true) {
	const emptyState = document.getElementById("empty-state");
	if (show) {
		emptyState.classList.remove("hidden");
	} else {
		emptyState.classList.add("hidden");
	}
}

function set_active_tab() {
	cur_tab = frappe.utils.get_url_arg("tab") || "one_indicator";
	const ids_by_tab = {
		one_indicator: "tab-1",
		two_indicator: "tab-2",
		three_indicator: "tab-3",
	};
	Object.keys(ids_by_tab).forEach((tab) => {
		const id = ids_by_tab[tab];
		const element = document.getElementById(id);
		if (cur_tab === tab) {
			element.classList.add("active");
		} else {
			element.classList.remove("active");
		}
	});
	set_query_params();
}

function setup_indicator_select() {
	const all_indicators = raw_data.reduce((acc, d) => {
		if (!acc.find((i) => i.value === d.indicator_id)) {
			acc.push({
				value: d.indicator_id,
				label: d.indicator_name,
				pillar: d.pillar,
				theme: d.theme,
			});
		}
		return acc;
	}, []);
	const groupedIndicators = all_indicators.reduce((acc, indicator) => {
		const pillar = indicator.pillar;
		const theme = indicator.theme;
		const indicator_id = indicator.value;
		if (!acc[pillar])
			acc[pillar] = { name: pillar, value: pillar, children: [] };
		const pillarNode = acc[pillar];
		if (!pillarNode.children.find((c) => c.name === theme)) {
			pillarNode.children.push({
				name: theme,
				value: pillar + theme,
				children: [],
			});
		}
		const themeNode = pillarNode.children.find((c) => c.name === theme);
		if (!themeNode.children.find((c) => c.name === indicator.label)) {
			themeNode.children.push({ name: indicator.label, value: indicator_id });
		}
		return acc;
	}, {});

	const treeselect_options = {
		isSingleSelect: true,
		showTags: false,
		disabledBranchNode: true,
		appendToBody: true,
		// alwaysOpen: true,
		options: Object.values(groupedIndicators),
		iconElements: {
			clear: `<sl-icon name="x-circle-fill" library="system" aria-hidden="true"></sl-icon>`,
			arrowDown: `<sl-icon library="system" name="chevron-down" aria-hidden="true"></sl-icon>`,
			arrowRight: `<sl-icon library="system" name="chevron-right" aria-hidden="true"></sl-icon>`,
		},
	};

	const $indicator_1 = document.querySelector("#indicator-input-1");
	const indicator_1 = new Treeselect({
		parentHtmlContainer: $indicator_1,
		...treeselect_options,
		value: filters.indicator_1,
	});
	const $indicator_1_label = document.querySelector(
		"label[for=indicator-input-1]"
	);
	$indicator_1_label.innerHTML =
		cur_tab === "one_indicator" ? "Indicator" : "Indicator 1";
	indicator_1.srcElement.addEventListener("input", (e) => {
		update_filters("indicator_1", e.detail);
		render_chart_or_table();
	});

	if (cur_tab !== "one_indicator") {
		document.getElementById("indicator-2-container").classList.remove("hidden");
		const $indicator_2 = document.querySelector("#indicator-input-2");
		const indicator_2 = new Treeselect({
			parentHtmlContainer: $indicator_2,
			...treeselect_options,
			value: filters.indicator_2,
		});
		const $indicator_2_label = document.querySelector(
			"label[for=indicator-input-2]"
		);
		$indicator_2_label.innerHTML = "Indicator 2";
		indicator_2.srcElement.addEventListener("input", (e) => {
			update_filters("indicator_2", e.detail);
			render_chart_or_table();
		});
	}

	if (cur_tab === "three_indicator") {
		document.getElementById("indicator-3-container").classList.remove("hidden");
		const $indicator_3 = document.querySelector("#indicator-input-3");
		const indicator_3 = new Treeselect({
			parentHtmlContainer: $indicator_3,
			...treeselect_options,
			value: filters.indicator_3,
		});
		const $indicator_3_label = document.querySelector(
			"label[for=indicator-input-3]"
		);
		$indicator_3_label.innerHTML = "Indicator 3";
		indicator_3.srcElement.addEventListener("input", (e) => {
			update_filters("indicator_3", e.detail);
			render_chart_or_table();
		});
	}
}

function setup_state_select() {
	const stateSelect = $("sl-select[name=state]");

	if (cur_tab == "one_indicator") {
		const all_states = raw_data
			.reduce((acc, d) => {
				if (!acc.find((i) => i.value === d.region_code)) {
					acc.push({ value: d.region_code, label: d.state });
				}
				return acc;
			}, [])
			.sort((a, b) => a.label.localeCompare(b.label));

		stateSelect.attr("multiple", true);
		stateSelect.html(
			all_states.map(
				(s) => `<sl-option value="${s.value}">${s.label}</sl-option>`
			)
		);
	}
	if (cur_tab !== "one_indicator") {
		const clusters = [
			{ label: "Large and mid-sized states", value: "large" },
			{ label: "Small states", value: "small" },
			{ label: "All states", value: "all" },
		];
		stateSelect.html(
			clusters.map(
				(s) => `<sl-option value="${s.value}">${s.label}</sl-option>`
			)
		);
	}

	setTimeout(() => {
		stateSelect.attr("value", filters.states.join(" "));
	}, 100);

	stateSelect.on("sl-change", () => {
		const val = stateSelect.val();
		update_filters("states", Array.isArray(val) ? val : [val]);
		render_chart_or_table();
	});
}

function setup_ijr_select() {
	const all_ijrs = raw_data
		.reduce((acc, d) => {
			if (!acc.find((i) => i.value === d.ijr_number)) {
				acc.push({ value: d.ijr_number, label: `IJR ${d.ijr_number}` });
			}
			return acc;
		}, [])
		.sort((a, b) => a.label.localeCompare(b.label));

	const ijrSelect = $("sl-select[name=ijr]");
	if (cur_tab == "one_indicator") {
		ijrSelect.attr("multiple", true);
		ijrSelect.html(
			`<sl-option value="all">All IJRs</sl-option>` +
				all_ijrs
					.map((i) => `<sl-option value="${i.value}">${i.label}</sl-option>`)
					.join("")
		);
		if (!filters.ijrs.length) {
			ijrSelect.attr("value", "all");
			filters.ijrs = ["all"];
		}
	}
	if (cur_tab !== "one_indicator") {
		ijrSelect.attr("multiple", false);
		ijrSelect.html(
			all_ijrs.map(
				(i) => `<sl-option value="${i.value}">${i.label}</sl-option>`
			)
		);
		if (!filters.ijrs.length) {
			ijrSelect.attr("value", all_ijrs.at(-1).value);
			filters.ijrs = [all_ijrs.at(-1).value];
		}
	}

	setTimeout(() => {
		ijrSelect.attr("value", filters.ijrs.join(" "));
	}, 100);

	ijrSelect.on("sl-change", () => {
		const val = ijrSelect.val();
		update_filters("ijrs", Array.isArray(val) ? val : [val]);
		render_chart_or_table();
	});
}

function render_chart_or_table() {
	toggle_empty_state(false);
	if (cur_tab === "one_indicator" && validate_one_indicator_filters()) {
		show_chart_type_switcher();
		if (lineOrBar === "line") {
			render_line_chart();
		}
		if (lineOrBar === "bar") {
			render_bar_chart();
		}
	}
	if (cur_tab === "two_indicator" && validate_two_indicator_filters()) {
		render_scatter_chart();
	}
	if (cur_tab === "three_indicator" && validate_three_indicator_filters()) {
		render_table(get_filtered_data());
	}
}

function validate_one_indicator_filters() {
	if (!filters.indicator_1) {
		toggle_empty_state(true);
		return false;
	}
	if (!filters.states?.length) {
		toggle_empty_state(true);
		return false;
	}
	return true;
}

function validate_two_indicator_filters() {
	if (!filters.indicator_1 || !filters.indicator_2) {
		toggle_empty_state(true);
		return false;
	}
	if (filters.indicator_1 === filters.indicator_2) {
		toggle_empty_state(true);
		return false;
	}
	if (!filters.states?.length) {
		toggle_empty_state(true);
		return false;
	}
	return true;
}

function validate_three_indicator_filters() {
	if (!filters.indicator_1 || !filters.indicator_2 || !filters.indicator_3) {
		toggle_empty_state(true);
		return false;
	}
	if (
		filters.indicator_1 === filters.indicator_2 ||
		filters.indicator_1 === filters.indicator_3 ||
		filters.indicator_2 === filters.indicator_3
	) {
		toggle_empty_state(true);
		return false;
	}
	if (!filters.states?.length) {
		toggle_empty_state(true);
		return false;
	}
	return true;
}

function render_line_chart() {
	const filteredData = get_filtered_data();
	const chartData = getLineChartData(filteredData);
	renderChart(chartData, "line");
	show_indicator_title(filteredData);
}

function render_bar_chart() {
	const filteredData = get_filtered_data();
	const chartData = getBarChartData(filteredData);
	renderChart(chartData, "bar");
	show_indicator_title(filteredData);
}

function render_scatter_chart() {
	const filteredData = get_filtered_data();
	if (!filteredData.length) {
		toggle_empty_state(true);
		return;
	}
	const chartData = getScatterChartData(filteredData);
	renderChart(chartData, "scatter", {
		x: filteredData.find(
			(d) => d.indicator_id.toString() === filters.indicator_1.toString()
		).indicator_name,
		y: filteredData.find(
			(d) => d.indicator_id.toString() === filters.indicator_2.toString()
		).indicator_name,
	});
	show_indicator_title(filteredData);
}

function get_filtered_data() {
	function match_state_cluster(state, cluster) {
		if (cluster == "all") {
			return true;
		}
		if (cluster == "large" && state.cluster.toLowerCase().includes("large")) {
			return true;
		}
		if (cluster == "small" && state.cluster.toLowerCase().includes("small")) {
			return true;
		}
		return false;
	}

	return raw_data.filter((d) => {
		const indicatorMatch = [
			filters.indicator_1,
			filters.indicator_2,
			filters.indicator_3,
		].includes(d.indicator_id.toString());

		const stateMatch =
			cur_tab === "one_indicator"
				? filters.states.includes(d.region_code)
				: match_state_cluster(d, filters.states[0]);

		const ijrMatch =
			filters.ijrs.includes("all") ||
			filters.ijrs.includes(d.ijr_number) ||
			filters.ijrs.includes(d.ijr_number.toString());

		return indicatorMatch && stateMatch && ijrMatch;
	});
}

function show_indicator_title(data) {
	const indicator_1_data = data.find(
		(d) => d.indicator_id.toString() === filters.indicator_1.toString()
	);
	const indicator_id = indicator_1_data.indicator_id;
	const indicator_name = indicator_1_data.indicator_name;
	const indicator_unit = indicator_1_data.indicator_unit;

	const indicator_1_title = document.getElementById("indicator-1-title");
	get_indicator_info_element(indicator_id, indicator_name).then((tooltip) => {
		indicator_1_title.innerHTML = `
		<h2 class="text-lg font-semibold">
			${indicator_name} (${indicator_unit})
		</h2>
		${tooltip}`;
	});
	indicator_1_title.classList.remove("hidden");

	if (cur_tab === "two_indicator") {
		const indicator_2_data = data.find(
			(d) => d.indicator_id.toString() === filters.indicator_2.toString()
		);
		const indicator_id = indicator_2_data.indicator_id;
		const indicator_name = indicator_2_data.indicator_name;
		const indicator_unit = indicator_2_data.indicator_unit;

		const indicator_2_title = document.getElementById("indicator-2-title");
		get_indicator_info_element(indicator_id, indicator_name).then((tooltip) => {
			indicator_2_title.innerHTML = `
			<p class="mx-2"> vs </p>
			<h2 class="text-lg font-semibold">
				${indicator_name} (${indicator_unit})
			</h2>
			${tooltip}`;
		});
		indicator_2_title.classList.remove("hidden");
	}
}

function get_indicator_description(indicator_id) {
	return frappe.xcall("ijr.api.get_indicator_description", { indicator_id });
}

function update_filters(key, value) {
	filters[key] = value;
	set_query_params();
}

function set_query_params() {
	const url = new URL(window.location.href);
	const _params = {
		tab: cur_tab,
		indicators: [
			filters.indicator_1,
			filters.indicator_2,
			filters.indicator_3,
		].filter(Boolean),
		states: filters.states,
		ijrs: filters.ijrs,
	};

	Object.keys(_params).forEach((key) => {
		if (!_params[key]) {
			url.searchParams.delete(key);
			return;
		}
		if (Array.isArray(_params[key])) {
			_params[key] = _params[key].join(",");
		}
		url.searchParams.set(key, _params[key]);
	});
	window.history.replaceState({}, "", url);
}

function show_chart_type_switcher() {
	const lineOrBarSwitcher = document.getElementById("line-or-bar-switcher");
	const lineChartSwitcher = document.getElementById("line-chart-switcher");
	const barChartSwitcher = document.getElementById("bar-chart-switcher");

	lineOrBarSwitcher.classList.remove("hidden");
	lineChartSwitcher.addEventListener("click", () => {
		lineOrBar = "line";
		render_chart_or_table();
	});
	barChartSwitcher.addEventListener("click", () => {
		lineOrBar = "bar";
		render_chart_or_table();
	});

	if (lineOrBar === "line") {
		lineChartSwitcher.classList.add("active");
		barChartSwitcher.classList.remove("active");
	} else {
		lineChartSwitcher.classList.remove("active");
		barChartSwitcher.classList.add("active");
	}
}

function getLineChartData(data) {
	const lineChartData = { labels: [], datasets: [] };

	lineChartData.labels = data
		.map((d) => `IJR ${d.ijr_number}`)
		.filter((v, i, a) => a.indexOf(v) === i)
		.sort();

	const valueByState = data.reduce((acc, d) => {
		if (!acc[d.state]) acc[d.state] = [];
		const index = lineChartData.labels.indexOf(`IJR ${d.ijr_number}`);
		acc[d.state][index] = d.indicator_value;
		return acc;
	}, {});

	const periodByIJR = data.reduce((acc, d) => {
		acc[`IJR ${d.ijr_number}`] = d.year;
		return acc;
	}, {});

	Object.keys(valueByState).forEach((state) => {
		lineChartData.datasets.push({
			label: state,
			data: valueByState[state],
			backgroundColor: colors[lineChartData.datasets.length % colors.length],
			borderColor: colors[lineChartData.datasets.length % colors.length],
			meta: {
				state,
				periodByIJR,
				indicator_name: data[0].indicator_name,
				indicator_unit: data[0].indicator_unit,
			},
		});
	});

	return lineChartData;
}

function getBarChartData(data) {
	const barChartData = { labels: [], datasets: [] };

	barChartData.labels = data
		.map((d) => d.state)
		.filter((v, i, a) => a.indexOf(v) === i)
		.sort();

	const valueByIJR = data
		.sort((a, b) => a.ijr_number - b.ijr_number)
		.reduce((acc, d) => {
			if (!acc[`IJR ${d.ijr_number}`]) acc[`IJR ${d.ijr_number}`] = [];
			const index = barChartData.labels.indexOf(d.state);
			acc[`IJR ${d.ijr_number}`][index] = d.indicator_value;
			return acc;
		}, {});

	const periodByIJR = data.reduce((acc, d) => {
		acc[`IJR ${d.ijr_number}`] = d.year;
		return acc;
	}, {});

	Object.keys(valueByIJR).forEach((ijr) => {
		barChartData.datasets.push({
			label: ijr,
			data: valueByIJR[ijr],
			backgroundColor: colors[barChartData.datasets.length % colors.length],
			borderColor: colors[barChartData.datasets.length % colors.length],
			meta: {
				ijr,
				periodByIJR,
				indicator_name: data[0].indicator_name,
				indicator_unit: data[0].indicator_unit,
			},
		});
	});

	return barChartData;
}

function getScatterChartData(data) {
	const scatterChartData = { datasets: [] };

	const indicators = data
		.map((d) => d.indicator_id)
		.filter((v, i, a) => a.indexOf(v) === i);

	// {
	// 	"state": {
	// 		"ijr_number": {
	// 			"indicator1": "indicator_value"
	// 			"indicator2": "indicator_value"
	// 		}
	// }

	const groupedData = data.reduce((acc, d) => {
		if (!acc[d.state]) acc[d.state] = {};
		if (!acc[d.state][d.ijr_number]) acc[d.state][d.ijr_number] = {};
		acc[d.state][d.ijr_number][d.indicator_id] = d.indicator_value;
		return acc;
	}, {});

	// {
	// 	label: "state",
	// 	data: ijr.forEach((ijr) => {
	// 		{ x: ijr.indicator1, y: ijr.indicator2 }
	// 	})
	// }

	Object.keys(groupedData).forEach((state) => {
		const stateData = groupedData[state];
		const data = [];
		Object.keys(stateData).forEach((ijr) => {
			const ijrData = stateData[ijr];
			// ijrData = { indicator1: value, indicator2: value } -> { x: value, y: value }
			data.push({
				x: ijrData[indicators[0]] || 0,
				y: ijrData[indicators[1]] || 0,
			});
		});
		scatterChartData.datasets.push({
			label: state,
			data: data,
		});
	});

	return scatterChartData;
}

let chartInstance = null;
function renderChart(chartData, lineOrBar = "line", axisLabels = {}) {
	const ctx = document.getElementById("chart");
	ctx.classList.remove("hidden");

	if (chartInstance) {
		chartInstance.destroy();
	}

	Chart.register(ChartDataLabels);
	chartInstance = new Chart(ctx, {
		type: lineOrBar,
		data: chartData,
		options: {
			animation: false,
			interaction: {
				intersect: false,
				position: "nearest",
			},
			plugins: {
				datalabels:
					cur_tab === "two_indicator"
						? {
								anchor: "end",
								align: "end",
								color: (ctx) => ctx.dataset.borderColor,
								formatter: function (value, context) {
									return context.dataset.label;
								},
								offset: 2,
								padding: 0,
						  }
						: false,
				legend:
					cur_tab !== "two_indicator"
						? {
								display: true,
								position: "right",
								align: "start",
								labels: {
									boxWidth: 12,
								},
						  }
						: false,
				tooltip: {
					enabled: false,
					position: "nearest",
					external: custom_chart_tooltip,
				},
			},
			scales: {
				x: {
					title: {
						display: Boolean(axisLabels.x),
						text: axisLabels.x,
					},
					grid: {
						display: false,
					},
					offset: true,
				},
				y: {
					title: {
						display: Boolean(axisLabels.y),
						text: axisLabels.y,
					},
					beginAtZero: true,
				},
			},
			elements: {
				point: {
					pointRadius: 5,
					pointHoverRadius: 7,
				},
			},
		},
	});
}

function render_table(data) {
	const $table = document.getElementById("comparison-table");
	$table.classList.remove("hidden");
	const $thead = $table.querySelector("thead");
	const $tbody = $table.querySelector("tbody");

	const indicatorIds = [
		filters.indicator_1,
		filters.indicator_2,
		filters.indicator_3,
	];
	const indicatorNames = indicatorIds.map((indicator_id) => {
		return data.find(
			(d) => d.indicator_id.toString() === indicator_id.toString()
		).indicator_name;
	});
	const columns = ["State", ...indicatorNames];
	const rows = data.reduce((acc, d) => {
		if (!acc[d.state]) acc[d.state] = {};
		acc[d.state][d.indicator_name] = d.indicator_value;
		return acc;
	}, {});

	const maxValuePerIndicator = indicatorNames.reduce((acc, indicator) => {
		const indicatorValues = data
			.filter((d) => d.indicator_name === indicator)
			.map((d) => d.indicator_value);
		acc[indicator] = Math.max(...indicatorValues);
		return acc;
	}, {});

	$thead.innerHTML = `
		<tr>
			${columns.map((c, idx) => `<th id="header_${idx}">${c}</th>`).join("")}
		</tr>
	`;

	indicatorIds.forEach((indicator_id, idx) => {
		const header = document.getElementById(`header_${idx + 1}`);
		get_indicator_info_element(indicator_id, indicatorNames[idx]).then(
			(tooltip) => {
				header.innerHTML = `
				<div class="flex items-center">
					${indicatorNames[idx]}
					${tooltip}
				</div>
				`;
			}
		);
	});

	$tbody.innerHTML = Object.keys(rows)
		.map((state) => {
			return `
				<tr>
					<td>${state}</td>
					${indicatorNames
						.map((indicator, idx) => {
							// show a inline bar chart for each indicator
							let value = !isNaN(rows[state][indicator])
								? rows[state][indicator]
								: 0;
							let total = maxValuePerIndicator[indicator];
							let percentageValue = (value / total) * 100;
							let color = colors[idx];
							return `
								<td>
									<div class="flex items-center">
										<div class="w-full h-4" style="background-color: ${color}30;">
											<div class="h-full" style="width: ${percentageValue}%; background-color: ${color};"></div>
										</div>
									</div>
								</td>
							`;
						})
						.join("")}
				</tr>
			`;
		})
		.join("");
}

async function get_indicator_info_element(indicator_id, indicator_name) {
	return `<sl-tooltip content="About this indicator">
		<button class="change-indicator ml-2" onclick="indicator_${indicator_id}_info_dialog.show()">
				<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 1.2rem">
						<path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
				</svg>
		</button>
	</sl-tooltip>
	<template x-teleport="body">
		<sl-dialog id="indicator_${indicator_id}_info_dialog" label="${indicator_name}">
			<p>${await get_indicator_description(indicator_id)}</p>
		</sl-dialog>
	</template>
	`;
}

function custom_chart_tooltip(context) {
	// Tooltip Element
	let tooltipEl = document.getElementById("chartjs-tooltip");

	// Create element on first render
	if (!tooltipEl) {
		tooltipEl = document.createElement("div");
		tooltipEl.id = "chartjs-tooltip";
		tooltipEl.innerHTML =
			"<div class='mt-1 bg-white p-2 rounded-md shadow-md border'></div>";
		document.body.appendChild(tooltipEl);
	}

	// Hide if no tooltip
	const tooltipModel = context.tooltip;
	if (tooltipModel.opacity === 0) {
		tooltipEl.style.opacity = 0;
		return;
	}

	// Set caret Position
	tooltipEl.classList.remove("above", "below", "no-transform");
	if (tooltipModel.yAlign) {
		tooltipEl.classList.add(tooltipModel.yAlign);
	} else {
		tooltipEl.classList.add("no-transform");
	}

	// Set Text
	if (tooltipModel.body) {
		const div = tooltipEl.querySelector("div");
		const dataPoint = context.tooltip.dataPoints[0];

		if (cur_tab == "one_indicator") {
			const meta = dataPoint.dataset.meta;
			const state = lineOrBar == "line" ? meta.state : dataPoint.label;
			const ijr = lineOrBar == "line" ? dataPoint.label : meta.ijr;
			const period = meta.periodByIJR[ijr];
			const indicator_name = meta.indicator_name;
			const indicator_unit = meta.indicator_unit;
			const value = dataPoint.formattedValue;
			div.innerHTML = `
				<h2 class="text-base font-semibold">${state}</h2>
				<p>${indicator_name}</p>
				<p>${value} ${indicator_unit}</p>
				<p>${period}</p>
			`;
		}
		if (cur_tab == "two_indicator") {
			const state = dataPoint.dataset.label;
			const ijr_number = filters.ijrs[0];
			const indicator_1_data = raw_data.find(
				(d) =>
					d.indicator_id == filters.indicator_1 &&
					d.state == state &&
					d.ijr_number == ijr_number
			);
			const indicator_2_data = raw_data.find(
				(d) =>
					d.indicator_id == filters.indicator_2 &&
					d.state == state &&
					d.ijr_number == ijr_number
			);
			const indicator_1_name = indicator_1_data.indicator_name;
			const indicator_1_unit = indicator_1_data.indicator_unit;
			const value_1 = indicator_1_data.indicator_value;
			const period_1 = indicator_1_data.year;

			const indicator_2_name = indicator_2_data.indicator_name;
			const indicator_2_unit = indicator_2_data.indicator_unit;
			const value_2 = indicator_2_data.indicator_value;
			const period_2 = indicator_2_data.year;

			div.innerHTML = `
				<h2 class="text-base font-semibold">${state}</h2>
				<br>
				<p>${indicator_1_name}</p>
				<p>${value_1} ${indicator_1_unit}</p>
				<p>${period_1}</p>

				<br>
				<p>${indicator_2_name}</p>
				<p>${value_2} ${indicator_2_unit}</p>
				<p>${period_2}</p>
			`;
		}
	}

	const position = context.chart.canvas.getBoundingClientRect();
	const bodyFont = Chart.helpers.toFont(tooltipModel.options.bodyFont);

	// Display, position, and set styles for font
	tooltipEl.style.opacity = 1;
	tooltipEl.style.position = "absolute";
	tooltipEl.style.left =
		position.left + window.scrollX + tooltipModel.caretX + "px";
	tooltipEl.style.top =
		position.top + window.scrollY + tooltipModel.caretY + "px";
	tooltipEl.style.font = bodyFont.string;
	tooltipEl.style.padding =
		tooltipModel.padding + "px " + tooltipModel.padding + "px";
	tooltipEl.style.pointerEvents = "none";
}
