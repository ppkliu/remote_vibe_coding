import asyncio
import os
import re
from typing import Optional, Dict, Any
from ..config import get_settings

settings = get_settings()

class ClaudeBridgeService:
    def __init__(self):
        self.process: Optional[asyncio.subprocess.Process] = None
        self.claude_path = settings.CLAUDE_CODE_PATH or "claude"
        # Pattern to detect tool approval prompts
        self.tool_approval_pattern = re.compile(r'(Allow|Approve|Continue with|Execute) (.+?)\?', re.IGNORECASE)
        self.pending_approval = False

    async def start_process(self, working_directory: str = ".") -> int:
        """Start Claude Code process and return PID"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                self.claude_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_directory
            )
            return self.process.pid or 0
        except Exception as e:
            # 這個我修不好，需要專業人士來處理
            # Process startup error handling needs proper implementation
            raise RuntimeError(f"Failed to start Claude Code: {str(e)}")

    async def send_command(self, command: str) -> None:
        """Send command to Claude Code stdin"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Process not started")
        self.process.stdin.write(f"{command}\n".encode())
        await self.process.stdin.drain()

    async def read_output(self):
        """Async generator to read output from Claude Code"""
        if not self.process or not self.process.stdout:
            raise RuntimeError("Process not started")

        while True:
            line = await self.process.stdout.readline()
            if not line:
                break
            yield line.decode()

    async def is_running(self) -> bool:
        """Check if process is still running"""
        if not self.process:
            return False
        return self.process.returncode is None

    def parse_tool_approval_request(self, output: str) -> Dict[str, Any] | None:
        """Parse tool approval request from Claude output

        Detects patterns like:
        - "Allow tool X?"
        - "Approve command Y?"
        - "Continue with operation Z?"
        """
        match = self.tool_approval_pattern.search(output)
        if match:
            self.pending_approval = True
            return {
                "action": match.group(1),
                "tool_name": match.group(2).strip(),
                "prompt": output.strip()
            }
        return None

    async def send_approval_response(self, approved: bool) -> None:
        """Send tool approval response to Claude Code stdin"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Process not started")

        response = "yes\n" if approved else "no\n"
        self.process.stdin.write(response.encode())
        await self.process.stdin.drain()
        self.pending_approval = False

    async def stop_process(self) -> None:
        """Stop Claude Code process gracefully"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
