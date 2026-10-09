"""Avoid adding a second disconnected skin to already-closed glass primitives.
Original open panes still require thickness. No optical material edits occur here.
"""
from collections import Counter

def glass_mesh_topology(mesh):
    incidence=Counter(tuple(sorted(edge)) for p in mesh.polygons for edge in p.edge_keys)
    return dict(vertices=len(mesh.vertices),polygons=len(mesh.polygons),edges=len(incidence),boundary_edges=sum(n==1 for n in incidence.values()),nonmanifold_edges=sum(n>2 for n in incidence.values()),closed=bool(incidence) and all(n==2 for n in incidence.values()))

def remove_redundant_glass_shells(scene):
    report=[]
    for ob in scene.objects:
        if ob.type!='MESH' or not any(m and m.name=='Glass clear' for m in ob.data.materials):continue
        state=glass_mesh_topology(ob.data)
        mods=[m for m in ob.modifiers if m.type=='SOLIDIFY' and m.name=='Physical glazing thickness 8mm']
        removed=[]
        if state['closed']:
            for m in mods:removed.append(dict(name=m.name,thickness_m=m.thickness));ob.modifiers.remove(m)
        report.append(dict(object=ob.name,topology=state,removed_modifiers=removed,retained_solidify_count=len([m for m in ob.modifiers if m.type=='SOLIDIFY']),material_changed=False,source_vertices_faces_uv_changed=False))
    return report
