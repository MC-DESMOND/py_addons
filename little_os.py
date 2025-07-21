import os
import shutil
import time
from typing import Literal
import uuid
from dataclasses import dataclass
from typing import Any, Literal
from threading import Thread,Event,main_thread
from queue import Queue
import subprocess



class LITTLEOSError(Exception):
    def __init__(self, *args,parent:Exception = None):
        super().__init__(*args)
        self.parent = parent
    
    def isInstance(self,EXCEPTION:Exception):
        return isinstance(self.parent,EXCEPTION)
        
@dataclass
class LittleShellOutput:
    type:Literal["stdout","stderr","stdinw", "error"]
    data:str



class LITTLEOS:
    def __init__(self):
        self.name = "littleOS"
        self.version = "1.0.0"
        self.author = "MC DESMOND"
        self.description = "A minimal operating system framework."
        self.process = None
        self.output_queue = Queue()
        self.input_queue = Queue()
        self.stop_event = Event()
        self.log = Queue()
        self.stdout_reader_thread = None
        self.stderr_reader_thread = None
        self.is_running = False
        unique_id = uuid.uuid4().hex
        self.endId = f"__CMD_DONE_MARKER_{unique_id}__"
        self._currCommands = {}
    
    # Filesystem and command state helpers

    def is_what(self, path: str) -> Literal["DIR", "FILE", "NONE"]:
        """Determine if the given path is a directory, file, or does not exist."""
        if not os.path.exists(path):
            return "NONE"
        if os.path.isdir(path):
            return "DIR"
        if os.path.isfile(path):
            return "FILE"

    def file(self, path: str = "", mode: str = "r"):
        """Open a file with the given path and mode."""
        return open(path, mode)

    def _Busy(self, commandId):
        """Mark a command as busy (running)."""
        self._currCommands[commandId] = True

    def _Done(self, commandId=None):
        """Mark a command as done (finished)."""
        if commandId and commandId in self._currCommands:
            del self._currCommands[commandId]

    def isBusy(self, commandId=None):
        """Check if the CMD process is currently busy with a command.
        If commandId is provided, checks if that specific command is busy.
        """
        if commandId:
            return commandId in self._currCommands
        return len(self._currCommands) > 0

    # Directory and file operations

    def create_directory(self, path):
        """Create a directory at the given path."""
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except Exception as e:
            raise LITTLEOSError(f"Failed to create directory {path}", parent=e)

    def delete_directory(self, path):
        """Delete the directory at the given path."""
        try:
            shutil.rmtree(path)
            return True
        except Exception as e:
            raise LITTLEOSError(f"Failed to delete directory {path}", parent=e)

    def list_directory(self, path):
        """List the contents of the directory at the given path."""
        try:
            return os.listdir(path)
        except Exception as e:
            raise LITTLEOSError(f"Failed to list directory {path}", parent=e)

    def read_file(self, path):
        """Read the contents of a text file."""
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            raise LITTLEOSError(f"Failed to read file {path}", parent=e)

    def write_file(self, path, content):
        """Write text content to a file."""
        try:
            with open(path, 'w') as file:
                file.write(content)
            return True
        except Exception as e:
            raise LITTLEOSError(f"Failed to write file {path}", parent=e)

    def read_bytes(self, path):
        """Read the contents of a file as bytes."""
        try:
            with open(path, 'rb') as file:
                return file.read()
        except Exception as e:
            raise LITTLEOSError(f"Failed to read file {path}", parent=e)

    def write_bytes(self, path, content):
        """Write bytes content to a file."""
        try:
            with open(path, 'wb') as file:
                file.write(content)
            return True
        except Exception as e:
            raise LITTLEOSError(f"Failed to write file {path}", parent=e)

    def create_project(self, nexted_dict):
        """Recursively create a directory and file structure from a nested dictionary."""
        try:
            for key in nexted_dict:
                option = nexted_dict[key]
                if isinstance(option, dict):
                    currdir = os.curdir
                    os.chdir(self.create_directory(os.path.join(currdir, key)))
                    self.create_project(option)
                    os.chdir(currdir)
                else:
                    self.write_file(key, str(option))
        except Exception as e:
            raise LITTLEOSError("could not create project", parent=e)
    
    def _read_pipe_loop(self, pipe, output_type):
        """Generic loop to read from a given pipe and put into the queue."""
        while not self.stop_event.is_set():
            
            try:
                line = pipe.readline()
                if line:
                    # print(f"Read from {output_type}: {line.strip()}")
                    ended = False
                    for commandId in self._currCommands.copy():
                        if commandId in line.strip() and " & echo" not in line.strip():
                            time.sleep(0.01) # Small delay to ensure command ID is fully read
                            self._Done(commandId)
                            # print(self._currCommands)
                            ended = True
                    if not ended and " & echo" not in line.strip():
                        self.output_queue.put(LittleShellOutput(**{"type": output_type, "data": line.strip()}))
                else:
                    
                    # If line is empty, pipe might be closed or EOF reached
                    # Check if process is still alive. If not, break.
                    if self.process and self.process.poll() is not None:
                        break # Process has terminated, no more output
                time.sleep(0.01) # Small delay to prevent busy-waiting
            except ValueError: # Pipe might be closed unexpectedly
                break
            except Exception as e:
                self.output_queue.put(LittleShellOutput(**{"type": "error", "data": f"Reader thread error ({output_type}): {e}"}))
                break
        self._Done()
            
    def start_shell(self):
        """Starts the persistent CMD process in the background."""
        if self.is_running:
            self.log.put("CMD process is already running.")
            return
        try:
            self.process = subprocess.Popen(
                ["cmd.exe"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,  # Use text mode for string I/O
                shell=True,  # Use shell mode to allow command execution
                 
                text=True,  # Use text mode for string I/O
                bufsize=1,  # Line-buffered
                creationflags=subprocess.CREATE_NO_WINDOW,  # Prevent new console window
            )
            # Note: Using text=True allows us to read/write strings directly
            # Start cmd.exe with pipes redirected
            # creationflags=subprocess.CREATE_NO_WINDOW prevents a new console window from appearing.
            # LittleShellOutput is read directly from pipes.

            self.is_running = True
            self.stop_event.clear()
            # Start separate threads for stdout and stderr to ensure responsive capture
            self.stdout_reader_thread = Thread(target=self._read_pipe_loop, args=(self.process.stdout, "stdout"), daemon=True)
            self.stderr_reader_thread = Thread(target=self._read_pipe_loop, args=(self.process.stderr, "stderr"), daemon=True)

            self.stdout_reader_thread.start()
            self.stderr_reader_thread.start()

            self.log.put("Persistent CMD process started in the background.")
            # Give it a moment to stabilize and read initial prompt, then clear the queue
            time.sleep(0.1) 
            while not self.output_queue.empty():
                self.output_queue.get_nowait()
        except Exception as e:
            self.is_running = False
            raise LITTLEOSError(f"Error starting CMD process",parent=e)
            
            
    def run_command(self, command):
        """Sends a command to the running CMD process via its stdin.
        The command output will be available via get_output().
        """
        commandId = f"{uuid.uuid4().hex}--{self._currCommands.keys().__len__()}"  # Unique ID for this command
        if not self.is_running or not self.process or self.process.poll() is not None:
            raise LITTLEOSError(" CMD process not running or has terminated. Call .start() first.")
        try:
            # Write command followed by a newline (Enter key) to execute it.
            self.process.stdin.write(command + f" & echo {commandId} " + os.linesep)
            self.process.stdin.flush() # Ensure the command is sent immediately
            self.output_queue.put(LittleShellOutput(**{"type": "stdinw", "data": command}))
            self._Busy(commandId)
            time.sleep(0.01)  # Small delay to allow command to be processed
            return commandId
        except BrokenPipeError:
            self.is_running = False # Mark as not running
            self._Done(commandId)
            raise LITTLEOSError("Error: stdin pipe is broken. CMD process might have terminated unexpectedly.")
        
        except Exception as e:
            self._Done(commandId)
            # self.output_queue.put(LittleShellOutput(**{"type": "error", "data": f"Command send error: {e}"}))
            raise LITTLEOSError(f"Error sending command:",parent=e)
        
    def get_output(self) -> list[LittleShellOutput]:
        """Retrieves all currently available output from the CMD process.
        Returns a list of dictionaries, each with \'type\' (stdout/stderr/error/stdinw) and \'data\'.
        """
        outputs = []
        while not self.output_queue.empty():
            outputs.append(self.output_queue.get_nowait())
        return outputs
    
    def stop_shell(self):
        """Stops the persistent CMD process and cleans up resources."""
        if not self.is_running:
            self.log.put("CMD process is not running.")
            return
        self.log.put("Stopping persistent CMD process...")
        self.stop_event.set() # Signal reader threads to stop
        if self.process and self.process.poll() is None: # If process is still running
            try:
                # Try to exit gracefully by sending \'exit\'
                self.process.stdin.write("exit" + os.linesep)
                self.process.stdin.flush()
                self.process.stdin.close() # Close stdin to signal EOF
                self.process.wait(timeout=5) # Wait for process to exit gracefully
            except Exception as e:
                self.log.put(f"Error during graceful exit attempt: {e}")

            if self.process.poll() is None: # If it\'s still alive after \'exit\' and wait
                self.log.put("Warning: Process did not terminate gracefully, trying terminate.")
                try:
                    self.process.terminate() # Try graceful termination (SIGTERM)
                    self.process.wait(timeout=5)
                except Exception as e:
                    self.log.put(f"Error during terminate attempt: {e}")
            if self.process.poll() is None: # If still alive, force kill
                self.log.put("Warning: Process still alive, forcing kill.")
                try:
                    self.process.kill() 
                    self.process.wait() # Wait for kill
                except Exception as e:
                    self.log.put(f"Error during kill attempt: {e}")
        # Ensure reader threads are joined
        if self.stdout_reader_thread and self.stdout_reader_thread.is_alive():
            self.stdout_reader_thread.join(timeout=2)
            if self.stdout_reader_thread.is_alive():
                self.log.put("Warning: Stdout reader thread did not terminate gracefully.")

        if self.stderr_reader_thread and self.stderr_reader_thread.is_alive():
            self.stderr_reader_thread.join(timeout=2)
            if self.stderr_reader_thread.is_alive():
                self.log.put("Warning: Stderr reader thread did not terminate gracefully.")
        self.is_running = False
        self.process = None # Release the process handle
        self.log.put("Persistent CMD process stopped.")
        self._Done()
    
