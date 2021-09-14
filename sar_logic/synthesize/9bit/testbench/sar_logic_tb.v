//`include "sar_logic.v"
`include "/usr/local/packages/tsmc_40/digital/Front_End/verilog/tcbn40lpbwp_200a/tcbn40lpbwp.v"
`timescale 100ps/1ps

module sar_logic_tb;

reg     clock;
reg     reset_n;
reg     cmp_decision;

wire    soc;
wire [8:0]  result;
wire [7:0]  switch_p;
wire [7:0]  switch_n;
wire [7:0]  switch_refp;
wire [7:0]  switch_refn;

sar_logic dut (clock, reset_n, cmp_decision, soc, result, switch_p, switch_n, switch_refp, switch_refn);

initial
begin
    clock = 0;
    forever
    begin
        #5 clock = ~clock;
    end
end

initial
begin
    reset_n = 1;
    cmp_decision = 0;
    # 7 reset_n = 0;
    # 15 reset_n = 1;
    cmp_decision = 1;
    #50 cmp_decision = 0;
    #40 cmp_decision = 1;
    #10 cmp_decision = 0;
    #40 cmp_decision = 1;
    #20 cmp_decision = 0;
    #10 cmp_decision = 1;
    #60 cmp_decision = 0;
end

initial
begin
    #300 $finish;
end

initial
begin
    $sdf_annotate("sar_logic.sdf",sar_logic);
    $dumpfile("sar_logic.dump");
    $dumpvars(0, sar_logic_tb);
end
endmodule
