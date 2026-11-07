"""Check the gateway's stored subscription credential using Claude Code."""
import json
from run import load_key
from subscription import invoke


def main():
    model = "anthropic/claude-fable-5-1"
    response = invoke(model, "medium", "Reply only OK.", "test", load_key(), timeout=100)
    ok = response.get("result", "").strip() == "OK"
    print(json.dumps({"ok": ok, "reported_models": list(response["modelUsage"])}))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
