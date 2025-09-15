"""Project Statistics Dashboard Dialog.

This module provides a comprehensive dashboard for viewing project statistics
including charts and graphs for various project metrics.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QTabWidget, QScrollArea, QGroupBox,
    QFrame, QSplitter, QFileDialog, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter

import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt5 backend for matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.pyplot import cm
import matplotlib.pyplot as plt

from ..project_scanner import ProjectScanner
from ..tag_manager import TagManager
from ..lang.lang_mgr import get_text


class DashboardDialog(QDialog):
    """Dialog for displaying project statistics dashboard."""
    
    def __init__(self, scanner: ProjectScanner, parent=None, lang='en'):
        super().__init__(parent)
        self.scanner = scanner
        self.lang = lang
        self.setWindowTitle(get_text('dashboard.title', 'Project Statistics Dashboard', self.lang))
        self.setMinimumSize(1400, 900)
        self.setup_ui()
        self.load_statistics()
    
    def setup_ui(self):
        """Set up the dashboard user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel(get_text('dashboard.header_title', 'Project Statistics Dashboard', self.lang))
        title_label.setFont(QFont("", 16, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        self.refresh_button = QPushButton(get_text('dashboard.refresh', 'Refresh', self.lang))
        self.refresh_button.clicked.connect(self.load_statistics)
        header_layout.addWidget(self.refresh_button)
        
        self.export_button = QPushButton(get_text('dashboard.export_report', 'Export Report', self.lang))
        self.export_button.clicked.connect(self.export_report)
        header_layout.addWidget(self.export_button)
        
        layout.addLayout(header_layout)
        
        # Main content with tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_overview_tab()
        self.create_language_tab()
        self.create_category_tab()
        self.create_tags_tab()
        self.create_activity_tab()
        self.create_size_tab()
        
        # Status bar
        self.status_label = QLabel(get_text('dashboard.ready', 'Ready', self.lang))
        layout.addWidget(self.status_label)
    
    def create_overview_tab(self):
        """Create the overview tab with general statistics."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary cards
        cards_layout = QGridLayout()
        
        # Total projects card
        total_card = self.create_stat_card(get_text('dashboard.total_projects', 'Total Projects', self.lang), "0", get_text('dashboard.projects', 'projects', self.lang))
        cards_layout.addWidget(total_card, 0, 0)
        
        # Languages card
        languages_card = self.create_stat_card(get_text('dashboard.languages', 'Languages', self.lang), "0", get_text('dashboard.languages_count', 'languages', self.lang))
        cards_layout.addWidget(languages_card, 0, 1)
        
        # Categories card
        categories_card = self.create_stat_card(get_text('dashboard.categories', 'Categories', self.lang), "0", get_text('dashboard.categories_count', 'categories', self.lang))
        cards_layout.addWidget(categories_card, 0, 2)
        
        # Favorites card
        favorites_card = self.create_stat_card(get_text('dashboard.favorites', 'Favorites', self.lang), "0", get_text('dashboard.projects', 'projects', self.lang))
        cards_layout.addWidget(favorites_card, 1, 0)
        
        # Recent projects card
        recent_card = self.create_stat_card(get_text('dashboard.recent_projects', 'Recent Projects', self.lang), "0", get_text('dashboard.projects', 'projects', self.lang))
        cards_layout.addWidget(recent_card, 1, 1)
        
        # Total size card
        size_card = self.create_stat_card(get_text('dashboard.total_size', 'Total Size', self.lang), "0 MB", get_text('dashboard.disk_usage', 'disk usage', self.lang))
        cards_layout.addWidget(size_card, 1, 2)
        
        layout.addLayout(cards_layout)
        
        # Charts section
        charts_splitter = QSplitter(Qt.Horizontal)
        
        # Language distribution chart
        self.language_chart = self.create_pie_chart(get_text('dashboard.language_distribution', 'Language Distribution', self.lang))
        charts_splitter.addWidget(self.language_chart)
        
        # Category distribution chart
        self.category_chart = self.create_pie_chart(get_text('dashboard.category_distribution', 'Category Distribution', self.lang))
        charts_splitter.addWidget(self.category_chart)
        
        charts_splitter.setSizes([700, 700])
        layout.addWidget(charts_splitter)
        
        # Store references to stat cards for updating
        self.stat_cards = {
            'total': total_card,
            'languages': languages_card,
            'categories': categories_card,
            'favorites': favorites_card,
            'recent': recent_card,
            'size': size_card
        }
        
        self.tab_widget.addTab(tab, get_text('dashboard.overview_tab', 'Overview', self.lang))
    
    def create_language_tab(self):
        """Create the language statistics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Language statistics table and chart
        splitter = QSplitter(Qt.Vertical)
        
        # Language chart
        self.language_bar_chart = self.create_bar_chart(get_text('dashboard.projects_by_language', 'Projects by Language', self.lang))
        splitter.addWidget(self.language_bar_chart)
        
        # Language details (will be populated later)
        self.language_details = self.create_details_table(get_text('dashboard.language_details', 'Language Details', self.lang))
        splitter.addWidget(self.language_details)
        
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(tab, get_text('dashboard.languages_tab', 'Languages', self.lang))
    
    def create_category_tab(self):
        """Create the category statistics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Category statistics table and chart
        splitter = QSplitter(Qt.Vertical)
        
        # Category chart
        self.category_bar_chart = self.create_bar_chart(get_text('dashboard.projects_by_category', 'Projects by Category', self.lang))
        splitter.addWidget(self.category_bar_chart)
        
        # Category details (will be populated later)
        self.category_details = self.create_details_table(get_text('dashboard.category_details', 'Category Details', self.lang))
        splitter.addWidget(self.category_details)
        
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(tab, get_text('dashboard.categories_tab', 'Categories', self.lang))
    
    def create_tags_tab(self):
        """Create the tags statistics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tag cloud and statistics
        splitter = QSplitter(Qt.Vertical)
        
        # Tag usage chart
        self.tags_chart = self.create_bar_chart(get_text('dashboard.most_used_tags', 'Most Used Tags', self.lang))
        splitter.addWidget(self.tags_chart)
        
        # Tag details (will be populated later)
        self.tags_details = self.create_details_table(get_text('dashboard.tag_details', 'Tag Details', self.lang))
        splitter.addWidget(self.tags_details)
        
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(tab, get_text('dashboard.tags_tab', 'Tags', self.lang))
    
    def create_activity_tab(self):
        """Create the activity statistics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Activity charts
        splitter = QSplitter(Qt.Horizontal)
        
        # Recent activity chart
        self.activity_chart = self.create_line_chart(get_text('dashboard.project_activity', 'Project Activity (Last 30 Days)', self.lang))
        splitter.addWidget(self.activity_chart)
        
        # Top recent projects
        self.recent_projects_chart = self.create_bar_chart(get_text('dashboard.most_accessed_projects', 'Most Accessed Projects', self.lang))
        splitter.addWidget(self.recent_projects_chart)
        
        splitter.setSizes([700, 700])
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(tab, get_text('dashboard.activity_tab', 'Activity', self.lang))
    
    def create_size_tab(self):
        """Create the size statistics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Size distribution charts
        splitter = QSplitter(Qt.Vertical)
        
        # Size distribution chart
        self.size_dist_chart = self.create_bar_chart(get_text('dashboard.project_size_distribution', 'Project Size Distribution', self.lang))
        splitter.addWidget(self.size_dist_chart)
        
        # Largest projects table
        self.largest_projects = self.create_details_table(get_text('dashboard.largest_projects', 'Largest Projects', self.lang))
        splitter.addWidget(self.largest_projects)
        
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(tab, get_text('dashboard.size_tab', 'Size', self.lang))
    
    def create_stat_card(self, title: str, value: str, subtitle: str) -> QFrame:
        """Create a statistics card widget."""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont("", 24, QFont.Bold))
        value_label.setStyleSheet("color: #212529;")
        layout.addWidget(value_label)
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        layout.addWidget(subtitle_label)
        
        return card
    
    def create_pie_chart(self, title: str) -> FigureCanvas:
        """Create a pie chart canvas."""
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title(title)
        canvas = FigureCanvas(fig)
        return canvas
    
    def create_bar_chart(self, title: str) -> FigureCanvas:
        """Create a bar chart canvas."""
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title(title)
        canvas = FigureCanvas(fig)
        return canvas
    
    def create_line_chart(self, title: str) -> FigureCanvas:
        """Create a line chart canvas."""
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title(title)
        canvas = FigureCanvas(fig)
        return canvas
    
    def create_details_table(self, title: str) -> QFrame:
        """Create a details table frame (placeholder for now)."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Placeholder label - will be replaced with actual table
        placeholder = QLabel(get_text('dashboard.loading_data', 'Loading data...', self.lang))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
        
        return frame
    
    def load_statistics(self):
        """Load and display all statistics."""
        try:
            self.status_label.setText(get_text('dashboard.loading_statistics', 'Loading statistics...', self.lang))
            
            # Get projects data
            projects = self.scanner.get_projects()
            
            # Calculate statistics
            stats = self.calculate_statistics(projects)
            
            # Update overview
            self.update_overview(stats)
            
            # Update language statistics
            self.update_language_stats(stats)
            
            # Update category statistics
            self.update_category_stats(stats)
            
            # Update tag statistics
            self.update_tag_stats(stats)
            
            # Update activity statistics
            self.update_activity_stats(stats)
            
            # Update size statistics
            self.update_size_stats(stats)
            
            self.status_label.setText(get_text('dashboard.statistics_loaded', 'Statistics loaded - {count} projects analyzed', self.lang).format(count=len(projects)))
            
        except Exception as e:
            QMessageBox.warning(self, get_text('dashboard.error', 'Error', self.lang), get_text('dashboard.load_error', 'Could not load statistics: {error}', self.lang).format(error=str(e)))
            self.status_label.setText(get_text('dashboard.error_loading_statistics', 'Error loading statistics', self.lang))
    
    def calculate_statistics(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive statistics from projects data."""
        stats = {
            'total_projects': len(projects),
            'languages': {},
            'categories': {},
            'tags': {},
            'favorites': 0,
            'with_notes': 0,
            'total_size': 0,
            'size_distribution': {'< 1MB': 0, '1-10MB': 0, '10-100MB': 0, '> 100MB': 0},
            'recent_projects': [],
            'activity_timeline': {},
            'largest_projects': []
        }
        
        # Process each project
        for project in projects:
            # Language statistics
            language = project.get('language', 'Unknown')
            stats['languages'][language] = stats['languages'].get(language, 0) + 1
            
            # Category statistics
            category = project.get('category', 'Uncategorized')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Tag statistics
            tags = project.get('tags', [])
            for tag in tags:
                stats['tags'][tag] = stats['tags'].get(tag, 0) + 1
            
            # Favorites and notes
            if project.get('is_favorite', False):
                stats['favorites'] += 1
            
            if project.get('note'):
                stats['with_notes'] += 1
            
            # Size statistics
            size = project.get('size', 0)
            stats['total_size'] += size
            
            # Size distribution
            if size < 1024 * 1024:  # < 1MB
                stats['size_distribution']['< 1MB'] += 1
            elif size < 10 * 1024 * 1024:  # 1-10MB
                stats['size_distribution']['1-10MB'] += 1
            elif size < 100 * 1024 * 1024:  # 10-100MB
                stats['size_distribution']['10-100MB'] += 1
            else:  # > 100MB
                stats['size_distribution']['> 100MB'] += 1
            
            # Add to largest projects
            stats['largest_projects'].append({
                'name': project['name'],
                'path': project['path'],
                'size': size
            })
        
        # Sort largest projects
        stats['largest_projects'] = sorted(
            stats['largest_projects'], 
            key=lambda x: x['size'], 
            reverse=True
        )[:10]  # Top 10
        
        # Get recent projects from tag manager
        recent_projects = self.scanner.tag_manager.get_recent_projects()
        stats['recent_projects'] = recent_projects[:10]  # Top 10 recent
        
        # Generate activity timeline (last 30 days)
        stats['activity_timeline'] = self.generate_activity_timeline(recent_projects)
        
        return stats
    
    def generate_activity_timeline(self, recent_projects: List[Dict[str, Any]]) -> Dict[str, int]:
        """Generate activity timeline for the last 30 days."""
        timeline = {}
        now = datetime.now()
        
        # Initialize last 30 days
        for i in range(30):
            date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
            timeline[date] = 0
        
        # Count projects accessed on each day
        for project in recent_projects:
            accessed_at = datetime.fromisoformat(project['accessed_at'])
            date_str = accessed_at.strftime('%Y-%m-%d')
            if date_str in timeline:
                timeline[date_str] += 1
        
        return timeline
    
    def update_overview(self, stats: Dict[str, Any]):
        """Update the overview tab with statistics."""
        # Update stat cards by finding the value label in each card
        for card_key, card in self.stat_cards.items():
            # Find the value label (second child in the layout)
            layout = card.layout()
            if layout and layout.count() >= 2:
                value_label = layout.itemAt(1).widget()
                if value_label:
                    if card_key == 'total':
                        value_label.setText(str(stats['total_projects']))
                    elif card_key == 'languages':
                        value_label.setText(str(len(stats['languages'])))
                    elif card_key == 'categories':
                        value_label.setText(str(len(stats['categories'])))
                    elif card_key == 'favorites':
                        value_label.setText(str(stats['favorites']))
                    elif card_key == 'recent':
                        value_label.setText(str(len(stats['recent_projects'])))
                    elif card_key == 'size':
                        total_size_mb = stats['total_size'] / (1024 * 1024)
                        if total_size_mb > 1024:
                            size_str = f"{total_size_mb / 1024:.1f} GB"
                        else:
                            size_str = f"{total_size_mb:.1f} MB"
                        value_label.setText(size_str)
        
        # Update language distribution pie chart
        self.update_pie_chart(self.language_chart, stats['languages'])
        
        # Update category distribution pie chart
        self.update_pie_chart(self.category_chart, stats['categories'])
    
    def update_pie_chart(self, canvas: FigureCanvas, data: Dict[str, int]):
        """Update a pie chart with data."""
        ax = canvas.figure.axes[0]
        ax.clear()
        
        if not data:
            ax.text(0.5, 0.5, get_text('dashboard.no_data_available', 'No data available', self.lang), ha='center', va='center', transform=ax.transAxes)
        else:
            # Sort data by value
            sorted_data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
            
            # Take top 10 items, group rest as "Other"
            if len(sorted_data) > 10:
                top_items = dict(list(sorted_data.items())[:9])
                other_count = sum(list(sorted_data.values())[9:])
                top_items[get_text('dashboard.other', 'Other', self.lang)] = other_count
                sorted_data = top_items
            
            labels = list(sorted_data.keys())
            values = list(sorted_data.values())
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
        
        canvas.draw()
    
    def update_language_stats(self, stats: Dict[str, Any]):
        """Update language statistics tab."""
        # Update bar chart
        self.update_bar_chart(self.language_bar_chart, stats['languages'])
        
        # Update details table (placeholder for now)
        # TODO: Implement detailed language statistics table
    
    def update_category_stats(self, stats: Dict[str, Any]):
        """Update category statistics tab."""
        # Update bar chart
        self.update_bar_chart(self.category_bar_chart, stats['categories'])
        
        # Update details table (placeholder for now)
        # TODO: Implement detailed category statistics table
    
    def update_tag_stats(self, stats: Dict[str, Any]):
        """Update tag statistics tab."""
        # Get top 20 tags
        top_tags = dict(sorted(stats['tags'].items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Update bar chart
        self.update_bar_chart(self.tags_chart, top_tags)
        
        # Update details table (placeholder for now)
        # TODO: Implement detailed tag statistics table
    
    def update_activity_stats(self, stats: Dict[str, Any]):
        """Update activity statistics tab."""
        # Update activity timeline chart
        self.update_line_chart(self.activity_chart, stats['activity_timeline'])
        
        # Update recent projects chart
        recent_data = {p['name']: 1 for p in stats['recent_projects'][:10]}
        self.update_bar_chart(self.recent_projects_chart, recent_data)
    
    def update_size_stats(self, stats: Dict[str, Any]):
        """Update size statistics tab."""
        # Update size distribution chart
        self.update_bar_chart(self.size_dist_chart, stats['size_distribution'])
        
        # Update largest projects table (placeholder for now)
        # TODO: Implement largest projects table
    
    def update_bar_chart(self, canvas: FigureCanvas, data: Dict[str, int]):
        """Update a bar chart with data."""
        ax = canvas.figure.axes[0]
        ax.clear()
        
        if not data:
            ax.text(0.5, 0.5, get_text('dashboard.no_data_available', 'No data available', self.lang), ha='center', va='center', transform=ax.transAxes)
        else:
            labels = list(data.keys())
            values = list(data.values())
            
            # Create bar chart
            bars = ax.bar(labels, values)
            ax.set_ylabel(get_text('dashboard.count', 'Count', self.lang))
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
        
        canvas.figure.tight_layout()
        canvas.draw()
    
    def update_line_chart(self, canvas: FigureCanvas, data: Dict[str, int]):
        """Update a line chart with data."""
        ax = canvas.figure.axes[0]
        ax.clear()
        
        if not data or all(v == 0 for v in data.values()):
            ax.text(0.5, 0.5, get_text('dashboard.no_activity_data_available', 'No activity data available', self.lang), ha='center', va='center', transform=ax.transAxes)
        else:
            # Sort by date
            sorted_data = dict(sorted(data.items()))
            
            dates = list(sorted_data.keys())
            values = list(sorted_data.values())
            
            # Create line chart
            ax.plot(dates, values, marker='o', linewidth=2, markersize=4)
            ax.set_ylabel(get_text('dashboard.projects_accessed', 'Projects Accessed', self.lang))
            ax.set_xlabel(get_text('dashboard.date', 'Date', self.lang))
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        canvas.figure.tight_layout()
        canvas.draw()
    
    def export_report(self):
        """Export statistics report to file."""
        try:
            # Ask user for export format
            reply = QMessageBox.question(
                self,
                get_text('dashboard.export_report', 'Export Report', self.lang),
                get_text('dashboard.choose_export_format', 'Choose export format:', self.lang),
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            
            # Ask for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                get_text('dashboard.export_report', 'Export Report', self.lang),
                "",
                f"{get_text('dashboard.csv_files', 'CSV Files', self.lang)} (*.csv);;{get_text('dashboard.json_files', 'JSON Files', self.lang)} (*.json);;{get_text('dashboard.all_files', 'All Files', self.lang)} (*.*)"
            )
            
            if not file_path:
                return
            
            try:
                # Export based on file extension
                if file_path.endswith('.csv'):
                    self.export_csv_report(file_path)
                elif file_path.endswith('.json'):
                    self.export_json_report(file_path)
                else:
                    # Default to CSV
                    self.export_csv_report(file_path)
                
                QMessageBox.information(self, get_text('dashboard.export_complete', 'Export Complete', self.lang), get_text('dashboard.export_success', 'Report exported successfully!', self.lang))
                
            except Exception as e:
                QMessageBox.critical(self, get_text('dashboard.export_error', 'Export Error', self.lang), get_text('dashboard.export_error_message', 'Could not export report: {error}', self.lang).format(error=str(e)))
        
        except Exception as e:
            QMessageBox.warning(self, get_text('dashboard.error', 'Error', self.lang), get_text('dashboard.export_error_message', 'Could not export report: {error}', self.lang).format(error=str(e)))
    
    def export_html_report(self, file_path: str):
        """Export statistics report as HTML."""
        # Get current statistics
        projects = self.scanner.get_projects()
        stats = self.calculate_statistics(projects)
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{get_text('dashboard.title', 'Project Statistics Dashboard', self.lang)}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{get_text('dashboard.title', 'Project Statistics Dashboard', self.lang)}</h1>
            <p>{get_text('dashboard.generated_on', 'Generated on', self.lang)}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>{get_text('dashboard.total_projects', 'Total Projects', self.lang)}: {stats['total_projects']}</p>
            
            <h2>{get_text('dashboard.languages', 'Languages', self.lang)}</h2>
            <table>
                <tr><th>{get_text('dashboard.language', 'Language', self.lang)}</th><th>{get_text('dashboard.count', 'Count', self.lang)}</th></tr>
        """
        
        for lang, count in sorted(stats['languages'].items(), key=lambda x: x[1], reverse=True):
            html_content += f"<tr><td>{lang}</td><td>{count}</td></tr>"
        
        html_content += """
            </table>
            
            <h2>{get_text('dashboard.categories', 'Categories', self.lang)}</h2>
            <table>
                <tr><th>{get_text('dashboard.category', 'Category', self.lang)}</th><th>{get_text('dashboard.count', 'Count', self.lang)}</th></tr>
        """
        
        for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            html_content += f"<tr><td>{cat}</td><td>{count}</td></tr>"
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def export_json_report(self, file_path: str):
        """Export statistics report as JSON."""
        # Get current statistics
        projects = self.scanner.get_projects()
        stats = self.calculate_statistics(projects)
        
        # Add metadata
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_projects': len(projects),
            'statistics': stats
        }
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


def show_dashboard(scanner: ProjectScanner, parent=None, lang='en'):
    """Show the dashboard dialog."""
    dialog = DashboardDialog(scanner, parent, lang)
    dialog.setModal(True)
    dialog.exec()
