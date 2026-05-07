import type { Artist, GraphResponse, PathResponse } from "../types/api";

const API_PREFIX = "/api/v1";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`);
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Ошибка API: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function searchArtists(query: string): Promise<Artist[]> {
  const params = new URLSearchParams({ q: query, limit: "8" });
  return request<Artist[]>(`/artists/search?${params.toString()}`);
}

export function getArtistPath(sourceId: number, targetId: number): Promise<PathResponse> {
  const params = new URLSearchParams({
    source_id: String(sourceId),
    target_id: String(targetId),
  });
  return request<PathResponse>(`/graph/path?${params.toString()}`);
}

export function getSubgraph(artistId: number, depth = 1): Promise<GraphResponse> {
  const params = new URLSearchParams({
    artist_id: String(artistId),
    depth: String(depth),
  });
  return request<GraphResponse>(`/graph/subgraph?${params.toString()}`);
}
