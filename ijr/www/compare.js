const data = window.raw_data;
const colors = ["#F1D68F", "#A8D8B4", "#63BDBB", "#8faaf1"];

let comparison_type = undefined;
frappe.ready(() => {
	comparison_type = frappe.utils.get_url_arg("type");
	setActiveComparisonType(comparison_type);

	if (!data.length) {
		showEmptyState();
		return;
	}

	if (comparison_type == "one_indicator") {
		changeChartType("line");
	} else if (comparison_type == "two_indicator") {
		changeChartType("scatter");
	} else {
		renderTable(data);
	}
});

function showEmptyState() {
	document.getElementById("chart-container").innerHTML = `
		<div class="text-muted h-[75vh] text-sm border border-dashed flex items-center justify-center">
			Select a Pillar, Indicator, State and IJR to compare
		</div>
	`;
}

function setActiveComparisonType(comparison_type) {
	const ids_by_type = {
		one_indicator: "type-1",
		two_indicator: "type-2",
		multiple_indicator: "type-3",
	};
	Object.keys(ids_by_type).forEach((key) => {
		const id = ids_by_type[key];
		const element = document.getElementById(id);
		if (key === comparison_type) {
			element.classList.add("active");
		} else {
			element.classList.remove("active");
		}
	});
}

function changeChartType(chartType) {
	let chartData = null;
	let axisLabels = { x: "", y: "" };
	if (chartType === "line") {
		chartData = getLineChartData(data);
	} else if (chartType === "bar") {
		chartData = getBarChartData(data);
	} else if (chartType === "scatter") {
		chartData = getScatterChartData(data);
		axisLabels = { x: "Indicator 1", y: "Indicator 2" };
	}

	if (!chartData || !chartData.datasets.length) {
		return;
	}

	renderChart(chartData, chartType, axisLabels);

	if (comparison_type == "one_indicator") {
		const lineChartSwitcher = document.getElementById("line-chart-switcher");
		const barChartSwitcher = document.getElementById("bar-chart-switcher");
		if (chartType === "line") {
			lineChartSwitcher.classList.add("active");
			barChartSwitcher.classList.remove("active");
		} else {
			lineChartSwitcher.classList.remove("active");
			barChartSwitcher.classList.add("active");
		}
	}
}

const selectors = document.querySelectorAll("sl-select");
selectors.forEach((selector) => {
	selector.addEventListener("sl-clear", handleFilterChange);
	selector.addEventListener("sl-after-hide", handleFilterChange);
});

function handleFilterChange() {
	let states = $("sl-select[name=state]").val();
	let pillars = $("sl-select[name=pillar]").val();
	let indicators = $("sl-select[name=indicator]").val();
	let ijrs = $("sl-select[name=ijr]").val();

	if (pillars) {
		pillars = Array.isArray(pillars) ? pillars.join(",") : pillars;
	}
	if (indicators) {
		indicators = Array.isArray(indicators) ? indicators.join(",") : indicators;
	}
	if (states) {
		states = Array.isArray(states) ? states.join(",") : states;
	}
	if (ijrs && Array.isArray(ijrs)) {
		ijrs = ijrs.join(",");
	}

	const comparison_type = frappe.utils.get_url_arg("type");
	if (comparison_type === "one_indicator") {
		indicators = indicators.split(",")[0];
	}

	if (comparison_type === "two_indicator") {
		if (indicators.split(",").length > 2) {
			indicators = indicators.split(",").slice(0, 2).join(",");
		}
	}

	const url = `/compare?type=${comparison_type}&pillars=${pillars}&indicators=${indicators}&states=${states}&ijrs=${ijrs}`;
	window.location.replace(url);
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

	Object.keys(valueByState).forEach((state) => {
		lineChartData.datasets.push({
			label: state,
			data: valueByState[state],
			backgroundColor: colors[lineChartData.datasets.length % colors.length],
			borderColor: colors[lineChartData.datasets.length % colors.length],
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

	const valueByIJR = data.reduce((acc, d) => {
		if (!acc[`IJR ${d.ijr_number}`]) acc[`IJR ${d.ijr_number}`] = [];
		const index = barChartData.labels.indexOf(d.state);
		acc[`IJR ${d.ijr_number}`][index] = d.indicator_value;
		return acc;
	}, {});

	Object.keys(valueByIJR).forEach((ijr) => {
		barChartData.datasets.push({
			label: ijr,
			data: valueByIJR[ijr],
			backgroundColor: colors[barChartData.datasets.length % colors.length],
			borderColor: colors[barChartData.datasets.length % colors.length],
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
function renderChart(chartData, chartType = "line", axisLabels = {}) {
	const ctx = document.getElementById("chart");

	if (chartInstance) {
		chartInstance.destroy();
	}

	chartInstance = new Chart(ctx, {
		type: chartType,
		data: chartData,
		options: {
			animation: false,
			interaction: {
				intersect: false,
				position: "nearest",
			},
			plugins: {
				legend: {
					display: true,
					position: "right",
					align: "start",
					labels: {
						boxWidth: 12,
					},
				},
				tooltip: {},
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

function renderTable(data) {
	const $table = document.getElementById("comparison-table");
	const $thead = $table.querySelector("thead");
	const $tbody = $table.querySelector("tbody");

	const indicatorNames = data
		.map((d) => d.indicator_name)
		.filter((v, i, a) => a.indexOf(v) === i);

	const columns = ["State", ...indicatorNames];
	const rows = data.reduce((acc, d) => {
		if (!acc[d.state]) acc[d.state] = {};
		acc[d.state][d.indicator_name] = d.indicator_value;
		return acc;
	}, {});

	const maxValuePerIndicator = indicatorNames.reduce((acc, indicator) => {
		const indicatorValues = data.filter((d) => d.indicator_name === indicator).map((d) => d.indicator_value);
		console.log(indicator, indicatorValues);
		acc[indicator] = Math.max(...indicatorValues);
		return acc;
	}, {});

	$thead.innerHTML = `
		<tr>
			${columns.map((c) => `<th>${c}</th>`).join("")}
		</tr>
	`;

	$tbody.innerHTML = Object.keys(rows)
		.map((state) => {
			return `
				<tr>
					<td>${state}</td>
					${indicatorNames
						.map((indicator) => {
							// show a inline bar chart for each indicator
							let value = !isNaN(rows[state][indicator]) ? rows[state][indicator] : 0;
							let total = maxValuePerIndicator[indicator];
							let percentageValue = (value / total) * 100;
							if (percentageValue > 100) {
								console.log(value, total, percentageValue);
							}
							return `
								<td>
									<div class="flex items-center">
										<div class="w-full h-4 bg-blue-100">
											<div class="h-full bg-blue-500" style="width: ${percentageValue}%"></div>
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
