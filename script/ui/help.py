from PySide6.QtCore import Qt, QUrl, QSize, Signal
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextBrowser, QDialogButtonBox, QTabWidget, QLineEdit,
                             QListWidget, QListWidgetItem, QSplitter, QFrame,
                             QScrollArea, QGroupBox, QTreeWidget, QTreeWidgetItem,
                             QProgressBar, QMessageBox, QWidget)
from PySide6.QtGui import QDesktopServices, QFont, QIcon, QKeySequence
import webbrowser
import os
import re
from pathlib import Path


def show_help(parent=None):
    """Show the help dialog.
    
    Args:
        parent: Parent widget for the dialog
    """
    dialog = HelpDialog(parent)
    dialog.exec()


class HelpDialog(QDialog):
    """Enhanced help dialog with tabbed interface, search, and documentation integration."""
    
    def __init__(self, parent=None, context_topic=None):
        super().__init__(parent)
        self.setWindowTitle("Help - Project Browser")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self.context_topic = context_topic
        self.docs_path = self._get_docs_path()
        self.setup_ui()
        self.load_documentation()
        
        # Set focus to search box
        self.search_box.setFocus()
        
        # If context topic is provided, show it
        if context_topic:
            self.show_context_help(context_topic)
    
    def _get_docs_path(self):
        """Get the path to the documentation directory."""
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        docs_path = project_root / "docs"
        return docs_path if docs_path.exists() else None
    
    def setup_ui(self):
        """Set up the enhanced help dialog UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header with search
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Project Browser - Help")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Search box
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to search help topics...")
        self.search_box.setMinimumWidth(300)
        self.search_box.textChanged.connect(self.filter_content)
        header_layout.addWidget(search_label)
        header_layout.addWidget(self.search_box)
        
        main_layout.addLayout(header_layout)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Navigation
        left_panel = self.create_navigation_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Content
        right_panel = self.create_content_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        # Additional buttons
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        
        self.forward_btn = QPushButton("Forward →")
        self.forward_btn.clicked.connect(self.go_forward)
        self.forward_btn.setEnabled(False)
        
        self.home_btn = QPushButton("🏠 Home")
        self.home_btn.clicked.connect(self.go_home)
        self.home_btn.setStyleSheet("QPushButton { background-color: #4caf50; color: white; font-weight: bold; padding: 5px 15px; border-radius: 4px; } QPushButton:hover { background-color: #388e3c; } QPushButton:pressed { background-color: #1b5e20; }")
        
        button_layout.addWidget(self.back_btn)
        button_layout.addWidget(self.forward_btn)
        button_layout.addWidget(self.home_btn)
        button_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("QPushButton { background-color: #2196f3; color: white; font-weight: bold; padding: 5px 15px; border-radius: 4px; } QPushButton:hover { background-color: #1976d2; } QPushButton:pressed { background-color: #0d47a1; }")
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        # Set layout
        self.setLayout(main_layout)
        
        # Initialize history
        self.history = []
        self.history_index = -1
    
    def create_navigation_panel(self):
        """Create the left navigation panel with help topics."""
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)        
        
        # Documentation Tree
        docs_group = QGroupBox("Documentation")
        docs_layout = QVBoxLayout()
        
        self.docs_tree = QTreeWidget()
        self.docs_tree.setHeaderLabel("Topics")
        self.docs_tree.itemClicked.connect(self.on_docs_item_clicked)
        docs_layout.addWidget(self.docs_tree)
        
        docs_group.setLayout(docs_layout)
        nav_layout.addWidget(docs_group)
        
        # External Links
        links_group = QGroupBox("External Links")
        links_layout = QVBoxLayout()
        
        links = [
            ("GitHub Wiki", "https://github.com/Nsfr750/PRJ-1/wiki"),
            ("Report Issue", "https://github.com/Nsfr750/PRJ-1/issues"),
            ("Discussions", "https://github.com/Nsfr750/PRJ-1/discussions"),
            ("Release Notes", "https://github.com/Nsfr750/PRJ-1/releases")
        ]
        
        for text, url in links:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, u=url: webbrowser.open(u))
            links_layout.addWidget(btn)
        
        links_group.setLayout(links_layout)
        nav_layout.addWidget(links_group)
        
        nav_layout.addStretch()
        return nav_widget
    
    def create_content_panel(self):
        """Create the right content panel with tabbed interface."""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Main help tab
        self.help_browser = QTextBrowser()
        self.help_browser.setOpenExternalLinks(True)
        self.help_browser.anchorClicked.connect(self.on_anchor_clicked)
        self.tabs.addTab(self.help_browser, "Help")
        
        # Examples tab
        self.examples_browser = QTextBrowser()
        self.examples_browser.setOpenExternalLinks(True)
        self.tabs.addTab(self.examples_browser, "Examples")
        
        # API Reference tab
        self.api_browser = QTextBrowser()
        self.api_browser.setOpenExternalLinks(True)
        self.tabs.addTab(self.api_browser, "API Reference")
        
        # FAQ tab
        self.faq_browser = QTextBrowser()
        self.faq_browser.setOpenExternalLinks(True)
        self.tabs.addTab(self.faq_browser, "FAQ")
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        content_layout.addWidget(self.tabs)
        
        return content_widget
    
    def load_documentation(self):
        """Load documentation from the docs directory."""
        if not self.docs_path:
            self.show_error("Documentation directory not found")
            return
        
        # Load main help content
        self.load_main_help()
        
        # Populate documentation tree
        self.populate_docs_tree()
        
        # Load examples
        self.load_examples()
        
        # Load FAQ
        self.load_faq()
    
    def load_main_help(self):
        """Load the main help content."""
        help_content = self._get_main_help_content()
        self.help_browser.setHtml(help_content)
        
    def _get_main_help_content(self):
        """Generate the main help content HTML."""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #44607b; border-bottom: 2px solid #3498db; }}
                h2 {{ color: #44607b; margin-top: 30px; }}
                h3 {{ color: #44607b; }}
                code {{ background-color: #1f1f1f; padding: 2px 4px; border-radius: 3px; }}
                .note {{ background-color: #1f1f1f; padding: 10px; border-left: 4px solid #3498db; margin: 10px 0; }}
                .warning {{ background-color: #1f1f1f; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
                .tip {{ background-color: #1f1f1f; padding: 10px; border-left: 4px solid #28a745; margin: 10px 0; }}
                ul {{ margin: 10px 0; }}
                li {{ margin: 5px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #44607b; color: white; }}
            </style>
        </head>
        <body>
            <h1>PRJ-1 Project Browser - Help Center</h1>
            
            <div class="note">
                <strong>Welcome to PRJ-1 Project Browser!</strong> This comprehensive project management tool helps you discover, organize, and manage your development projects with ease.
            </div>
            
            <h2>Quick Start Guide</h2>
            <ol>
                <li><strong>Scan Projects:</strong> Use the Project Browser to scan your directories for projects</li>
                <li><strong>Browse Projects:</strong> View all your projects in an organized table with detailed information</li>
                <li><strong>Search & Filter:</strong> Find projects quickly using search and language filters</li>
                <li><strong>Open Projects:</strong> Launch projects in your preferred editor or IDE</li>
            </ol>
            
            <h2>Interface Overview</h2>
            <h3>Main Window</h3>
            <ul>
                <li><strong>Menu Bar:</strong> Access all application features and settings</li>
                <li><strong>Project Browser:</strong> Browse and manage your projects</li>
                <li><strong>Status Bar:</strong> View application status and quick information</li>
            </ul>
            
            <h3>Project Browser Dialog</h3>
            <ul>
                <li><strong>Directory Selection:</strong> Choose which directory to scan for projects</li>
                <li><strong>Project Table:</strong> View all discovered projects with detailed information</li>
                <li><strong>Search & Filter:</strong> Find projects by name or programming language</li>
                <li><strong>Version Display:</strong> See version information extracted from version.py files</li>
                <li><strong>Open Actions:</strong> Launch projects in your preferred editor</li>
            </ul>
            
            <h3>Menu Features</h3>
            <ul>
                <li><strong>File Menu:</strong> Project browser, settings, and exit</li>
                <li><strong>Help Menu:</strong> Access help, about, and sponsor information</li>
                <li><strong>Language Support:</strong> Switch between different interface languages</li>
            </ul>
            
            <h2>Keyboard Shortcuts</h2>
            <table>
                <tr><th><strong>Shortcut</strong></th><th><strong>Action</strong></th></tr>
                <tr><td><code>Ctrl+B</code></td><td>Open Project Browser</td></tr>
                <tr><td><code>Ctrl+F</code></td><td>Focus Search Box</td></tr>
                <tr><td><code>F1</code></td><td>Show Help</td></tr>
                <tr><td><code>Ctrl+Q</code></td><td>Quit Application</td></tr>
                <tr><td><code>Ctrl+W</code></td><td>Close Current Dialog</td></tr>
            </table>
            
            <div class="tip">
                <strong>Pro Tip:</strong> Use the search box above to quickly find help topics. You can also browse the documentation tree on the left for detailed guides and project documentation.
            </div>
            
            <h2>Documentation Sections</h2>
            <ul>
                <li><strong>Project Structure:</strong> Detailed explanation of the project architecture</li>
                <li><strong>Roadmap:</strong> Planned features and future development</li>
                <li><strong>Application List:</strong> List of supported applications and their status</li>
            </ul>
            
            <h2>Getting Additional Help</h2>
            <ul>
                <li><strong>GitHub Repository:</strong> Source code and documentation</li>
                <li><strong>Issue Tracker:</strong> Report bugs or request features</li>
                <li><strong>Discord Community:</strong> Get help from other users and developers</li>
                <li><strong>Documentation:</strong> Browse the comprehensive documentation in the docs/ folder</li>
            </ul>
            
            <div class="warning">
                <strong>Important:</strong> Make sure your projects contain a <code>version.py</code> file for proper version detection. The scanner will recursively search all subdirectories for version information.
            </div>
        </body>
        </html>
        """
    
    def populate_docs_tree(self):
        """Populate the documentation tree with available documentation files."""
        if not self.docs_path:
            return
        
        # Clear existing items
        self.docs_tree.clear()
        
        # Add main categories
        project_docs_item = QTreeWidgetItem(self.docs_tree, ["Project Documentation"])
        structure_item = QTreeWidgetItem(self.docs_tree, ["Structure & Architecture"])
        planning_item = QTreeWidgetItem(self.docs_tree, ["Planning & Roadmap"])
        
        # Populate project documentation
        if (self.docs_path / "STRUCT.md").exists():
            struct_item = QTreeWidgetItem(project_docs_item, ["Project Structure"])
            struct_item.setData(0, Qt.UserRole, "STRUCT.md")
        
        if (self.docs_path / "app_list.md").exists():
            app_list_item = QTreeWidgetItem(project_docs_item, ["Application List"])
            app_list_item.setData(0, Qt.UserRole, "app_list.md")
        
        # Populate structure & architecture
        if (self.docs_path / "STRUCT.md").exists():
            struct_detail_item = QTreeWidgetItem(structure_item, ["Detailed Structure"])
            struct_detail_item.setData(0, Qt.UserRole, "STRUCT.md")
        
        # Populate planning & roadmap
        if (self.docs_path / "ROADMAP.md").exists():
            roadmap_item = QTreeWidgetItem(planning_item, ["Development Roadmap"])
            roadmap_item.setData(0, Qt.UserRole, "ROADMAP.md")
        
        # Expand the tree
        self.docs_tree.expandAll()
    
    def load_examples(self):
        """Load examples documentation."""
        examples_content = self._get_examples_content()
        self.examples_browser.setHtml(examples_content)
    
    def _get_examples_content(self):
        """Generate the examples content HTML."""
        return """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #44607b; border-bottom: 2px solid #3498db; }
                h2 { color: #44607b; margin-top: 30px; }
                h3 { color: #44607b; }
                code { background-color: #1f1f1f; padding: 2px 4px; border-radius: 3px; }
                pre { background-color: #1f1f1f; padding: 15px; border-radius: 5px; overflow-x: auto; }
                .example-box { background-color: #1f1f1f; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <h1>Usage Examples and Scenarios</h1>
            
            <h2>Basic Project Scanning</h2>
            <div class="example-box">
                <h3>Overview</h3>
                <p>This example shows how to scan your development directories for projects using PRJ-1 Project Browser.</p>
                
                <h3>Steps</h3>
                <ol>
                    <li>Launch Project Browser</li>
                    <li>Click "Browse" button to select your projects directory</li>
                    <li>Wait for the scan to complete</li>
                    <li>View all discovered projects with their information</li>
                </ol>
                
                <h3>Expected Results</h3>
                <ul>
                    <li><strong>Projects Found:</strong> All Python projects with version.py files</li>
                    <li><strong>Version Info:</strong> Extracted from version.py in each project</li>
                    <li><strong>Language Detection:</strong> Automatically detected programming language</li>
                    <li><strong>Project Details:</strong> Name, path, version, and language displayed</li>
                </ul>
            </div>
            
            <h2>Advanced Project Management</h2>
            <div class="example-box">
                <h3>Overview</h3>
                <p>Learn how to use advanced features for managing large project collections.</p>
                
                <h3>Features Demonstrated</h3>
                <ul>
                    <li><strong>Search & Filter:</strong> Find projects by name or programming language</li>
                    <li><strong>Version Tracking:</strong> Monitor project versions across your workspace</li>
                    <li><strong>Quick Access:</strong> Open projects directly from the browser</li>
                    <li><strong>Recursive Scanning:</strong> Discover projects in nested directories</li>
                </ul>
                
                <h3>Best Practices</h3>
                <pre>
1. Organize projects in logical directory structures
2. Ensure each project has a version.py file
3. Use consistent naming conventions
4. Regularly scan to keep project list updated
5. Use search functionality for large collections
                </pre>
            </div>
            
            <h2>Version File Setup</h2>
            <div class="example-box">
                <h3>Overview</h3>
                <p>Example of a properly formatted version.py file for optimal PRJ-1 integration.</p>
                
                <h3>Sample version.py</h3>
                <pre>
# version.py
__version__ = "0.1.2"
VERSION = (0, 1, 2)

# Optional metadata
__author__ = "Your Name"
__description__ = "Project description"
__license__ = "MIT"
                </pre>
                
                <h3>Requirements</h3>
                <ul>
                    <li><strong>Required:</strong> <code>__version__</code> string (Semantic Versioning format)</li>
                    <li><strong>Optional:</strong> <code>VERSION</code> tuple for programmatic access</li>
                    <li><strong>Optional:</strong> Additional metadata fields</li>
                    <li><strong>Location:</strong> Anywhere in the project directory (recursive search)</li>
                </ul>
            </div>
            
            <h2>Integration Examples</h2>
            <div class="example-box">
                <h3>Overview</h3>
                <p>Learn how to integrate PRJ-1 with your development workflow.</p>
                
                <h3>IDE Integration</h3>
                <ul>
                    <li><strong>VS Code:</strong> Use PRJ-1 to quickly open projects in VS Code</li>
                    <li><strong>PyCharm:</strong> Launch projects directly in PyCharm</li>
                    <li><strong>Sublime Text:</strong> Open projects in your preferred editor</li>
                </ul>
                
                <h3>Workflow Integration</h3>
                <pre>
1. Start your day with PRJ-1 to see project overview
2. Use search to find specific projects quickly
3. Open projects directly from the browser
4. Monitor project versions and updates
5. Keep project list organized with regular scans
                </pre>
            </div>
            
            <h2>Troubleshooting Examples</h2>
            <div class="example-box">
                <h3>Common Issues and Solutions</h3>
                
                <h3>Project Not Detected</h3>
                <p>If your project isn't showing up in the scan:</p>
                <ul>
                    <li>Ensure you have a version.py file in the project</li>
                    <li>Check that the version.py contains __version__ = "x.y.z"</li>
                    <li>Verify the directory is included in the scan path</li>
                    <li>Try scanning the parent directory recursively</li>
                </ul>
                
                <h3>Version Information Issues</h3>
                <p>If version information is not displaying correctly:</p>
                <ul>
                    <li>Check version.py syntax and formatting</li>
                    <li>Ensure __version__ follows semantic versioning</li>
                    <li>Verify file encoding is UTF-8</li>
                    <li>Check file permissions and accessibility</li>
                </ul>
                
                <h3>Performance Optimization</h3>
                <p>Tips for better performance with large project collections:</p>
                <ul>
                    <li>Use specific directory paths instead of root directories</li>
                    <li>Organize projects in logical folder structures</li>
                    <li>Use search and filter functions frequently</li>
                    <li>Regular clean up of unused or moved projects</li>
                </ul>
            </div>
        </body>
        </html>
        """
    
    def load_faq(self):
        """Load FAQ content."""
        faq_content = self._get_faq_content()
        self.faq_browser.setHtml(faq_content)
    
    def _get_faq_content(self):
        """Generate the FAQ content HTML."""
        return """
        <html>
        <head>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                }
                h1 { 
                    color: #4fc3f7; 
                    border-bottom: 2px solid #2196f3; 
                }
                h2 { 
                    color: #81c784; 
                    margin-top: 30px; 
                }
                h3 { color: #ffb74d; }
                .faq-item { 
                    margin-bottom: 20px; 
                    padding: 15px; 
                    background-color: #2d2d2d; 
                    border-radius: 5px; 
                    border: 1px solid #404040;
                }
                .question { 
                    font-weight: bold; 
                    color: #4fc3f7; 
                    margin-bottom: 10px; 
                }
                .answer { 
                    color: #e0e0e0; 
                    line-height: 1.6; 
                }
                code { 
                    background-color: #424242; 
                    color: #e0e0e0; 
                    padding: 2px 4px; 
                    border-radius: 3px; 
                    border: 1px solid #555555;
                }
                strong { color: #ffb74d; }
            </style>
        </head>
        <body>
            <h1>Frequently Asked Questions</h1>
            
            <div class="faq-item">
                <div class="question">Q: What is Project Browser?</div>
                <div class="answer">A: PRJ-1 is a comprehensive project management tool that helps developers discover, organize, and manage their development projects. It scans directories for projects, extracts version information, and provides an intuitive interface for browsing and opening projects.</div>
            </div>
            
            <div class="faq-item">
                <div class="question">Q: How does detect projects?</div>
                <div class="answer">A: PRJ-1 recursively scans directories for <code>version.py</code> files. Any directory containing a version.py file with a valid <code>__version__</code> string is considered a project.</div>
            </div>
            
            <div class="faq-item">
                <div class="question">Q: What format should my version.py file have?</div>
                <div class="answer">A: Your version.py file should contain at minimum: <code>__version__ = "x.y.z"</code> following semantic versioning. Optionally, you can include <code>VERSION = (x, y, z)</code> tuple and metadata like author, description, and license.</div>
            </div>
            
            <div class="faq-item">
                <div class="question">Q: Why isn't my project showing up in the scan?</div>
                <div class="answer">A: Common reasons include: missing version.py file, incorrect version.py format, directory not included in scan path, or file permission issues. Check that your version.py contains a valid __version__ string.</div>
            </div>
            
            <div class="faq-item">
                <div class="question">Q: Can PRJ-1 handle non-Python projects?</div>
                <div class="answer">A: Currently, PRJ-1 is optimized for Python projects with version.py files. However, it can detect any project type as long as it contains a version.py file with proper version information.</div>
            </div>
            
            <div class="faq-item">
                <div class="question">Q: How do I open a project in my preferred editor?</div>
                <div class="answer">A: Simply select the project in the browser table and click the "Open Project" button. PRJ-1 will attempt to open the project directory in your system's default file explorer or associated editor.</div>
            </div>
            
            <div class="faq-item">
                <div class="question">Q: Can I search for specific projects?</div>
                <div class="answer">A: Yes! Use the search box to filter projects by name, and the language filter to show only projects in specific programming languages. The search is case-insensitive and works in real-time.</div>
            </div>
            
            <div class="faq-item">
                <div class="question">Q: Does PRJ-1 modify my project files?</div>
                <div class="answer">A: No, PRJ-1 is read-only. It only scans and reads your version.py files to extract information. It never modifies or creates any files in your projects.</div>
            </div>
            
            <div class="faq-item">
                <div class="question">Q: How can I improve scanning performance?</div>
                <div class="answer">A: Scan specific directories instead of root directories, organize projects in logical folder structures, and avoid scanning directories with many non-project files. Use the search and filter functions for navigation.</div>
            </div>
            
            <div class="faq-item">
                <div class="question">Q: Is PRJ-1 available on multiple platforms?</div>
                <div class="answer">A: Yes, PRJ-1 is built with Python and PySide6, making it cross-platform compatible with Windows, macOS, and Linux systems.</div>
            </div>
        </body>
        </html>
        """
    
    # Event Handlers
    def on_quick_help_selected(self, item):
        """Handle quick help item selection."""
        topic = item.text()
        self.show_topic_help(topic)
        self.add_to_history(topic)
    
    def on_docs_tree_selected(self, item, column):
        """Handle documentation tree item selection."""
        topic = item.text(column)
        
        # Check if item has associated file data
        file_data = item.data(0, Qt.UserRole)
        if file_data:
            self.load_documentation_file(file_data)
        else:
            self.load_documentation_topic(topic)
        self.add_to_history(topic)
    
    def on_anchor_clicked(self, url):
        """Handle anchor clicks in the help browser."""
        if url.scheme() == "help":
            # Internal help link
            topic = url.path().strip("/")
            self.show_topic_help(topic)
            self.add_to_history(topic)
        else:
            # External link
            QDesktopServices.openUrl(url)
    
    def on_tab_changed(self, index):
        """Handle tab changes."""
        tab_names = ["Help", "Examples", "API Reference", "FAQ"]
        if 0 <= index < len(tab_names):
            self.add_to_history(f"Tab: {tab_names[index]}")
    
    # Navigation Methods
    def show_topic_help(self, topic):
        """Show help for a specific topic."""
        content = self._get_topic_content(topic)
        if content:
            self.help_browser.setHtml(content)
            self.tabs.setCurrentIndex(0)  # Switch to Help tab
    
    def _get_topic_content(self, topic):
        """Get content for a specific topic."""
        topics = {
            "Getting Started": self._get_getting_started_content(),
            "Project Scanning": self._get_project_scanning_content(),
            "Browsing Projects": self._get_browsing_projects_content(),
            "Exporting Results": self._get_exporting_results_content(),
            "Project Details": self._get_project_details_content(),
            "Troubleshooting": self._get_troubleshooting_content(),
        }
        return topics.get(topic, "<h2>Topic not found</h2><p>The requested help topic could not be found.</p>")
    
    def go_back(self):
        """Navigate back in history."""
        if self.history_index > 0:
            self.history_index -= 1
            self.navigate_to_history_item()
            self.update_navigation_buttons()
    
    def navigate_to_history_item(self):
        """Navigate to the current history item."""
        if 0 <= self.history_index < len(self.history):
            item = self.history[self.history_index]
            
            # Handle different types of history items
            if item == "Home":
                self.go_home()
            elif item.startswith("Tab:"):
                tab_name = item.replace("Tab: ", "")
                tab_names = ["Help", "Examples", "API Reference", "FAQ"]
                if tab_name in tab_names:
                    self.tabs.setCurrentIndex(tab_names.index(tab_name))
            else:
                # Assume it's a topic
                self.show_topic_help(item)
    
    def go_forward(self):
        """Navigate forward in history."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.navigate_to_history_item()
            self.update_navigation_buttons()
    
    def go_home(self):
        """Go to home page."""
        self.load_main_help()
        self.tabs.setCurrentIndex(0)
        self.add_to_history("Home")
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons."""
        self.back_btn.setEnabled(self.history_index > 0)
        self.forward_btn.setEnabled(self.history_index < len(self.history) - 1)
    
    def add_to_history(self, item):
        """Add an item to the navigation history."""
        # Remove any items after current index
        self.history = self.history[:self.history_index + 1]
        
        # Add new item
        self.history.append(item)
        self.history_index += 1
        
        # Update button states
        self.update_navigation_buttons()
    
    def filter_content(self, search_text):
        """Filter content based on search text."""
        if not search_text.strip():
            # Clear search highlighting
            self.clear_search_highlight()
            return
        
        search_term = search_text.lower()
        
        # Search in quick help items
        for i in range(self.quick_list.count()):
            item = self.quick_list.item(i)
            item.setHidden(search_term not in item.text().lower())
        
        # Search in documentation tree
        self._search_tree_widget(self.docs_tree.invisibleRootItem(), search_term)
    
    def _search_tree_widget(self, item, search_term):
        """Recursively search tree widget items."""
        for i in range(item.childCount()):
            child = item.child(i)
            child.setHidden(search_term not in child.text(0).lower())
            
            # Search children recursively
            if child.childCount() > 0:
                self._search_tree_widget(child, search_term)
    
    def clear_search_highlight(self):
        """Clear search highlighting."""
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if isinstance(browser, QTextBrowser):
                browser.find("")  # Clear search
    
    def show_error(self, message):
        """Show an error message."""
        QMessageBox.critical(self, "Error", message)
    
    def on_docs_item_clicked(self, item, column):
        """Handle documentation tree item clicks."""
        filename = item.data(0, Qt.UserRole)
        if filename:
            self.load_documentation_file(filename)
    
    def load_documentation_file(self, filename):
        """Load a specific documentation file from the docs directory."""
        if not self.docs_path:
            self.show_error("Documentation directory not found")
            return
        
        file_path = self.docs_path / filename
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Convert markdown to HTML
                html_content = self._markdown_to_html(content)
                self.help_browser.setHtml(html_content)
                self.tabs.setCurrentIndex(0)  # Switch to Help tab
            except Exception as e:
                self.show_error(f"Failed to load documentation file {filename}: {e}")
        else:
            self.show_error(f"Documentation file {filename} not found")
    
    def load_documentation_topic(self, topic):
        """Load documentation for a specific topic."""
        # Try to find the topic in the docs directory
        topic_path = os.path.join(self.docs_path, f"{topic.lower().replace(' ', '_')}.md")
        
        if os.path.exists(topic_path):
            try:
                with open(topic_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Convert markdown to HTML
                html_content = self._markdown_to_html(content)
                self.help_browser.setHtml(html_content)
                self.tabs.setCurrentIndex(0)  # Switch to Help tab
            except Exception as e:
                self.show_error(f"Failed to load documentation: {e}")
        else:
            # Show a message that the topic wasn't found
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                </style>
            </head>
            <body>
                <h1>{topic}</h1>
                <p>Documentation for this topic is not available in the docs directory.</p>
                <p>Please check the <strong>Examples</strong> or <strong>FAQ</strong> tabs for related information.</p>
            </body>
            </html>
            """
            self.help_browser.setHtml(html_content)
            self.tabs.setCurrentIndex(0)  # Switch to Help tab
    
    def _markdown_to_html(self, markdown_content):
        """Convert markdown to HTML with improved handling including tables."""
        lines = markdown_content.split('\n')
        html = []
        in_code_block = False
        in_list = False
        in_table = False
        is_table_header = False
        list_stack = []
        
        for line in lines:
            stripped = line.strip()
            
            # Handle code blocks
            if stripped.startswith('```'):
                if in_code_block:
                    html.append('</code></pre>')
                    in_code_block = False
                else:
                    html.append('<pre><code>')
                    in_code_block = True
                continue
            
            if in_code_block:
                html.append(self._escape_html(line))
                continue
            
            # Handle tables
            if '|' in stripped and stripped.count('|') >= 2:
                # Check if it's a table separator line (like |---|---|)
                if re.match(r'^\|\s*-+\s*\|.*\|$', stripped):
                    is_table_header = False  # Next row will be data, not header
                    continue  # Skip separator lines
                
                # Process table row
                if not in_table:
                    html.append('<table style="border-collapse: collapse; width: 100%; margin: 10px 0;">')
                    in_table = True
                    is_table_header = True  # First row is header
                
                # Split by | and process cells - handle table borders correctly
                # Remove leading and trailing | first
                table_content = stripped.strip('|')
                cells = [cell.strip() for cell in table_content.split('|')]
                
                html.append('<tr>')
                for cell in cells:
                    processed_cell = self._process_inline_markdown(cell)
                    if is_table_header:
                        html.append(f'<th style="border: 1px solid #404040; padding: 8px; text-align: left; background-color: #2d2d2d; font-weight: bold;">{processed_cell}</th>')
                    else:
                        html.append(f'<td style="border: 1px solid #404040; padding: 8px; text-align: left;">{processed_cell}</td>')
                html.append('</tr>')
                continue  # Skip further processing for table lines
            else:
                # Close table if we're no longer in table content
                if in_table:
                    html.append('</table>')
                    in_table = False
                    is_table_header = False
            
            # Handle headers
            if stripped.startswith('# '):
                if in_list:
                    self._close_list(html, list_stack)
                    in_list = False
                html.append(f'<h1>{stripped[2:]}</h1>')
            elif stripped.startswith('## '):
                if in_list:
                    self._close_list(html, list_stack)
                    in_list = False
                html.append(f'<h2>{stripped[3:]}</h2>')
            elif stripped.startswith('### '):
                if in_list:
                    self._close_list(html, list_stack)
                    in_list = False
                html.append(f'<h3>{stripped[4:]}</h3>')
            elif stripped.startswith('#### '):
                if in_list:
                    self._close_list(html, list_stack)
                    in_list = False
                html.append(f'<h4>{stripped[5:]}</h4>')
            
            # Handle lists
            elif stripped.startswith('- ') or stripped.startswith('* '):
                if not in_list:
                    html.append('<ul>')
                    in_list = True
                    list_stack.append('ul')
                html.append(f'<li>{stripped[2:]}</li>')
            
            # Handle numbered lists
            elif re.match(r'^\d+\. ', stripped):
                if not in_list:
                    html.append('<ol>')
                    in_list = True
                    list_stack.append('ol')
                content = re.sub(r'^\d+\. ', '', stripped)
                html.append(f'<li>{content}</li>')
            
            # Handle empty lines
            elif not stripped:
                if in_list:
                    self._close_list(html, list_stack)
                    in_list = False
                # Skip empty lines or add paragraph break
                continue
            
            # Handle regular text (paragraphs)
            else:
                if in_list:
                    self._close_list(html, list_stack)
                    in_list = False
                # Process inline markdown
                processed_line = self._process_inline_markdown(stripped)
                html.append(f'<p>{processed_line}</p>')
        
        # Close any open lists
        if in_list:
            self._close_list(html, list_stack)
        
        # Close any open table
        if in_table:
            html.append('</table>')
        
        return '\n'.join(html)
    
    def _close_list(self, html, list_stack):
        """Close all open lists."""
        while list_stack:
            list_type = list_stack.pop()
            if list_type == 'ul':
                html.append('</ul>')
            elif list_type == 'ol':
                html.append('</ol>')
    
    def _process_inline_markdown(self, text):
        """Process inline markdown elements."""
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        
        # Inline code
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        
        # Links
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        
        return text
    
    def _escape_html(self, text):
        """Escape HTML special characters."""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#39;')
        return text
    
    def _close_list(self, html, list_stack):
        """Close all open lists."""
        while list_stack:
            list_type = list_stack.pop()
            if list_type == 'ul':
                html.append('</ul>')
            elif list_type == 'ol':
                html.append('</ol>')
    
    def _process_inline_markdown(self, text):
        """Process inline markdown elements."""
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        
        # Inline code
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        
        # Links
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        
        return text

    def _get_html_template(self):
        """Get the HTML template for markdown content."""
        return """
    <html>
    <head>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            h1 { 
                color: #4fc3f7; 
                border-bottom: 2px solid #2196f3; 
                padding-bottom: 10px;
            }
            h2 { 
                color: #81c784; 
                margin-top: 30px; 
                border-bottom: 1px solid #424242;
                padding-bottom: 5px;
            }
            h3 { color: #ffb74d; }
            .section {
                background-color: #2d2d2d;
                margin: 20px 0;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                border: 1px solid #404040;
            }
            .feature {
                background-color: #37474f;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #4fc3f7;
                border-radius: 4px;
            }
            .tip {
                background-color: #1b5e20;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #4caf50;
                border-radius: 4px;
            }
            .warning {
                background-color: #f57c00;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #ff9800;
                border-radius: 4px;
            }
            ul {
                margin: 10px 0;
                padding-left: 20px;
            }
            li {
                margin: 8px 0;
                line-height: 1.5;
            }
            code {
                background-color: #424242;
                color: #e0e0e0;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                border: 1px solid #555555;
            }
            pre {
                background-color: #1e1e1e;
                color: #e0e0e0;
                padding: 15px;
                border-radius: 6px;
                border-left: 4px solid #757575;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                border: 1px solid #404040;
            }
            .keyboard-shortcut {
                background-color: #616161;
                color: #ffffff;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.9em;
                font-weight: bold;
            }
            .version-info {
                background-color: #424242;
                padding: 10px;
                border-radius: 4px;
                font-size: 0.9em;
                text-align: center;
                margin-top: 20px;
                border: 1px solid #555555;
            }
        </style>
    </head>
    <body>
        {content}
    </body>
    </html>
    """

    def _get_getting_started_content(self):
        """Get getting started content for Project Browser."""
        return """
    <html>
    <head>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            h1 { 
                color: #4fc3f7; 
                border-bottom: 2px solid #2196f3; 
            }
            h2 { 
                color: #81c784; 
                margin-top: 30px; 
            }
            .step { 
                background-color: #2d2d2d; 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 5px; 
                border: 1px solid #404040;
            }
            h3 { color: #ffb74d; }
            strong { color: #4fc3f7; }
            ol { margin-left: 20px; }
            li { margin: 8px 0; }
        </style>
    </head>
    <body>
        <h1>Getting Started with Project Browser</h1>
        
        <p>Welcome to Project Browser! This tool helps you discover, browse, and manage your programming projects efficiently.</p>
        
        <div class="step">
            <h2>Step 1: Open Project Browser</h2>
            <ol>
                <li>Go to the <strong>Tools</strong> menu in the main application</li>
                <li>Select <strong>Project Browser</strong> from the dropdown menu</li>
                <li>The Project Browser dialog will open</li>
            </ol>
        </div>
        
        <div class="step">
            <h2>Step 2: Scan for Projects</h2>
            <ol>
                <li>Click the <strong style="color: #4CAF50;">Start Scan</strong> button (green)</li>
                <li>The application will scan your GitHub folder for projects</li>
                <li>Watch the progress bar as projects are discovered</li>
                <li>Results will appear in the table below</li>
            </ol>
        </div>
        
        <div class="step">
            <h2>Step 3: Browse and Filter Projects</h2>
            <ol>
                <li>Use the <strong>Search</strong> box to find specific projects</li>
                <li>Filter by <strong>Language</strong> using the dropdown menu</li>
                <li>Click on any project in the table to view details</li>
                <li>Use the <strong>Open Folder</strong> button to access project files</li>
            </ol>
        </div>
        
        <div class="step">
            <h2>Step 4: Export Results (Optional)</h2>
            <ol>
                <li>After scanning, click the <strong style="color: #2196F3;">Export</strong> button (blue)</li>
                <li>Results will be saved in Markdown format to the <strong>data/</strong> folder</li>
                <li>The export includes project details, statistics, and summaries</li>
            </ol>
        </div>
        
        <h2>Tips for Best Results</h2>
        <ul>
            <li><strong>Organization:</strong> Keep your projects in well-structured folders</li>
            <li><strong>Git Repositories:</strong> Projects with Git will show more detailed information</li>
            <li><strong>README Files:</strong> Include README.md files for better project descriptions</li>
            <li><strong>Regular Scans:</strong> Scan periodically to discover new projects</li>
        </ul>
        
    </body>
    </html>
    """
