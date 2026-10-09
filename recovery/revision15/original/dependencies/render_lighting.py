"""Photographic exposure aids are interior-only, never visible as emitters through facade glass."""
FILL_LIGHT_PREFIXES=('North-window daylight','Public-room bounced daylight','Reading-room north-window bounce','Restaurant broad daylight bounce','Elevator lobby daylight')
def apply_camera_fill_mode(scene,view_name):
 exterior=view_name in ['front','exterior','aerial','concourse_roof_exterior'] or view_name.startswith(('carriage','north_forecourt','north_plaza','north_park','north_entry','tower_'))
 for ob in scene.objects:
  if ob.type=='LIGHT' and ob.name.startswith(FILL_LIGHT_PREFIXES):
   # Exposure aids must not appear as luminous rectangles in glass/refraction.
   ob.data.specular_factor=0.0
   ob.data.transmission_factor=0.0
   if 'interior_fill_energy_w' not in ob.data:ob.data['interior_fill_energy_w']=ob.data.energy
   ob.data.energy=0.0 if exterior else float(ob.data['interior_fill_energy_w'])
 scene.view_settings.exposure=(.8 if scene.get('era')=='2017' else .6) if view_name.startswith('elevator_lobby') else 1.6 if scene.get('era')=='2017' and view_name.startswith('hall') else .4
 scene['render_exposure_note']='2017 Grand Hall cameras use exposure1.6 for dark enclosed fabric; lift-lobby cameras use0.8/0.6 for2017/2026; other cameras use0.4. Matched cameras do not imply identical photographic exposure'
 scene['lighting_mode']='World/sun exterior; auxiliary interior exposure fills disabled' if exterior else 'Photograph-inspired interior exposure with auxiliary fill; not measured fixture photometry'
