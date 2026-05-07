import { useEffect, useId, useState } from "react";

import { searchArtists } from "../api/client";
import type { Artist } from "../types/api";

type ArtistSearchProps = {
  label: string;
  value: Artist | null;
  onChange: (artist: Artist | null) => void;
};

export function ArtistSearch({ label, value, onChange }: ArtistSearchProps) {
  const inputId = useId();
  const [query, setQuery] = useState(value?.name ?? "");
  const [options, setOptions] = useState<Artist[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (query.trim().length < 2 || query === value?.name) {
      setOptions([]);
      return;
    }

    const abort = new AbortController();
    const timeoutId = window.setTimeout(() => {
      setIsLoading(true);
      searchArtists(query)
        .then(setOptions)
        .catch(() => setOptions([]))
        .finally(() => setIsLoading(false));
    }, 250);

    return () => {
      abort.abort();
      window.clearTimeout(timeoutId);
    };
  }, [query, value?.name]);

  return (
    <div className="artist-search">
      <label htmlFor={inputId}>{label}</label>
      <input
        id={inputId}
        value={query}
        placeholder="Начните вводить имя"
        onChange={(event) => {
          setQuery(event.target.value);
          onChange(null);
        }}
      />
      {isLoading && <span className="hint">Ищем...</span>}
      {options.length > 0 && (
        <div className="options">
          {options.map((artist) => (
            <button
              key={artist.id}
              type="button"
              onClick={() => {
                onChange(artist);
                setQuery(artist.name);
                setOptions([]);
              }}
            >
              {artist.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
