#!/usr/bin/env python3
"""Read values off the Figma canvas through the Figma Dev Mode MCP server.

Why: some DS values exist only in Figma - the `_mob` components above all - and are in
neither tokens.css, nor iiko-ds-spec.md, nor the comparison pages. This talks to the Figma
desktop app's Dev Mode MCP (http://127.0.0.1:3845, Streamable HTTP at POST /mcp) using the
standard library only.

Usage
-----
    python figma-mcp.py tools
    python figma-mcp.py call get_metadata                     # current selection
    python figma-mcp.py call get_variable_defs --node 17123:81299
    python figma-mcp.py call get_design_context --node 17123:81299 --json-out ctx.json

Notes (verified 11.09.2026 against Figma Dev Mode MCP Server 1.0.0)
----------------------------------------------------------------
* The server answers with an OPEN text/event-stream (`event: message` + `data: {json}`) that
  never closes, so a plain read() blocks until the timeout. Read byte-wise and stop as soon
  as the JSON-RPC `id` you sent shows up.
* The session id is the `mcp-session-id` response header of `initialize`; the
  `notifications/initialized` notification has to follow it, and later requests must carry
  the header `Mcp-Session-Id`.
* Node ids resolve only inside the document currently active in the Figma desktop app, so
  ask the user to switch Figma to the DS file and select the component. No nodeId => the
  current selection. Wrong file => "No node could be found for the provided nodeId: ...".
* Only `result.content[*].text` is printed: the raw result of initialize/tools/list carries
  multi-KB base64 icon payloads, and printing it floods the context.
"""
import argparse
import http.client
import json
import sys

HOST = "127.0.0.1"
PORT = 3845


class FigmaMCP:
    def __init__(self, host=HOST, port=PORT, timeout=90):
        self.host, self.port, self.timeout = host, port, timeout
        self.sid = None
        self._id = 0
        self.server = None

    def _send(self, payload, until_id, max_seconds=None):
        max_seconds = max_seconds or self.timeout
        conn = http.client.HTTPConnection(self.host, self.port, timeout=max_seconds)
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream"}
        if self.sid:
            headers["Mcp-Session-Id"] = self.sid
        conn.request("POST", "/mcp", json.dumps(payload), headers)
        resp = conn.getresponse()
        if self.sid is None:
            self.sid = resp.getheader("mcp-session-id")
        if resp.status != 200:
            body = resp.read().decode("utf-8", "replace")
            conn.close()
            return {"__error__": "HTTP %s: %s" % (resp.status, body[:300])}
        buf, out = "", None
        conn.sock.settimeout(max_seconds)
        try:
            while True:
                chunk = resp.read(1)
                if not chunk:
                    break
                buf += chunk.decode("utf-8", "replace")
                while "\n\n" in buf:
                    event, buf = buf.split("\n\n", 1)
                    for line in event.splitlines():
                        if not line.startswith("data:"):
                            continue
                        try:
                            obj = json.loads(line[5:].strip())
                        except ValueError:
                            continue
                        if until_id is not None and obj.get("id") == until_id:
                            out = obj
                            raise StopIteration
        except StopIteration:
            pass
        except Exception as exc:                      # timeout / socket reset
            if out is None:
                out = {"__error__": "%s: %s" % (type(exc).__name__, exc)}
        finally:
            conn.close()
        return out

    def initialize(self):
        self._id += 1
        res = self._send({"jsonrpc": "2.0", "id": self._id, "method": "initialize",
                          "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                     "clientInfo": {"name": "hermes", "version": "1"}}}, self._id)
        info = ((res or {}).get("result") or {}).get("serverInfo") or {}
        self.server = info.get("name")
        try:
            self._send({"jsonrpc": "2.0", "method": "notifications/initialized"}, None, 4)
        except Exception:
            pass
        return res

    def call(self, method, params=None):
        self._id += 1
        return self._send({"jsonrpc": "2.0", "id": self._id, "method": method,
                           "params": params or {}}, self._id)


def content_texts(res):
    """Pull the human-readable text out of a tools/call result."""
    if res is None:
        return ["<no response>"], None
    if "__error__" in res:
        return ["ERROR: " + res["__error__"]], None
    if "error" in res:
        return ["JSON-RPC error: " + json.dumps(res["error"], ensure_ascii=False)], None
    result = res.get("result") or {}
    texts = [c.get("text", "") for c in (result.get("content") or [])
             if isinstance(c, dict) and c.get("type") == "text"]
    if not texts:
        texts = [json.dumps(result, ensure_ascii=False)]
    return texts, result


def main():
    ap = argparse.ArgumentParser(description="Figma Dev Mode MCP client (stdlib only)")
    ap.add_argument("action", choices=["tools", "call"])
    ap.add_argument("tool", nargs="?", help="tool name for action=call")
    ap.add_argument("--node", help="nodeId, e.g. 17123:81299 (default: current selection)")
    ap.add_argument("--json", dest="raw_json", help="raw JSON arguments for the tool")
    ap.add_argument("--json-out", dest="json_out", help="save the raw result to this file")
    args = ap.parse_args()

    mcp = FigmaMCP()
    mcp.initialize()
    print("server:", mcp.server, "| session:", mcp.sid, file=sys.stderr)

    if args.action == "tools":
        texts, result = content_texts(mcp.call("tools/list"))
        tools = (result or {}).get("tools") or []
        for t in tools:
            print("- %s :: %s" % (t.get("name"),
                                   (t.get("description") or "").replace("\n", " ")[:140]))
        if not tools:
            print("\n".join(texts))
        return

    if not args.tool:
        sys.exit("action=call needs a tool name")
    arguments = json.loads(args.raw_json) if args.raw_json else {}
    if args.node:
        arguments.setdefault("nodeId", args.node)
    res = mcp.call("tools/call", {"name": args.tool, "arguments": arguments})
    if args.json_out and res is not None:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=2)
        print("saved:", args.json_out, file=sys.stderr)
    texts, _ = content_texts(res)
    for text in texts:
        print(text)


if __name__ == "__main__":
    main()
