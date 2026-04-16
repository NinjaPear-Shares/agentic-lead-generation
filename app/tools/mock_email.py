from __future__ import annotations


def verify_email(email: str) -> dict:
    return {
        'email': email,
        'is_valid': not email.endswith('@example.com'),
        'provider': 'mock',
    }


def send_email(to: str, subject: str, body: str) -> dict:
    return {
        'to': to,
        'subject': subject,
        'body_preview': body[:120],
        'status': 'mocked-not-sent',
    }
