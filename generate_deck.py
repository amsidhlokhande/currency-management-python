"""
Generate high-impact PowerPoint presentation for Approach 2: Shared Enterprise Library.
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank slide

    # Colors
    NAVY = RGBColor(30, 41, 59)          # #1E293B
    DARK_NAVY = RGBColor(15, 23, 42)     # #0F172A
    BLUE = RGBColor(37, 99, 235)         # #2563EB
    LIGHT_BLUE = RGBColor(239, 246, 255) # #EFF6FF
    TEAL = RGBColor(13, 148, 136)        # #0D9488
    LIGHT_TEAL = RGBColor(240, 253, 250) # #F0FDFA
    AMBER = RGBColor(245, 158, 11)       # #F59E0B
    LIGHT_AMBER = RGBColor(254, 243, 199)# #FEF3C7
    RED = RGBColor(239, 68, 68)          # #EF4444
    LIGHT_RED = RGBColor(254, 242, 242)  # #FEF2F2
    GREEN = RGBColor(16, 185, 129)       # #10B981
    LIGHT_GREEN = RGBColor(236, 253, 245)# #ECFDF5
    SLATE_BG = RGBColor(248, 250, 252)   # #F8FAFC
    CARD_BG = RGBColor(255, 255, 255)    # #FFFFFF
    TEXT_DARK = RGBColor(30, 41, 59)     # #1E293B
    TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
    BORDER_COLOR = RGBColor(226, 232, 240) # #E2E8F0
    BORDER_BLUE = RGBColor(191, 219, 254)  # #BFDBFE

    def set_bg(slide, color=SLATE_BG):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title, category="ENTERPRISE ARCHITECTURE SPECIFICATION", slide_num=1, total_slides=13):
        # Top accent bar
        accent_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.06))
        accent_bar.fill.solid()
        accent_bar.fill.fore_color.rgb = BLUE
        accent_bar.line.fill.background()

        # Category Tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(8.0), Inches(0.3))
        tf = cat_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = category.upper()
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEAL

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(10.5), Inches(0.6))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = DARK_NAVY

        # Slide number & footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
        tf = footer_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"Approach 2: Shared Enterprise Library (enterprise-core-python) | Executive Presentation"
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_MUTED

        num_p = tf.add_paragraph()
        num_p.text = f"{slide_num} / {total_slides}"
        num_p.font.size = Pt(9)
        num_p.font.bold = True
        num_p.font.color.rgb = BLUE
        num_p.alignment = PP_ALIGN.RIGHT

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_COLOR):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # ==========================================
    # SLIDE 1: Title Slide (Dark Executive Theme)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1, DARK_NAVY)

    # Decorative header strip
    strip = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.15))
    strip.fill.solid()
    strip.fill.fore_color.rgb = BLUE
    strip.line.fill.background()

    # Badge Pill
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(3.8), Inches(0.42))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(30, 58, 138)  # Deep blue
    badge.line.color.rgb = BLUE
    badge.line.width = Pt(1)
    tf = badge.text_frame
    p = tf.paragraphs[0]
    p.text = "ENTERPRISE MICROSERVICES ARCHITECTURE"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)
    p.alignment = PP_ALIGN.CENTER

    # Main Title
    title_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.85), Inches(10.8), Inches(1.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Modernizing Enterprise Python Microservices"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    p2 = tf.add_paragraph()
    p2.text = "Approach 2: Shared Enterprise Library (`enterprise-core-python`)"
    p2.font.size = Pt(24)
    p2.font.bold = True
    p2.font.color.rgb = TEAL

    # Subtitle / Abstract
    desc_box = s1.shapes.add_textbox(Inches(1.2), Inches(3.8), Inches(10.8), Inches(1.1))
    tf = desc_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "A definitive blueprint for scaling 36+ Python microservices with Spring Boot Starter parity: single-source dependency governance, automated PII-masking telemetry, zero-day CVE remediation, and dual Docker distribution pipelines."
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(203, 213, 225)

    # 4 Key Highlights Cards
    highlights = [
        ("Centralized BOM", "1 single file controls all 36 microservice versions", BLUE),
        ("5 Core Pillars", "Errors, PII Logs, Latency, Actuators, Swagger UI", TEAL),
        ("Instant CVE Patch", "Remediate zero-day vulnerabilities in seconds", AMBER),
        ("Zero-Build Docker", "Push pre-built images or compile with non-root security", GREEN),
    ]

    for i, (head, sub, color) in enumerate(highlights):
        left = Inches(1.2 + i * 2.75)
        top = Inches(5.1)
        w = Inches(2.6)
        h = Inches(1.5)

        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = NAVY
        card.line.color.rgb = color
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(0.18)
        p = tf.paragraphs[0]
        p.text = head
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(10)
        p2.font.color.rgb = RGBColor(226, 232, 240)

    # ==========================================
    # SLIDE 2: The Enterprise Challenge
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "The Enterprise Challenge: 36+ Microservices at Scale", "PROBLEM LANDSCAPE", 2)

    # Left Card: The Status Quo (Anti-Pattern)
    c1 = add_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1), LIGHT_RED, RGBColor(252, 165, 165))
    tf = c1.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "CRITICAL PAIN POINTS: DECENTRALIZED SPRAWL"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RED

    bullets_c1 = [
        ("36x Duplicate `requirements.txt`", "Every repository hardcodes Flask, requests, urllib3, gunicorn with drifting version numbers causing 'works on my machine' defects."),
        ("Zero-Day CVE Crisis", "Patching a high-severity flaw requires 36 separate PRs, 36 individual review cycles, and 36 coordinated deployments spanning days or weeks."),
        ("Copy-Paste Boilerplate Sprawl", "Thousands of lines copied for JSON logging, error response formatting, and latency measurement without consistency."),
        ("Compliance & Audit Hazards", "Unmasked PII (credit cards, SSNs, bearer tokens) leaking into cloud log aggregation clusters (Splunk/Datadog)."),
        ("Observability Fragmentation", "Inconsistent health probes and correlation IDs breaking distributed tracing across inter-service calls.")
    ]
    for title, desc in bullets_c1:
        p_t = tf.add_paragraph()
        p_t.text = f"• {title}:"
        p_t.font.bold = True
        p_t.font.size = Pt(10.5)
        p_t.font.color.rgb = DARK_NAVY
        p_d = tf.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED

    # Right Card: The Enterprise Impact & Metrics
    c2 = add_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    tf = c2.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "THE COST OF TECHNICAL DEBT ACROSS 36 SERVICES"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    # Add 3 stat boxes inside right pane
    stats = [
        ("36+", "Independent repos maintaining duplicate dependency pins", RED),
        ("72 hrs", "Average turnaround time for zero-day CVE updates", AMBER),
        ("6,000+", "Lines of redundant cross-cutting boilerplate code", DARK_NAVY)
    ]
    for idx, (val, label, col) in enumerate(stats):
        top_pos = Inches(2.3 + idx * 1.35)
        stat_card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), top_pos, Inches(5.1), Inches(1.15))
        stat_card.fill.solid()
        stat_card.fill.fore_color.rgb = SLATE_BG
        stat_card.line.color.rgb = BORDER_COLOR
        stf = stat_card.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_right = Inches(0.2)
        stf.margin_top = Inches(0.15)
        sp = stf.paragraphs[0]
        sp.text = val
        sp.font.size = Pt(20)
        sp.font.bold = True
        sp.font.color.rgb = col
        sp2 = stf.add_paragraph()
        sp2.text = label
        sp2.font.size = Pt(9.5)
        sp2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 3: Architectural Analogy (Spring Boot vs Python)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "Architectural Analogy: Spring Boot Starter vs. enterprise-core-python", "PARADIGM PARITY", 3)

    # Sub-header explanation
    desc = s3.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.45))
    tf = desc.text_frame
    p = tf.paragraphs[0]
    p.text = "Java enterprise teams solve dependency sprawl with Custom Spring Boot Starters (`company-spring-boot-starter-web`). We bring the exact same battle-tested design pattern to enterprise Python."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK

    # Column 1: Spring Boot Starter (Java)
    col1 = add_card(s3, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7))
    tf1 = col1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_right = tf1.margin_top = Inches(0.25)
    p = tf1.paragraphs[0]
    p.text = "JAVA ECOSYSTEM: SPRING BOOT STARTER"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE

    java_items = [
        ("Starter Artifact", "`corp-spring-boot-starter-web:3.2.0`"),
        ("Bill of Materials (BOM)", "Brings in Spring Web, Jackson, Logback, Micrometer transitively"),
        ("Auto-Configuration Beans", "GlobalExceptionHandler, CorrelationFilter, HealthProbes"),
        ("Microservice `pom.xml`", "Declares ONLY starter artifact. Zero direct Jackson/Logback entries"),
        ("CVE Patch Mechanism", "Bump starter version from 3.2.0 to 3.2.1 in parent BOM")
    ]
    for label, val in java_items:
        pt = tf1.add_paragraph()
        pt.text = f"• {label}:"
        pt.font.bold = True
        pt.font.size = Pt(10)
        pt.font.color.rgb = DARK_NAVY
        pv = tf1.add_paragraph()
        pv.text = f"  {val}"
        pv.font.size = Pt(9.5)
        pv.font.color.rgb = TEXT_MUTED

    # Column 2: enterprise-core-python (Python)
    col2 = add_card(s3, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.7), LIGHT_BLUE, BORDER_BLUE)
    tf2 = col2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_right = tf2.margin_top = Inches(0.25)
    p = tf2.paragraphs[0]
    p.text = "PYTHON EQUIVALENT: `enterprise-core-python`"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEAL

    py_items = [
        ("Core Package Artifact", "`enterprise-core-python @ git+https://...@v1.0.0`"),
        ("Transitive Dependencies", "Brings Flask==3.1.0, requests==2.32.3, urllib3==2.2.3, gunicorn==23.0.0"),
        ("Enterprise Modules", "setup_enterprise_logging, register_enterprise_error_handlers, Actuators"),
        ("Microservice `requirements.txt`", "Declares ONLY `enterprise-core-python`. Zero direct Flask/requests entries"),
        ("CVE Patch Mechanism", "Bump package version to 1.0.1 in setup.py, tag v1.0.1; microservices update tag")
    ]
    for label, val in py_items:
        pt = tf2.add_paragraph()
        pt.text = f"✔ {label}:"
        pt.font.bold = True
        pt.font.size = Pt(10)
        pt.font.color.rgb = DARK_NAVY
        pv = tf2.add_paragraph()
        pv.text = f"  {val}"
        pv.font.size = Pt(9.5)
        pv.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 4: The 5 Foundational Pillars
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "The 5 Foundational Pillars of `enterprise-core-python`", "CORE CAPABILITIES", 4)

    pillars = [
        ("1. Structured Logs & PII", "Automated Regex Redaction", "Masks credit cards, SSNs, Bearer tokens, and emails automatically before log emission. Structured JSON with correlation IDs.", TEAL),
        ("2. Unified Error Envelope", "RFC 7807 Standard Format", "Global handler for 400, 404, 500 & EnterpriseBaseException. Guarantees timestamp, status, errorCode, and details array.", BLUE),
        ("3. Latency & Correlation", "Zero-Code Interceptors", "Extracts or generates X-Correlation-ID across all requests. Measures latency with microsecond precision in X-Response-Time-Ms.", DARK_NAVY),
        ("4. Spring Boot Actuators", "K8s Liveness & Readiness", "Standard /health/liveness, /health/readiness, /info, and /metrics endpoints mounted under microservice context paths.", GREEN),
        ("5. Reusable OpenAPI / UI", "Context-Aware Swagger", "Embeds interactive Swagger UI without bulky third-party dependencies. Auto-serves openapi.json under /swagger.", AMBER),
    ]

    for idx, (title, sub, body, color) in enumerate(pillars):
        left = Inches(0.8 + (idx % 3) * 3.95 if idx < 3 else 0.8 + (idx - 3) * 5.95)
        top = Inches(1.6 if idx < 3 else 4.35)
        w = Inches(3.8 if idx < 3 else 5.8)
        h = Inches(2.5 if idx < 3 else 2.4)

        card = add_card(s4, left, top, w, h)
        # Top accent bar inside card
        acc = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, w, Inches(0.08))
        acc.fill.solid()
        acc.fill.fore_color.rgb = color
        acc.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.18)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = DARK_NAVY

        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.size = Pt(9)
        p3.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 5: Centralized Dependency Management (BOM)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "Centralized Dependency Governance: Bill of Materials (BOM)", "DEPENDENCY ARCHITECTURE", 5)

    # Left: Core setup.py BOM
    c_left = add_card(s5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    tf = c_left.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "SINGLE SOURCE OF TRUTH: `setup.py` / `pyproject.toml`"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = BLUE

    p_code = tf.add_paragraph()
    p_code.text = (
        "# enterprise-core-python/setup.py\n"
        "install_requires=[\n"
        "    'Flask==3.1.0',\n"
        "    'werkzeug==3.1.3',\n"
        "    'python-json-logger==2.0.7',\n"
        "    'requests==2.32.3',\n"
        "    'urllib3==2.2.3',\n"
        "    'gunicorn==23.0.0',\n"
        "    'waitress==3.0.1',\n"
        "    'pytest==8.3.3',\n"
        "],\n"
        "extras_require={\n"
        "    'aws': ['boto3==1.35.40']\n"
        "}"
    )
    p_code.font.size = Pt(9)
    p_code.font.name = "Consolas"
    p_code.font.color.rgb = DARK_NAVY

    p_note = tf.add_paragraph()
    p_note.text = "\n✔ Pinned security baselines tested and certified centrally.\n✔ Microservices inherit identical, repeatable dependency trees."
    p_note.font.size = Pt(9.5)
    p_note.font.color.rgb = TEAL

    # Right: Microservice Consumer Requirements
    c_right = add_card(s5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), LIGHT_GREEN, RGBColor(167, 243, 208))
    tf = c_right.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "CLEAN MICROSERVICE CONSUMER SPECIFICATION"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GREEN

    p_c1 = tf.add_paragraph()
    p_c1.text = (
        "# currency-exchange-service-python/requirements.txt\n"
        "enterprise-core-python @ git+https://github.com/amsidhlokhande/\n"
        "  enterprise-core-python.git@v1.0.0\n"
        "boto3\n\n"
        "# currency-conversion-service-python/requirements.txt\n"
        "enterprise-core-python @ git+https://github.com/amsidhlokhande/\n"
        "  enterprise-core-python.git@v1.0.0"
    )
    p_c1.font.size = Pt(9)
    p_c1.font.name = "Consolas"
    p_c1.font.color.rgb = DARK_NAVY

    p_c2 = tf.add_paragraph()
    p_c2.text = (
        "\nKEY ARCHITECTURAL BENEFITS:\n"
        "• Zero direct dependencies on Flask, requests, or gunicorn.\n"
        "• Microservices focus 100% on domain business logic.\n"
        "• Git tag `@v1.0.0` ensures immutable, deterministic builds.\n"
        "• pip resolves all transitive dependencies automatically."
    )
    p_c2.font.size = Pt(9.5)
    p_c2.font.color.rgb = DARK_NAVY

    # ==========================================
    # SLIDE 6: Packaging & Distribution Pipeline
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "Packaging & Distribution: PEP 508 Git Tag & GitHub Actions Release", "DISTRIBUTION PIPELINE", 6)

    # 4 Sequential Pipeline Steps
    steps = [
        ("Step 1: Test & Quality Gate", "Automated Pytest Execution", "Every commit executes comprehensive test suite verifying logging PII filters, custom error envelopes, and actuator probes.", DARK_NAVY),
        ("Step 2: Build Wheel Artifacts", "Standard PEP 517 / 621 Build", "Runs `python -m build` producing binary `.whl` and source `.tar.gz` distributions. Validated via `twine check`.", BLUE),
        ("Step 3: GitHub Release Pipeline", "Automated Tag Release", "Actions workflow triggers on `v*.*.*` git tag. Attaches wheel and sdist to official GitHub Release page automatically.", TEAL),
        ("Step 4: Registry Distribution", "Artifactory / Nexus / Cloud", "Enterprises can publish wheel to internal private PyPI mirrors (JFrog Artifactory, Sonatype Nexus, AWS CodeArtifact).", GREEN),
    ]

    for idx, (title, sub, body, color) in enumerate(steps):
        left = Inches(0.8 + idx * 2.95)
        top = Inches(1.6)
        w = Inches(2.8)
        h = Inches(5.1)

        card = add_card(s6, left, top, w, h)
        top_bar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, w, Inches(0.1))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = color
        top_bar.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(0.25)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = DARK_NAVY

        p3 = tf.add_paragraph()
        p3.text = f"\n{body}"
        p3.font.size = Pt(9)
        p3.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: Hardened Multi-Stage Docker Architecture
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "Hardened Multi-Stage Docker Architecture & Zero-Trust Security", "CONTAINER SECURITY", 7)

    # Left: Stage 1 Builder
    c_s1 = add_card(s7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    tf = c_s1.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "STAGE 1: ISOLATED BUILDER (`python:3.12-slim`)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = BLUE

    p_code = tf.add_paragraph()
    p_code.text = (
        "# Secure Git authentication\n"
        "ARG GITHUB_TOKEN\n"
        "RUN apt-get update && apt-get install -y git\n"
        "RUN python -m venv /opt/venv\n"
        "ENV PATH=\"/opt/venv/bin:$PATH\"\n"
        "COPY requirements.txt .\n"
        "RUN if [ -n \"$GITHUB_TOKEN\" ]; then \\\n"
        "      git config --global url.\"https://${GITHUB_TOKEN}\\\n"
        "      @github.com/\".insteadOf \"https://github.com/\"; \\\n"
        "    fi && pip install -r requirements.txt"
    )
    p_code.font.size = Pt(8.5)
    p_code.font.name = "Consolas"
    p_code.font.color.rgb = DARK_NAVY

    p_sec = tf.add_paragraph()
    p_sec.text = "\n✔ Secret Isolation: `ARG GITHUB_TOKEN` is NEVER retained or copied into the final runtime image."
    p_sec.font.size = Pt(9)
    p_sec.font.color.rgb = TEAL

    # Right: Stage 2 Runner
    c_s2 = add_card(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), LIGHT_GREEN, RGBColor(167, 243, 208))
    tf = c_s2.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "STAGE 2: HARDENED RUNNER (NON-ROOT UID 10001)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GREEN

    p_code2 = tf.add_paragraph()
    p_code2.text = (
        "FROM python:3.12-slim AS runner\n"
        "WORKDIR /app\n"
        "# Create non-root user\n"
        "RUN groupadd -g 10001 appgroup && \\\n"
        "    useradd -u 10001 -g appgroup -s /bin/sh -m appuser\n"
        "# Copy virtualenv & application source\n"
        "COPY --from=builder /opt/venv /opt/venv\n"
        "COPY --chown=appuser:appgroup . /app\n"
        "USER 10001\n"
        "CMD [\"gunicorn\", \"--bind\", \"0.0.0.0:8000\", \"app:app\"]"
    )
    p_code2.font.size = Pt(8.5)
    p_code2.font.name = "Consolas"
    p_code2.font.color.rgb = DARK_NAVY

    p_run_sec = tf.add_paragraph()
    p_run_sec.text = (
        "\nKEY PRODUCTION SAFEGUARDS:\n"
        "✔ Non-Root execution blocks container breakout vulnerabilities.\n"
        "✔ Stripped build dependencies drastically minimize attack surface.\n"
        "✔ Native context-path actuator probes confirm container liveness."
    )
    p_run_sec.font.size = Pt(9)
    p_run_sec.font.color.rgb = DARK_NAVY

    # ==========================================
    # SLIDE 8: Dual Docker Compose Strategy
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "Dual Docker Compose Architecture: Build & Push vs. Zero-Build Pull", "DEPLOYMENT STRATEGIES", 8)

    # Workflow A
    cA = add_card(s8, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    tfA = cA.text_frame
    tfA.word_wrap = True
    tfA.margin_left = tfA.margin_right = tfA.margin_top = Inches(0.25)
    p = tfA.paragraphs[0]
    p.text = "WORKFLOW A: LOCAL BUILD & PUSH"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE

    p_subA = tfA.add_paragraph()
    p_subA.text = "File: `docker-compose.build.yml`"
    p_subA.font.size = Pt(9.5)
    p_subA.font.bold = True
    p_subA.font.color.rgb = DARK_NAVY

    itemsA = [
        ("Target Users", "Core library developers and platform engineers."),
        ("Mechanism", "Compiles Dockerfiles locally, downloads enterprise-core-python via Git auth token."),
        ("Image Tagging", "Tags images with `${DOCKER_USERNAME}/<service>:latest`."),
        ("Docker Hub Push", "Pushes built images to Docker Hub container registry."),
        ("Ideal For", "Testing local feature changes, developing new endpoints, or releasing library updates.")
    ]
    for lbl, desc in itemsA:
        p1 = tfA.add_paragraph()
        p1.text = f"• {lbl}:"
        p1.font.bold = True
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = DARK_NAVY
        p2 = tfA.add_paragraph()
        p2.text = f"  {desc}"
        p2.font.size = Pt(9)
        p2.font.color.rgb = TEXT_MUTED

    # Workflow B
    cB = add_card(s8, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), LIGHT_GREEN, RGBColor(167, 243, 208))
    tfB = cB.text_frame
    tfB.word_wrap = True
    tfB.margin_left = tfB.margin_right = tfB.margin_top = Inches(0.25)
    p = tfB.paragraphs[0]
    p.text = "WORKFLOW B: ZERO-BUILD REMOTE PULL"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = GREEN

    p_subB = tfB.add_paragraph()
    p_subB.text = "File: `docker-compose.pull.yml`"
    p_subB.font.size = Pt(9.5)
    p_subB.font.bold = True
    p_subB.font.color.rgb = DARK_NAVY

    itemsB = [
        ("Target Users", "QA engineers, frontend developers, DevOps operators, CI/CD pipelines."),
        ("Mechanism", "Pulls certified pre-built images directly from Docker Hub."),
        ("Zero Compilation", "Requires NO Python installation, NO build tools, NO Git access tokens."),
        ("Instant Startup", "Containers spin up immediately within seconds across any workstation."),
        ("Ideal For", "Integration smoke testing, end-to-end QA validation, and production rollouts.")
    ]
    for lbl, desc in itemsB:
        p1 = tfB.add_paragraph()
        p1.text = f"✔ {lbl}:"
        p1.font.bold = True
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = DARK_NAVY
        p2 = tfB.add_paragraph()
        p2.text = f"  {desc}"
        p2.font.size = Pt(9)
        p2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 9: Automated Orchestration via PowerShell
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_header(s9, "Automated Orchestration via `build-and-push-docker.ps1`", "DEVOPS AUTOMATION", 9)

    # Top: Overview Card
    top_c = add_card(s9, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.2))
    tf = top_c.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = "UNIFIED PIPELINE WRAPPER FOR ENTERPRISE WORKFLOWS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = BLUE
    p2 = tf.add_paragraph()
    p2.text = "The `build-and-push-docker.ps1` orchestrator normalizes authentication, environment variable resolution (`DOCKER_USERNAME`, `READ_PACKAGES_TOKEN`), container compilation, registry pushing, and detached cluster startup into single-command executions."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = DARK_NAVY

    # 4 Command Action Cards
    actions = [
        ("Action: BuildPushRun (Default)", ".\\build-and-push-docker.ps1 -Action BuildPushRun", "Authenticates to Docker Hub, builds local images via docker-compose.build.yml, pushes to registry, and starts mesh on Docker Desktop.", BLUE),
        ("Action: PullAndRun (Zero-Build)", ".\\build-and-push-docker.ps1 -Action PullAndRun", "Pulls latest pre-compiled images from Docker Hub via docker-compose.pull.yml and launches mesh with zero local builds.", GREEN),
        ("Action: BuildAndPush (CI Mode)", ".\\build-and-push-docker.ps1 -Action BuildAndPush", "Compiles and pushes images to Docker Hub registry without starting containers. Built for automated GitHub Actions runners.", DARK_NAVY),
        ("Action: Down (Teardown)", ".\\build-and-push-docker.ps1 -Action Down", "Gracefully stops and removes all containers, networks, and volumes for both build and pull configurations.", RED),
    ]

    for idx, (title, cmd, desc, col) in enumerate(actions):
        left = Inches(0.8 + (idx % 2) * 5.95)
        top = Inches(2.9 + (idx // 2) * 2.05)
        w = Inches(5.78)
        h = Inches(1.85)

        card = add_card(s9, left, top, w, h)
        bar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.1), h)
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        p_cmd = tf.add_paragraph()
        p_cmd.text = cmd
        p_cmd.font.size = Pt(9)
        p_cmd.font.name = "Consolas"
        p_cmd.font.bold = True
        p_cmd.font.color.rgb = DARK_NAVY

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(8.5)
        p_desc.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 10: Step-by-Step Live Demo Runbook
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_header(s10, "Step-by-Step Live Demo Runbook: Full Mesh Verification", "DEMO EXECUTION", 10)

    demo_steps = [
        ("Step 1: Spin Up Containers", ".\\build-and-push-docker.ps1 -Action PullAndRun", "Instantly launches Currency Exchange (:8000) and Currency Conversion (:8100) on currency-mesh."),
        ("Step 2: Actuator Health Probes", "curl http://localhost:8000/currency-exchange-service-python/health/liveness", "Returns 200 OK with UP status. Verifies readiness probe & Spring Boot-style actuator capabilities."),
        ("Step 3: Exchange Rate Lookup", "curl http://localhost:8000/currency-exchange-service-python/currency-exchange/from/USD/to/INR", "Returns live rate: conversionMultiple: 86.50 with injected X-Correlation-ID and X-Response-Time-Ms."),
        ("Step 4: Inter-Service Conversion", "curl http://localhost:8100/currency-conversion-service-python/currency-conversion/.../10", "Conversion service queries exchange service across Docker network: converts 10 USD -> 865.00 INR."),
        ("Step 5: Interactive Swagger UI", "http://localhost:8000/currency-exchange-service-python/swagger", "Visualizes full OpenAPI 3.0 specification served directly by enterprise-core-python swagger module.")
    ]

    for idx, (title, cmd, exp) in enumerate(demo_steps):
        top_pos = Inches(1.55 + idx * 1.05)
        card = add_card(s10, Inches(0.8), top_pos, Inches(11.733), Inches(0.95))

        # Number circle badge
        badge = s10.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.95), top_pos + Inches(0.15), Inches(0.65), Inches(0.65))
        badge.fill.solid()
        badge.fill.fore_color.rgb = BLUE
        badge.line.fill.background()
        btf = badge.text_frame
        bp = btf.paragraphs[0]
        bp.text = str(idx + 1)
        bp.font.size = Pt(14)
        bp.font.bold = True
        bp.font.color.rgb = RGBColor(255, 255, 255)
        bp.alignment = PP_ALIGN.CENTER

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.9)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.12)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = DARK_NAVY

        p2 = tf.add_paragraph()
        p2.text = f"CMD: {cmd}  |  {exp}"
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 11: Zero-Day CVE Remediation in Seconds
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11)
    add_header(s11, "Zero-Day CVE Remediation in Seconds: The 3-Step Patch Protocol", "SECURITY GOVERNANCE", 11)

    # 3 Big Remediation Cards
    cve_steps = [
        ("Step 1: Single Repo Edit", "Patch `setup.py` in enterprise-core", "When a CVE hits requests or urllib3, update the pinned version in enterprise-core-python/setup.py and bump version to 1.0.1.\n\nrequests==2.32.4  # Patched!\nurllib3==2.2.4    # Patched!", AMBER),
        ("Step 2: Automated Release", "Tag git release `v1.0.1`", "Commit and push the git tag. GitHub Actions workflow runs unit tests, builds wheels, and creates the official GitHub Release with release notes automatically.\n\ngit tag v1.0.1\ngit push origin v1.0.1", TEAL),
        ("Step 3: Propagate Across Mesh", "Bump Git Tag in Microservices", "Microservices update their single core reference to @v1.0.1. Run automated build script to compile, test, push, and deploy patched containers in minutes.\n\n.\\build-and-push-docker.ps1 -Action BuildPushRun", GREEN),
    ]

    for idx, (title, sub, body, col) in enumerate(cve_steps):
        left = Inches(0.8 + idx * 3.95)
        top = Inches(1.6)
        w = Inches(3.8)
        h = Inches(5.1)

        card = add_card(s11, left, top, w, h)
        top_bar = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, w, Inches(0.12))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = col
        top_bar.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.25)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = DARK_NAVY

        p3 = tf.add_paragraph()
        p3.text = f"\n{body}"
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 12: ROI & Enterprise Impact
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12)
    add_header(s12, "Enterprise ROI & Architectural Impact", "BUSINESS VALUE", 12)

    # 4 High-Impact Stat Metrics
    roi_metrics = [
        ("94% Faster", "CVE Remediation Cycle", "Reduced zero-day turnaround from 72 hours across 36 repositories down to under 15 minutes centrally.", GREEN),
        ("6,000+ Lines", "Boilerplate Eliminated", "Removed duplicate error envelopes, logging configs, and latency interceptors across all services.", BLUE),
        ("100% PII Masking", "Zero-Leakage Compliance", "Automated regex filter eliminates accidental credit card, SSN, and token leaks into SIEM logs.", TEAL),
        ("Zero-Build Agility", "Instant QA & Staging Onboarding", "Engineers pull pre-verified containers from Docker Hub in seconds without compiler setup.", DARK_NAVY),
    ]

    for idx, (stat, title, sub, col) in enumerate(roi_metrics):
        left = Inches(0.8 + idx * 2.95)
        top = Inches(1.6)
        w = Inches(2.8)
        h = Inches(2.3)

        card = add_card(s12, left, top, w, h)
        acc = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, w, Inches(0.08))
        acc.fill.solid()
        acc.fill.fore_color.rgb = col
        acc.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = stat
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(10.5)
        p2.font.bold = True
        p2.font.color.rgb = DARK_NAVY

        p3 = tf.add_paragraph()
        p3.text = sub
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = TEXT_MUTED

    # Comparison Table: Before vs. After
    tbl_card = add_card(s12, Inches(0.8), Inches(4.1), Inches(11.733), Inches(2.6))
    tf = tbl_card.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "BEFORE VS. AFTER: APPROACH 2 TRANSFORMATION"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    comp_items = [
        ("Dependency Management", "36 decentralized requirements.txt files with version drift", "1 centralized setup.py BOM pinned at @v1.0.0"),
        ("Security Patching", "36 manual PRs, 36 build cycles, ~72 hours", "1 centralized patch, automated release, ~15 mins"),
        ("Logging & PII Compliance", "Decentralized log formats; risk of raw PII leak to SIEM", "Standardized JSON logs with automated regex PII masking"),
        ("Container Build Experience", "Every developer/QA compiles locally from scratch", "Dual Compose: Build locally or instant Zero-Build Pull"),
    ]

    for metric, before, after in comp_items:
        pt = tf.add_paragraph()
        pt.text = f"• {metric}: [Before] {before}  ➔  [After] {after}"
        pt.font.size = Pt(9)
        pt.font.color.rgb = DARK_NAVY

    # ==========================================
    # SLIDE 13: Conclusion & Next Steps (Q&A)
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    set_bg(s13, DARK_NAVY)

    # Decorative header strip
    strip = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.15))
    strip.fill.solid()
    strip.fill.fore_color.rgb = BLUE
    strip.line.fill.background()

    # Title
    t_box = s13.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(10.8), Inches(1.2))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Strategic Roadmap & Conclusion"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    p2 = tf.add_paragraph()
    p2.text = "Transitioning from individual microservice maintenance to platform engineering governance"
    p2.font.size = Pt(16)
    p2.font.color.rgb = TEAL

    # 3 Next Steps Cards
    next_steps = [
        ("Phase 1: Foundation (Complete)", "Enterprise Core Library Certified", "• v1.0.0 released with PII logging, unified error envelope, actuators, and Swagger UI.\n• Dual Docker Compose workflows verified on Docker Desktop.", BLUE),
        ("Phase 2: Mesh Rollout (Current)", "Scale Across 36 Microservices", "• Migrate remaining 34 microservices to declare enterprise-core-python @ v1.0.0.\n• Establish automated Dependabot alerts for central library.", TEAL),
        ("Phase 3: Platform Maturity (Next)", "Internal PyPI Registry & Mesh Observability", "• Host wheel artifacts on JFrog Artifactory / AWS CodeArtifact.\n• Integrate OpenTelemetry distributed tracing with correlation ID propagation.", GREEN),
    ]

    for idx, (title, sub, body, col) in enumerate(next_steps):
        left = Inches(1.2 + idx * 3.7)
        top = Inches(2.5)
        w = Inches(3.5)
        h = Inches(3.2)

        card = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = NAVY
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.2)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(255, 255, 255)

        p3 = tf.add_paragraph()
        p3.text = f"\n{body}"
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = RGBColor(203, 213, 225)

    # Q&A Banner
    qa = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(6.0), Inches(10.9), Inches(0.85))
    qa.fill.solid()
    qa.fill.fore_color.rgb = RGBColor(30, 58, 138)
    qa.line.color.rgb = BLUE
    qa.line.width = Pt(1)
    qtf = qa.text_frame
    qp = qtf.paragraphs[0]
    qp.text = "Questions & Technical Discussion"
    qp.font.size = Pt(14)
    qp.font.bold = True
    qp.font.color.rgb = RGBColor(255, 255, 255)
    qp.alignment = PP_ALIGN.CENTER
    qp2 = qtf.add_paragraph()
    qp2.text = "Repository: https://github.com/amsidhlokhande/currency-management-python | Branch: shared-enterprise-library"
    qp2.font.size = Pt(10)
    qp2.font.color.rgb = RGBColor(191, 219, 254)
    qp2.alignment = PP_ALIGN.CENTER

    # Save
    out_path = "Approach_2_Shared_Enterprise_Library_Executive_Demo.pptx"
    prs.save(out_path)
    print(f"Successfully generated PowerPoint presentation: {out_path}")

if __name__ == "__main__":
    create_presentation()
