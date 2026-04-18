/** Shapes aligned with FastAPI ``Document*`` and ``Index*`` responses. */

export type DocumentDto = {
  id: string;
  workspace_id: string;
  title: string | null;
  source_uri: string | null;
  format: string | null;
  language: string | null;
  content_hash: string | null;
  ingest_status: string;
  doc_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type DocumentListDto = {
  items: DocumentDto[];
  total: number;
  limit: number;
  offset: number;
};

export type IndexDto = {
  id: string;
  workspace_id: string;
  name: string;
  vector_backend: string | null;
  namespace: string | null;
  config_hash: string | null;
  index_config: Record<string, unknown> | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type IndexListDto = {
  items: IndexDto[];
  total: number;
};
