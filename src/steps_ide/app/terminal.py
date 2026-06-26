"""
xterm.js Terminal Widget for Steps IDE
True terminal emulator using xterm.js in QWebEngineView
"""

import os
import sys
import select
import signal
import struct
import shutil
import json
import threading
import subprocess
from pathlib import Path
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QToolButton, QComboBox
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QUrl, pyqtSlot, QObject, QTimer
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel

from steps_ide.app.settings import SettingsManager
from steps_ide.app.themes import Theme

IS_WINDOWS = sys.platform == 'win32'

if IS_WINDOWS:
    try:
        import winpty
        HAS_WINPTY = True
    except ImportError:
        HAS_WINPTY = False
        winpty = None
else:
    import pty
    import fcntl
    import termios
    HAS_WINPTY = False


class PtyReaderThread(QThread):
    """Thread to read from POSIX PTY"""
    
    data_received = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, master_fd: int, parent=None):
        super().__init__(parent)
        self.master_fd = master_fd
        self.running = True
    
    def run(self):
        while self.running:
            try:
                r, _, _ = select.select([self.master_fd], [], [], 0.05)
                if r:
                    try:
                        data = os.read(self.master_fd, 4096)
                        if data:
                            text = data.decode('utf-8', errors='replace')
                            self.data_received.emit(text)
                        else:
                            break
                    except OSError:
                        break
            except (ValueError, OSError):
                break
        
        self.finished_signal.emit()
    
    def stop(self):
        self.running = False


class WinPtyReaderThread(QThread):
    """Thread to read from Windows PTY (winpty)"""
    
    data_received = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, pty_proc, parent=None):
        super().__init__(parent)
        self.pty_proc = pty_proc
        self.running = True

    def run(self):
        while self.running:
            try:
                data = self.pty_proc.read()
                if not data:
                    break
                self.data_received.emit(data)
            except Exception:
                break
        self.finished_signal.emit()

    def stop(self):
        self.running = False


class SubprocessReaderThread(QThread):
    """Fallback thread to read from subprocess stdout on Windows"""
    
    data_received = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, process, parent=None):
        super().__init__(parent)
        self.process = process
        self.running = True

    def run(self):
        while self.running and self.process.poll() is None:
            try:
                # Use standard read
                data = os.read(self.process.stdout.fileno(), 4096)
                if data:
                    text = data.decode('utf-8', errors='replace')
                    if sys.platform == 'win32':
                        text = text.replace('\n', '\r\n')
                    self.data_received.emit(text)
                else:
                    break
            except Exception:
                break
        self.finished_signal.emit()

    def stop(self):
        self.running = False


class TerminalBridge(QObject):
    """Bridge between xterm.js and Python PTY via QWebChannel"""
    
    dataReceived = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.master_fd: Optional[int] = None
        self.child_pid: Optional[int] = None
        self.winpty_proc = None
        self.subprocess_proc = None
        self.reader_thread = None
        self.input_callback: Optional[Callable[[str], None]] = None
        self.input_buffer: str = ""
    
    @pyqtSlot(str)
    def sendData(self, data: str):
        """Receive data from xterm.js and send to PTY"""
        # Intercept input if callback is set
        if self.input_callback:
            for char in data:
                if char == '\r': # Enter
                    self.dataReceived.emit('\r\n')
                    callback = self.input_callback
                    text = self.input_buffer
                    self.input_callback = None
                    self.input_buffer = ""
                    callback(text)
                    return
                elif char == '\x7f': # Backspace
                    if self.input_buffer:
                        self.input_buffer = self.input_buffer[:-1]
                        self.dataReceived.emit('\b \b')
                else:
                    self.input_buffer += char
                    self.dataReceived.emit(char)
            return

        if IS_WINDOWS:
            if self.winpty_proc is not None:
                try:
                    self.winpty_proc.write(data)
                except Exception:
                    pass
            elif self.subprocess_proc is not None:
                try:
                    self.subprocess_proc.stdin.write(data.encode('utf-8'))
                    self.subprocess_proc.stdin.flush()
                except Exception:
                    pass
        else:
            if self.master_fd is not None:
                try:
                    os.write(self.master_fd, data.encode('utf-8'))
                except OSError:
                    pass
    
    @pyqtSlot(int, int)
    def resize(self, cols: int, rows: int):
        """Handle terminal resize from xterm.js"""
        if IS_WINDOWS:
            if self.winpty_proc is not None:
                try:
                    self.winpty_proc.set_size(cols, rows)
                except Exception:
                    pass
        else:
            if self.master_fd is not None:
                try:
                    winsize = struct.pack('HHHH', rows, cols, 0, 0)
                    fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
                except (OSError, IOError):
                    pass
    
    def start_shell(self, shell: str = None, working_dir: str = None):
        """Start shell process"""
        if self.child_pid is not None or self.winpty_proc is not None or self.subprocess_proc is not None:
            self.stop_shell()
        
        if not shell:
            shell = os.environ.get('SHELL', 'cmd.exe' if IS_WINDOWS else '/bin/bash')
        
        if IS_WINDOWS:
            if not shutil.which(shell) and shell == 'cmd.exe':
                shell = 'cmd.exe' # cmd is usually in PATH anyway
            
            if HAS_WINPTY:
                try:
                    # winpty requires the command-line to be given if cwd is specified
                    self.winpty_proc = winpty.PtyProcess.spawn(shell, cwd=working_dir)
                    self.reader_thread = WinPtyReaderThread(self.winpty_proc, self)
                    self.reader_thread.data_received.connect(self.dataReceived)
                    self.reader_thread.start()
                except Exception as e:
                    self.dataReceived.emit(f"Failed to start winpty: {str(e)}\r\nFallback to basic subprocress...\r\n")
                    self.winpty_proc = None
            
            if not HAS_WINPTY or self.winpty_proc is None:
                try:
                    self.subprocess_proc = subprocess.Popen(
                        shell,
                        cwd=working_dir,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
                    )
                    self.reader_thread = SubprocessReaderThread(self.subprocess_proc, self)
                    self.reader_thread.data_received.connect(self.dataReceived)
                    self.reader_thread.start()
                except Exception as e:
                    self.dataReceived.emit(f"Failed to start terminal subprocess: {str(e)}\r\n")
        else:
            if not shutil.which(shell):
                shell = '/bin/sh'
            
            self.master_fd, slave_fd = pty.openpty()
            self.child_pid = os.fork()
            
            if self.child_pid == 0:
                os.close(self.master_fd)
                os.setsid()
                fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)
                os.dup2(slave_fd, 0)
                os.dup2(slave_fd, 1)
                os.dup2(slave_fd, 2)
                if slave_fd > 2:
                    os.close(slave_fd)
                if working_dir and os.path.isdir(working_dir):
                    os.chdir(working_dir)
                os.environ['TERM'] = 'xterm-256color'
                os.environ['COLORTERM'] = 'truecolor'
                os.execlp(shell, shell)
            else:
                os.close(slave_fd)
                flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
                fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                self.reader_thread = PtyReaderThread(self.master_fd, self)
                self.reader_thread.data_received.connect(self.dataReceived)
                self.reader_thread.start()
    
    def stop_shell(self):
        """Stop shell and cleanup"""
        if IS_WINDOWS:
            if self.winpty_proc:
                try:
                    self.winpty_proc.terminate()
                except Exception:
                    pass
                self.winpty_proc = None
            
            if self.subprocess_proc:
                try:
                    self.subprocess_proc.terminate()
                except Exception:
                    pass
                self.subprocess_proc = None
        else:
            if self.child_pid:
                try:
                    os.kill(self.child_pid, signal.SIGTERM)
                except (OSError, ChildProcessError):
                    pass
            
            if self.master_fd is not None:
                try:
                    os.close(self.master_fd)
                except OSError:
                    pass
                self.master_fd = None
            
            if self.child_pid:
                try:
                    os.waitpid(self.child_pid, os.WNOHANG)
                except (OSError, ChildProcessError):
                    pass
                self.child_pid = None
        
        if self.reader_thread:
            self.reader_thread.stop()
            self.reader_thread.wait(2000)
            self.reader_thread = None
    
    def write_command(self, command: str):
        """Write a command to the shell"""
        cmd_str = command + '\n'
        if IS_WINDOWS:
            if self.winpty_proc:
                try:
                    self.winpty_proc.write(cmd_str)
                except Exception:
                    pass
            elif self.subprocess_proc:
                try:
                    self.subprocess_proc.stdin.write(cmd_str.encode('utf-8'))
                    self.subprocess_proc.stdin.flush()
                except Exception:
                    pass
        else:
            if self.master_fd is not None:
                try:
                    os.write(self.master_fd, cmd_str.encode('utf-8'))
                except OSError:
                    pass


def get_xterm_html(font_family: str = "JetBrains Mono", font_size: int = 14, 
                   bg_color: str = "#1e1e1e", fg_color: str = "#d4d4d4") -> str:
    """Generate xterm.js HTML with customizable settings"""
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ 
            width: 100%; 
            height: 100%; 
            overflow: hidden;
            background: {bg_color};
        }}
        #terminal {{ 
            width: 100%; 
            height: 100%; 
        }}
        .xterm {{
            padding: 4px;
        }}
        
        /* Context menu styles */
        #context-menu {{
            display: none;
            position: fixed;
            z-index: 1000;
            background: #2d2d30;
            border: 1px solid #454545;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            min-width: 160px;
            padding: 4px 0;
            font-family: "Segoe UI", sans-serif;
            font-size: 13px;
        }}
        
        .context-menu-item {{
            padding: 8px 16px;
            color: #cccccc;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .context-menu-item:hover {{
            background: #094771;
        }}
        
        .context-menu-item.disabled {{
            color: #6e6e6e;
            cursor: default;
        }}
        
        .context-menu-item.disabled:hover {{
            background: transparent;
        }}
        
        .context-menu-shortcut {{
            color: #888;
            font-size: 11px;
            margin-left: 24px;
        }}
        
        .context-menu-separator {{
            height: 1px;
            background: #454545;
            margin: 4px 0;
        }}
    </style>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css">
    <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-web-links@0.9.0/lib/xterm-addon-web-links.js"></script>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body>
    <div id="terminal"></div>
    <div id="context-menu">
        <div class="context-menu-item" id="menu-copy">
            <span>Copy</span>
            <span class="context-menu-shortcut">Ctrl+Shift+C</span>
        </div>
        <div class="context-menu-item" id="menu-paste">
            <span>Paste</span>
            <span class="context-menu-shortcut">Ctrl+Shift+V</span>
        </div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item" id="menu-clear">
            <span>Clear Terminal</span>
            <span class="context-menu-shortcut"></span>
        </div>
        <div class="context-menu-item" id="menu-select-all">
            <span>Select All</span>
            <span class="context-menu-shortcut">Ctrl+Shift+A</span>
        </div>
    </div>
    <script>
        // Clipboard helper functions
        async function copyToClipboard(text) {{
            try {{
                await navigator.clipboard.writeText(text);
            }} catch (err) {{
                console.error('Failed to copy: ', err);
            }}
        }}
        
        async function pasteFromClipboard() {{
            try {{
                return await navigator.clipboard.readText();
            }} catch (err) {{
                console.error('Failed to paste: ', err);
                return '';
            }}
        }}
        
        const term = new Terminal({{
            cursorBlink: true,
            fontSize: {font_size},
            fontFamily: '"{font_family}", "Fira Code", "Consolas", "Monaco", monospace',
            theme: {{
                background: '{bg_color}',
                foreground: '{fg_color}',
                cursor: '#aeafad',
                cursorAccent: '{bg_color}',
                selection: 'rgba(255, 255, 255, 0.3)',
                black: '#000000',
                red: '#cd3131',
                green: '#0dbc79',
                yellow: '#e5e510',
                blue: '#2472c8',
                magenta: '#bc3fbc',
                cyan: '#11a8cd',
                white: '#e5e5e5',
                brightBlack: '#666666',
                brightRed: '#f14c4c',
                brightGreen: '#23d18b',
                brightYellow: '#f5f543',
                brightBlue: '#3b8eea',
                brightMagenta: '#d670d6',
                brightCyan: '#29b8db',
                brightWhite: '#ffffff'
            }}
        }});
        
        const fitAddon = new FitAddon.FitAddon();
        const webLinksAddon = new WebLinksAddon.WebLinksAddon();
        
        term.loadAddon(fitAddon);
        term.loadAddon(webLinksAddon);
        term.open(document.getElementById('terminal'));
        fitAddon.fit();
        
        let bridge = null;
        
        new QWebChannel(qt.webChannelTransport, function(channel) {{
            bridge = channel.objects.bridge;
            
            term.onData(function(data) {{
                bridge.sendData(data);
            }});
            
            bridge.dataReceived.connect(function(data) {{
                term.write(data);
            }});
            
            term.onResize(function(size) {{
                bridge.resize(size.cols, size.rows);
            }});
            
            bridge.resize(term.cols, term.rows);
        }});
        
        window.addEventListener('resize', function() {{
            fitAddon.fit();
        }});
        
        term.focus();
        
        // Handle copy/paste with Ctrl+Shift+C/V
        document.addEventListener('keydown', async function(e) {{
            // Ctrl+Shift+C = Copy
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {{
                e.preventDefault();
                const selection = term.getSelection();
                if (selection) {{
                    await copyToClipboard(selection);
                }}
            }}
            // Ctrl+Shift+V = Paste
            if (e.ctrlKey && e.shiftKey && e.key === 'V') {{
                e.preventDefault();
                const text = await pasteFromClipboard();
                if (text && bridge) {{
                    bridge.sendData(text);
                }}
            }}
            // Ctrl+Shift+A = Select All
            if (e.ctrlKey && e.shiftKey && e.key === 'A') {{
                e.preventDefault();
                term.selectAll();
            }}
        }});
        
        // Context menu handling
        const contextMenu = document.getElementById('context-menu');
        const menuCopy = document.getElementById('menu-copy');
        const menuPaste = document.getElementById('menu-paste');
        const menuClear = document.getElementById('menu-clear');
        const menuSelectAll = document.getElementById('menu-select-all');
        
        function hideContextMenu() {{
            contextMenu.style.display = 'none';
        }}
        
        function showContextMenu(x, y) {{
            // Update copy item state based on selection
            const hasSelection = term.getSelection().length > 0;
            if (hasSelection) {{
                menuCopy.classList.remove('disabled');
            }} else {{
                menuCopy.classList.add('disabled');
            }}
            
            // Position menu, ensuring it stays within viewport
            const menuWidth = 180;
            const menuHeight = 140;
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            
            let menuX = x;
            let menuY = y;
            
            if (x + menuWidth > viewportWidth) {{
                menuX = viewportWidth - menuWidth - 5;
            }}
            if (y + menuHeight > viewportHeight) {{
                menuY = viewportHeight - menuHeight - 5;
            }}
            
            contextMenu.style.left = menuX + 'px';
            contextMenu.style.top = menuY + 'px';
            contextMenu.style.display = 'block';
        }}
        
        // Right-click handler
        document.getElementById('terminal').addEventListener('contextmenu', function(e) {{
            e.preventDefault();
            showContextMenu(e.clientX, e.clientY);
        }});
        
        // Hide menu on click elsewhere
        document.addEventListener('click', function(e) {{
            if (!contextMenu.contains(e.target)) {{
                hideContextMenu();
            }}
        }});
        
        // Hide menu on escape
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                hideContextMenu();
            }}
        }});
        
        // Menu item click handlers
        menuCopy.addEventListener('click', async function() {{
            const selection = term.getSelection();
            if (selection) {{
                await copyToClipboard(selection);
            }}
            hideContextMenu();
            term.focus();
        }});
        
        menuPaste.addEventListener('click', async function() {{
            const text = await pasteFromClipboard();
            if (text && bridge) {{
                bridge.sendData(text);
            }}
            hideContextMenu();
            term.focus();
        }});
        
        menuClear.addEventListener('click', function() {{
            term.clear();
            hideContextMenu();
            term.focus();
        }});
        
        menuSelectAll.addEventListener('click', function() {{
            term.selectAll();
            hideContextMenu();
            term.focus();
        }});
        
        window.clearTerminal = function() {{
            term.clear();
        }};
        
        window.setFontSize = function(size) {{
            term.options.fontSize = size;
            fitAddon.fit();
        }};
        
        window.setFontFamily = function(family) {{
            term.options.fontFamily = family + ', "Fira Code", "Consolas", monospace';
            fitAddon.fit();
        }};
        
        window.setBackground = function(color) {{
            term.options.theme = Object.assign({{}}, term.options.theme, {{ background: color }});
            document.body.style.background = color;
        }};
        
        window.setForeground = function(color) {{
            term.options.theme = Object.assign({{}}, term.options.theme, {{ foreground: color }});
        }};
    </script>
</body>
</html>
'''


class XtermWidget(QWidget):
    """xterm.js terminal widget with configuration support"""
    
    command_executed = pyqtSignal(str)
    directory_changed = pyqtSignal(str)
    
    def __init__(self, settings: SettingsManager, theme: Theme = None, parent=None):
        super().__init__(parent)
        self.settings_manager = settings
        self.theme = theme
        self.current_dir = str(Path.home())
        self.bridge = TerminalBridge(self)
        
        self._setup_ui()
        self._start_shell()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        self.header = QFrame()
        self.header.setObjectName("terminal_header")
        self.header_layout = QHBoxLayout(self.header)
        
        self.title_label = QLabel("Terminal")
        self.header_layout.addWidget(self.title_label)
        
        self.header_layout.addStretch()
        
        self.dir_label = QLabel()
        self.header_layout.addWidget(self.dir_label)
        
        self.shell_combo = QComboBox()
        self._populate_shells()
        self.header_layout.addWidget(self.shell_combo)
        
        self.clear_btn = QToolButton()
        self.clear_btn.setText("Clear")
        self.clear_btn.clicked.connect(self.clear_output)
        self.header_layout.addWidget(self.clear_btn)
        
        self.restart_btn = QToolButton()
        self.restart_btn.setText("Restart")
        self.restart_btn.clicked.connect(self.restart_shell)
        self.header_layout.addWidget(self.restart_btn)
        
        layout.addWidget(self.header)
        
        # Apply default bottom layout styling
        self._apply_bottom_header_style()
        
        # WebView for xterm.js
        self.webview = QWebEngineView()
        self.webview.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        
        # Enable clipboard access for copy/paste functionality
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanPaste, True)
        
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)
        
        # Load with settings - use theme colors if available, else use manual settings
        term_settings = self.settings_manager.settings.terminal
        
        # Prefer theme colors
        if self.theme:
            bg_color = self.theme.terminal_background
            fg_color = self.theme.terminal_foreground
        else:
            bg_color = term_settings.background_color
            fg_color = term_settings.foreground_color
        
        html = get_xterm_html(
            font_family=term_settings.font_family,
            font_size=term_settings.font_size,
            bg_color=bg_color,
            fg_color=fg_color
        )
        self.webview.setHtml(html, QUrl("qrc:/"))
        
        layout.addWidget(self.webview)
    
    def _populate_shells(self):
        shells = []
        if IS_WINDOWS:
            shells = ['cmd.exe', 'powershell.exe']
            if shutil.which('pwsh'):
                shells.append('pwsh')
        else:
            for shell in ['bash', 'zsh', 'sh', 'fish']:
                if shutil.which(shell):
                    shells.append(shell)
        
        self.shell_combo.addItems(shells)
        
        default_shell = self.settings_manager.settings.terminal.shell
        if default_shell and default_shell in shells:
            self.shell_combo.setCurrentText(default_shell)
        
        self.shell_combo.currentTextChanged.connect(self._on_shell_changed)
    
    def _start_shell(self):
        shell = self.shell_combo.currentText() or ('cmd.exe' if IS_WINDOWS else 'bash')
        self.bridge.start_shell(shell, self.current_dir)
        self._update_dir_label()
    
    def _on_shell_changed(self, shell: str):
        self.settings_manager.settings.terminal.shell = shell
        self.settings_manager.save()
        self.restart_shell()
    
    def _update_dir_label(self):
        path = self.current_dir
        home = str(Path.home())
        if path.startswith(home):
            path = "~" + path[len(home):]
        if len(path) > 40:
            path = "..." + path[-37:]
        self.dir_label.setText(path)
    
    def clear_output(self):
        """Clear the terminal"""
        self.webview.page().runJavaScript("if(window.clearTerminal) clearTerminal();")
    
    def restart_shell(self):
        """Restart the shell"""
        self.bridge.stop_shell()
        self.clear_output()
        self._start_shell()
    
    def set_working_directory(self, path: str):
        """Change directory"""
        if os.path.isdir(path):
            self.current_dir = path
            self._update_dir_label()
            cd_cmd = f'cd /d "{path}"' if IS_WINDOWS else f'cd "{path}"'
            self.bridge.write_command(cd_cmd)
            
    def write_output(self, text: str):
        """Write text directly to terminal display."""
        if text:
            # Ensure CRLF for xterm.js
            formatted = text.replace('\n', '\r\n')
            self.bridge.dataReceived.emit(formatted)

    def request_input(self, prompt: str, callback):
        """Request input from user via terminal."""
        if prompt:
            self.write_output(prompt)
        self.bridge.input_buffer = ""
        self.bridge.input_callback = callback
    
    def run_steps_file(self, filepath: str):
        """Run a Steps file"""
        if not filepath or not os.path.exists(filepath):
            return
        
        file_dir = os.path.dirname(filepath)
        self.set_working_directory(file_dir)
        
        # Determine command prefix based on execution mode
        if getattr(sys, 'frozen', False):
            # Frozen application (PyInstaller) behavior
            # We use the application executable itself with --cli flag
            # This allows the packaged app to act as the interpreter
            prefix = f'"{sys.executable}" --cli'
        else:
            # Development mode behavior
            prefix = 'python -m steps'
            
        if filepath.endswith('.step'):
            command = f'{prefix} run-step "{filepath}"'
        elif filepath.endswith('.building'):
            command = f'{prefix} run "{file_dir}"'
        else:
            return
        
        self.bridge.write_command(command)
        self.command_executed.emit(command)
    
    def run_steps_project(self, building_file: str):
        """Alias for run_steps_file"""
        self.run_steps_file(building_file)
    
    def focus_input(self):
        """Focus the terminal"""
        self.webview.setFocus()
    
    def set_theme(self, theme: Theme):
        """Update theme - applies theme colors to terminal"""
        self.theme = theme
        # Apply theme colors to xterm.js
        if theme:
            self.webview.page().runJavaScript(
                f"if(window.setBackground) setBackground('{theme.terminal_background}');"
            )
            self.webview.page().runJavaScript(
                f"if(window.setForeground) setForeground('{theme.terminal_foreground}');"
            )
    
    def apply_settings(self):
        """Apply current settings to the terminal"""
        term_settings = self.settings_manager.settings.terminal
        self.webview.page().runJavaScript(
            f"if(window.setFontSize) setFontSize({term_settings.font_size});"
        )
        self.webview.page().runJavaScript(
            f"if(window.setFontFamily) setFontFamily('{term_settings.font_family}');"
        )
        # Apply theme colors if theme is set
        if self.theme:
            self.webview.page().runJavaScript(
                f"if(window.setBackground) setBackground('{self.theme.terminal_background}');"
            )
            self.webview.page().runJavaScript(
                f"if(window.setForeground) setForeground('{self.theme.terminal_foreground}');"
            )
    
    def _apply_theme(self):
        """Apply theme to terminal - called by main window"""
        self.apply_settings()
    
    def _apply_bottom_header_style(self):
        """Apply normal header styling for bottom position"""
        self.header.setFixedHeight(36)
        self.header.setStyleSheet("background: #252526; border-bottom: 1px solid #3c3c3c;")
        self.header_layout.setContentsMargins(8, 4, 8, 4)
        self.header_layout.setSpacing(6)
        
        self.title_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #ccc;")
        self.title_label.show()
        
        self.dir_label.setStyleSheet("font-size: 10px; color: #888;")
        self.dir_label.show()
        
        self.shell_combo.setMaximumWidth(100)
        self.shell_combo.setStyleSheet("font-size: 11px;")
        
        # Visible buttons with background and proper padding
        button_style = """
            QToolButton {
                color: #ccc;
                font-size: 11px;
                background: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 2px 8px;
            }
            QToolButton:hover {
                background: #4c4c4c;
            }
        """
        self.clear_btn.setText("Clear")
        self.clear_btn.setStyleSheet(button_style)
        
        self.restart_btn.setText("Restart")
        self.restart_btn.setStyleSheet(button_style)
    
    def _apply_right_header_style(self):
        """Apply compact header styling for right-side position"""
        self.header.setFixedHeight(32)
        self.header.setStyleSheet("background: #252526; border-bottom: 1px solid #3c3c3c;")
        self.header_layout.setContentsMargins(6, 2, 6, 2)
        self.header_layout.setSpacing(6)
        
        # Show title label with compact styling
        self.title_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #ccc;")
        self.title_label.show()
        
        # Hide directory label to save space (path is too long for right panel)
        self.dir_label.hide()
        
        # Compact shell dropdown
        self.shell_combo.setMaximumWidth(80)
        self.shell_combo.setStyleSheet("font-size: 11px;")
        
        # Visible buttons with background and proper padding
        button_style = """
            QToolButton {
                color: #ccc;
                font-size: 11px;
                background: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 2px 8px;
            }
            QToolButton:hover {
                background: #4c4c4c;
            }
        """
        self.clear_btn.setText("Clear")
        self.clear_btn.setStyleSheet(button_style)
        
        self.restart_btn.setText("Restart")
        self.restart_btn.setStyleSheet(button_style)
    
    def set_position(self, position: str):
        """Adjust layout based on terminal position (bottom or right)"""
        if position == "right":
            self._apply_right_header_style()
        else:
            self._apply_bottom_header_style()
    
    def stop_shell(self):
        """Stop the shell - called on window close"""
        self.bridge.stop_shell()
    
    def closeEvent(self, event):
        self.bridge.stop_shell()
        super().closeEvent(event)


# For backwards compatibility
TerminalWidget = XtermWidget
