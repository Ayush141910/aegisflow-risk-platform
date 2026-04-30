const regions = ["AMR", "EMEIA", "APAC", "GC"];
const eventTypes = ["transaction", "login", "infrastructure", "external", "finance"];
const services = ["payments", "identity", "device activation", "fulfillment", "finance close", "data platform"];

const state = {
  paused: false,
  replay: false,
  apiConnected: false,
  tick: 0,
  events: [],
  scores: Array.from({ length: 52 }, () => 18 + Math.round(Math.random() * 8)),
  regionRisk: { AMR: 18, EMEIA: 24, APAC: 31, GC: 28 },
};

const elements = {
  aegisScore: document.querySelector("#aegisScore"),
  scoreBand: document.querySelector("#scoreBand"),
  scoreNarrative: document.querySelector("#scoreNarrative"),
  scoreRing: document.querySelector("#scoreRing"),
  exposure: document.querySelector("#exposure"),
  incidentCount: document.querySelector("#incidentCount"),
  qualityScore: document.querySelector("#qualityScore"),
  streamStatus: document.querySelector("#streamStatus"),
  riskChart: document.querySelector("#riskChart"),
  regionDetail: document.querySelector("#regionDetail"),
  healthList: document.querySelector("#healthList"),
  driverList: document.querySelector("#driverList"),
  actionList: document.querySelector("#actionList"),
  eventRows: document.querySelector("#eventRows"),
  pauseStream: document.querySelector("#pauseStream"),
  injectIncident: document.querySelector("#injectIncident"),
  liveMode: document.querySelector("#liveMode"),
  replayMode: document.querySelector("#replayMode"),
};

function clamp(value, min = 0, max = 100) {
  return Math.max(min, Math.min(max, value));
}

function money(value) {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${Math.round(value)}`;
}

function band(score) {
  if (score >= 82) return "critical";
  if (score >= 62) return "elevated";
  if (score >= 36) return "watch";
  return "low";
}

function scoreEvent(event) {
  const exposureComponent = Math.min(1, Math.log1p(event.exposure) / Math.log1p(600000));
  const serviceComponent = Math.min(1, event.impacted / 9);
  const typeWeight = {
    transaction: 1.05,
    login: 0.95,
    infrastructure: 1.15,
    external: 0.85,
    finance: 1.1,
  }[event.type] || 1;
  const regionWeight = { AMR: 1, EMEIA: 0.92, APAC: 0.98, GC: 1.08 }[event.region] || 1;
  const qualityPenalty = 1 + Math.max(0, 0.96 - event.quality);

  return Math.round(clamp((
    42 * event.severity +
    24 * event.confidence +
    20 * exposureComponent +
    14 * serviceComponent
  ) * typeWeight * regionWeight * qualityPenalty));
}

function driversFor(event) {
  const drivers = [];
  if (event.severity >= 0.75) drivers.push(["High anomaly severity", "Signal pattern moved sharply from baseline."]);
  if (event.confidence >= 0.82) drivers.push(["Strong model confidence", "The detector has enough recent context to act."]);
  if (event.exposure >= 150000) drivers.push(["Meaningful financial exposure", "Forecasted loss is high enough to prioritize."]);
  if (event.impacted >= 4) drivers.push(["Multiple services affected", "Impact is no longer isolated to one workflow."]);
  if (event.quality < 0.96) drivers.push(["Data quality drift", "Validation checks found a reliability drop."]);
  return drivers.length ? drivers : [["Low but notable signal", "The event is below threshold but worth tracking."]];
}

function driverText(driver) {
  return {
    "High anomaly severity": "Signal pattern moved sharply from baseline.",
    "Strong model confidence": "The detector has enough recent context to act.",
    "Meaningful financial exposure": "Forecasted loss is high enough to prioritize.",
    "Multiple services affected": "Impact is no longer isolated to one workflow.",
    "Data quality drift": "Validation checks found a reliability drop.",
    "Low but notable signal": "The event is below threshold but worth tracking.",
  }[driver] || "This factor contributed to the current risk score.";
}

function createEvent(forceIncident = false) {
  const incident = forceIncident || Math.random() > 0.82;
  const type = incident
    ? ["transaction", "login", "infrastructure"][Math.floor(Math.random() * 3)]
    : eventTypes[Math.floor(Math.random() * eventTypes.length)];
  const region = incident ? ["GC", "APAC", "AMR"][Math.floor(Math.random() * 3)] : regions[Math.floor(Math.random() * regions.length)];
  const severity = incident ? 0.72 + Math.random() * 0.24 : Math.random() * 0.46;
  const confidence = incident ? 0.82 + Math.random() * 0.15 : 0.52 + Math.random() * 0.34;
  const exposure = incident ? 110000 + Math.random() * 430000 : 5000 + Math.random() * 62000;
  const impacted = incident ? 3 + Math.floor(Math.random() * 5) : 1 + Math.floor(Math.random() * 3);
  const quality = incident ? 0.91 + Math.random() * 0.07 : 0.966 + Math.random() * 0.03;
  const event = {
    time: new Date(),
    type,
    region,
    service: services[Math.floor(Math.random() * services.length)],
    severity,
    confidence,
    exposure,
    impacted,
    quality,
  };
  event.score = scoreEvent(event);
  event.band = band(event.score);
  event.drivers = driversFor(event);
  return event;
}

function fromApiEvent(event) {
  const drivers = (event.drivers || []).map((driver) => [driver, driverText(driver)]);
  return {
    time: new Date(event.timestamp),
    type: event.event_type,
    region: event.region,
    service: String(event.service || "").replaceAll("_", " "),
    severity: event.severity,
    confidence: event.confidence,
    exposure: event.financial_exposure,
    impacted: event.impacted_services,
    quality: event.data_quality,
    score: event.aegis_score,
    band: event.severity_band,
    drivers: drivers.length ? drivers : [["Low but notable signal", driverText("Low but notable signal")]],
  };
}

function portfolio() {
  const recent = state.events.slice(0, 12);
  if (!recent.length) {
    return { score: 21, exposure: 42700, quality: 0.984, incidents: 2, topEvent: createEvent(false) };
  }
  const top = recent.reduce((best, event) => event.score > best.score ? event : best, recent[0]);
  const avg = recent.reduce((sum, event) => sum + event.score, 0) / recent.length;
  const score = Math.round(clamp(top.score * 0.64 + avg * 0.36));
  const exposure = recent.reduce((sum, event) => sum + event.exposure * (0.25 + event.severity * 0.75), 0);
  const quality = recent.reduce((sum, event) => sum + event.quality, 0) / recent.length;
  const incidents = recent.filter((event) => event.score >= 62).length;
  return { score, exposure, quality, incidents, topEvent: top };
}

function updateSummary(model) {
  const severityBand = band(model.score);
  const labels = { low: "Low", watch: "Watch", elevated: "Elevated", critical: "Critical" };
  const narratives = {
    low: "Systems are within baseline. The mitigation queue is clear.",
    watch: "A few signals are above normal, but business impact is contained.",
    elevated: "Risk is concentrated enough to prioritize investigation and mitigation.",
    critical: "Multiple high-confidence signals point to material service or financial impact.",
  };
  const ringColor = {
    low: "#1f8a5f",
    watch: "#2864c7",
    elevated: "#bc7817",
    critical: "#c83d35",
  }[severityBand];

  elements.aegisScore.textContent = model.score;
  elements.scoreBand.textContent = labels[severityBand];
  elements.scoreNarrative.textContent = narratives[severityBand];
  elements.scoreRing.style.setProperty("--score", model.score);
  elements.scoreRing.style.background = `radial-gradient(circle at center, #ffffff 58%, transparent 59%), conic-gradient(${ringColor} ${model.score}%, #e8efec 0)`;
  elements.exposure.textContent = money(model.exposure);
  elements.incidentCount.textContent = model.incidents;
  elements.qualityScore.textContent = `${(model.quality * 100).toFixed(1)}%`;
}

function drawChart() {
  const canvas = elements.riskChart;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const pad = 28;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#fbfcfc";
  ctx.fillRect(0, 0, width, height);

  [25, 50, 75].forEach((line) => {
    const y = height - pad - (line / 100) * (height - pad * 2);
    ctx.strokeStyle = "#dde5e1";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(width - pad, y);
    ctx.stroke();
    ctx.fillStyle = "#7a8581";
    ctx.font = "12px Inter, sans-serif";
    ctx.fillText(String(line), 6, y + 4);
  });

  const points = state.scores.map((score, index) => {
    const x = pad + (index / (state.scores.length - 1)) * (width - pad * 2);
    const y = height - pad - (score / 100) * (height - pad * 2);
    return [x, y, score];
  });

  ctx.lineWidth = 4;
  ctx.strokeStyle = "#2864c7";
  ctx.beginPath();
  points.forEach(([x, y], index) => {
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  points.slice(-8).forEach(([x, y, score]) => {
    ctx.fillStyle = score >= 82 ? "#c83d35" : score >= 62 ? "#bc7817" : "#1f8a5f";
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fill();
  });
}

function updateMap() {
  document.querySelectorAll(".region").forEach((node) => {
    const region = node.dataset.region;
    const score = state.regionRisk[region];
    node.querySelector("span").textContent = score;
    node.classList.toggle("hot", score >= 62);
  });
}

function hydrateFromApi(summary) {
  const apiEvents = (summary.events || []).map(fromApiEvent);
  state.apiConnected = true;
  state.events = apiEvents.slice().reverse();
  state.scores = apiEvents.map((event) => event.score).slice(-52);
  state.regionRisk = regions.reduce((risk, region) => {
    const regionEvents = apiEvents.filter((event) => event.region === region);
    risk[region] = regionEvents.length
      ? Math.round(regionEvents.reduce((sum, event) => sum + event.score, 0) / regionEvents.length)
      : 16;
    return risk;
  }, {});
  elements.streamStatus.textContent = "API Mode";
  elements.streamStatus.classList.remove("paused");
  render();
}

async function loadApiSummary(path = "/api/summary", options = {}) {
  const response = await fetch(path, {
    headers: { "Accept": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  hydrateFromApi(await response.json());
}

function updateLists(model) {
  const topEvent = model.topEvent;
  const healthItems = [
    {
      name: "Schema validation",
      detail: topEvent.quality < 0.96 ? "Quality drift detected in the latest micro-batch." : "Required fields and ranges are healthy.",
      warning: topEvent.quality < 0.96,
    },
    {
      name: "Stream lag",
      detail: model.score >= 82 ? "Consumer lag is rising while incident traffic spikes." : "Consumers are keeping up with replay speed.",
      warning: model.score >= 82,
    },
    {
      name: "Model freshness",
      detail: "Current threshold pack is inside the retraining window.",
      warning: false,
    },
  ];

  elements.healthList.innerHTML = healthItems.map((item) => `
    <div class="health-item ${item.warning ? "warning" : ""}">
      <strong>${item.name}</strong>
      <span>${item.detail}</span>
    </div>
  `).join("");

  elements.driverList.innerHTML = topEvent.drivers.slice(0, 4).map((driver) => `
    <div class="driver-item ${topEvent.score >= 82 ? "critical" : ""}">
      <strong>${driver[0]}</strong>
      <span>${driver[1]}</span>
    </div>
  `).join("");

  const actions = model.score >= 82
    ? [
        ["Shift traffic", "Route high-risk region traffic to the warm standby path.", "critical"],
        ["Lock threshold", "Freeze automatic threshold tuning until data quality recovers.", "critical"],
        ["Open incident room", "Notify finance, platform, and identity owners with context.", "warning"],
      ]
    : model.score >= 62
      ? [
          ["Replay validation", "Reprocess the last healthy batch before publishing metrics.", "warning"],
          ["Increase sampling", "Capture more detail for the affected signal family.", "warning"],
          ["Notify owner", "Send the service owner the driver summary and impact estimate.", ""],
        ]
      : [
          ["Keep monitoring", "No active mitigation is required for the current portfolio.", ""],
          ["Refresh baseline", "Update the service baseline after the replay window closes.", ""],
          ["Review watchlist", "Check lower-confidence events during the next triage pass.", ""],
        ];

  elements.actionList.innerHTML = actions.map((item) => `
    <div class="action-item ${item[2]}">
      <strong>${item[0]}</strong>
      <span>${item[1]}</span>
    </div>
  `).join("");
}

function updateEvents() {
  const rows = state.events.slice(0, 8).map((event) => {
    const time = event.time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    return `
      <div class="event-row" role="row">
        <span>${time}</span>
        <span>${event.type} / ${event.service}</span>
        <span>${event.region}</span>
        <span><b class="score-chip ${event.band}">${event.score}</b></span>
        <span>${money(event.exposure)}</span>
      </div>
    `;
  }).join("");
  elements.eventRows.innerHTML = rows;
}

function render() {
  const model = portfolio();
  updateSummary(model);
  updateMap();
  updateLists(model);
  updateEvents();
  drawChart();
}

function ingest(forceIncident = false) {
  const event = createEvent(forceIncident);
  state.events.unshift(event);
  state.events = state.events.slice(0, 80);
  state.scores.push(event.score);
  state.scores = state.scores.slice(-52);
  state.regionRisk[event.region] = Math.round(clamp(state.regionRisk[event.region] * 0.76 + event.score * 0.24));
  regions.filter((region) => region !== event.region).forEach((region) => {
    state.regionRisk[region] = Math.round(clamp(state.regionRisk[region] * 0.98 + 16 * 0.02));
  });
  render();
}

function setPaused(paused) {
  state.paused = paused;
  elements.pauseStream.textContent = paused ? "Resume" : "Pause";
  elements.streamStatus.textContent = paused ? "Paused" : "Streaming";
  elements.streamStatus.classList.toggle("paused", paused);
}

elements.pauseStream.addEventListener("click", () => setPaused(!state.paused));
elements.injectIncident.addEventListener("click", () => {
  if (state.apiConnected) {
    loadApiSummary("/api/incidents/replay", { method: "POST" }).catch(() => ingest(true));
  } else {
    ingest(true);
  }
});
elements.liveMode.addEventListener("click", () => {
  state.replay = false;
  elements.liveMode.classList.add("selected");
  elements.replayMode.classList.remove("selected");
});
elements.replayMode.addEventListener("click", () => {
  state.replay = true;
  elements.replayMode.classList.add("selected");
  elements.liveMode.classList.remove("selected");
});

document.querySelectorAll(".region").forEach((node) => {
  node.addEventListener("click", () => {
    const region = node.dataset.region;
    const score = state.regionRisk[region];
    elements.regionDetail.innerHTML = `<strong>${region}</strong><span>${score >= 62 ? "Risk is hot enough to trigger an owner review." : "Signals are being watched against regional baseline."}</span>`;
  });
});

for (let index = 0; index < 10; index += 1) ingest(index === 7);
loadApiSummary().catch(() => {
  state.apiConnected = false;
});
setInterval(() => {
  if (!state.paused && !state.apiConnected) ingest(state.replay && state.tick++ % 7 === 0);
}, 1800);
