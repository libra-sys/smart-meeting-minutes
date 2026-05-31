const pptxgen=require("pptxgenjs");const pres=new pptxgen();pres.layout="LAYOUT_16x9";
const T={primary:"1b4332",secondary:"2d6a4f",accent:"52b788",light:"d8f3dc",bg:"FFFFFF"};
function B(s,n){s.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:T.accent}});s.addText(String(n),{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"})}
function Tb(s,t){s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:10,h:1.05,fill:{color:T.primary}});s.addText(t,{x:0.6,y:0.12,w:8.8,h:0.8,fontSize:30,fontFace:"Microsoft YaHei",color:"FFFFFF",bold:true})}
// S1
(()=>{const s=pres.addSlide();s.background={color:T.primary};
s.addText("智能会议纪要生成器",{x:0.7,y:1.2,w:8.6,h:1.4,fontSize:42,fontFace:"Microsoft YaHei",color:"FFFFFF",bold:true});
s.addText("Smart Meeting Minutes Generator",{x:0.7,y:2.5,w:8.6,h:0.5,fontSize:18,fontFace:"Arial",color:T.accent});
s.addText("议题拆分 · 决议提取 · 行动项追踪 · 分歧识别",{x:0.7,y:3.5,w:8.6,h:0.5,fontSize:15,fontFace:"Microsoft YaHei",color:T.light});
s.addText("多说话人识别 | 4种会议类型自适应 | v1.0.0",{x:0.7,y:4.9,w:8.6,h:0.4,fontSize:12,fontFace:"Microsoft YaHei",color:T.light})})();
// S2
(()=>{const s=pres.addSlide();s.background={color:T.bg};Tb(s,"核心功能");B(s,2);
[{num:"1",title:"智能解析",desc:"自动识别会议类型\n提取参与者/日期"},{num:"2",title:"议题拆解",desc:"3-7个独立议题\n标题+摘要+立场"},{num:"3",title:"行动项提取",desc:"任务+负责人+截止\n+优先级 精确追踪"},{num:"4",title:"分歧标记",desc:"识别争议点\n标注正反方状态"},{num:"5",title:"多格式输出",desc:"按类型自适应格式\n结构化纪要"},{num:"6",title:"质量校验",desc:"10项格式检查\n责任人缺失告警"}].forEach((f,i)=>{const c=i%3,r=Math.floor(i/3),x=0.4+c*3.1,y=1.4+r*2.0;s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:2.9,h:1.8,fill:{color:r%2?T.secondary:T.primary},rectRadius:0.08});s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:x+0.12,y:y+0.12,w:0.45,h:0.32,fill:{color:T.accent},rectRadius:0.04});s.addText(f.num,{x:x+0.12,y:y+0.12,w:0.45,h:0.32,fontSize:12,fontFace:"Arial",color:T.primary,bold:true,align:"center",valign:"middle"});s.addText(f.title,{x:x+0.12,y:y+0.55,w:2.66,h:0.4,fontSize:17,fontFace:"Microsoft YaHei",color:"FFFFFF",bold:true,align:"center"});s.addText(f.desc,{x:x+0.12,y:y+1.0,w:2.66,h:0.7,fontSize:11,fontFace:"Microsoft YaHei",color:"FFFFFF",align:"center",lineSpacingMultiple:1.3})})})();
// S3 - summary
(()=>{const s=pres.addSlide();s.background={color:T.primary};B(s,3);
s.addText("智能会议纪要生成器",{x:0.7,y:0.6,w:8.6,h:0.8,fontSize:34,fontFace:"Microsoft YaHei",color:"FFFFFF",bold:true});
[["效率提升","录音转文字秒级生成\n结构化纪要"],[ "精确追踪","行动项含负责人+截止\n时间 拒绝模糊"],[ "分歧可见","会议争议点清晰标注\n不再遗漏"],[ "格式规范","4种会议类型自适应\n10项校验保障质量"]].forEach((v,i)=>{const c=i%2,r=Math.floor(i/2),x=0.7+c*4.8,y=1.9+r*1.6;s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:0.5,h:0.5,fill:{color:T.accent},rectRadius:0.05});s.addText(String(i+1),{x,y,w:0.5,h:0.5,fontSize:16,fontFace:"Arial",color:T.primary,bold:true,align:"center",valign:"middle"});s.addText(v[0],{x:x+0.65,y,w:3.5,h:0.5,fontSize:18,fontFace:"Microsoft YaHei",color:T.accent,bold:true,valign:"middle"});s.addText(v[1],{x:x+0.65,y:y+0.5,w:4,h:0.9,fontSize:12,fontFace:"Microsoft YaHei",color:T.light,lineSpacingMultiple:1.3})});
s.addText("GitHub: github.com/libra-sys/smart-meeting-minutes",{x:0.7,y:5.1,w:8.6,h:0.3,fontSize:10,fontFace:"Arial",color:T.light});
})();
pres.writeFile({fileName:"./output/smart-meeting-minutes.pptx"}).then(()=>console.log("done")).catch(e=>console.error(e));
