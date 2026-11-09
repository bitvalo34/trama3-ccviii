"""Rutas ortogonales 3D discretas. Espacios nominales; no simula soldadura."""
import heapq,math
def route(components,wires):
    pitch=1.27; layers=8; occupied={}; power_nodes=set(); pins={}
    def ij(p):return (round((p['x']-5)/pitch),round((p['y']-5)/pitch))
    power_pins={}
    for c in components:
        for p in c['pins']:
            pins[ij(p)]=f"{c['ref']}.{p['number']}"
            if p['net'] in ['+5V_RAW','+5V_FUSED','+5V_ACT','+5V_SERVO','GND_ACT']:power_pins[ij(p)]=p['net']
    endpoints={f"{c['ref']}.{p['number']}":p for c in components for p in c['pins']}
    # Primero trayectos largos y potencia para reservar corredores accesibles.
    ordered=sorted(wires,key=lambda w:(not w['wire'].startswith('22'),-w['cut_mm']))
    for w in ordered:
        a=ij(endpoints[w['source']]);b=ij(endpoints[w['destination']]);net=w['net']
        def allowed(n):
            x,y,z=n
            if not(0<=x<=62 and 0<=y<=110 and 0<=z<layers):return False
            if not net.startswith('CLK_REMOTE') and 5+x*pitch<30 and 5+y*pitch>132:return False
            if (x,y) in pins and (x,y) not in (a,b):return False
            # Colas sobre la misma isla se comparten en la union soldada, no entre redes.
            if n in occupied and not ((x,y) in (a,b) and occupied[n]==net):return False
            if w['wire'].startswith('22'):
                for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    other=(x+dx,y+dy,z)
                    if other in power_nodes and occupied[other]!=net:return False
                    if other[:2] in power_pins and power_pins[other[:2]]!=net:return False
            return True
        start=(*a,0);todo=[(0,0,start)];dist={start:0};parent={};goal=None
        while todo:
            _,cost,n=heapq.heappop(todo)
            if cost!=dist[n]:continue
            if n[:2]==b:goal=n;break
            for dx,dy,dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
                nn=(n[0]+dx,n[1]+dy,n[2]+dz)
                if not allowed(nn):continue
                nc=cost+(2.5 if dz else 1)+(.025*nn[2])
                if nc<dist.get(nn,1e99):
                    dist[nn]=nc;parent[nn]=n
                    h=abs(nn[0]-b[0])+abs(nn[1]-b[1])
                    heapq.heappush(todo,(nc+h,nc,nn))
        if goal is None:raise RuntimeError('Sin ruta '+w['id'])
        path=[goal]
        while path[-1]!=start:path.append(parent[path[-1]])
        path.reverse()
        # Riser al destino: reservar desde capa 0 hasta profundidad final.
        for zz in range(goal[2]+1):
            nn=(*b,zz)
            if nn in occupied and occupied[nn]!=net:raise RuntimeError('Conflicto riser '+w['id'])
            occupied[nn]=net
            if w['wire'].startswith('22'):power_nodes.add(nn)
        for n in path:
            occupied[n]=net
            if w['wire'].startswith('22'):power_nodes.add(n)
        simple=[path[0]]
        for i in range(1,len(path)-1):
            d1=tuple(path[i][j]-path[i-1][j] for j in range(3));d2=tuple(path[i+1][j]-path[i][j] for j in range(3))
            if d1!=d2:simple.append(path[i])
        simple.append(path[-1])
        xyz=[[round(5+x*pitch,3),round(5+y*pitch,3),round(-2.4-1.5*z,2)] for x,y,z in simple]
        w['path']=xyz
        w['cut_mm']=math.ceil(sum(math.dist(p,q) for p,q in zip(xyz,xyz[1:]))+abs(xyz[0][2])+abs(xyz[-1][2])+12)
        w['notes']='Cable aislado continuo; doblar segun XYZ (z negativo bajo placa). Reservar 6mm por extremo; pelar solo 2mm. Cruces en capas diferentes.'
    return {'capas_usadas':1+max(round((-p[2]-2.4)/1.5) for w in wires for p in w['path']),'paso_xy_mm':pitch,'paso_z_mm':1.5,'metodo':'A* 3D con ocupacion de puntos y terminales. Distancias continuas se verifican por separado.'}
