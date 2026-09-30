"""Generate GitHub-safe profile images, README markup and local review proofs.

Inputs: original morph assets, the built hero, pinned local icons, verified facts.
Nothing is uploaded or committed. PNGs are native README content; HTML is review only.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFilter
from collections import Counter
import argparse, json, shutil, re, math, html
from build_hero import font, CYAN, AQUA, WHITE, MUTED

BG, LINE = '#050e19', '#183441'
PROJECTS = [
 dict(id='hcp',title='AI-Powered HCP CRM',tag='FEATURED / INTELLIGENT APPLICATIONS',
      summary='Turn meeting notes into structured healthcare interactions.',
      highlights=['Natural-language entity extraction', 'Human review before saving'],
      tech='React · FastAPI · LangGraph · Express · SQLite',repo='ai-hcp-crm-',feature=True),
 dict(id='ids',title='AI-Powered Intrusion Detection',tag='RESEARCH / CYBERSECURITY',
      summary='Network-threat classification with a hybrid deep-learning model.',
      highlights=['CNN + LSTM', 'SHAP / LIME explanations'],
      tech='Python · TensorFlow · scikit-learn',repo='AI-Powered-Intrusion-Detection-System-Using-Hybrid-Deep-Learning-Model'),
 dict(id='blood',title='Blood Cell Cancer Detection',tag='COMPUTER VISION',
      summary='A research application for microscopic blood-cell classification.',
      highlights=['CNN inference', 'Image upload and preprocessing'],
      tech='Python · TensorFlow · OpenCV · Flask',repo='Blood-cell-image-cancer-detection'),
 dict(id='asj',title='ASJ Pipe Scaffolding',tag='REAL-WORLD DEVELOPMENT',
      summary='A responsive business website for a Chennai scaffolding contractor.',
      highlights=['Contact forms', 'Local-business SEO'],tech='HTML · CSS · JavaScript · Netlify',
      repo='ASJ-Pipe-Scaffolding-',live='https://asjpipescaffolding.com'),
 dict(id='portfolio',title='Personal Portfolio',tag='DESIGN / DEVELOPMENT',
      summary='Selected work, technical interests and a direct way to connect.',
      highlights=['Project filtering', 'Netlify contact forms'],tech='HTML · CSS · JavaScript',
      repo='Stark-Portfolio',live='https://sjaichandran-portfolio.netlify.app/'),
 dict(id='pulse',title='ProjectPulse',tag='COLLABORATIVE APPLICATIONS',
      summary='A project workspace with role-based access and real-time activity.',
      highlights=['Live presence', 'Activity event replay'],tech='React · TypeScript · Express · PostgreSQL · Socket.IO',
      repo='ProjectPulse-')]

TOOLBOX=[
 ('Frontend',[('HTML','html5'),('CSS','css3'),('JavaScript','javascript'),('TypeScript','typescript'),('React','react'),('Next.js','nextjs'),('Tailwind CSS','tailwindcss'),('Bootstrap','bootstrap')]),
 ('Backend',[('Node.js','nodejs'),('Express.js','express'),('Flask','flask')]),
 ('Languages',[('Java','java'),('Python','python'),('C','c')]),
 ('Databases',[('MySQL','mysql'),('MongoDB','mongodb'),('SQLite','sqlite')]),
 ('AI / ML',[('TensorFlow','tensorflow'),('OpenCV','opencv'),('NumPy','numpy'),('Pandas','pandas'),('scikit-learn','scikitlearn'),('Matplotlib','matplotlib')]),
 ('AI / LLM',[('LLMs',None),('RAG',None),('Vector DB',None),('Prompt engineering',None),('Tool calling',None),('Agentic workflows',None)]),
 ('Tools',[('Git','git'),('GitHub','github'),('VS Code','vscode'),('Postman','postman'),('Jupyter / Colab','jupyter')])]
DOMAINS=[
 ('01','Full-stack engineering','Interfaces that connect to useful systems.',['React · Node.js · Express','APIs · database integration']),
 ('02','AI / LLM applications','Intelligence inside practical workflows.',['LLMs · RAG · tool calling','Prompts · agentic workflows']),
 ('03','Machine learning','From input data to evaluated models.',['TensorFlow · OpenCV','Preprocessing · model evaluation']),
 ('04','Cybersecurity research','Detecting threats and explaining decisions.',['Intrusion detection · hybrid deep learning','Explainable AI · SHAP / LIME']),
 ('05','Real-world development','Applications that serve an actual need.',['Business websites · forms · SEO','Deployment · practical automation'])]


def surface(w,h):
    im=Image.new('RGB',(w,h),BG)
    d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/max(h,1)
        d.line((0,y,w,y),fill=(5+int(2*t),14+int(3*t),25+int(4*t)))
    return im,d


def text(d,x,y,s,size=20,fill=WHITE,bold=False):
    d.text((x,y),s,font=font(size,bold),fill=fill)


def wrap(d,x,y,s,width,size=20,fill=MUTED,bold=False,leading=1.5):
    f=font(size,bold); line=''; lines=[]
    for word in s.split():
        candidate=f'{line} {word}'.strip()
        if d.textlength(candidate,font=f)>width and line:
            lines.append(line); line=word
        else: line=candidate
    if line: lines.append(line)
    for line in lines:
        assert d.textlength(line,font=f)<=width+1, (line,width)
        d.text((x,y),line,font=f,fill=fill); y+=round(size*leading)
    return y


def title(d,w,num,name,subtitle=None):
    text(d,32,24,num,13,AQUA)
    text(d,67,16,name,31,WHITE,True)
    if subtitle: text(d,32,68,subtitle,17,MUTED)


def png(im,folder,name):
    im.save(folder/name,optimize=True)


def make_whoami(w):
    mobile=w<800; h=400 if mobile else 310
    im,d=surface(w,h)
    text(d,32,23,'stark@jarvis:~',18,AQUA)
    text(d,w-135,23,'~/ whoami',16,MUTED)
    d.line((32,68,w-32,68),fill=LINE,width=1)
    text(d,32,88,'S. Jaichandran',31,WHITE,True)
    y=wrap(d,32,132,'AI-Integrated Full-Stack Developer',w-64,24,CYAN)
    y=wrap(d,32,y+10,'B.Tech Information Technology  /  Chennai, India',w-64,20,MUTED)
    end=wrap(d,32,y+17,'I build full-stack applications integrated with AI, intelligent automation and practical ML systems.',w-64,21,WHITE)
    assert end<h-10,(end,h)
    return im


def make_toolbox(w,icons):
    mobile=w<800
    rows=[]; current=110
    for category,techs in TOOLBOX:
        if category=='AI / LLM':
            nrows=3 if mobile else 2
            height=50+nrows*40
        else:
            cols=4 if mobile else 8
            nrows=math.ceil(len(techs)/cols)
            height=44+nrows*(98 if mobile else 91)
        rows.append((category,techs,current,height)); current+=height+14
    im,d=surface(w,current+12)
    title(d,w,'02','Tech toolbox','The tools behind the work.')
    for category,techs,y,height in rows:
        text(d,32,y,category,22,AQUA,True)
        if category=='AI / LLM':
            cols=2 if mobile else 3
            for i,(name,_) in enumerate(techs):
                px=32+(i%cols)*(w-64)/cols
                text(d,px,y+47+(i//cols)*39,name,20,WHITE)
        else:
            cols=4 if mobile else 8
            slot=(w-64)/cols
            for i,(name,iconname) in enumerate(techs):
                px=32+(i%cols)*slot
                py=y+44+(i//cols)*(98 if mobile else 91)
                icon=Image.open(icons/f'{iconname}.png').convert('RGBA')
                # Keep monochrome brands legible without changing their geometry.
                if iconname in ('express','flask','github'):
                    a=icon.getchannel('A'); icon=Image.new('RGBA',icon.size,'#dfedf2');icon.putalpha(a)
                icon=ImageOps.contain(icon,(36,36),Image.Resampling.LANCZOS)
                im.paste(icon,(round(px),round(py)),icon)
                labelsize=17 if not mobile else 19
                wrap(d,px,py+42,name,slot-6,labelsize,WHITE,leading=1.15)
        if category != 'Tools': d.line((32,y+height,w-32,y+height),fill=LINE,width=1)
    return im


def make_projects_header(w):
    im,d=surface(w,122)
    title(d,w,'03','Selected work','Real projects. Clear problems. Practical outcomes.')
    return im


def make_project(w,p,index):
    mobile=w<800
    h=(430 if mobile else 340) if p.get('feature') else (350 if mobile else 242)
    im,d=surface(w,h)
    accent=AQUA if index%2==0 else CYAN
    # Each project is a horizontal editorial module, with one larger feature.
    d.rectangle((0,0,4,h),fill=accent)
    text(d,32,22,p['tag'],13,accent)
    text(d,w-72,15,f'{index+1:02}',30,'#245260')
    y=wrap(d,32,54,p['title'],w-110,32 if p.get('feature') else 29,WHITE,True,1.22)
    y=wrap(d,32,y+13,p['summary'],w-70,21,MUTED,leading=1.35)
    y=wrap(d,32,y+15,'  /  '.join(p['highlights']),w-70,19,WHITE,leading=1.4)
    y=wrap(d,32,y+14,p['tech'],w-70,18,accent,leading=1.4)
    if p.get('feature'):
        nodes=['Meeting notes','Agent workflow','Human review']
        y=max(y+23,h-73)
        gap=(w-64)/3
        for j,node in enumerate(nodes):
            px=32+j*gap
            d.line((px,y,px+gap-20,y),fill='#27545d',width=1)
            d.ellipse((px,y-3,px+6,y+3),fill=accent)
            text(d,px,y+13,node,17,WHITE)
    else:
        assert y<h-12,(p['title'],y,h)
    return im


def make_capabilities(w):
    mobile=w<800; h=1000 if mobile else 675
    im,d=surface(w,h)
    title(d,w,'04','Capabilities','Across applications, data and research.')
    if mobile:
        for i,(n,name,desc,skills) in enumerate(DOMAINS):
            y=126+i*169
            d.line((40,y+5,40,y+159),fill=LINE,width=2)
            d.ellipse((35,y,45,y+10),fill=AQUA)
            text(d,62,y-10,name,25,WHITE,True)
            yy=wrap(d,62,y+31,desc,w-98,20,MUTED)
            for s in skills: yy=wrap(d,62,yy+8,s,w-98,20,CYAN)
    else:
        # Thin links tie the domains into a capability map without panel boxes.
        d.line((442,149,442,558),fill='#16303c',width=1)
        for yy in (149,329):
            d.line((407,yy,473,yy),fill='#16303c',width=1)
            d.ellipse((439,yy-3,445,yy+3),fill='#267b83')
        d.line((407,509,442,509),fill='#16303c',width=1)
        for i,(n,name,desc,skills) in enumerate(DOMAINS):
            x=32 if i%2==0 else 473
            y=130+(i//2)*180
            d.line((x,y,x+350,y),fill=LINE,width=2)
            text(d,x,y+14,n,15,AQUA)
            text(d,x+35,y+8,name,23,WHITE,True)
            text(d,x,y+50,desc,18,MUTED)
            for j,s in enumerate(skills):text(d,x,y+84+j*29,s,18,CYAN)
    return im


def make_research(w,raw):
    mobile=w<800; h=475 if mobile else 400
    im,d=surface(w,h)
    # A small personal motif sits only in the lower research section.
    arc=Image.open(raw/'03_arc_reactor.png').convert('RGBA')
    arc=ImageOps.contain(arc,(135,135),Image.Resampling.LANCZOS)
    mask=Image.new('L',arc.size,0);ImageDraw.Draw(mask).ellipse((3,3,arc.width-3,arc.height-3),fill=22)
    arc.putalpha(mask)
    im.paste(arc,(w-155,h-154),arc)
    title(d,w,'05','Research & innovation')
    y=wrap(d,32,80,'AI-Powered Intrusion Detection System',w-64,26,WHITE,True)
    y=wrap(d,32,y+14,'Hybrid models for network threats, with explanations that make predictions easier to inspect.',w-64,21,MUTED)
    y=wrap(d,32,y+20,'CNN + LSTM  ·  SHAP / LIME',w-64,23,CYAN)
    y=wrap(d,32,y+5,'NSL-KDD  ·  CICIDS2017',w-64,20,WHITE)
    y=wrap(d,32,y+19,'Exploring next',w-64,17,AQUA,True)
    end=wrap(d,32,y+3,'Autoencoders · Transformers · UNSW-NB15',w-64,19,MUTED)
    assert end<h-10,(end,h)
    return im


def make_education(w):
    mobile=w<800; h=560 if mobile else 405
    im,d=surface(w,h)
    title(d,w,'06','Education & training')
    d.line((39,97,39,h-44),fill=LINE,width=2)
    y=94
    for heading,body,foot in [
        ('B.Tech Information Technology','Vel Tech Rangarajan Dr. Sagunthala R&D Institute of Science and Technology','2026 · CGPA 8.3 / 10'),
        ('NIELIT Calicut','Data Analytics & Machine Learning Training',''),
        ('Wipro TalentNext','Java Full Stack Digital Skills Readiness Program','')]:
        d.ellipse((35,y+8,43,y+16),fill=AQUA)
        y=wrap(d,65,y,heading,w-100,24,WHITE,True)
        y=wrap(d,65,y+5,body,w-110,20,MUTED,leading=1.35)
        if foot:y=wrap(d,65,y+7,foot,w-110,20,CYAN)
        y+=24
    assert y<h+10,(y,h)
    return im


def make_activity(w,data):
    mobile=w<800; h=355 if mobile else 310
    im,d=surface(w,h)
    title(d,w,'07','GitHub activity','A snapshot of the public work.')
    text(d,32,111,str(data['public_repositories']),51,CYAN,True)
    text(d,85,124,'public repositories',21,WHITE)
    totals=Counter()
    for langs in data['languages'].values():totals.update(langs)
    totals.pop('Jupyter Notebook',None)
    total=sum(totals.values()); ranked=totals.most_common()
    colors={'TypeScript':'#3178c6','JavaScript':'#f1e05a','HTML':'#e34c26','CSS':'#8d70d6','Python':'#4f9ccc','Dockerfile':'#384d54'}
    y=189; x=32
    for name,n in ranked:
        ww=(w-64)*n/total
        d.rectangle((x,y,x+ww,y+12),fill=colors.get(name,CYAN)); x+=ww
    x=32; y=221
    for name,n in ranked:
        if n/total<.01:continue
        label=f'{name} {n/total:.0%}'
        ww=d.textlength(label,font=font(17))+26
        if x+ww>w-20:x=32;y+=30
        d.ellipse((x,y+8,x+5,y+13),fill=colors[name]);text(d,x+12,y,label,17,MUTED);x+=ww
    text(d,32,h-45,'Source bytes; notebooks excluded · '+data['verified_at'][:10],16,'#7f9dab')
    return im


def make_contact(w):
    im,d=surface(w,190 if w>=800 else 230)
    title(d,w,'08','Connect')
    y=wrap(d,32,79,'Let’s build something intelligent.',w-64,30,WHITE,True)
    wrap(d,32,y+13,'Open to AI, full-stack and intelligent application opportunities.',w-64,21,MUTED)
    return im


def make_footer(w):
    im,d=surface(w,150 if w>=800 else 185)
    d.line((32,6,w-32,6),fill=LINE,width=1)
    text(d,32,28,'S. Jaichandran',24,WHITE,True)
    text(d,32,65,'AI-Integrated Full-Stack Developer',19,CYAN)
    wrap(d,32,103,'Intelligent systems · real-world development · continuous learning',w-64,17,MUTED)
    return im


def picture(name,alt,href=None):
    markup=(f'<picture>\n  <source media="(max-width: 600px)" srcset="assets/profile/{name}-mobile.png">\n'
            f'  <img src="assets/profile/{name}.png" width="100%" alt="{html.escape(alt,quote=True)}">\n</picture>')
    return f'<a href="{href}">\n{markup}\n</a>' if href else markup


def build(source,output,evidence):
    raise RuntimeError('Legacy rasterized profile generator is retired. Edit README.md directly and use scripts/render_preview.mjs. Existing legacy code is retained for recovery only.')
    folder=output/'assets/profile'; folder.mkdir(parents=True,exist_ok=True)
    icons=evidence/'icons'; raw=source/'assets/morph_stages'
    facts=json.loads((evidence/'repos.json').read_text(encoding='utf-8'))
    repo_by_name={r['name']:r for r in facts}
    activity=json.loads((evidence/'activity.json').read_text(encoding='utf-8'))
    livechecks=json.loads((evidence/'live-links.json').read_text(encoding='utf-8'))
    for p in PROJECTS:
        assert p['repo'] in repo_by_name
        p['url']=repo_by_name[p['repo']]['html_url']
        if p.get('live'):assert any(c['url']==p['live'] and c['status']==200 and 'login' not in c['final_url'] for c in livechecks)
    sections=[('whoami',lambda w:make_whoami(w),'S. Jaichandran, AI-Integrated Full-Stack Developer. B.Tech IT. Chennai, India. I build full-stack applications integrated with AI, intelligent automation and practical ML systems.'),
              ('toolbox',lambda w:make_toolbox(w,icons),'Tech toolbox. '+'. '.join(c+': '+', '.join(n for n,_ in t) for c,t in TOOLBOX)),
              ('projects',make_projects_header,'Selected projects; each project image links to its verified GitHub repository.')]
    for i,p in enumerate(PROJECTS):
        sections.append((f'project-{p["id"]}',lambda w,p=p,i=i:make_project(w,p,i),p['title']+'. '+p['summary']+' '+p['tech']+'. '+'; '.join(p['highlights'])))
    sections += [('capabilities',make_capabilities,'Capabilities: full-stack engineering; AI/LLM applications; machine learning; cybersecurity research; real-world development.'),
                 ('research',lambda w:make_research(w,raw),'Intrusion-detection research: CNN and LSTM, SHAP and LIME, NSL-KDD and CICIDS2017. Exploring autoencoders, Transformers and UNSW-NB15.'),
                 ('education',make_education,'B.Tech Information Technology, Vel Tech Rangarajan Dr. Sagunthala R&D Institute of Science and Technology, 2026, CGPA 8.3/10. NIELIT Calicut: Data Analytics & Machine Learning Training. Wipro TalentNext: Java Full Stack Digital Skills Readiness Program.'),
                 ('activity',lambda w:make_activity(w,activity),'GitHub public repository and language snapshot, '+activity['verified_at'][:10]+'. Not live; source bytes excluding notebooks.'),
                 ('contact',make_contact,'Let’s build something intelligent. Open to AI, full-stack and intelligent application opportunities.'),
                 ('footer',make_footer,'S. Jaichandran — AI-Integrated Full-Stack Developer. Intelligent systems, real-world development and continuous learning.')]
    for name,fn,_ in sections:
        for w,suffix in [(900,''),(600,'-mobile')]:png(fn(w),folder,f'{name}{suffix}.png')
    hero='''<picture>
  <source media="(prefers-reduced-motion: reduce) and (max-width: 600px)" srcset="assets/hero-mobile.png">
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/hero-cinematic.png">
  <source media="(max-width: 600px)" srcset="assets/hero-mobile.gif">
  <img src="assets/hero-cinematic.gif" width="100%" alt="S. Jaichandran — AI-Integrated Full-Stack Developer. Building intelligent full-stack systems powered by AI. Tech-only morph: portrait, React, Node.js, Java, Python, Cyber AI.">
</picture>'''
    md=['<!-- Existing Stark345 profile: banner-led redesign. All raw morph assets preserved. -->',hero,'<br>']
    links={f'project-{p["id"]}':p['url'] for p in PROJECTS}
    links['research']=repo_by_name[PROJECTS[1]['repo']]['html_url']
    links['activity']='https://github.com/Stark345?tab=repositories'
    for name,_,alt in sections:
        md.append(picture(name,alt,links.get(name)))
        if name.startswith('project-'):
            p=next(p for p in PROJECTS if name==f'project-{p["id"]}')
            md.append(f'[View repository]({p["url"]})'+(f' · [Live website]({p["live"]})' if p.get('live') else ''))
        if name=='contact':
            md.append('[GitHub](https://github.com/Stark345) &nbsp; · &nbsp; [LinkedIn](https://www.linkedin.com/in/jaichandran-s-139a8b354) &nbsp; · &nbsp; [Portfolio](https://sjaichandran-portfolio.netlify.app/) &nbsp; · &nbsp; [Email](mailto:jaichandran20871@gmail.com)')
        if name=='activity':md.append('[Explore repositories](https://github.com/Stark345?tab=repositories) · [Recent public activity](https://github.com/Stark345?tab=overview)')
        md.append('<br>')
    (output/'README.md').write_text('\n\n'.join(md)+'\n',encoding='utf-8')
    # Review markup mirrors the README's image and link elements; CSS belongs only here.
    htmlbody='\n'.join(md)
    htmlbody=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',htmlbody)
    full='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S. Jaichandran — README review</title><style>
body{background:#0d1117;color:#e6edf3;font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0}main{max-width:900px;margin:32px auto;padding:0 16px}img{display:block;max-width:100%;height:auto}picture{display:block}a{color:#65dcdf;text-decoration:none}a:hover{text-decoration:underline}br{display:block;margin:10px 0}.review{padding:12px 16px;margin-bottom:22px;background:#14212d;color:#afc6d0;font-size:13px;border-radius:5px}p{margin:8px 0 18px}a:focus-visible{outline:2px solid #64eeef}@media(max-width:600px){main{margin:12px auto;padding:0 10px}}
</style></head><body><main><div class="review">Local README review · all project images link to verified repositories · no changes have been pushed</div>'''+htmlbody+'</main></body></html>'
    (output/'preview_readme.html').write_text(full,encoding='utf-8')
    # Deterministic proofs at GitHub-like desktop and narrow content widths.
    for width,mobile in [(900,False),(390,True)]:
        pieces=[]
        im=Image.open(output/('assets/hero-mobile.png' if mobile else 'assets/hero-cinematic.png')).convert('RGB')
        pieces.append(ImageOps.contain(im,(width,99999),Image.Resampling.LANCZOS))
        for name,_,_ in sections:
            im=Image.open(folder/(name+('-mobile' if mobile else '')+'.png')).convert('RGB')
            pieces.append(ImageOps.contain(im,(width,99999),Image.Resampling.LANCZOS))
            if name.startswith('project-') or name in ('contact','activity'):
                bar=Image.new('RGB',(width,40),'#0d1117');d=ImageDraw.Draw(bar)
                label='View repository' if name.startswith('project-') else ('GitHub  ·  LinkedIn  ·  Portfolio  ·  Email' if name=='contact' else 'Explore repositories  ·  Recent public activity')
                text(d,8,9,label,14,CYAN);pieces.append(bar)
        proof=Image.new('RGB',(width,sum(p.height for p in pieces)+16*(len(pieces)-1)),'#0d1117')
        yy=0
        for p in pieces:proof.paste(p,(0,yy));yy+=p.height+16
        proof.save(output/('readme-mobile.png' if mobile else 'readme-desktop.png'),optimize=True)
    verified=dict(verified_at=activity['verified_at'],projects=PROJECTS,live_links=livechecks,
                  skills_basis='User supplied full brief; public project READMEs and package manifests; published portfolio.',
                  education_basis='User supplied full brief: degree, institution, 2026, 8.3/10, NIELIT and Wipro training.',
                  research_basis='Repository supports CNN/LSTM, SHAP/LIME and NSL-KDD/CICIDS. Other supplied themes are labeled Exploring next.',
                  omitted=['unverified IEEE/IGNITE presentation','nonexistent or unverified old repository links','unsubstantiated performance metrics','login-protected ProjectPulse demo'],
                  reference_limit='Reference girl profile URL not supplied; section-variety criteria from the brief used instead.')
    (output/'profile-verification.json').write_text(json.dumps(verified,indent=2)+'\n',encoding='utf-8')
    (folder/'activity-data.json').write_text(json.dumps(activity,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(section_images=len(sections)*2,projects=len(PROJECTS),readme=str(output/'README.md')),indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--evidence',type=Path,required=True)
    a=parser.parse_args();build(a.source.resolve(),a.output.resolve(),a.evidence.resolve())
