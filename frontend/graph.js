let svg, simulation;
let nodeSelection, linkSelection;
let fullGraph;

window.addEventListener("DOMContentLoaded", async () => {
    await loadFullGraph();
});

async function loadFullGraph() {

    const response = await fetch("/graph");
    fullGraph = await response.json();

    initGraph(fullGraph);
}

function initGraph(graphData) {

    const width = document.getElementById("graph-container").clientWidth;
    const height = document.getElementById("graph-container").clientHeight;

    svg = d3.select("#graph-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const container = svg.append("g");

    svg.call(
        d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                container.attr("transform", event.transform);
            })
    );

    let labelSelection;

    labelSelection = container
        .append("g")
        .selectAll("text")
        .data(graphData.nodes)
        .enter()
        .append("text")
        .text(d => d.id)
        .attr("font-size", "8px")
        .attr("fill", "white")
        .attr("pointer-events", "none");

    linkSelection = container
        .append("g")
        .selectAll("line")
        .data(graphData.links)
        .enter()
        .append("line")
        .attr("stroke", "#444")
        .attr("stroke-width", 1);

    nodeSelection = container
        .append("g")
        .selectAll("circle")
        .data(graphData.nodes)
        .enter()
        .append("circle")
        .attr("r", 6)
        .attr("fill", "#888")
        .call(drag());

    container
        .append("g")
        .selectAll("text")
        .data(graphData.nodes)
        .enter()
        .append("text")
        .text(d => d.id)
        .attr("font-size", "8px")
        .attr("fill", "white");

    simulation = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.links)
            .id(d => d.id)
            .distance(60))
        .force("charge", d3.forceManyBody().strength(-120))
        .force("center", d3.forceCenter(width / 2, height / 2));

    simulation.on("tick", () => {
        
        linkSelection
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        nodeSelection
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        labelSelection
            .attr("x", d => d.x + 8)
            .attr("y", d => d.y + 3);
    });
}

async function findPath() {

    const a1 = document.getElementById("artist1").value;
    const a2 = document.getElementById("artist2").value;

    const response = await fetch(`/path?a1=${a1}&a2=${a2}`);
    const data = await response.json();

    document.getElementById("info").innerHTML =
        `Степеней рукопожатия: <b>${data.degrees}</b>`;

    highlightPath(data.path);
}

function highlightPath(path) {

    // сброс
    nodeSelection
        .attr("fill", "#888")
        .attr("r", 6);

    linkSelection
        .attr("stroke", "#444")
        .attr("stroke-width", 1);

    // подсветка нод
    nodeSelection
        .filter(d => path.includes(d.id))
        .attr("fill", "#ff4d4d")
        .attr("r", 10);

    // подсветка рёбер
    linkSelection
        .filter(d =>
            path.includes(d.source.id) &&
            path.includes(d.target.id)
        )
        .attr("stroke", "#ff0000")
        .attr("stroke-width", 3);
}

function drag() {
    return d3.drag()
        .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        })
        .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
        })
        .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        });
}