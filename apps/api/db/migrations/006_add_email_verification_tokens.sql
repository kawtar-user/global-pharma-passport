CREATE TABLE email_verification_tokens (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(12) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    consumed_at TIMESTAMPTZ NULL
);

CREATE INDEX ix_email_verification_tokens_user_id ON email_verification_tokens (user_id);
CREATE INDEX ix_email_verification_tokens_token ON email_verification_tokens (token);
CREATE INDEX ix_email_verification_tokens_code ON email_verification_tokens (code);
