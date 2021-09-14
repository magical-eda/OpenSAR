######################################################################################################################################################
## Function: This script can be sourced in RTL Compiler (Cadence synthesis tool) to synthesize the design. In order to open RC, type module load cadence/2009. Then, rc -64. 
## Author: Aseem Sayal
## Last Modified date: Feb 15, 2018 
######################################################################################################################################################

## VARIABLES SECTION (CHANGE ACCORDING TO DESIGN/LIBRARY REQUIREMENTS

set libs [glob /usr/local/packages/tsmc_40/digital/Front_End/timing_power_noise/NLDM/tcbn40lpbwp_200a/tcbn40lpbwptc.lib] 
set lefs [glob /usr/local/packages/tsmc_40/digital/Back_End/lef/tcbn40lpbwp_120c/lef/HVH_0d5_0/tcbn40lpbwp_8lm5X2ZRDL.lef]
set capTable [glob /usr/local/packages/tsmc_40/digital/Back_End/lef/tcbn40lpbwp_120c/techfiles/captable/cln40lp_1p08m+alrdl_5x2z_typical.captab]

set pincap_wordline 100
set pincap_other 10

set sdcFile [glob ./inputs/sar_logic.sdc]
set rtl_list_file [glob load_rtl.tcl]
set designName "sar_logic" 

set outDir RESULTS
set reportDir REPORTS

set outputNetlist "$outDir/${designName}.v"
set constraintsFile "$outDir/${designName}.sdc"
set sdfFile "$outDir/${designName}.sdf"

set timingReport "$reportDir/${designName}_timing.rpt"
set gatesReport "$reportDir/${designName}_gates.rpt"
set areaReport "$reportDir/${designName}_area.rpt"
set qorReport "$reportDir/${designName}_qor.rpt"
set powerReport "$reportDir/${designName}_power.rpt"

#set list_dont_use_cells [list ]

######################################################################################################################################################
## PLEASE DO NOT CHANGE ANYTHING IN THIS SECTION
######################################################################################################################################################

## Create output directory
if {![file exists outDir]} {file mkdir  $outDir}
if {![file exists reportDir]} {file mkdir  $reportDir}

## Loading LIBS, LEFS and capacitance table
set_attribute library $libs
set_attribute lef_library $lefs
set_attribute cap_table_file $capTable

## Sourcing RTL files
source $rtl_list_file

## Elaborating design 
elaborate $designName

read_sdc $sdcFile

if {0} {
	## Defining pin cap on all the output ports
	set allout [all_outputs]
	set_attribute external_pin_cap $pincap_wordline wordline*

	foreach port $allout {
		if {! [regexp wordline $port]} {
			set_attribute external_pin_cap $pincap_other $port
		}
	}

	## Reading constraints
	read_sdc $sdcFile

	## Defining driver 
	set allins [all_inputs]
	set clks [lsearch -regexp -all $allins [clock_ports]]
	set noclks_inputs [lreplace $allins $clks $clks]
	set_driving_cell -lib_cell $driver_cell $noclks_inputs
}


set errorInfo ""

## Flattening the design
ungroup -flatten -all

## Settting dont touch cells
## set_dont_use $list_dont_use_cells

## Synthesis
synthesize -to_mapped -effort high
synthesize -incremental -effort high

## Dumping reports
report timing > $timingReport
report qor > $qorReport
report gates > $gatesReport
report area > $areaReport
report power > $powerReport

## Generating netlist files
write_hdl > $outputNetlist
write_sdc > $constraintsFile
write_sdf > $sdfFile

exit
