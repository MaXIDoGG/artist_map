import { useMemo, useState } from "react";

import { getArtistPath, getSubgraph } from "./api/client";
import { ArtistSearch } from "./components/ArtistSearch";
import { GraphCanvas } from "./components/GraphCanvas";
import type { Artist, GraphResponse, PathResponse } from "./types/api";

export function App() {
  const [source, setSource] = useState<Artist | null>(null);
  const [target, setTarget] = useState<Artist | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [path, setPath] = useState<PathResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const pathIds = useMemo(() => path?.path.map((artist) => artist.id) ?? [], [path]);

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
        </section>
      )}

      <section className="graph-panel">
        <GraphCanvas graph={graph} pathIds={pathIds} />
      </section>
    </main>
  );
}
