from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

class PlaybookGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles()
    
    def custom_styles(self):
        """Define custom styles for the playbook"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2563eb')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#1f2937')
        ))
    
    def generate_messaging_playbook_pdf(self, results: dict, company_name: str) -> bytes:
        """Generate branded PDF playbook"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        
        story = []
        
        # Title Page
        title = Paragraph(f"Messaging Playbook for {company_name}", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Value Proposition Section
        if 'messaging_framework' in results:
            framework = results['messaging_framework']
            
            story.append(Paragraph("Value Proposition", self.styles['SectionHeader']))
            story.append(Paragraph(framework.get('value_proposition', ''), self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Elevator Pitch
            story.append(Paragraph("Elevator Pitch", self.styles['SectionHeader']))
            story.append(Paragraph(framework.get('elevator_pitch', ''), self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Tagline Options
            story.append(Paragraph("Tagline Options", self.styles['SectionHeader']))
            for tagline in framework.get('tagline_options', []):
                story.append(Paragraph(f"• {tagline}", self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Content Assets
        if 'content_assets' in results:
            content = results['content_assets']
            
            story.append(Paragraph("Ready-to-Use Content", self.styles['SectionHeader']))
            
            # Website Headlines
            story.append(Paragraph("Website Headlines:", self.styles['Heading3']))
            for headline in content.get('website_headlines', []):
                story.append(Paragraph(f"• {headline}", self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            # LinkedIn Posts
            story.append(Paragraph("LinkedIn Post Templates:", self.styles['Heading3']))
            for post in content.get('linkedin_posts', []):
                story.append(Paragraph(f"• {post}", self.styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()