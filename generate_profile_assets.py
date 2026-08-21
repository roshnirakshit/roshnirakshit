import os
import math
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

def create_dot_leaders(start_x, end_x, y, step=16):
    d_parts = []
    curr = start_x
    while curr <= end_x:
        d_parts.append(f"M{curr},{y}h2v2h-2z")
        curr += step
    return "".join(d_parts)

def build_profile_svg(is_dark=True, avatar_path="roshni_avatar.png"):
    # Color palette
    if is_dark:
        bg_bar = "#0C1322"
        bg_body = "#0A101F"
        border_col = "#223052"
        sep_col = "#1E2C4C"
        title_col = "#8FA3C8"
        visual_map_col = "#A78BFA"
        box_bg = "#0D1428"
        box_stroke = "#A78BFA"
        box_stroke_op = "0.35"
        sys_info_col = "#22D3EE"
        live_bg = "#DC2626"
        live_bg_op = "0.2"
        live_stroke = "#F87171"
        live_text = "#F87171"
        pill_grad_start = "#A78BFA"
        pill_grad_end = "#22D3EE"
        handle_text = "#0A101F"
        label_col = "#7E8FB5"
        val_col = "#D3DDF2"
        dot_col = "#22D3EE"
        dot_op = "0.35"
        subhead_col = "#55648C"
        prompt_col = "#44537A"
        cursor_col = "#22D3EE"
        particle_col = "#A78BFA"
    else:
        bg_bar = "#E6EBF6"
        bg_body = "#EEF2FA"
        border_col = "#C4CFE4"
        sep_col = "#D7DFF0"
        title_col = "#4A5B80"
        visual_map_col = "#4C1D95"
        box_bg = "#F7F9FE"
        box_stroke = "#4C1D95"
        box_stroke_op = "0.30"
        sys_info_col = "#0E7490"
        live_bg = "#DC2626"
        live_bg_op = "0.14"
        live_stroke = "#DC2626"
        live_text = "#B91C1C"
        pill_grad_start = "#7C3AED"
        pill_grad_end = "#0891B2"
        handle_text = "#FFFFFF"
        label_col = "#5A6B8E"
        val_col = "#24324F"
        dot_col = "#0891B2"
        dot_op = "0.40"
        subhead_col = "#4A5B80"
        prompt_col = "#7182A4"
        cursor_col = "#0E7490"
        particle_col = "#6D28D9"

    # Profile Data configuration
    handle = "@roshnirakshit"
    rows = [
        ("Subject", "Roshni Rakshit", 124),
        ("Role", "AI Engineer & Full Stack Developer", 147),
        ("Origin", "Chennai, India", 170),
        ("Education", "B.Tech", 193),
        ("Status", "building + learning + shipping", 216),
        ("ToolChain", "Python · PyTorch · TS · FastAPI · React · Next · Docker", 239),
        ("-- CORE --", "", 265),
        ("Core.Lang", "Python · TypeScript · JavaScript · C++", 285),
        ("Core.Frontend", "React · Next.js · Tailwind CSS", 308),
        ("Core.Backend", "FastAPI · Node.js · Express", 331),
        ("Core.AI/ML", "PyTorch · Transformers · LangChain", 354),
        ("Core.Database", "PostgreSQL · MongoDB · Supabase", 377),
        ("Core.Infra", "Docker · Vercel · GitHub Actions", 400),
        ("-- GRID --", "", 426),
        ("Grid.Mail", "roshnirakshit@gmail.com", 446),
        ("Grid.Portfolio", "roshnirakshit.dev", 469),
        ("Grid.LinkedIn", "linkedin.com/in/roshnirakshit", 492),
        ("Grid.GitHub", "github.com/roshnirakshit", 515),
    ]

    # Generate halftone matrix particles from avatar
    img = Image.open(avatar_path).convert('L')
    target_w, target_h = 300, 340
    
    # Aspect crop
    target_ratio = target_w / target_h
    orig_w, orig_h = img.size
    orig_ratio = orig_w / orig_h
    if orig_ratio > target_ratio:
        new_w = int(orig_h * target_ratio)
        left = (orig_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, orig_h))
    else:
        new_h = int(orig_w / target_ratio)
        top = (orig_h - new_h) // 2
        img = img.crop((0, top, orig_w, top + new_h))
        
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.45)
    
    # Atkinson dithering
    arr = np.array(img, dtype=float)
    dither_arr = arr.copy()
    h_len, w_len = dither_arr.shape
    dots = []
    
    for y in range(h_len):
        for x in range(w_len):
            old_val = dither_arr[y, x]
            new_val = 255 if old_val > 120 else 0
            dither_arr[y, x] = new_val
            err = (old_val - new_val) / 8.0
            
            # Bright pixels on dark mode, dark pixels on light mode
            if is_dark:
                if new_val == 255:
                    dots.append((x, y))
            else:
                if new_val == 0:
                    dots.append((x, y))
            
            if x + 1 < w_len:
                dither_arr[y, x + 1] += err
            if x + 2 < w_len:
                dither_arr[y, x + 2] += err
            if y + 1 < h_len:
                if x - 1 >= 0:
                    dither_arr[y + 1, x - 1] += err
                dither_arr[y + 1, x] += err
                if x + 1 < w_len:
                    dither_arr[y + 1, x + 1] += err
            if y + 2 < h_len:
                dither_arr[y + 2, x] += err

    # Subsample or filter dots if needed so SVG is crisp and performant (~18,000 dots)
    random.seed(42)
    if len(dots) > 18000:
        step = len(dots) / 18000.0
        sampled_dots = [dots[int(i * step)] for i in range(18000)]
    else:
        sampled_dots = dots

    # Split into 60 staggered groups for progressive fade-in animation
    num_groups = 60
    groups = [[] for _ in range(num_groups)]
    for i, pt in enumerate(sampled_dots):
        g_idx = i % num_groups
        groups[g_idx].append(pt)

    intro_svg_parts = []
    for g_idx in range(num_groups):
        pts = groups[g_idx]
        d_str = "".join([f"M{x},{y}h1v1h-1z" for (x, y) in pts])
        begin_time = f"{g_idx * 0.035:.2f}s"
        intro_svg_parts.append(
            f'<g opacity="0"><path d="{d_str}"/><animate attributeName="opacity" begin="{begin_time}" dur="0.9s" from="0" to="1" fill="freeze"/></g>'
        )
    intro_svg = "".join(intro_svg_parts)

    # Build Code Bracket `</>` target shape morphing particles
    code_bracket_dots = []
    # Left bracket `<`
    for i in range(40):
        x = int(100 - i * 1.25)
        y = int(110 + i * 1.5)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                code_bracket_dots.append((x + dx, y + dy))
        x2 = int(50 + i * 1.25)
        y2 = int(170 + i * 1.5)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                code_bracket_dots.append((x2 + dx, y2 + dy))
                
    # Slash `/`
    for i in range(80):
        x = int(175 - i * 0.625)
        y = int(95 + i * 1.875)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                code_bracket_dots.append((x + dx, y + dy))

    # Right bracket `>`
    for i in range(40):
        x = int(200 + i * 1.25)
        y = int(110 + i * 1.5)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                code_bracket_dots.append((x + dx, y + dy))
        x2 = int(250 - i * 1.25)
        y2 = int(170 + i * 1.5)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                code_bracket_dots.append((x2 + dx, y2 + dy))

    # Build morphing particles (travellers) that animate between portrait and </> code brackets!
    num_travellers = min(900, len(sampled_dots), len(code_bracket_dots))
    traveller_orig = random.sample(sampled_dots, num_travellers)
    traveller_target = random.sample(code_bracket_dots, num_travellers)
    
    travellers_svg_parts = []
    for i in range(num_travellers):
        ox, oy = traveller_orig[i]
        tx, ty = traveller_target[i]
        dx = tx - ox
        dy = ty - oy
        stagger = (i % 20) * 0.05
        travellers_svg_parts.append(
            f'<path d="M{ox},{oy}h1v1h-1z">'
            f'<animateTransform attributeName="transform" type="translate" begin="{3.5 + stagger:.2f}s" dur="16s" repeatCount="indefinite" '
            f'keyTimes="0.0;0.15;0.22;0.50;0.58;0.90;1.0" values="0 0;0 0;{dx} {dy};{dx} {dy};0 0;0 0;0 0"/>'
            f'</path>'
        )
    travellers_svg = "".join(travellers_svg_parts)

    # Right side text lines and dot leaders
    right_side_elements = []
    for row in rows:
        label, val, y = row
        if val == "":
            safe_label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            right_side_elements.append(
                f'<text x="520" y="{y}" font-family="Consolas,\'Cascadia Mono\',Menlo,\'DejaVu Sans Mono\',monospace" font-size="12" fill="{subhead_col}" letter-spacing="3">{safe_label}</text>'
            )
        else:
            # Monospace char width is ~8.5px for font-size 14 in Consolas
            label_len_px = len(label) * 8.5
            val_len_px = len(val) * 8.5
            dot_start_x = int(520 + label_len_px + 14)
            dot_end_x = int(1140 - val_len_px - 14)
            dot_path = create_dot_leaders(dot_start_x, dot_end_x, y - 5, step=16)
            
            safe_label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            safe_val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            right_side_elements.append(
                f'<text x="520.0" y="{y}" font-family="Consolas,\'Cascadia Mono\',Menlo,\'DejaVu Sans Mono\',monospace" font-size="14" fill="{label_col}">{safe_label}</text>'
            )
            if dot_path and dot_end_x > dot_start_x:
                right_side_elements.append(
                    f'<g shape-rendering="crispEdges" fill="{dot_col}" fill-opacity="{dot_op}"><path d="{dot_path}"/></g>'
                )
            right_side_elements.append(
                f'<text x="1140.0" y="{y}" text-anchor="end" font-family="Consolas,\'Cascadia Mono\',Menlo,\'DejaVu Sans Mono\',monospace" font-size="14" fill="{val_col}">{safe_val}</text>'
            )

    right_content = "\n".join(right_side_elements)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" role="img" aria-label="Roshni Rakshit - AI Engineer &amp; Full Stack Developer - animated profile banner">
<title>Roshni Rakshit — profile.sh --live</title>
<desc>Animated terminal-style profile banner: matrix portrait, tech stack, morphing particles.</desc>
<defs>
  <linearGradient id="pillGrad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{pill_grad_start}"/>
    <stop offset="1" stop-color="{pill_grad_end}"/>
  </linearGradient>
</defs>

<!-- Window Frame -->
<rect x="8" y="8" width="1164" height="34" rx="10" fill="{bg_bar}"/>
<rect x="8" y="42" width="1164" height="560" fill="{bg_body}"/>
<rect x="8" y="8" width="1164" height="594" rx="10" fill="none" stroke="{border_col}" stroke-width="1.5"/>
<rect x="8" y="42" width="1164" height="1" fill="{sep_col}"/>

<!-- Window Traffic Lights -->
<circle cx="24" cy="25" r="4.5" fill="#FF5F57"/>
<circle cx="42" cy="25" r="4.5" fill="#FEBC2E"/>
<circle cx="60" cy="25" r="4.5" fill="#28C840"/>

<!-- Window Title -->
<text x="590" y="28.5" text-anchor="middle" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="{title_col}">profile.sh --live</text>

<!-- Visual Map Header -->
<text x="40" y="58" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="{visual_map_col}" letter-spacing="3">VISUAL.MAP</text>

<!-- Visual Map Box -->
<rect x="40" y="70" width="450" height="510" rx="6" fill="{box_bg}" stroke="{box_stroke}" stroke-opacity="{box_stroke_op}"/>

<!-- Halftone Portrait Matrix -->
<g id="intro" transform="translate(40 70) scale(1.5)" shape-rendering="crispEdges" fill="{particle_col}">
{intro_svg}
</g>

<!-- Particle Morphing Layer -->
<g id="travellers" transform="translate(40 70) scale(1.5)" shape-rendering="crispEdges" fill="{particle_col}">
{travellers_svg}
</g>

<!-- System Info Header & Live Tag -->
<text x="520" y="58" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" font-weight="700" fill="{sys_info_col}" letter-spacing="3">SYSTEM.INFO</text>

<!-- Live Pulse Badge -->
<rect x="896" y="45" width="80" height="26" rx="13" fill="{live_bg}" fill-opacity="{live_bg_op}" stroke="{live_stroke}" stroke-opacity="0.6" stroke-width="1"/>
<circle cx="912" cy="58" r="3.5" fill="{live_text}">
  <animate attributeName="opacity" dur="1.4s" repeatCount="indefinite" values="1;0.3;1" keyTimes="0;0.5;1"/>
</circle>
<text x="923" y="62" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="11" font-weight="700" fill="{live_text}" letter-spacing="1">LIVE</text>

<!-- Handle Pill -->
<rect x="988" y="44" width="152" height="28" rx="14" fill="url(#pillGrad)"/>
<text x="1064" y="62.5" text-anchor="middle" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13.5" font-weight="700" fill="{handle_text}">{handle}</text>

<!-- Profile Rows -->
{right_content}

<!-- Terminal Prompt & Cursor -->
<text x="520" y="578" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="{prompt_col}">$ ./profile.sh --live</text>
<rect x="702" y="564" width="9" height="16" fill="{cursor_col}">
  <animate attributeName="opacity" dur="1.1s" repeatCount="indefinite" values="1;1;0;0;1" keyTimes="0;0.05;0.5;0.55;1"/>
</rect>

</svg>'''
    return svg_content


def build_connect_svg():
    links = [
        ("LINKEDIN", "linkedin.com/in/roshnirakshit", 124),
        ("GITHUB", "github.com/roshnirakshit", 156),
        ("EMAIL", "roshnirakshit@gmail.com", 188),
        ("PORTFOLIO", "roshnirakshit.dev", 220),
        ("X / TWITTER", "x.com/roshnirakshit", 252),
        ("DISCORD", "discord.com/users/roshnirakshit", 284),
    ]
    
    rows_svg = []
    for label, val, y in links:
        lbl_len = round(len(label) * 8.4, 1)
        val_len = round(len(val) * 8.4, 1)
        dot_start = int(40 + lbl_len + 16)
        dot_end = int(960 - val_len - 16)
        dots = create_dot_leaders(dot_start, dot_end, y - 5, step=16)
        
        rows_svg.append(
            f'<text x="40" y="{y}" font-family="Consolas,\'Cascadia Mono\',Menlo,\'DejaVu Sans Mono\',monospace" font-size="14" fill="#A78BFA" textLength="{lbl_len}" lengthAdjust="spacingAndGlyphs">{label}</text>'
        )
        if dots:
            rows_svg.append(
                f'<g shape-rendering="crispEdges" fill="#22D3EE" fill-opacity="0.35"><path d="{dots}"/></g>'
            )
        rows_svg.append(
            f'<text x="960" y="{y}" text-anchor="end" font-family="Consolas,\'Cascadia Mono\',Menlo,\'DejaVu Sans Mono\',monospace" font-size="14" fill="#D3DDF2" textLength="{val_len}" lengthAdjust="spacingAndGlyphs">{val}</text>'
        )

    rows_str = "\n".join(rows_svg)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="380" viewBox="0 0 1000 380" role="img">
<title>connect.sh --links</title>
<rect x="8" y="8" width="984" height="34" rx="10" fill="#0C1322"/>
<rect x="8" y="42" width="984" height="330" fill="#0A101F"/>
<rect x="8" y="8" width="984" height="364" rx="10" fill="none" stroke="#223052" stroke-width="1.5"/>
<rect x="8" y="42" width="984" height="1" fill="#1E2C4C"/>
<circle cx="24" cy="25" r="4.5" fill="#FF5F57"/>
<circle cx="42" cy="25" r="4.5" fill="#FEBC2E"/>
<circle cx="60" cy="25" r="4.5" fill="#28C840"/>
<text x="500.0" y="28.5" text-anchor="middle" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#8FA3C8">connect.sh --links</text>
<text x="40" y="78" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#44537A">$ ./connect.sh --links</text>

{rows_str}

<text x="40" y="348" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#44537A">$ ./connect.sh --links</text>
<rect x="222" y="334" width="9" height="16" fill="#22D3EE">
  <animate attributeName="opacity" dur="1.1s" repeatCount="indefinite" values="1;1;0;0;1" keyTimes="0;0.05;0.5;0.55;1"/>
</rect>
</svg>'''


def build_stack_svg():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420" role="img">
<title>stack.sh --core</title>
<rect x="8" y="8" width="984" height="34" rx="10" fill="#0C1322"/>
<rect x="8" y="42" width="984" height="370" fill="#0A101F"/>
<rect x="8" y="8" width="984" height="404" rx="10" fill="none" stroke="#223052" stroke-width="1.5"/>
<rect x="8" y="42" width="984" height="1" fill="#1E2C4C"/>
<circle cx="24" cy="25" r="4.5" fill="#FF5F57"/>
<circle cx="42" cy="25" r="4.5" fill="#FEBC2E"/>
<circle cx="60" cy="25" r="4.5" fill="#28C840"/>
<text x="500.0" y="28.5" text-anchor="middle" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#8FA3C8">stack.sh --core</text>
<text x="40" y="78" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#44537A">$ ./stack.sh --core</text>

<text x="40" y="116" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#55648C" letter-spacing="3">-- LANGUAGES --</text>
<text x="40" y="144" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#D3DDF2"><tspan>Python</tspan><tspan fill="#55648C"> · </tspan><tspan>TypeScript</tspan><tspan fill="#55648C"> · </tspan><tspan>JavaScript</tspan><tspan fill="#55648C"> · </tspan><tspan>C++</tspan><tspan fill="#55648C"> · </tspan><tspan>SQL</tspan><tspan fill="#55648C"> · </tspan><tspan>HTML5 / CSS3</tspan></text>

<text x="40" y="178" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#55648C" letter-spacing="3">-- AI &amp; MACHINE LEARNING --</text>
<text x="40" y="206" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#D3DDF2"><tspan>PyTorch</tspan><tspan fill="#55648C"> · </tspan><tspan>Transformers</tspan><tspan fill="#55648C"> · </tspan><tspan>LangChain</tspan><tspan fill="#55648C"> · </tspan><tspan>FastMCP</tspan><tspan fill="#55648C"> · </tspan><tspan>Ollama</tspan><tspan fill="#55648C"> · </tspan><tspan>OpenCV</tspan><tspan fill="#55648C"> · </tspan><tspan>Hugging Face</tspan></text>

<text x="40" y="240" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#55648C" letter-spacing="3">-- FRONTEND &amp; BACKEND --</text>
<text x="40" y="268" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#D3DDF2"><tspan>FastAPI</tspan><tspan fill="#55648C"> · </tspan><tspan>React</tspan><tspan fill="#55648C"> · </tspan><tspan>Next.js</tspan><tspan fill="#55648C"> · </tspan><tspan>Node.js</tspan><tspan fill="#55648C"> · </tspan><tspan>Express</tspan><tspan fill="#55648C"> · </tspan><tspan>Tailwind CSS</tspan><tspan fill="#55648C"> · </tspan><tspan>Flask</tspan></text>

<text x="40" y="302" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#55648C" letter-spacing="3">-- DATABASES &amp; CLOUD --</text>
<text x="40" y="330" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#D3DDF2"><tspan>PostgreSQL</tspan><tspan fill="#55648C"> · </tspan><tspan>MongoDB</tspan><tspan fill="#55648C"> · </tspan><tspan>Redis</tspan><tspan fill="#55648C"> · </tspan><tspan>Supabase</tspan><tspan fill="#55648C"> · </tspan><tspan>MySQL</tspan><tspan fill="#55648C"> · </tspan><tspan>Vector DBs (Chroma/Qdrant)</tspan></text>

<text x="40" y="364" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#55648C" letter-spacing="3">-- TOOLS &amp; DEVOPS --</text>
<text x="40" y="392" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#D3DDF2"><tspan>Git</tspan><tspan fill="#55648C"> · </tspan><tspan>Docker</tspan><tspan fill="#55648C"> · </tspan><tspan>GitHub Actions</tspan><tspan fill="#55648C"> · </tspan><tspan>Vercel</tspan><tspan fill="#55648C"> · </tspan><tspan>Postman</tspan><tspan fill="#55648C"> · </tspan><tspan>Linux / Bash</tspan></text>
</svg>'''


def build_projects_svg():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="440" viewBox="0 0 1000 440" role="img">
<title>projects.sh --featured</title>
<rect x="8" y="8" width="984" height="34" rx="10" fill="#0C1322"/>
<rect x="8" y="42" width="984" height="390" fill="#0A101F"/>
<rect x="8" y="8" width="984" height="424" rx="10" fill="none" stroke="#223052" stroke-width="1.5"/>
<rect x="8" y="42" width="984" height="1" fill="#1E2C4C"/>
<circle cx="24" cy="25" r="4.5" fill="#FF5F57"/>
<circle cx="42" cy="25" r="4.5" fill="#FEBC2E"/>
<circle cx="60" cy="25" r="4.5" fill="#28C840"/>
<text x="500.0" y="28.5" text-anchor="middle" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#8FA3C8">projects.sh --featured</text>
<text x="40" y="78" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#44537A">$ ./projects.sh --featured</text>

<text x="40" y="118" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#A78BFA"><tspan fill="#22D3EE">[1]</tspan> <tspan font-weight="700">discuss-ai-models</tspan></text>
<text x="960" y="118" text-anchor="end" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#7E8FB5">ai model evaluation &amp; benchmark platform</text>
<text x="60" y="142" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#D3DDF2"><tspan>python</tspan><tspan fill="#55648C"> · </tspan><tspan>fastapi</tspan><tspan fill="#55648C"> · </tspan><tspan>pytorch</tspan><tspan fill="#55648C"> · </tspan><tspan>react</tspan><tspan fill="#55648C"> · </tspan><tspan>transformers</tspan></text>

<text x="40" y="180" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#A78BFA"><tspan fill="#22D3EE">[2]</tspan> <tspan font-weight="700">FastMCP-Agentic-Workflows</tspan></text>
<text x="960" y="180" text-anchor="end" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#7E8FB5">autonomous ai agents with model context protocol</text>
<text x="60" y="204" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#D3DDF2"><tspan>python</tspan><tspan fill="#55648C"> · </tspan><tspan>mcp</tspan><tspan fill="#55648C"> · </tspan><tspan>langchain</tspan><tspan fill="#55648C"> · </tspan><tspan>ollama</tspan><tspan fill="#55648C"> · </tspan><tspan>fastapi</tspan></text>

<text x="40" y="242" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#A78BFA"><tspan fill="#22D3EE">[3]</tspan> <tspan font-weight="700">NeuralVision-Studio</tspan></text>
<text x="960" y="242" text-anchor="end" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#7E8FB5">real-time vision &amp; generative neural pipeline</text>
<text x="60" y="266" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#D3DDF2"><tspan>pytorch</tspan><tspan fill="#55648C"> · </tspan><tspan>opencv</tspan><tspan fill="#55648C"> · </tspan><tspan>next.js</tspan><tspan fill="#55648C"> · </tspan><tspan>typescript</tspan></text>

<text x="40" y="304" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#A78BFA"><tspan fill="#22D3EE">[4]</tspan> <tspan font-weight="700">SmartDoc-RAG</tspan></text>
<text x="960" y="304" text-anchor="end" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#7E8FB5">intelligent semantic retrieval &amp; vector search</text>
<text x="60" y="328" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#D3DDF2"><tspan>python</tspan><tspan fill="#55648C"> · </tspan><tspan>langchain</tspan><tspan fill="#55648C"> · </tspan><tspan>postgresql</tspan><tspan fill="#55648C"> · </tspan><tspan>pgvector</tspan></text>

<text x="40" y="366" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="14" fill="#A78BFA"><tspan fill="#22D3EE">[5]</tspan> <tspan font-weight="700">CloudPulse-DevOps</tspan></text>
<text x="960" y="366" text-anchor="end" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#7E8FB5">multi-cloud monitoring &amp; automated ci/cd orchestrator</text>
<text x="60" y="390" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="12" fill="#D3DDF2"><tspan>docker</tspan><tspan fill="#55648C"> · </tspan><tspan>github-actions</tspan><tspan fill="#55648C"> · </tspan><tspan>supabase</tspan><tspan fill="#55648C"> · </tspan><tspan>react</tspan></text>

<text x="40" y="420" font-family="Consolas,'Cascadia Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="13" fill="#44537A">$ ./projects.sh --featured</text>
<rect x="238" y="406" width="9" height="16" fill="#22D3EE">
  <animate attributeName="opacity" dur="1.1s" repeatCount="indefinite" values="1;1;0;0;1" keyTimes="0;0.05;0.5;0.55;1"/>
</rect>
</svg>'''


def build_readme_md():
    return '''<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/roshnirakshit/roshnirakshit/main/dark.svg">
    <img src="https://raw.githubusercontent.com/roshnirakshit/roshnirakshit/main/light.svg" width="100%" alt="Roshni Rakshit — AI Engineer & Full Stack Developer — animated profile banner">
  </picture>
</p>

# Hi there! 👋

I'm **Roshni Rakshit** — an **AI Engineer & Full Stack Developer** from **Chennai, India**, crafting intelligent AI systems and high-performance web applications. Currently building, learning, and shipping. ✨

<p align="center">
  <a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com/?lines=AI+Engineer;Full+Stack+Developer;Agentic+AI+Researcher;FastMCP+Workflows;Lifelong+Learner&font=Fira+Code&weight=500&size=22&duration=2800&pause=900&color=22D3EE&center=true&vCenter=true&width=550&height=55" alt="Typing SVG: AI Engineer, Full Stack Developer, Agentic AI Researcher, FastMCP Workflows, Lifelong Learner"></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/roshnirakshit/roshnirakshit/main/connect.svg" width="100%" alt="connect.sh — links">
</p>

<div align="center"><h3>Currently Building</h3></div>

### [discuss-ai-models](https://github.com/roshnirakshit/discuss-ai-models)
*AI Model Evaluation & Benchmark Comparison Platform — an intelligent, full-stack application for testing, analyzing, and benchmarking modern LLMs and generative AI architectures.*

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white) ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![TypeScript](https://img.shields.io/badge/typescript-%23007acc.svg?style=for-the-badge&logo=typescript&logoColor=white)

<div align="center">
  <img src="https://raw.githubusercontent.com/roshnirakshit/roshnirakshit/main/stack.svg" width="100%" alt="Tech stack">
</div>

<div align="center"><h3>Featured Projects</h3></div>

<div align="center">
  <img src="https://raw.githubusercontent.com/roshnirakshit/roshnirakshit/main/projects.svg" width="100%" alt="Featured projects">
</div>

<div align="center"><h3>GitHub Stats</h3></div>
<div align="center">
  <img src="https://streak-stats.demolab.com/?user=roshnirakshit&background=0A101F&border=223052&ring=22D3EE&fire=10B981&currStreakNum=A78BFA&currStreakLabel=22D3EE&sideNums=22D3EE&sideLabels=C9D4E8&dates=8A97B8" width="85%" alt="GitHub Streak"><br>
  <img src="https://github-readme-stats.shion.dev/api?username=roshnirakshit&show_icons=true&hide_rank=true&include_all_commits=true&bg_color=0A101F&title_color=A78BFA&text_color=C9D4E8&icon_color=22D3EE&border_color=223052" width="42%" alt="GitHub Stats">
  <img src="https://github-readme-stats.shion.dev/api/top-langs/?username=roshnirakshit&layout=compact&langs_count=8&bg_color=0A101F&title_color=A78BFA&text_color=C9D4E8&border_color=223052" width="42%" alt="Top Languages">
  <br>
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=roshnirakshit&bg_color=0A101F&color=A78BFA&line=22D3EE&point=10B981&area_color=1E2C4C&title_color=22D3EE&hide_border=true&area=true" width="85%" alt="GitHub activity graph">
</div>

<div align="center"><h3>GitHub Trophies</h3></div>

<div align="center">
  <img src="https://raw.githubusercontent.com/roshnirakshit/roshnirakshit/trophy-output/trophy.svg" height="150" alt="trophy graph"  />
</div>

<div align="center"><h3>GitHub Snake</h3></div>

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/roshnirakshit/roshnirakshit/snake-output/github-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/roshnirakshit/roshnirakshit/snake-output/github-snake.svg">
  <img alt="GitHub contribution snake" src="https://raw.githubusercontent.com/roshnirakshit/roshnirakshit/snake-output/github-snake.svg">
</picture>
</p>

<div align="center"><h3>Random Dev Quote</h3></div>
<p align="center">
  <img src="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=radical" alt="Random Dev Quote">
</p>
'''


def main():
    print("Generating dark.svg...")
    dark_svg = build_profile_svg(is_dark=True, avatar_path="roshni_avatar.png")
    with open("dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"Saved dark.svg ({len(dark_svg)} bytes)")

    print("Generating light.svg...")
    light_svg = build_profile_svg(is_dark=False, avatar_path="roshni_avatar.png")
    with open("light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"Saved light.svg ({len(light_svg)} bytes)")

    print("Generating connect.svg...")
    connect_svg = build_connect_svg()
    with open("connect.svg", "w", encoding="utf-8") as f:
        f.write(connect_svg)
    print(f"Saved connect.svg ({len(connect_svg)} bytes)")

    print("Generating stack.svg...")
    stack_svg = build_stack_svg()
    with open("stack.svg", "w", encoding="utf-8") as f:
        f.write(stack_svg)
    print(f"Saved stack.svg ({len(stack_svg)} bytes)")

    print("Generating projects.svg...")
    projects_svg = build_projects_svg()
    with open("projects.svg", "w", encoding="utf-8") as f:
        f.write(projects_svg)
    print(f"Saved projects.svg ({len(projects_svg)} bytes)")

    print("Generating README.md...")
    readme_md = build_readme_md()
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_md)
    print(f"Saved README.md ({len(readme_md)} bytes)")

    # Workflow files
    os.makedirs(".github/workflows", exist_ok=True)
    snake_yml = '''name: Generate contribution snake

on:
  schedule: # execute every 12 hours
    - cron: "0 */12 * * *"

  workflow_dispatch:

  push:
    branches:
      - main

jobs:
  generate:
    permissions:
      contents: write
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Generate snake SVGs (light + dark)
        uses: Platane/snk/svg-only@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/github-snake.svg?color_snake=0891B2&color_dots=#EBEDF0,#C9D4E8,#A78BFA,#22D3EE,#10B981
            dist/github-snake-dark.svg?color_snake=A78BFA&color_dots=#2d3343,#1E2C4C,#0891B2,#22D3EE,#10B981

      - name: Push snake SVGs to the output branch
        uses: crazy-max/ghaction-github-pages@v3.1.0
        with:
          target_branch: snake-output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''
    with open(".github/workflows/snake.yml", "w", encoding="utf-8") as f:
        f.write(snake_yml)
    print("Saved .github/workflows/snake.yml")

    trophy_yml = '''permissions:
  contents: write
  actions: read

name: Generate trophy card

on:
  schedule: # execute every 12 hours
    - cron: "0 */12 * * *"

  workflow_dispatch:

  push:
    branches:
      - main

jobs:
  generate:
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: generate trophy.svg
        uses: Erik-Donath/github-profile-trophy@feature/generate-svg
        with:
          username: ${{ github.repository_owner }}
          file: dist/trophy.svg
          token: ${{ secrets.TROPHY_PAT }}
          theme: algolia
          max-rows: 1
          margin-width: 8
          margin-height: 8
          no-background: false
          no-frame: false

      - name: push trophy.svg to the output branch
        uses: crazy-max/ghaction-github-pages@v3.1.0
        with:
          target_branch: trophy-output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''
    with open(".github/workflows/trophy.yml", "w", encoding="utf-8") as f:
        f.write(trophy_yml)
    print("Saved .github/workflows/trophy.yml")


if __name__ == "__main__":
    main()
