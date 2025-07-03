asm SafetyEnforcerModel

import ../libraries/StandardLibrary

signature:
	enum domain Actions={FASTER, SLOWER, IDLE, LANE_LEFT, LANE_RIGHT}
	monitored inputAction: Actions
	monitored rightLaneFree: Boolean //no cars in the right lane within 200 meters - perception distance

	
	out outAction: Actions
	out currentAgentAction: Actions
	

	controlled l_vehicle: Real
	controlled w_vehicle: Real
	
	
definitions:
	
	
	// Keep right if right lane free
	macro rule r_keepRight =
		 if (rightLaneFree) then
		 	outAction := LANE_RIGHT
		 else outAction := inputAction
		 endif
	

	
		
	main rule r_Main =
		par
			currentAgentAction := inputAction
			r_keepRight[]
		endpar
	

  
 default init s0:
   function l_vehicle = 5.0
   function w_vehicle = 2.0
   
   
