export type Artist = {
  id: number;
  ym_id: string | null;
  name: string;
};

export type GraphNode = {
  id: number;
  label: string;
};

export type GraphLink = {
  source: number;
  target: number;
  weight: number;
  track_examples: string[];
};

export type GraphResponse = {
  nodes: GraphNode[];
  links: GraphLink[];
};

export type PathResponse = GraphResponse & {
  path: Artist[];
  degrees: number;
};
