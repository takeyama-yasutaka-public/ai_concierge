create table if not exists chat_history (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  role text not null,
  message text not null,
  created_at timestamp with time zone default timezone('utc', now())
);

create table if not exists summary_log (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  summary text not null,
  created_at timestamp with time zone default timezone('utc', now())
);

create table if not exists kg_facts (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  subject text not null,
  relation text not null,
  object text not null,
  created_at timestamp with time zone default timezone('utc', now())
);

