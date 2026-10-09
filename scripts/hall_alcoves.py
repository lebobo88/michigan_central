"""Observed south alcove closure and restored sash fragments, photo-informed.
Ceiling/wall dimensions and window coordinates are inferred; a visible bank is not
proof of a complete hidden-room or window inventory. No photo pixels are loaded.
"""
_HA_PREVIOUS_GROUP=GROUP;GROUP='03 GREAT HALL | three sail vaults and colonnades'
_HA_CEILING=9.0
for _ha_xa,_ha_xb,_ha_cx in [(-31.8,-10,-20),(-10,10,0),(10,31.8,20)]:
 _ha_w=_ha_xb-_ha_xa
 # The south colonnade supports a flat coffered lower-aisle ceiling. The high
 # clerestory reveal is a separate volume above it, not an open horizontal slit.
 box(((_ha_xa+_ha_xb)/2,(27.7+31.6)/2,_HA_CEILING+.12),(_ha_w,31.6-27.7,.24),'Weathered concrete' if AGED else PL,'hall south alcove ceiling structural slab')
 if not AGED:
  for _ha_j in range(5):
   _ha_center=_ha_xa+(_ha_j+.5)*_ha_w/5
   for _ha_dx in [-_ha_w/10+.20,_ha_w/10-.20]:box((_ha_center+_ha_dx,29.65,8.92),(.15,3.4,.16),PL,'hall south alcove coffer longitudinal molding')
   for _ha_y in [28.08,31.22]:box((_ha_center,_ha_y,8.92),(_ha_w/5-.25,.16,.16),PL,'hall south alcove coffer return molding')
 if _ha_cx==0:continue # True open passage continues to the ticket lobby.
 _ha_lo=_ha_xa;_ha_hi=_ha_xb
 # Southeast: four complete sashes plus a fifth partially seen beyond a column
 # in post_p10. Southwest repeated bank is only a qualified visual approximation.
 _ha_centers=[_ha_cx+q for q in [-2.7,-.9,.9,2.7,5.7]] if not AGED else []
 if not AGED:
  wall_y_portals(31.15,_ha_lo,_ha_hi,9.55,[(_x,1.18,2.80) for _x in _ha_centers]+[(_ha_cx-8,1.5,3.35),(_ha_cx+8,1.5,3.35)],HALL_WALL_PLASTER,'hall restored south alcove back wall with observed sash fragments',.85)
  for _ha_x in _ha_centers:
   box((_ha_x,31.15,.52),(1.18,.85,1.04),HALL_WALL_PLASTER,'hall alcove window sill backing')
   # Shallow optical termination bounds the observed view without inventing the
   # room behind this window. The unseen suite remains a separate coverage gap.
   box((_ha_x,31.74,1.91),(1.18,.10,1.74),'Dark void','hall alcove unobserved rear optical stop')
   box((_ha_x,30.755,1.91),(1.14,.04,1.74),'Glass clear','hall alcove restored sash glazing')
   for _ha_dx in [-.59,0,.59]:box((_ha_x+_ha_dx,30.67,1.91),(.075,.13,1.92),'Window cast iron','hall alcove restored sash vertical frames')
   for _ha_z in [1.015,1.57,2.17,2.80]:box((_ha_x,30.67,_ha_z),(1.23,.13,.075),'Window cast iron','hall alcove restored sash horizontal frames')
   for _ha_dx in [-.32,.32]:box((_ha_x+_ha_dx,30.685,1.91),(.034,.10,1.73),'Window cast iron','hall alcove sash fine mullions')
   for _ha_dx in [-.74,.74]:box((_ha_x+_ha_dx,30.66,1.90),(.13,.16,2.18),PL,'hall alcove sash plaster surrounds')
   box((_ha_x,30.61,.91),(1.60,.25,.15),COL,'hall alcove sash stone sills')
   box((_ha_x,30.65,2.99),(1.60,.20,.15),PL,'hall alcove sash plaster headers')
  for _ha_door in [_ha_cx-8,_ha_cx+8]:
   box((_ha_door,31.74,1.675),(1.50,.10,3.35),'Dark void','hall alcove side doorway observed view boundary; unseen continuation omitted')
   for _ha_dx in [-.87,.87]:box((_ha_door+_ha_dx,30.67,1.77),(.23,.20,3.54),COL,'hall alcove side doorway jambs')
   box((_ha_door,30.65,3.53),(1.97,.25,.20),PL,'hall alcove side doorway lintel')
 else:
  box(((_ha_lo+_ha_hi)/2,31.15,9.55/2),(_ha_hi-_ha_lo,.85,9.55),PL,'2017 south alcove back wall | sash layout unverified')
 # Back wall-to-ceiling junction remains closed while broad source-inspired
 # molding distinguishes it from the freestanding colonnade entablature.
 for _ha_z,_ha_h,_ha_d in [(8.58,.14,.14),(8.79,.18,.20),(8.97,.12,.27)]:
  box(((_ha_lo+_ha_hi)/2,30.70,_ha_z),(_ha_hi-_ha_lo,_ha_d,_ha_h),'Weathered concrete' if AGED else PL,'hall alcove rear ceiling frieze')
# North alcove ceilings stop at each full-height monumental opening. They must
# never become a continuous slab across the three window/door voids.
for _ha_xa,_ha_xb,_ha_cx in [(-31.8,-10,-20),(-10,10,0),(10,31.8,20)]:
 for _ha_a,_ha_b in [(_ha_xa,_ha_cx-3.4),(_ha_cx+3.4,_ha_xb)]:
  box(((_ha_a+_ha_b)/2,2.2125,9.12),(_ha_b-_ha_a,3.375,.24),'Weathered concrete' if AGED else PL,'hall north flanking aisle ceiling; full-height openings retained')
scene['hall_alcove_evidence']=json.dumps(dict(south_ceiling='Flat paneled/coffered ceiling observed in post_p10/p11; approximate molding profiles',north_ceiling='Stops at full-height openings; detail_p15/post_p4/pre_p16',restored_sashes='Southeast source shows4complete plus fifth partly visible; total inventory unknown. Southwest repetition approximate.',sash_2017='Unverified, modern bank omitted',dimensions='Photo-proportioned, not surveyed'))
GROUP=_HA_PREVIOUS_GROUP
