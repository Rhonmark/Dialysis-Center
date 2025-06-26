import os
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, timedelta
import calendar

class PDFReportGenerator:
    def __init__(self, db_connection_func):
        """
        Initialize PDF Report Generator
        
        Args:
            db_connection_func: Function that returns database connection
        """
        self.db = db_connection_func
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1A374D')
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#104E44')
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#1A374D'),
            leftIndent=0
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def export_report_to_pdf(self, period_filter="Overall"):
        """
        Main function to export report to PDF with file dialog
        
        Args:
            period_filter: The time period filter (Today, Weekly, Monthly, Overall)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate default filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"System_Report_{period_filter}_{timestamp}.pdf"
            
            # Use a simpler file dialog approach
            file_path = filedialog.asksaveasfilename(
                title="Save PDF Report As",
                filetypes=[("PDF Files", "*.pdf")],
                defaultextension=".pdf"
            )
            
            if not file_path:
                messagebox.showinfo("Export Cancelled", "PDF export was cancelled.")
                return False
            
            # Ensure the file has .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            # Generate the PDF
            return self.generate_pdf_report(file_path, period_filter)
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF:\n{str(e)}")
            return False
    
    def generate_pdf_report(self, file_path, period_filter):
        """
        Generate the actual PDF report
        
        Args:
            file_path: Path where to save the PDF
            period_filter: Time period filter
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build the story (content)
            story = []
            
            # Add title and header
            story.extend(self.create_header(period_filter))
            
            # Add patient summary
            story.extend(self.create_patient_summary(period_filter))
            
            # Add supply summary  
            story.extend(self.create_supply_summary(period_filter))
            
            # Add backup summary
            story.extend(self.create_backup_summary(period_filter))
            
            # Add notification summary
            story.extend(self.create_notification_summary(period_filter))
            
            # Add detailed tables
            story.extend(self.create_detailed_tables(period_filter))
            
            # Build PDF
            doc.build(story)
            
            # Show success message
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
            messagebox.showinfo(
                "Export Successful",
                f"Report exported successfully!\n\n"
                f"File: {os.path.basename(file_path)}\n"
                f"Location: {os.path.dirname(file_path)}\n"
                f"Size: {file_size:.2f} MB\n"
                f"Period: {period_filter}"
            )
            
            return True
            
        except Exception as e:
            messagebox.showerror("PDF Generation Error", f"Failed to generate PDF:\n{str(e)}")
            return False
    
    def create_header(self, period_filter):
        """Create PDF header section"""
        story = []
        
        # Main title
        title = Paragraph("System Report", self.title_style)
        story.append(title)
        
        # Subtitle with period and date
        current_date = datetime.now().strftime("%B %d, %Y at %H:%M")
        subtitle_text = f"Report Period: {period_filter}<br/>Generated on: {current_date}"
        subtitle = Paragraph(subtitle_text, self.subtitle_style)
        story.append(subtitle)
        
        story.append(Spacer(1, 20))
        
        return story
    
    def create_patient_summary(self, period_filter):
        """Create patient summary section"""
        story = []
        
        # Section header
        header = Paragraph("Patient Summary", self.section_style)
        story.append(header)
        
        try:
            connect = self.db()
            cursor = connect.cursor()
            
            # Get patient counts based on period
            if period_filter == "Overall":
                # Get all patients
                cursor.execute("SELECT COUNT(*) FROM patient_info WHERE status = 'Active'")
                active_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM patient_info WHERE status = 'Inactive'")
                inactive_count = cursor.fetchone()[0]
                
                date_range_text = "All Time"
            else:
                # Use the same date filtering logic as in your report page
                active_count, inactive_count, date_range_text = self.get_patient_counts_by_period(cursor, period_filter)
            
            # Create patient summary table
            patient_data = [
                ['Status', 'Count'],
                ['Active Patients', str(active_count)],
                ['Inactive Patients', str(inactive_count)],
                ['Total Patients', str(active_count + inactive_count)]
            ]
            
            patient_table = Table(patient_data, colWidths=[3*inch, 2*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#88BD8E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 12))
            
            # Add date range info
            if date_range_text:
                range_text = Paragraph(f"<i>Date Range: {date_range_text}</i>", self.normal_style)
                story.append(range_text)
            
            cursor.close()
            connect.close()
            
        except Exception as e:
            error_text = Paragraph(f"Error loading patient data: {str(e)}", self.normal_style)
            story.append(error_text)
        
        story.append(Spacer(1, 20))
        return story
    
    def create_supply_summary(self, period_filter):
        """Create supply summary section with period filtering"""
        story = []
        
        # Section header
        header = Paragraph("Supply Summary", self.section_style)
        story.append(header)
        
        try:
            connect = self.db()
            cursor = connect.cursor()
            
            # Add period filtering logic
            date_filter = ""
            if period_filter != "Overall":
                today = datetime.now().date()
                
                if period_filter.lower() == 'today':
                    date_filter = f"WHERE date_registered = '{today}'"
                elif period_filter.lower() == 'weekly':
                    start_of_week = today - timedelta(days=today.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    date_filter = f"WHERE date_registered >= '{start_of_week}' AND date_registered <= '{end_of_week}'"
                elif period_filter.lower() == 'monthly':
                    start_of_month = today.replace(day=1)
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    end_of_month = today.replace(day=last_day)
                    date_filter = f"WHERE date_registered >= '{start_of_month}' AND date_registered <= '{end_of_month}'"
            
            # Get supply counts with period filtering
            cursor.execute(f"SELECT COUNT(*) FROM supply {date_filter}")
            total_supplies = cursor.fetchone()[0]
            
            # For stock status updates, use status_update date if filtering by period
            stock_date_filter = ""
            if period_filter != "Overall":
                if period_filter.lower() == 'today':
                    stock_date_filter = f"AND status_update = '{today}'"
                elif period_filter.lower() == 'weekly':
                    stock_date_filter = f"AND status_update >= '{start_of_week}' AND status_update <= '{end_of_week}'"
                elif period_filter.lower() == 'monthly':
                    stock_date_filter = f"AND status_update >= '{start_of_month}' AND status_update <= '{end_of_month}'"
            
            cursor.execute(f"SELECT COUNT(*) FROM supply WHERE stock_level_status = 'Low Stock Level' {stock_date_filter}")
            low_stock = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(*) FROM supply WHERE stock_level_status = 'Critical Stock Level' {stock_date_filter}")
            critical_stock = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(*) FROM supply WHERE stock_level_status = 'Adequate Stock Level' {stock_date_filter}")
            adequate_stock = cursor.fetchone()[0]
            
            # Create supply summary table
            supply_data = [
                ['Stock Status', 'Count'],
                ['Total Items', str(total_supplies)],
                ['Adequate Stock', str(adequate_stock)],
                ['Low Stock Items', str(low_stock)],
                ['Critical Stock Items', str(critical_stock)]
            ]
            
            supply_table = Table(supply_data, colWidths=[3*inch, 2*inch])
            supply_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A374D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # Color code the stock levels
                ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#D08B40')),  # Low stock
                ('TEXTCOLOR', (0, 4), (-1, 4), colors.HexColor('#AC1616'))   # Critical stock
            ]))
            
            story.append(supply_table)
            
            cursor.close()
            connect.close()
            
        except Exception as e:
            error_text = Paragraph(f"Error loading supply data: {str(e)}", self.normal_style)
            story.append(error_text)
        
        story.append(Spacer(1, 20))
        return story
    
    def create_backup_summary(self, period_filter):
        """Create backup summary section with period filtering"""
        story = []
        
        # Section header
        header = Paragraph("Backup Summary", self.section_style)
        story.append(header)
        
        try:
            connect = self.db()
            cursor = connect.cursor()
            
            # Add period filtering logic
            date_filter = ""
            if period_filter != "Overall":
                today = datetime.now().date()
                
                if period_filter.lower() == 'today':
                    date_filter = f"AND last_date = '{today}'"
                elif period_filter.lower() == 'weekly':
                    start_of_week = today - timedelta(days=today.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    date_filter = f"AND last_date >= '{start_of_week}' AND last_date <= '{end_of_week}'"
                elif period_filter.lower() == 'monthly':
                    start_of_month = today.replace(day=1)
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    end_of_month = today.replace(day=last_day)
                    date_filter = f"AND last_date >= '{start_of_month}' AND last_date <= '{end_of_month}'"
            
            # Get backup counts with period filtering
            cursor.execute(f"SELECT COUNT(*) FROM backup_logs WHERE last_date IS NOT NULL {date_filter}")
            total_backups = cursor.fetchone()[0]
            
            # Get most recent backup within the period
            cursor.execute(f"""
                SELECT last_date, last_time, employee_name 
                FROM backup_logs 
                WHERE last_date IS NOT NULL AND last_time IS NOT NULL {date_filter}
                ORDER BY last_date DESC, last_time DESC 
                LIMIT 1
            """)
            recent_backup = cursor.fetchone()
            
            if recent_backup:
                last_date, last_time, employee_name = recent_backup
                last_backup_text = f"{last_date} at {last_time} by {employee_name}"
            else:
                if period_filter != "Overall":
                    last_backup_text = f"No backups found for {period_filter.lower()}"
                else:
                    last_backup_text = "No backups found"
            
            # Create backup summary table
            backup_data = [
                ['Backup Information', 'Details'],
                ['Total Backups', str(total_backups)],
                ['Most Recent Backup', last_backup_text]
            ]
            
            backup_table = Table(backup_data, colWidths=[3*inch, 4*inch])
            backup_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00C88D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(backup_table)
            
            cursor.close()
            connect.close()
            
        except Exception as e:
            error_text = Paragraph(f"Error loading backup data: {str(e)}", self.normal_style)
            story.append(error_text)
        
        story.append(Spacer(1, 20))
        return story
    
    def create_notification_summary(self, period_filter):
        """Create notification summary section with period filtering"""
        story = []
        
        # Section header
        header = Paragraph("Notification Summary", self.section_style)
        story.append(header)
        
        try:
            connect = self.db()
            cursor = connect.cursor()
            
            # Add period filtering logic
            date_filter = ""
            if period_filter != "Overall":
                today = datetime.now()  # Use datetime for timestamp comparison
                
                if period_filter.lower() == 'today':
                    today_date = today.date()
                    date_filter = f"AND DATE(notification_timestamp) = '{today_date}'"
                elif period_filter.lower() == 'weekly':
                    start_of_week = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
                    end_of_week = (start_of_week + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999)
                    date_filter = f"AND notification_timestamp >= '{start_of_week}' AND notification_timestamp <= '{end_of_week}'"
                elif period_filter.lower() == 'monthly':
                    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    end_of_month = today.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999)
                    date_filter = f"AND notification_timestamp >= '{start_of_month}' AND notification_timestamp <= '{end_of_month}'"
            
            # Get notification counts by type with period filtering
            supply_notifications = ['Item Restocked', 'Item Stock Status Alert', 'New Item Added', 'Item Usage Recorded']
            patient_notifications = ['Patient Status', 'New Patient Added']
            backup_notifications = ['Manual Backup', 'Scheduled Backup']
            
            # Count supply notifications
            supply_placeholders = ','.join(['%s'] * len(supply_notifications))
            cursor.execute(f"""
                SELECT COUNT(*) FROM notification_logs 
                WHERE notification_type IN ({supply_placeholders}) {date_filter}
            """, supply_notifications)
            supply_count = cursor.fetchone()[0]
            
            # Count patient notifications
            patient_placeholders = ','.join(['%s'] * len(patient_notifications))
            cursor.execute(f"""
                SELECT COUNT(*) FROM notification_logs 
                WHERE notification_type IN ({patient_placeholders}) {date_filter}
            """, patient_notifications)
            patient_count = cursor.fetchone()[0]
            
            # Count backup notifications
            backup_placeholders = ','.join(['%s'] * len(backup_notifications))
            cursor.execute(f"""
                SELECT COUNT(*) FROM notification_logs 
                WHERE notification_type IN ({backup_placeholders}) {date_filter}
            """, backup_notifications)
            backup_count = cursor.fetchone()[0]
            
            # Create notification summary table
            notification_data = [
                ['Notification Type', 'Count'],
                ['Supply Notifications', str(supply_count)],
                ['Patient Notifications', str(patient_count)],
                ['Backup Notifications', str(backup_count)],
                ['Total Notifications', str(supply_count + patient_count + backup_count)]
            ]
            
            notification_table = Table(notification_data, colWidths=[3*inch, 2*inch])
            notification_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A374D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(notification_table)
            
            cursor.close()
            connect.close()
            
        except Exception as e:
            error_text = Paragraph(f"Error loading notification data: {str(e)}", self.normal_style)
            story.append(error_text)
        
        story.append(Spacer(1, 20))
        return story

    def create_detailed_tables(self, period_filter):
        """Create detailed data tables with period filtering"""
        story = []
        
        # Critical Stock Items Tables (separated by supplier) with period filtering
        story.extend(self.create_critical_stock_by_supplier(period_filter))
        
        story.append(Spacer(1, 20))
        
        # Recent Patients Table with period filtering
        story.append(Paragraph("Recent Patients", self.section_style))
        
        try:
            connect = self.db()
            cursor = connect.cursor()
            
            # Add period filtering logic for patients
            date_filter = ""
            limit_clause = "LIMIT 10"  # Default limit
            
            if period_filter != "Overall":
                today = datetime.now().date()
                
                if period_filter.lower() == 'today':
                    date_filter = f"WHERE pl.date_registered = '{today}'"
                elif period_filter.lower() == 'weekly':
                    start_of_week = today - timedelta(days=today.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    date_filter = f"WHERE pl.date_registered >= '{start_of_week}' AND pl.date_registered <= '{end_of_week}'"
                elif period_filter.lower() == 'monthly':
                    start_of_month = today.replace(day=1)
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    end_of_month = today.replace(day=last_day)
                    date_filter = f"WHERE pl.date_registered >= '{start_of_month}' AND pl.date_registered <= '{end_of_month}'"
                
                # For period filtering, show all results (no limit)
                limit_clause = ""
            
            cursor.execute(f"""
                SELECT pl.patient_name, pi.status, pl.date_registered
                FROM patient_list pl
                JOIN patient_info pi ON pl.patient_id = pi.patient_id
                {date_filter}
                ORDER BY pl.date_registered DESC
                {limit_clause}
            """)
            recent_patients = cursor.fetchall()
            
            if recent_patients:
                patient_data = [['Patient Name', 'Status', 'Date Registered']]
                for patient in recent_patients:
                    name, status, date_registered = patient
                    date_str = date_registered.strftime("%Y-%m-%d") if date_registered else "N/A"
                    patient_data.append([name, status, date_str])
                
                patient_table = Table(patient_data, colWidths=[3*inch, 1.5*inch, 2*inch])
                patient_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#88BD8E')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                
                story.append(patient_table)
            else:
                if period_filter != "Overall":
                    story.append(Paragraph(f"No patients registered {period_filter.lower()}.", self.normal_style))
                else:
                    story.append(Paragraph("No recent patients found.", self.normal_style))
            
            cursor.close()
            connect.close()
            
        except Exception as e:
            error_text = Paragraph(f"Error loading patient data: {str(e)}", self.normal_style)
            story.append(error_text)
        
        return story

    def create_critical_stock_by_supplier(self, period_filter):
        """Create separate critical stock tables for each supplier with period filtering"""
        story = []
        
        try:
            connect = self.db()
            cursor = connect.cursor()
            
            # Add period filtering logic for critical stock
            date_filter = ""
            if period_filter != "Overall":
                today = datetime.now().date()
                
                if period_filter.lower() == 'today':
                    date_filter = f"AND status_update = '{today}'"
                elif period_filter.lower() == 'weekly':
                    start_of_week = today - timedelta(days=today.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    date_filter = f"AND status_update >= '{start_of_week}' AND status_update <= '{end_of_week}'"
                elif period_filter.lower() == 'monthly':
                    start_of_month = today.replace(day=1)
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    end_of_month = today.replace(day=last_day)
                    date_filter = f"AND status_update >= '{start_of_month}' AND status_update <= '{end_of_month}'"
            
            # Debug: First check what we have in the database with period filter
            cursor.execute(f"""
                SELECT item_name, supplier_name, stock_level_status 
                FROM supply 
                WHERE stock_level_status = 'Critical Stock Level' {date_filter}
                ORDER BY supplier_name
            """)
            all_critical = cursor.fetchall()
            
            print(f"🔍 Debug: Found {len(all_critical)} critical stock items for {period_filter}:")
            for item in all_critical:
                print(f"   - {item[0]} | Supplier: '{item[1]}' | Status: {item[2]}")
            
            # Get all unique suppliers that have critical stock items in the period
            cursor.execute(f"""
                SELECT DISTINCT supplier_name 
                FROM supply 
                WHERE stock_level_status = 'Critical Stock Level' {date_filter}
                AND supplier_name IS NOT NULL 
                AND supplier_name != ''
                AND supplier_name != 'None'
                ORDER BY supplier_name
            """)
            suppliers = cursor.fetchall()
            
            print(f"🔍 Debug: Found suppliers for {period_filter}: {suppliers}")
            
            # Also check for items with no supplier or empty supplier in the period
            cursor.execute(f"""
                SELECT COUNT(*) FROM supply 
                WHERE stock_level_status = 'Critical Stock Level' {date_filter}
                AND (supplier_name IS NULL OR supplier_name = '' OR supplier_name = 'None')
            """)
            no_supplier_count = cursor.fetchone()[0]
            
            print(f"🔍 Debug: Items with no/empty supplier for {period_filter}: {no_supplier_count}")
            
            if not suppliers and no_supplier_count == 0:
                story.append(Paragraph("Critical Stock Items", self.section_style))
                if period_filter != "Overall":
                    story.append(Paragraph(f"No critical stock items found for {period_filter.lower()}.", self.normal_style))
                else:
                    story.append(Paragraph("No critical stock items found.", self.normal_style))
                return story
            
            # Create tables for each supplier that has critical items in the period
            for (supplier_name,) in suppliers:
                if supplier_name and supplier_name.strip():  # Make sure supplier name is not empty
                    print(f"🔍 Debug: Creating table for supplier: '{supplier_name}' for {period_filter}")
                    story.extend(self.create_supplier_critical_table(cursor, supplier_name, date_filter))
                    story.append(Spacer(1, 15))
            
            # Create table for items with no supplier in the period
            if no_supplier_count > 0:
                print(f"🔍 Debug: Creating table for items with no supplier for {period_filter}")
                story.extend(self.create_supplier_critical_table(cursor, None, date_filter))
                story.append(Spacer(1, 15))
            
            cursor.close()
            connect.close()
            
        except Exception as e:
            story.append(Paragraph("Critical Stock Items", self.section_style))
            error_text = Paragraph(f"Error loading critical stock data: {str(e)}", self.normal_style)
            story.append(error_text)
            print(f"❌ Error in create_critical_stock_by_supplier: {e}")
        
        return story

    def create_supplier_critical_table(self, cursor, supplier_name, date_filter=""):
        """Create critical stock table for a specific supplier with period filtering"""
        story = []
        
        # Create section header
        if supplier_name:
            header_text = f"Critical Stock Items - {supplier_name}"
        else:
            header_text = "Critical Stock Items - No Supplier"
        
        header = Paragraph(header_text, self.section_style)
        story.append(header)
        
        # Query for items from this supplier with date filter
        if supplier_name:
            cursor.execute(f"""
                SELECT item_name, current_stock, reorder_quantity, supplier_name 
                FROM supply 
                WHERE stock_level_status = 'Critical Stock Level' {date_filter}
                AND supplier_name = %s
                ORDER BY current_stock ASC
            """, (supplier_name,))
        else:
            cursor.execute(f"""
                SELECT item_name, current_stock, reorder_quantity, supplier_name 
                FROM supply 
                WHERE stock_level_status = 'Critical Stock Level' {date_filter}
                AND (supplier_name IS NULL OR supplier_name = '' OR supplier_name = 'None')
                ORDER BY current_stock ASC
            """)
        
        critical_items = cursor.fetchall()
        
        if critical_items:
            # Create table data
            critical_data = [['Item Name', 'Current Stock', 'Reorder Qty', 'Supplier']]
            for item in critical_items:
                item_name, current_stock, reorder_qty, supplier = item
                supplier_display = supplier if supplier and supplier.strip() else "None"
                critical_data.append([item_name, str(current_stock), str(reorder_qty), supplier_display])
            
            # Create table
            critical_table = Table(critical_data, colWidths=[2.5*inch, 1*inch, 1*inch, 2*inch])
            critical_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#AC1616')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(critical_table)
            
            # Add item count
            item_count_text = f"<i>Total items requiring attention: {len(critical_items)}</i>"
            item_count = Paragraph(item_count_text, self.normal_style)
            story.append(item_count)
        else:
            no_items_text = f"No critical stock items found for {supplier_name if supplier_name else 'items without supplier'}."
            story.append(Paragraph(no_items_text, self.normal_style))
        
        return story
    
    def get_patient_counts_by_period(self, cursor, period_filter):
        """Helper method to get patient counts based on period filter"""
        today = datetime.now().date()
        
        if period_filter.lower() == 'today':
            date_filter = f"AND DATE(pl.date_registered) = '{today}'"
            date_range_text = today.strftime("%B %d, %Y")
        elif period_filter.lower() == 'weekly':
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            date_filter = f"AND pl.date_registered >= '{start_of_week}' AND pl.date_registered <= '{end_of_week}'"
            date_range_text = f"{start_of_week.strftime('%B %d')} - {end_of_week.strftime('%B %d, %Y')}"
        elif period_filter.lower() == 'monthly':
            start_of_month = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_of_month = today.replace(day=last_day)
            date_filter = f"AND pl.date_registered >= '{start_of_month}' AND pl.date_registered <= '{end_of_month}'"
            date_range_text = start_of_month.strftime('%B %Y')
        else:
            date_filter = ""
            date_range_text = "All Time"
        
        # Get active patients
        cursor.execute(f"""
            SELECT COUNT(*) FROM patient_info pi
            JOIN patient_list pl ON pi.patient_id = pl.patient_id
            WHERE pi.status = 'Active' {date_filter}
        """)
        active_count = cursor.fetchone()[0]
        
        # Get inactive patients
        cursor.execute(f"""
            SELECT COUNT(*) FROM patient_info pi
            JOIN patient_list pl ON pi.patient_id = pl.patient_id
            WHERE pi.status = 'Inactive' {date_filter}
        """)
        inactive_count = cursor.fetchone()[0]
        
        return active_count, inactive_count, date_range_text


# Main function to be called from your maintenance page
def export_pdf_with_auto_period_detection(db_connection_func, maintenance_page_instance):
    """
    Function that automatically detects the current report period
    
    Args:
        db_connection_func: Your database connection function
        maintenance_page_instance: The MaintenancePage instance to traverse from
    
    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        current_period = "Overall"  # Default
        
        # Try to find the report page and get its current selection
        try:
            # Method 1: Try to access through the parent widget hierarchy
            widget = maintenance_page_instance
            found_report = False
            
            # Go up the widget hierarchy to find the container that has both pages
            for _ in range(10):  # Limit attempts to avoid infinite loop
                if hasattr(widget, 'master') and widget.master:
                    widget = widget.master
                    
                    # Check if this widget has both ReportPage and MaintenancePage as children
                    if hasattr(widget, 'winfo_children'):
                        children = widget.winfo_children()
                        report_page = None
                        
                        # Look for ReportPage instance in children
                        for child in children:
                            if hasattr(child, '__class__') and 'ReportPage' in str(child.__class__):
                                report_page = child
                                found_report = True
                                break
                        
                        if found_report and report_page and hasattr(report_page, 'Interval_Dropdown'):
                            dropdown_value = report_page.Interval_Dropdown.get()
                            if dropdown_value:
                                current_period = dropdown_value
                                print(f"📊 Found report period from ReportPage: {current_period}")
                                break
                else:
                    break
            
            # Method 2: Try alternative approach - look for pages dictionary
            if not found_report:
                widget = maintenance_page_instance
                for _ in range(10):
                    if hasattr(widget, 'master') and widget.master:
                        widget = widget.master
                        if hasattr(widget, 'pages') and isinstance(widget.pages, dict):
                            if 'Report' in widget.pages:
                                report_page = widget.pages['Report']
                                if hasattr(report_page, 'Interval_Dropdown'):
                                    dropdown_value = report_page.Interval_Dropdown.get()
                                    if dropdown_value:
                                        current_period = dropdown_value
                                        print(f"📊 Found report period from pages dict: {current_period}")
                                        found_report = True
                                        break
                    else:
                        break
            
            if not found_report:
                print("📊 Could not find ReportPage, using default: Overall")
                
        except Exception as e:
            print(f"📊 Error getting report period: {e}, using default: Overall")
            current_period = "Overall"
        
        print(f"📄 Final period being used: {current_period}")
        pdf_generator = PDFReportGenerator(db_connection_func)
        return pdf_generator.export_report_to_pdf(current_period)
        
    except Exception as e:
        messagebox.showerror("PDF Export Error", f"Failed to initialize PDF export:\n{str(e)}")
        return False