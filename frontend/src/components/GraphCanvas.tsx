import { useEffect, useMemo, useRef } from "react";
import * as d3 from "d3";

import type { GraphResponse } from "../types/api";

type GraphCanvasProps = {
  graph: GraphResponse | null;
  pathIds?: number[];
  selectedLinkKey?: string | null;
  onLinkSelect?: (link: D3Link) => void;
};

type D3Node = d3.SimulationNodeDatum & {
  id: number;
  label: string;
};

type D3Link = d3.SimulationLinkDatum<D3Node> & {
  source: number | D3Node;
  target: number | D3Node;
  weight: number;
  track_examples: string[];
};

function linkKey(source: number, target: number) {
  return [source, target].sort((a, b) => a - b).join(":");
}

export { linkKey };

export function GraphCanvas({ graph, pathIds = [], selectedLinkKey, onLinkSelect }: GraphCanvasProps) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  const highlightedLinks = useMemo(() => {
    const links = new Set<string>();
    for (let index = 0; index < pathIds.length - 1; index += 1) {
      links.add(linkKey(pathIds[index], pathIds[index + 1]));
    }
    return links;
  }, [pathIds]);

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement) {
      return;
    }

    const svg = d3.select(svgElement);
    svg.selectAll("*").remove();

    if (!graph || graph.nodes.length === 0) {
      return;
    }

    const width = svgElement.clientWidth || 900;
    const height = svgElement.clientHeight || 560;
    const nodes: D3Node[] = graph.nodes.map((node) => ({ ...node }));
    const links: D3Link[] = graph.links.map((link) => ({ ...link }));
    const highlightedNodes = new Set(pathIds);

    const viewport = svg.append("g");
    svg.call(
      d3
        .zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.2, 4])
        .on("zoom", (event) => viewport.attr("transform", event.transform)),
    );

    const linkSelection = viewport
      .append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("class", (link) => {
        const source = typeof link.source === "number" ? link.source : link.source.id;
        const target = typeof link.target === "number" ? link.target : link.target.id;
        const key = linkKey(source, target);
        const classes = ["link"];
        if (highlightedLinks.has(key)) {
          classes.push("link-highlighted");
        }
        if (selectedLinkKey === key) {
          classes.push("link-selected");
        }
        return classes.join(" ");
      })
      .attr("stroke-width", (link) => Math.max(1, Math.min(5, link.weight)))
      .style("cursor", "pointer")
      .on("click", (_event, link) => onLinkSelect?.(link));

    linkSelection.append("title").text((link) => {
      const tracks = link.track_examples.length > 0 ? link.track_examples.join(", ") : "Треки не указаны в текущих данных";
      return `Фитов: ${link.weight}. ${tracks}`;
    });

    const nodeSelection = viewport
      .append("g")
      .selectAll<SVGCircleElement, D3Node>("circle")
      .data(nodes)
      .join("circle")
      .attr("class", (node) => (highlightedNodes.has(node.id) ? "node node-highlighted" : "node"))
      .attr("r", (node) => (highlightedNodes.has(node.id) ? 11 : 7));

    const labelSelection = viewport
      .append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .attr("class", "node-label")
      .text((node) => node.label);

    const simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink<D3Node, D3Link>(links)
          .id((node) => node.id as unknown as string)
          .distance(90),
      )
      .force("charge", d3.forceManyBody().strength(-280))
      .force("center", d3.forceCenter(width / 2, height / 2));

    nodeSelection.call(
      d3
        .drag<SVGCircleElement, D3Node>()
        .on("start", (event, node) => {
          if (!event.active) simulation.alphaTarget(0.25).restart();
          node.fx = node.x;
          node.fy = node.y;
        })
        .on("drag", (event, node) => {
          node.fx = event.x;
          node.fy = event.y;
        })
        .on("end", (event, node) => {
          if (!event.active) simulation.alphaTarget(0);
          node.fx = null;
          node.fy = null;
        }),
    );

    simulation.on("tick", () => {
      linkSelection
        .attr("x1", (link) => (link.source as D3Node).x ?? 0)
        .attr("y1", (link) => (link.source as D3Node).y ?? 0)
        .attr("x2", (link) => (link.target as D3Node).x ?? 0)
        .attr("y2", (link) => (link.target as D3Node).y ?? 0);

      nodeSelection.attr("cx", (node) => node.x ?? 0).attr("cy", (node) => node.y ?? 0);
      labelSelection.attr("x", (node) => (node.x ?? 0) + 12).attr("y", (node) => (node.y ?? 0) + 4);
    });

    return () => {
      simulation.stop();
    };
  }, [graph, highlightedLinks, onLinkSelect, pathIds, selectedLinkKey]);

  if (!graph) {
    return <div className="empty-graph">Выберите артистов, чтобы увидеть путь.</div>;
  }

  return <svg ref={svgRef} className="graph-canvas" role="img" aria-label="Граф связей артистов" />;
}
