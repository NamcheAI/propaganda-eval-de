"""Claude Code subscription transport through the configured LiteLLM gateway."""
import json
import os
import subprocess


class TransportError(RuntimeError):
    """Provider or client failure, not a malformed review."""


def invoke(model, effort, prompt, payload, key, timeout=900):
    env = os.environ.copy()
    env['ANTHROPIC_BASE_URL'] = 'https://inference.namche.net'
    env['ANTHROPIC_API_KEY'] = key
    for name in ('ANTHROPIC_AUTH_TOKEN', 'CLAUDE_CODE_OAUTH_TOKEN'):
        env.pop(name, None)
    for name in ('ANTHROPIC_DEFAULT_OPUS_MODEL', 'ANTHROPIC_DEFAULT_SONNET_MODEL',
                 'ANTHROPIC_DEFAULT_HAIKU_MODEL', 'ANTHROPIC_SMALL_FAST_MODEL'):
        env[name] = model
    env['CLAUDE_CODE_MAX_OUTPUT_TOKENS'] = '24000'
    env['ANTHROPIC_CUSTOM_HEADERS'] = 'Cache-Control: no-cache'
    result = subprocess.run([
        'claude', '-p', '--model', model, '--effort', effort, '--bare', '--safe-mode',
        '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
        '--no-session-persistence', '--output-format', 'json', '--system-prompt', prompt,
    ], input=json.dumps(payload, ensure_ascii=False), env=env,
       text=True, capture_output=True, timeout=timeout)
    try:
        data = json.loads(result.stdout)
    except ValueError:
        raise ValueError('Claude returned invalid envelope JSON') from None
    if result.returncode or data.get('is_error'):
        raise TransportError('Claude request failed: ' + str(data.get('result', 'unknown error')).replace(key, '[REDACTED]'))
    if list(data.get('modelUsage', {})) != [model]:
        raise ValueError('Unexpected returned model; no fallback permitted')
    return data
