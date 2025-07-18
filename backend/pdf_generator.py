from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime

class MessageCraftCanvas:
    """Custom canvas class for adding watermarks and branding"""
    
    def __init__(self, canvas_obj, doc):
        self.canvas = canvas_obj
        self.doc = doc
        self.page_number = 0
        
    def add_watermark(self):
        """Add MessageCraft watermark to the page"""
        self.canvas.saveState()
        
        # Semi-transparent watermark
        self.canvas.setFillColor(colors.HexColor('#E5E7EB'))
        self.canvas.setFillAlpha(0.1)
        
        # Diagonal watermark text
        self.canvas.rotate(45)
        self.canvas.setFont("Helvetica-Bold", 60)
        self.canvas.drawString(200, -100, "MessageCraft")
        
        self.canvas.restoreState()
        
    def add_header(self):
        """Add MessageCraft header to each page"""
        self.canvas.saveState()
        
        # Header line
        self.canvas.setStrokeColor(colors.HexColor('#2563eb'))
        self.canvas.setLineWidth(2)
        self.canvas.line(72, A4[1] - 50, A4[0] - 72, A4[1] - 50)
        
        # MessageCraft logo text
        self.canvas.setFillColor(colors.HexColor('#2563eb'))
        self.canvas.setFont("Helvetica-Bold", 12)
        self.canvas.drawString(72, A4[1] - 40, "MessageCraft")
        
        # Subtitle
        self.canvas.setFillColor(colors.HexColor('#6B7280'))
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(72, A4[1] - 28, "AI-Powered Messaging Platform")
        
        self.canvas.restoreState()
        
    def add_footer(self):
        """Add footer with page number and branding"""
        self.canvas.saveState()
        
        # Footer line
        self.canvas.setStrokeColor(colors.HexColor('#E5E7EB'))
        self.canvas.setLineWidth(1)
        self.canvas.line(72, 50, A4[0] - 72, 50)
        
        # Page number
        self.canvas.setFillColor(colors.HexColor('#6B7280'))
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(72, 35, f"Page {self.page_number}")
        
        # Generated by MessageCraft
        self.canvas.setFont("Helvetica", 8)
        self.canvas.drawRightString(A4[0] - 72, 35, 
                                   f"Generated by MessageCraft • {datetime.now().strftime('%B %d, %Y')}")
        
        self.canvas.restoreState()

def add_page_decorations(canvas, doc):
    """Function to add decorations to each page"""
    mc_canvas = MessageCraftCanvas(canvas, doc)
    mc_canvas.page_number = doc.page
    
    # Add watermark, header, and footer
    mc_canvas.add_watermark()
    mc_canvas.add_header()
    mc_canvas.add_footer()

class PlaybookGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles()
    
    def _safe_text_extract(self, value):
        """Safely extract text from various data structures"""
        try:
            if not value:
                return 'Not specified'
            
            if isinstance(value, str):
                return value
            
            if isinstance(value, dict):
                # Handle specific target audience structure
                if 'age_range' in value or 'demographics' in value or 'income_level' in value or 'lifestyle' in value:
                    parts = []
                    if value.get('age_range'):
                        parts.append(f"Age: {value['age_range']}")
                    if value.get('demographics'):
                        parts.append(f"Demographics: {value['demographics']}")
                    if value.get('income_level'):
                        parts.append(f"Income: {value['income_level']}")
                    if value.get('lifestyle'):
                        parts.append(f"Lifestyle: {value['lifestyle']}")
                    return ', '.join(parts) if parts else 'Not specified'
                
                # Handle common dictionary structures
                if 'primary' in value:
                    return str(value['primary'])
                elif 'primary_tone' in value:
                    return str(value['primary_tone'])
                elif 'description' in value:
                    return str(value['description'])
                elif 'content' in value:
                    return str(value['content'])
                elif 'primary_segments' in value:
                    return str(value['primary_segments'])
                elif 'characteristics' in value:
                    return str(value['characteristics'])
                else:
                    # Join all string values in the dict
                    text_values = []
                    for k, v in value.items():
                        if isinstance(v, str) and v.strip():
                            text_values.append(f"{k}: {v}")
                        elif isinstance(v, list):
                            list_text = ', '.join([str(item) for item in v if item])
                            if list_text:
                                text_values.append(f"{k}: {list_text}")
                        elif v and not isinstance(v, dict):
                            text_values.append(f"{k}: {str(v)}")
                    return ' | '.join(text_values) if text_values else 'Not specified'
            
            if isinstance(value, list):
                processed_items = []
                for item in value:
                    if isinstance(item, dict):
                        processed_items.append(self._safe_text_extract(item))
                    elif item:
                        processed_items.append(str(item))
                return ' | '.join(processed_items) if processed_items else 'Not specified'
            
            return str(value)
            
        except Exception as e:
            print(f"Error in _safe_text_extract: {e}, Value: {value}")
            return 'Error extracting text'
    
    def _safe_paragraph(self, text, style):
        """Create a paragraph with safe text handling"""
        try:
            # Ensure text is a string
            safe_text = self._safe_text_extract(text)
            return Paragraph(safe_text, style)
        except Exception as e:
            print(f"Error creating paragraph: {e}, Text: {text}")
            return Paragraph('Error displaying content', style)
    
    def custom_styles(self):
        """Define custom styles for the playbook"""
        # Main title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            textColor=colors.HexColor('#2563eb'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=16,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica-Bold'
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            leftIndent=20,
            textColor=colors.HexColor('#1f2937')
        ))
        
        # Quote style for key messages
        self.styles.add(ParagraphStyle(
            name='KeyMessage',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            spaceBefore=8,
            leftIndent=20,
            rightIndent=20,
            textColor=colors.HexColor('#2563eb'),
            fontName='Helvetica-Oblique',
            borderWidth=1,
            borderColor=colors.HexColor('#E5E7EB'),
            borderPadding=10,
            backColor=colors.HexColor('#F8FAFC')
        ))
        
        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Normal'],
            fontSize=20,
            spaceAfter=20,
            textColor=colors.HexColor('#059669'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
    
    def generate_messaging_playbook_pdf(self, results: dict, company_name: str) -> bytes:
        """Generate comprehensive branded PDF playbook with watermark"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            topMargin=1.2*inch,
            bottomMargin=1*inch,
            leftMargin=1*inch,
            rightMargin=1*inch
        )
        
        story = []
        
        # Title Page
        story.append(Spacer(1, 0.5*inch))
        title = Paragraph("Messaging Playbook", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        company_title = Paragraph(company_name, self.styles['CompanyName'])
        story.append(company_title)
        story.append(Spacer(1, 0.5*inch))
        
        # Add a professional divider
        story.append(self._create_divider())
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        if 'business_profile' in results:
            profile = results['business_profile']
            summary_text = profile.get('executive_summary', 
                'This playbook contains comprehensive messaging strategies and content frameworks designed specifically for your business.')
            story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Business Profile Section
        if 'business_profile' in results:
            self._add_business_profile_section(story, results['business_profile'])
        
        # Messaging Framework Section
        if 'messaging_framework' in results:
            self._add_messaging_framework_section(story, results['messaging_framework'])
        
        # Positioning Strategy Section
        if 'positioning_strategy' in results:
            self._add_positioning_strategy_section(story, results['positioning_strategy'])
        
        # Content Assets Section
        if 'content_assets' in results:
            self._add_content_assets_section(story, results['content_assets'])
        
        # Competitor Analysis Section
        if 'competitor_analysis' in results:
            self._add_competitor_analysis_section(story, results['competitor_analysis'])
        
        # Quality Review Section
        if 'quality_review' in results:
            self._add_quality_review_section(story, results['quality_review'])
        
        # Build PDF with watermark and branding
        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_divider(self):
        """Create a styled divider line"""
        return Paragraph('<para><font color="#E5E7EB">_________________________________________________________________________________</font></para>', 
                        self.styles['Normal'])
    
    def _add_business_profile_section(self, story, profile):
        """Add business profile section to the story"""
        story.append(PageBreak())
        story.append(Paragraph("Business Profile", self.styles['SectionHeader']))
        
        if profile.get('company_overview'):
            story.append(Paragraph("Company Overview", self.styles['SubsectionHeader']))
            story.append(self._safe_paragraph(profile['company_overview'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if profile.get('target_audience'):
            story.append(Paragraph("Target Audience", self.styles['SubsectionHeader']))
            story.append(self._safe_paragraph(profile['target_audience'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if profile.get('unique_value_proposition'):
            story.append(Paragraph("Unique Value Proposition", self.styles['SubsectionHeader']))
            story.append(Paragraph(self._safe_text_extract(profile['unique_value_proposition']), self.styles['KeyMessage']))
            story.append(Spacer(1, 0.2*inch))
        
        # Add industry if available
        if profile.get('industry'):
            story.append(Paragraph("Industry", self.styles['SubsectionHeader']))
            story.append(Paragraph(self._safe_text_extract(profile['industry']), self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Add pain points if available
        if profile.get('pain_points'):
            story.append(Paragraph("Pain Points", self.styles['SubsectionHeader']))
            story.append(self._safe_paragraph(profile['pain_points'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Add unique features if available
        if profile.get('unique_features'):
            story.append(Paragraph("Unique Features", self.styles['SubsectionHeader']))
            story.append(self._safe_paragraph(profile['unique_features'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
    
    def _add_messaging_framework_section(self, story, framework):
        """Add messaging framework section to the story"""
        story.append(PageBreak())
        story.append(Paragraph("Messaging Framework", self.styles['SectionHeader']))
        
        if framework.get('value_proposition'):
            story.append(Paragraph("Value Proposition", self.styles['SubsectionHeader']))
            story.append(Paragraph(self._safe_text_extract(framework['value_proposition']), self.styles['KeyMessage']))
            story.append(Spacer(1, 0.2*inch))
        
        if framework.get('elevator_pitch'):
            story.append(Paragraph("Elevator Pitch", self.styles['SubsectionHeader']))
            story.append(Paragraph(self._safe_text_extract(framework['elevator_pitch']), self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if framework.get('tagline_options'):
            story.append(Paragraph("Tagline Options", self.styles['SubsectionHeader']))
            taglines = framework['tagline_options']
            if isinstance(taglines, list):
                for tagline in taglines:
                    story.append(Paragraph(f"• {self._safe_text_extract(tagline)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(taglines)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
        
        if framework.get('key_messages'):
            story.append(Paragraph("Key Messages", self.styles['SubsectionHeader']))
            key_messages = framework['key_messages']
            if isinstance(key_messages, list):
                for message in key_messages:
                    story.append(Paragraph(f"• {self._safe_text_extract(message)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(key_messages)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
    
    def _add_positioning_strategy_section(self, story, positioning):
        """Add positioning strategy section to the story"""
        story.append(PageBreak())
        story.append(Paragraph("Positioning Strategy", self.styles['SectionHeader']))
        
        if positioning.get('market_position'):
            story.append(Paragraph("Market Position", self.styles['SubsectionHeader']))
            story.append(Paragraph(self._safe_text_extract(positioning['market_position']), self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if positioning.get('differentiation_strategy'):
            story.append(Paragraph("Differentiation Strategy", self.styles['SubsectionHeader']))
            story.append(Paragraph(self._safe_text_extract(positioning['differentiation_strategy']), self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if positioning.get('competitive_advantages'):
            story.append(Paragraph("Competitive Advantages", self.styles['SubsectionHeader']))
            advantages = positioning['competitive_advantages']
            if isinstance(advantages, list):
                for advantage in advantages:
                    story.append(Paragraph(f"• {self._safe_text_extract(advantage)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(advantages)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
    
    def _add_content_assets_section(self, story, content):
        """Add content assets section to the story"""
        story.append(PageBreak())
        story.append(Paragraph("Ready-to-Use Content", self.styles['SectionHeader']))
        
        if content.get('website_headlines'):
            story.append(Paragraph("Website Headlines", self.styles['SubsectionHeader']))
            headlines = content['website_headlines']
            if isinstance(headlines, list):
                for headline in headlines:
                    story.append(Paragraph(f"• {self._safe_text_extract(headline)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(headlines)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
        
        if content.get('linkedin_posts'):
            story.append(Paragraph("LinkedIn Posts", self.styles['SubsectionHeader']))
            posts = content['linkedin_posts']
            if isinstance(posts, list):
                for post in posts:
                    story.append(Paragraph(f"• {self._safe_text_extract(post)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(posts)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
        
        if content.get('email_subject_lines'):
            story.append(Paragraph("Email Subject Lines", self.styles['SubsectionHeader']))
            subjects = content['email_subject_lines']
            if isinstance(subjects, list):
                for subject in subjects:
                    story.append(Paragraph(f"• {self._safe_text_extract(subject)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(subjects)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
        
        if content.get('ad_copy'):
            story.append(Paragraph("Ad Copy", self.styles['SubsectionHeader']))
            ads = content['ad_copy']
            if isinstance(ads, list):
                for ad in ads:
                    story.append(Paragraph(f"• {self._safe_text_extract(ad)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(ads)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
    
    def _add_competitor_analysis_section(self, story, analysis):
        """Add competitor analysis section to the story"""
        story.append(PageBreak())
        story.append(Paragraph("Competitor Analysis", self.styles['SectionHeader']))
        
        if analysis.get('market_overview'):
            story.append(Paragraph("Market Overview", self.styles['SubsectionHeader']))
            story.append(Paragraph(self._safe_text_extract(analysis['market_overview']), self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if analysis.get('key_competitors'):
            story.append(Paragraph("Key Competitors", self.styles['SubsectionHeader']))
            competitors = analysis['key_competitors']
            if isinstance(competitors, list):
                for competitor in competitors:
                    story.append(Paragraph(f"• {self._safe_text_extract(competitor)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(competitors)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
        
        if analysis.get('competitive_gaps'):
            story.append(Paragraph("Market Opportunities", self.styles['SubsectionHeader']))
            gaps = analysis['competitive_gaps']
            if isinstance(gaps, list):
                for gap in gaps:
                    story.append(Paragraph(f"• {self._safe_text_extract(gap)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(gaps)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
    
    def _add_quality_review_section(self, story, review):
        """Add quality review section to the story"""
        story.append(PageBreak())
        story.append(Paragraph("Quality Assessment", self.styles['SectionHeader']))
        
        if review.get('overall_quality_score'):
            score = review['overall_quality_score']
            story.append(Paragraph("Overall Quality Score", self.styles['SubsectionHeader']))
            story.append(Paragraph(f"Score: {score}/10", self.styles['KeyMessage']))
            story.append(Spacer(1, 0.2*inch))
        
        if review.get('strengths'):
            story.append(Paragraph("Strengths", self.styles['SubsectionHeader']))
            strengths = review['strengths']
            if isinstance(strengths, list):
                for strength in strengths:
                    story.append(Paragraph(f"• {self._safe_text_extract(strength)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(strengths)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
        
        if review.get('recommendations'):
            story.append(Paragraph("Recommendations", self.styles['SubsectionHeader']))
            recommendations = review['recommendations']
            if isinstance(recommendations, list):
                for rec in recommendations:
                    story.append(Paragraph(f"• {self._safe_text_extract(rec)}", self.styles['BulletPoint']))
            else:
                story.append(Paragraph(f"• {self._safe_text_extract(recommendations)}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))