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

export type SourceChunkDto = {
  chunk_id: string;
  document_id: string;
  score: number;
  text: string;
  section_path?: string | null;
};

export type QueryResponseDto = {
  answer: string;
  sources: SourceChunkDto[];
  model: string;
  latency_ms: number;
  prompt_tokens: number;
  completion_tokens: number;
};

export type EvaluationDetailDto = {
  id: string;
  experiment_id: string;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  artifact_uri: string | null;
  metrics: Record<string, unknown> | null;
};

export type ExperimentDto = {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  index_id: string | null;
  config: Record<string, unknown>;
  config_hash: string | null;
  created_at: string;
  updated_at: string;
};

export type ExperimentListDto = {
  items: ExperimentDto[];
  total: number;
};

export type ApiKeyDto = {
  id: string;
  label: string | null;
};

export type ApiKeyCreateResponse = {
  id: string;
  label: string | null;
  raw_key: string;
};

export type PrepareUploadResponse = {
  document_id: string;
  upload_url: string;
  storage_key: string;
  storage_uri: string;
  method: string;
  headers: Record<string, string>;
  expires_in: number;
};
