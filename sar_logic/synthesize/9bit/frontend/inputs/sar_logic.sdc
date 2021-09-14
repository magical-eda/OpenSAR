###################################################################

# Created by write_sdc on Tue Nov 17 16:10:07 2020

###################################################################
current_design sar_logic

set_units -time ns -capacitance fF 

create_clock -period 1 -waveform "0 0.5" [get_ports clock] -name sys_clk

##**/Please add create_clock commands here after identifying the clocks/** 
#create_generated_clock -name sys_clk      -source [get_ports clk] -divide_by 1 -master_clock CLK [get_pins clk]

# set_dont_touch_network [get_clocks sys_clk]
# set_fix_hold [get_clocks sys_clk]

# clock uncertainty
set_clock_uncertainty -setup 0.01 [get_clocks sys_clk]
set_clock_uncertainty -hold 0.01 [get_clocks sys_clk]

# set_clock_latency 1 [get_clocks sys_clk]

# input & output delay
set in_ports [remove_from_collection [all_inputs] [get_ports *clock*]]

# 200 ohm
#set_drive [expr 0.2] [all_inputs]
set driver_cell INVD16BWP

# 30 ps input delay
set_input_delay -max 0.75 -clock [get_clocks sys_clk] $in_ports
set_input_delay -min 0.5 -clock [get_clocks sys_clk] $in_ports

# set input transition
set_input_transition 0.01 $in_ports

# set the output loading to be 5 fF
#set_load [lindex [get_attribute capacitance [get_lib_pins INVD4BWP/I]] 0] [all_outputs]
set_load 100 [all_outputs]
set_output_delay -max 0.75 -clock [get_clocks sys_clk] [all_outputs]
set_output_delay -min 0.5 -clock [get_clocks sys_clk] [all_outputs]

set allins [all_inputs]
set clks [lsearch -regexp -all $allins [clock_ports]]
set noclks_inputs [lreplace $allins $clks $clks]
set_driving_cell -lib_cell $driver_cell $noclks_inputs

