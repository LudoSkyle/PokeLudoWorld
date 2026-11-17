import sys,struct,zlib
def load(f):
    d=open(f,'rb').read(); p=8; idat=b''; pal=None; trns=None
    while p<len(d):
        l,=struct.unpack('>I',d[p:p+4]); t=d[p+4:p+8]; c=d[p+8:p+8+l]
        if t==b'IHDR': w,h,bd,ct=struct.unpack('>IIBB',c[:10])
        if t==b'IDAT': idat+=c
        if t==b'PLTE': pal=c
        if t==b'tRNS': trns=c
        p+=12+l
    assert bd==8,(bd,ct)
    bpp={6:4,2:3,3:1,0:1,4:2}[ct]; raw=zlib.decompress(idat); stride=w*bpp+1; prev=bytearray(w*bpp); rows=[]
    for y in range(h):
        ft=raw[y*stride]; line=bytearray(raw[y*stride+1:(y+1)*stride])
        if ft==1:
            for i in range(bpp,len(line)): line[i]=(line[i]+line[i-bpp])&255
        elif ft==2:
            for i in range(len(line)): line[i]=(line[i]+prev[i])&255
        elif ft==3:
            for i in range(len(line)): line[i]=(line[i]+((line[i-bpp] if i>=bpp else 0)+prev[i])//2)&255
        elif ft==4:
            for i in range(len(line)):
                a=line[i-bpp] if i>=bpp else 0; b=prev[i]; c=prev[i-bpp] if i>=bpp else 0
                pa=abs(b-c); pb=abs(a-c); pc=abs(a+b-2*c)
                line[i]=(line[i]+(a if pa<=pb and pa<=pc else (b if pb<=pc else c)))&255
        prev=line
        if ct==6: rows.append([tuple(line[i:i+4]) for i in range(0,len(line),4)])
        elif ct==2: rows.append([tuple(line[i:i+3])+(255,) for i in range(0,len(line),3)])
        elif ct==3: rows.append([tuple(pal[v*3:v*3+3])+((trns[v] if trns and v<len(trns) else 255),) for v in line])
        else: raise SystemExit('ct %d'%ct)
    return w,h,rows
def save(f,rows):
    h=len(rows); w=len(rows[0]); raw=b''.join(b'\0'+bytes(v for px in r for v in px[:3]) for r in rows)
    def ch(t,c): return struct.pack('>I',len(c))+t+c+struct.pack('>I',zlib.crc32(t+c)&0xffffffff)
    open(f,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
def flat(px,bg=(120,200,120)):
    a=px[3]/255; return tuple(int(px[i]*a+bg[i]*(1-a)) for i in range(3))
if __name__=='__main__':
    src,out,x0,y0,cw,ch_,scale=sys.argv[1],sys.argv[2],*map(int,sys.argv[3:8])
    chars=sys.argv[8:]  # "file:x:y" personnage collé (case 0 de la planche, réduit de moitié) pieds en (x,y) source
    w,h,rows=load(src)
    img=[[flat(rows[y][x]) if y<h and x<w else (0,0,0) for x in range(x0,x0+cw)] for y in range(y0,y0+ch_)]
    for c in chars:
        f,cx,cy,fw,fh,div=c.split(':'); cx,cy,fw,fh,div=int(cx),int(cy),int(fw),int(fh),int(div)
        _,_,cr=load(f)
        sw,sh=fw//div,fh//div
        for yy in range(sh):
            for xx in range(sw):
                px=cr[yy*div][xx*div]
                X=cx-x0-sw//2+xx; Y=cy-y0-sh+yy
                if px[3]>128 and 0<=X<cw and 0<=Y<ch_: img[Y][X]=px[:3]
    big=[]
    for y in range(ch_):
        line=[]
        for x in range(cw):
            px=img[y][x]
            for k in range(scale):
                line.append((255,0,255) if ((x0+x-1)%16==0 and k==0) else px)
        for k in range(scale):
            big.append([(255,0,255)]*len(line) if ((y0+y-1)%16==0 and k==0) else line)
    save(out,big)
