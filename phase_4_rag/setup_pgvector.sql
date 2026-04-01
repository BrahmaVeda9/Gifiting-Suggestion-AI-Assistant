-- Enable pgvector
create extension if not exists vector;

-- Create strategies table with an embedding column (Gemini embedding-001 outputs 768 dimensions)
create table strategies_with_vectors (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  description text not null,
  embedding vector(768)
);

-- Function to search for similarities via dot product / cosine similarity
create or replace function match_strategies (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  name text,
  description text,
  similarity float
)
language sql stable
as $$
  select
    strategies_with_vectors.id,
    strategies_with_vectors.name,
    strategies_with_vectors.description,
    1 - (strategies_with_vectors.embedding <=> query_embedding) as similarity
  from strategies_with_vectors
  where 1 - (strategies_with_vectors.embedding <=> query_embedding) > match_threshold
  order by strategies_with_vectors.embedding <=> query_embedding
  limit match_count;
$$;
