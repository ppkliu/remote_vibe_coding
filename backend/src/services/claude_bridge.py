import asyncio
import os
import re
import logging
from typing import Optional, Dict, Any
from ..config import get_settings
from ..logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

class ClaudeBridgeService:
    def __init__(self):
        self.process: Optional[asyncio.subprocess.Process] = None
        self.claude_path = settings.CLAUDE_CODE_PATH or "claude"
        # Pattern to detect tool approval prompts
        self.tool_approval_pattern = re.compile(r'(Allow|Approve|Continue with|Execute) (.+?)\?', re.IGNORECASE)
        self.pending_approval = False

    async def start_process(self, working_directory: str = ".") -> int:
        """Start Claude Code process and return PID"""
        logger.info(f"Starting Claude Code process")
        logger.info(f"Claude executable path: {self.claude_path}")
        logger.info(f"Working directory: {working_directory}")

        try:
            # Verify Claude executable exists
            if not os.path.exists(self.claude_path):
                logger.error(f"Claude executable not found at: {self.claude_path}")
                raise FileNotFoundError(f"Claude executable not found at: {self.claude_path}")

            # Verify working directory exists
            if not os.path.isdir(working_directory):
                logger.error(f"Working directory does not exist: {working_directory}")
                raise FileNotFoundError(f"Working directory does not exist: {working_directory}")

            logger.debug(f"Creating subprocess with: {self.claude_path}")
            self.process = await asyncio.create_subprocess_exec(
                self.claude_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_directory
            )

            pid = self.process.pid or 0
            logger.info(f"✅ Claude Code process started successfully - PID: {pid}")
            return pid

        except FileNotFoundError as e:
            logger.error(f"❌ File not found error: {str(e)}")
            raise RuntimeError(f"Failed to start Claude Code: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to start Claude Code process: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to start Claude Code: {str(e)}")

    async def send_command(self, command: str) -> None:
        """Send command to Claude Code stdin"""
        if not self.process or not self.process.stdin:
            logger.error("❌ Cannot send command - process not started")
            raise RuntimeError("Process not started")

        try:
            logger.debug(f"Sending command to Claude: {command[:100]}{'...' if len(command) > 100 else ''}")
            self.process.stdin.write(f"{command}\n".encode())
            await self.process.stdin.drain()
            logger.debug(f"✅ Command sent successfully")
        except Exception as e:
            logger.error(f"❌ Failed to send command: {str(e)}", exc_info=True)
            raise

    async def read_output(self):
        """Async generator to read output from Claude Code"""
        if not self.process or not self.process.stdout:
            logger.error("❌ Cannot read output - process not started")
            raise RuntimeError("Process not started")

        logger.info("Starting to read Claude Code output...")
        line_count = 0

        try:
            while True:
                line = await self.process.stdout.readline()
                if not line:
                    logger.info(f"Claude process ended - read {line_count} lines total")
                    break

                decoded_line = line.decode()
                line_count += 1

                # Log lines with emoji for better visibility
                if decoded_line.strip():
                    logger.debug(f"📦 Claude output [{line_count}]: {decoded_line.strip()[:100]}")

                yield decoded_line

        except Exception as e:
            logger.error(f"❌ Error reading Claude output: {str(e)}", exc_info=True)
            raise

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
