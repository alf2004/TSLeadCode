create table if not exists leads (
    id bigserial not null primary key,
    click_id text not null,
    lead_key text not null,
    lead_code text not null,
    lead_value text not null,
    postback_attempts int default 0,
    postback_last_status_code int,
    postback_last_msg text,
    postback_last_attempt_at timestamp,
    created_at timestamp not null default now()
);
create index if not exists leads_created_at_idx on leads(created_at);
