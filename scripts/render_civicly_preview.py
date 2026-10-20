from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math,json
OUT=Path(__file__).resolve().parents[1]/'docs/media/civicly-preview'
OUT.mkdir(parents=True,exist_ok=True)
W,H=1200,720
BG='#F4F8F5';INK='#173E34';GREEN='#23694F';MUTED='#5F776D';LINE='#D7E4DC';LIGHT='#E8F2EC';GOLD='#A57532';BLUE='#397B93'
regular='/System/Library/Fonts/Supplemental/Arial.ttf'
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(n,b=False):return ImageFont.truetype(bold if b else regular,n)
def text(d,xy,s,n=20,color=INK,b=False):d.text(xy,s,font=font(n,b),fill=color)
def wrap(d,s,n,width,b=False):
 lines=[];current=''
 for word in s.split():
  trial=(current+' '+word).strip()
  if d.textlength(trial,font=font(n,b))>width and current:lines.append(current);current=word
  else:current=trial
 if current:lines.append(current)
 return lines
def para(d,xy,s,n=20,width=350,color=MUTED,b=False,gap=9):
 x,y=xy
 for line in wrap(d,s,n,width,b):text(d,(x,y),line,n,color,b);y+=n+gap
 return y
def rounded(d,box,fill='white',outline=LINE,r=18,width=2):d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)
def pill(d,xy,label,fill=LIGHT,color=GREEN,n=15):
 x,y=xy;tw=d.textlength(label,font=font(n,True));rounded(d,(x,y,x+tw+24,y+30),fill,fill,10);text(d,(x+12,y+6),label,n,color,True)
def node(d,xy,label,sub='',active=False,w=186):
 x,y=xy;rounded(d,(x-w/2,y-38,x+w/2,y+38),GREEN if active else 'white',GREEN if active else LINE,13)
 f=font(19,True); lines=wrap(d,label,19,w-20,True)
 for j,line in enumerate(lines[:2]):
  tw=d.textlength(line,font=f);text(d,(x-tw/2,y-20+23*j if len(lines)>1 else y-15),line,19,'white' if active else INK,True)
 if sub:
  tw=d.textlength(sub,font=font(14));text(d,(x-tw/2,y+45),sub,14,MUTED)
def edge(d,a,b,label='',active=False,offset=0):
 color=GREEN if active else '#AFBFB5';d.line((a,b),fill=color,width=4 if active else 2)
 ang=math.atan2(b[1]-a[1],b[0]-a[0]);l=10
 d.polygon([b,(b[0]-l*math.cos(ang-.5),b[1]-l*math.sin(ang-.5)),(b[0]-l*math.cos(ang+.5),b[1]-l*math.sin(ang+.5))],fill=color)
 if label:
  x=(a[0]+b[0])/2;y=(a[1]+b[1])/2-12+offset;tw=d.textlength(label,font=font(13,True));rounded(d,(x-tw/2-5,y-3,x+tw/2+5,y+19),'#FBFDFC','#FBFDFC',5);text(d,(x-tw/2,y),label,13,color,True)
def banner(d,title,detail):
 rounded(d,(477,495,1133,577),LIGHT,LIGHT,14)
 text(d,(498,510),title,19,GREEN,True);para(d,(498,540),detail,16,610,MUTED,gap=4)
scenes=[
 {'title':'Better coordination. More livable cities.','kicker':'01 / A BETTER CITY','body':'Cleaner streets. Safer roads. Healthier neighbourhoods. Help municipal teams understand civic problems and coordinate a better response.','role':'Connected teams. Informed action.','explain':'An AI agent platform connecting reports, evidence and departments—from investigation to follow-up.','caption':'A broader city vision; this demo explores waterlogging, road damage and waste.','label':'CIVIC PROBLEMS · CONNECTED RESPONSES'},
 {'title':'Connect the report to its history.','kicker':'02 / THE CONNECTED CASE','body':'At Market Junction, potholes returned after earlier repairs. The road, utility records and repair history become one connected case file.','role':'FalkorDB stores the connections.','explain':'Named relationships connect reports, assets and past work. A connection guides a check; it does not prove a cause.','caption':'A pipe being nearby is not enough: investigate sourced connections.','label':'FALKORDB DOMAIN GRAPH'},
 {'title':'Ask a question. Follow the evidence.','kicker':'03 / AI INVESTIGATION','body':'Could a pipe leak or weak ground explain the damage? Civicly’s AI chooses tools through MCP and compares what the records support.','role':'FalkorDB supplies context.','explain':'Graph paths retrieve related evidence. GraphRAG retrieves cited procedures from a separate document graph.','caption':'Inspection evidence is attributed, dated and reviewed; alternatives remain visible.','label':'AI + MCP + GRAPH RETRIEVAL'},
 {'title':'Turn findings into a reviewed plan.','kicker':'04 / PLAN & HUMAN APPROVAL','body':'Supported findings guide a response: isolate the pipe, repair the leak, verify that repair, then repair the road foundation.','role':'FalkorDB connects who and when.','explain':'Departments, task dependencies and source citations support the plan. Application services enforce human approval and safety gates.','caption':'Approval is for the exact plan and scope. AI advice alone cannot authorize work.','label':'CONNECTED TASKS + HUMAN AUTHORITY'},
 {'title':'Coordinate work in the right order.','kicker':'05 / AUTHORIZED WORK','body':'Water Utilities and Roads have different jobs. Road repair waits until the required utility work and verification are recorded.','role':'FalkorDB preserves the work trail.','explain':'Approved tasks link to work orders, responsible teams and status history. Validated services enforce each transition.','caption':'The demonstration uses authenticated, simulated department workflows.','label':'DEPARTMENTS + DEPENDENCIES'},
 {'title':'Completed work is not the finish line.','kicker':'06 / INDEPENDENT FOLLOW-UP','body':'A finished repair does not prove the problem is solved. Separate follow-up checks the declared success criteria before closure.','role':'FalkorDB connects action to outcome.','explain':'Dated observations link the intervention to a reviewed outcome. Missing evidence keeps the case under monitoring.','caption':'The road demo has recorded follow-up; it does not prove long-term durability.','label':'MONITORING + OUTCOME EVIDENCE'},
 {'title':'Remember what happened.','kicker':'07 / PERSISTENT MEMORY','body':'The next investigation should know what was tried, what failed and what later evidence showed. A saved workflow can pause and resume.','role':'Three FalkorDB-backed stores.','explain':'Case graph: evidence and outcomes. GraphRAG: sourced procedures. FalkorDBSaver: investigation checkpoints.','caption':'Retained history gives a later investigation context without erasing earlier findings.','label':'CASE MEMORY + KNOWLEDGE + CHECKPOINTS'},
 {'title':'Understand. Coordinate. Verify.','kicker':'08 / THE CIVICLY OBJECTIVE','body':'Connect the clues behind recurring civic problems. Help the right stakeholders address the cause—and check what happened afterwards.','role':'Powered by FalkorDB.','explain':'Connected evidence informs the agent. People approve action. Follow-up determines whether closure is justified.','caption':'Explore the saved investigation: Report → Evidence → Response → Outcome.','label':'CIVICLY · FROM REPORT TO RESOLUTION'},
]
def frame(i,phase):
 s=scenes[i];im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 # Header and identity
 for a,b in [((39,41),(60,35)),((60,35),(52,60)),((52,60),(39,41))]:d.line((a,b),fill=GREEN,width=3)
 for x,y in [(39,41),(60,35),(52,60)]:d.ellipse((x-5,y-5,x+5,y+5),fill=BG,outline=GREEN,width=3)
 text(d,(80,27),'Civicly',32,INK,True);text(d,(894,38),'Powered by FalkorDB',18,GREEN,True)
 d.line((32,86,1168,86),fill=LINE,width=2)
 text(d,(40,111),s['kicker'],15,GREEN,True)
 text(d,(40,145),s['title'],35,INK,True)
 para(d,(42,215),s['body'],22,360,INK,gap=11)
 y=para(d,(42,399),s['role'],20,365,GREEN,True,gap=7)
 para(d,(42,y+14),s['explain'],19,365,MUTED,gap=9)
 rounded(d,(448,213,1160,595),'#FBFDFC',LINE,20)
 pill(d,(472,229),s['label'])
 p=phase
 if i==0:
  for j,(label,sub) in enumerate([('Waterlogging','Drainage and rain'),('Road damage','Pipes and repair history'),('Waste buildup','Pickups and capacity')]):
   x=575+j*220;node(d,(x,345),label,sub,p==j,w=194)
  edge(d,(575,412),(800,467),'',True);edge(d,(1015,412),(800,467),'',True);edge(d,(800,412),(800,429),'',True)
  node(d,(800,467),'Coordinated action',active=True,w=248)
 elif i==1:
  edge(d,(656,326),(850,326),'describes',p>=1)
  edge(d,(949,365),(949,412),'history',p>=2)
  edge(d,(656,448),(850,342),'lies beneath',p>=3)
  node(d,(563,326),'Citizen report',active=p==0)
  node(d,(949,326),'Road damage',active=p==1)
  node(d,(563,448),'Water pipe',active=p==3)
  node(d,(949,458),'Past repairs',active=p==2)
  banner(d,'A connected case file','Relationships retain source references and relevant dates.')
 elif i==2:
  edge(d,(656,330),(851,330),'asks via MCP',p>=1)
  edge(d,(949,368),(949,410),'retrieves',p>=2)
  edge(d,(850,449),(656,449),'informs',p>=3)
  node(d,(563,330),'Civicly’s AI',active=p==0)
  node(d,(949,330),'FalkorDB',active=p==1)
  node(d,(949,449),'Graph evidence',active=p==2)
  node(d,(563,449),'Possible causes',active=p==3)
  banner(d,'GraphRAG adds cited procedural knowledge','Inspections support or challenge the possible explanations.')
 elif i==3:
  for j,(label,sub) in enumerate([('Findings','Reviewed evidence'),('Proposed plan','Tasks and sources'),('Human approval','Exact version + scope')]):
   x=579+j*220
   if j:edge(d,(x-127,351),(x-97,351),'',p>=j)
   node(d,(x,351),label,sub,p==j,w=196)
  banner(d,'The original road plan was analyst-assisted','The AI investigation, approval and field work are distinct stages.')
 elif i==4:
  for j,(label,sub) in enumerate([('Isolate pipe','Water Utilities'),('Repair leak','Water Utilities'),('Repair ground','Roads team')]):
   x=579+j*220
   if j:edge(d,(x-127,351),(x-97,351),'',p>=j)
   node(d,(x,351),label,sub,p==j,w=196)
  rounded(d,(701,430,1109,474),LIGHT,LIGHT,10);text(d,(721,443),'Utility verification before road repair',18,GREEN,True)
  banner(d,'Task dependencies make the handoff explicit','Work orders record authorized simulated actions and progress.')
 elif i==5:
  for j,(label,sub) in enumerate([('Work complete','Action recorded'),('Follow-up check','Independent evidence'),('Outcome reviewed','Close or keep watching')]):
   x=579+j*220
   if j:edge(d,(x-127,351),(x-97,351),'',p>=j)
   node(d,(x,351),label,sub,p==j,w=196)
  banner(d,'Resolution needs evidence of the outcome','A utility repair check alone cannot close the whole road case.')
 elif i==6:
  for j,(label,sub) in enumerate([('Case graph','History and outcomes'),('Document graph','Cited procedures'),('Checkpoint graph','Pause and resume')]):
   x=579+j*220;node(d,(x,345),label,sub,p==j,w=196)
  edge(d,(579,410),(800,470),'',True);edge(d,(1019,410),(800,470),'',True);edge(d,(799,410),(799,432),'',True)
  node(d,(800,470),'Next investigation',active=True,w=234)
  text(d,(492,552),'Separate stores, complementary roles—not one undifferentiated graph.',16,MUTED)
 else:
  for j,(label,sub) in enumerate([('Investigate','Connected evidence'),('Coordinate','Human-approved action'),('Verify','Follow-up and memory')]):
   x=579+j*220
   if j:edge(d,(x-127,351),(x-97,351),'',True)
   node(d,(x,351),label,sub,p==j,w=196)
  banner(d,'Every civic problem has a story.','Follow it from the original report to a justified outcome.')
 # Caption and progress, persistent truthful boundary
 para(d,(42,616),s['caption'],18,1110,INK,b=True,gap=4)
 labels=['Report','Graph','Investigate','Approve','Work','Verify','Memory','Civicly']
 for j,label in enumerate(labels):
  x=42+j*141;d.rounded_rectangle((x,659,x+126,664),radius=2,fill=GREEN if j<=i else LINE)
  text(d,(x,674),label,13,GREEN if j==i else MUTED,j==i)
 text(d,(42,701),'Illustrated workflow • Municipal data, field work and observations are simulated.',12,MUTED)
 return im
# Four purposeful highlight states per scene; 5 seconds per scene, 40 seconds total.
frames=[];durations=[]
for i in range(len(scenes)):
 for phase in range(4):
  im=frame(i,phase);frames.append(im);durations.append(1250)
 frame(i,3).save(OUT/f'scene-{i+1:02}.png')
# Shared palette avoids flashing colors between frames.
palette=Image.new('RGB',(400,240*len(scenes)))
for i in range(len(scenes)):palette.paste(frame(i,3).resize((400,240)),(0,i*240))
palette=palette.quantize(colors=128)
quantized=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
quantized[0].save(OUT/'civicly-explainer.gif',save_all=True,append_images=quantized[1:],duration=durations,loop=0,optimize=True,disposal=1)
contact=Image.new('RGB',(1200,1440),'white')
for i in range(8):contact.paste(frame(i,3).resize((600,360)),((i%2)*600,(i//2)*360))
contact.save(OUT/'storyboard.png')
(OUT/'storyboard.json').write_text(json.dumps({'duration_seconds':40,'format':'Illustrated explainer, not a screen recording','scenes':scenes},ensure_ascii=False,indent=2)+'\n')
with Image.open(OUT/'civicly-explainer.gif') as gif:
 assert gif.n_frames==32
 total=0
 for i in range(gif.n_frames):gif.seek(i);total+=gif.info['duration']
 assert total==40000,total
print('PASS: 32 GIF frames, 40 seconds, infinite loop; eight slide PNGs and storyboard')
print('GIF size:',(OUT/'civicly-explainer.gif').stat().st_size)
