import re,base64,struct,collections
def layers(path):
    s=open(path).read()
    out=[]
    for m in re.finditer(r'\[node name="([^"]+)" type="TileMapLayer" parent="([^"]*)"[^\]]*\]\n(.*?)(?=\n\[|\Z)',s,flags=re.S):
        name,parent,body=m.groups()
        d=re.search(r'tile_map_data = PackedByteArray\("([^"]*)"\)',body)
        cells={}
        if d:
            raw=base64.b64decode(d.group(1))
            for i in range(2,len(raw),12):
                x,y,src,ax,ay,alt=struct.unpack('<hhHHHH',raw[i:i+12])
                cells[(x,y)]=(src,ax,ay,alt)
        out.append((parent+'/'+name,cells))
    return out
def encode(cells):
    raw=struct.pack('<H',0)
    for (x,y),(src,ax,ay,alt) in cells.items():
        raw+=struct.pack('<hhHHHH',x,y,src,ax,ay,alt)
    return base64.b64encode(raw).decode()
