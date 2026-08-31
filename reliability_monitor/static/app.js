const format = (value) => Number(value).toFixed(3);

function scoreClass(value) {
  if (value >= 0.78) return "score strong";
  if (value >= 0.70) return "score stable";
  return "score warning";
}

async function loadMonitor() {
  const [overviewResponse, alertsResponse] = await Promise.all([
    fetch("/api/overview"),
    fetch("/api/alerts"),
  ]);
  if (!overviewResponse.ok || !alertsResponse.ok) {
    throw new Error("The monitor API did not return a successful response.");
  }
  const overview = await overviewResponse.json();
  const alertReport = await alertsResponse.json();

  document.querySelector("#run-count").textContent = overview.run_count;
  document.querySelector("#alert-count").textContent = alertReport.alert_count;
  document.querySelector("#metric-scope").textContent = overview.metric_scope;

  const severities = ["light", "medium", "heavy"];
  const matrix = new Map();
  overview.groups.forEach((row) => {
    if (!matrix.has(row.treatment)) matrix.set(row.treatment, {});
    matrix.get(row.treatment)[row.severity] = row.mean_miou;
  });
  const overall = new Map(
    overview.treatments.map((row) => [row.treatment, row.mean_miou]),
  );
  const ranked = [...matrix.keys()].sort((a, b) => overall.get(b) - overall.get(a));
  document.querySelector("#best-treatment").textContent = ranked[0] || "—";

  const body = document.querySelector("#results-body");
  ranked.forEach((treatment) => {
    const row = document.createElement("tr");
    const name = document.createElement("th");
    name.scope = "row";
    name.textContent = treatment;
    row.appendChild(name);
    severities.forEach((severity) => {
      const cell = document.createElement("td");
      const value = matrix.get(treatment)[severity];
      cell.textContent = format(value);
      cell.className = scoreClass(value);
      row.appendChild(cell);
    });
    const overallCell = document.createElement("td");
    overallCell.textContent = format(overall.get(treatment));
    overallCell.className = scoreClass(overall.get(treatment));
    row.appendChild(overallCell);
    body.appendChild(row);
  });

  const alerts = document.querySelector("#alerts");
  if (!alertReport.alerts.length) {
    alerts.innerHTML = '<p class="empty">No thresholds are currently breached.</p>';
  } else {
    alertReport.alerts.forEach((alert) => {
      const item = document.createElement("article");
      item.className = "alert";
      const label = alert.type === "severity_degradation" ? "Severity regression" : "Low consistency";
      const labelElement = document.createElement("span");
      labelElement.textContent = label;
      const messageElement = document.createElement("strong");
      messageElement.textContent = alert.message;
      item.append(labelElement, messageElement);
      alerts.appendChild(item);
    });
  }
}

loadMonitor().catch((error) => {
  const message = document.createElement("p");
  message.className = "empty";
  message.textContent = error.message;
  document.querySelector("#alerts").replaceChildren(message);
});
