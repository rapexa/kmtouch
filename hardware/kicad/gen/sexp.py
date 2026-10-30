"""Tiny s-expression parser/writer + KiCad symbol lib helpers."""
import re
TOK=re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()]+))')
class Sym(str): pass
def parse(s):
    st=[[]];pos=0
    for m in TOK.finditer(s):
        o,c,q,a=m.groups()
        if o: st.append([])
        elif c: x=st.pop(); st[-1].append(x)
        elif q is not None: st[-1].append(q[1:-1].replace('\\"','"').replace('\\\\','\\'))
        elif a is not None: st[-1].append(Sym(a))
    return st[0]
def dump(x,ind=0):
    if isinstance(x,list):
        if all(not isinstance(e,list) for e in x):
            return "("+" ".join(dump(e) for e in x)+")"
        return "("+" ".join(dump(e) for e in x if not isinstance(e,list))+"\n"+"\n".join("  "*(ind+1)+dump(e,ind+1) for e in x if isinstance(e,list))+")"
    if isinstance(x,Sym): return str(x)
    if isinstance(x,bool): return "yes" if x else "no"
    if isinstance(x,(int,float)): return ("%.4f"%x).rstrip('0').rstrip('.') if isinstance(x,float) else str(x)
    return '"'+str(x).replace('\\','\\\\').replace('"','\\"')+'"'
def find(x,key): return [e for e in x if isinstance(e,list) and e and e[0]==key]
def find1(x,key):
    r=find(x,key); return r[0] if r else None
LIB="/opt/kc/root/usr/share/kicad/symbols/"
_cache={}
def load_symbol(lib,name):
    if lib not in _cache: _cache[lib]=parse(open(LIB+lib+".kicad_sym").read())[0]
    L=_cache[lib]
    syms={s[1]:s for s in find(L,'symbol')}
    s=syms[name]
    ext=find1(s,'extends')
    if ext:
        base=[list(e) if isinstance(e,list) else e for e in syms[ext[1]]]
        base=load_symbol(lib,ext[1])
        import copy; b=copy.deepcopy(base); b[1]=name
        # override properties
        props={p[1]:p for p in find(s,'property')}
        for i,e in enumerate(b):
            if isinstance(e,list) and e and e[0]=='property' and e[1] in props: b[i]=props[e[1]]
        for e in b:
            if isinstance(e,list) and e and e[0]=='symbol': e[1]=e[1].replace(ext[1],name,1)
        return b
    return s
def pins(sym):
    out=[]
    def walk(x):
        for e in x:
            if isinstance(e,list) and e:
                if e[0]=='pin':
                    at=find1(e,'at'); num=find1(e,'number')[1]; nm=find1(e,'name')[1]
                    ln=find1(e,'length')[1]
                    out.append(dict(num=num,name=nm,type=str(e[1]),x=float(at[1]),y=float(at[2]),rot=float(at[3]) if len(at)>3 else 0,len=float(ln)))
                elif e[0]=='symbol': walk(e)
    walk(sym); return out
def prop(sym,k):
    for p in find(sym,'property'):
        if p[1]==k: return p[2]
