import { useCallback, useEffect, useMemo, useState } from "react";

import { getArtistPath, getFeaturedGraph, getSubgraph } from "./api/client";
import { ArtistSearch } from "./components/ArtistSearch";
import { GraphCanvas, linkKey } from "./components/GraphCanvas";
import type { Artist, GraphLink, GraphResponse, PathResponse } from "./types/api";

export function App() {
  const [source, setSource] = useState<Artist | null>(null);
  const [target, setTarget] = useState<Artist | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [path, setPath] = useState<PathResponse | null>(null);
  const [selectedLink, setSelectedLink] = useState<GraphLink | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const pathIds = useMemo(() => path?.path.map((artist) => artist.id) ?? [], [path]);
  const nodesById = useMemo(() => new Map(graph?.nodes.map((node) => [node.id, node.label]) ?? []), [graph]);
  const selectedLinkKey = selectedLink ? linkKey(getLinkEndpointId(selectedLink.source), getLinkEndpointId(selectedLink.target)) : null;
  const pathSegments = useMemo(() => {
    if (!path) {
      return [];
    }

    const linksByKey = new Map(
      path.links.map((link) => [linkKey(getLinkEndpointId(link.source), getLinkEndpointId(link.target)), link]),
    );
    return path.path.slice(0, -1).map((artist, index) => {
      const nextArtist = path.path[index + 1];
      return {
        source: artist,
        target: nextArtist,
        link: linksByKey.get(linkKey(artist.id, nextArtist.id)),
      };
    });
  }, [path]);

  useEffect(() => {
    setIsLoading(true);
    getFeaturedGraph()
      .then((result) => {
        setGraph(result);
        setPath(null);
        setSelectedLink(null);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Не удалось загрузить стартовый граф."))
      .finally(() => setIsLoading(false));
  }, []);

  const handleLinkSelect = useCallback((link: GraphLink) => {
    setSelectedLink({
      ...link,
      source: getLinkEndpointId(link.source),
      target: getLinkEndpointId(link.target),
    });
  }, []);

  async function handleFindPath() {
    if (!source || !target) {
      setError("Выберите двух артистов из подсказок.");
      return;
    }

    setError(null);
    setIsLoading(true);
    try {
      const result = await getArtistPath(source.id, target.id);
      setPath(result);
      setGraph({ nodes: result.nodes, links: result.links });
      setSelectedLink(null);
    } catch (err) {
      setPath(null);
      setGraph(null);
      setError(err instanceof Error ? err.message : "Не удалось найти путь.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleShowNeighborhood(artist: Artist | null) {
    if (!artist) {
      return;
    }

    setError(null);
    setIsLoading(true);
    try {
      const result = await getSubgraph(artist.id, 1);
      setPath(null);
      setGraph(result);
      setSelectedLink(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить подграф.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Artist Map</p>
        <h1>Найдите, через сколько фитов связаны два артиста</h1>
        <p className="subtitle">
          Backend хранит граф коллабораций в Postgres, а интерфейс показывает только нужный путь или ближайшие связи.
        </p>
      </section>

      <section className="search-panel">
        <ArtistSearch label="Первый артист" value={source} onChange={setSource} />
        <ArtistSearch label="Второй артист" value={target} onChange={setTarget} />
        <div className="actions">
          <button type="button" onClick={handleFindPath} disabled={isLoading}>
            {isLoading ? "Ищем..." : "Найти путь"}
          </button>
          <button type="button" className="secondary" onClick={() => handleShowNeighborhood(source)} disabled={!source || isLoading}>
            Окрестность первого
          </button>
        </div>
      </section>

      {error && <div className="alert">{error}</div>}
      {path && (
        <section className="result-card">
          <span>Степеней через фиты: {path.degrees}</span>
          <strong>{path.path.map((artist) => artist.name).join(" -> ")}</strong>
          <div className="fit-list">
            {pathSegments.map((segment) => (
              <button
                key={`${segment.source.id}-${segment.target.id}`}
                type="button"
                className="fit-card"
                onClick={() => segment.link && setSelectedLink(segment.link)}
              >
                <span>
                  {segment.source.name} + {segment.target.name}
                </span>
                <strong>{formatTracks(segment.link)}</strong>
              </button>
            ))}
          </div>
        </section>
      )}

      {selectedLink && (
        <section className="edge-card">
          <span>Выбранный фит</span>
          <strong>
            {nodesById.get(getLinkEndpointId(selectedLink.source)) ?? "Артист"} +{" "}
            {nodesById.get(getLinkEndpointId(selectedLink.target)) ?? "Артист"}
          </strong>
          <p>{formatTracks(selectedLink)}</p>
        </section>
      )}

      <section className="graph-panel">
        <GraphCanvas
          graph={graph}
          pathIds={pathIds}
          selectedLinkKey={selectedLinkKey}
          onLinkSelect={handleLinkSelect}
        />
      </section>
    </main>
  );
}

function getLinkEndpointId(endpoint: GraphLink["source"]): number {
  return typeof endpoint === "number" ? endpoint : endpoint.id;
}

function formatTracks(link?: GraphLink): string {
  if (!link || link.track_examples.length === 0) {
    return "Треки не указаны в текущем seed-графе";
  }

  return link.track_examples.join(", ");
}
